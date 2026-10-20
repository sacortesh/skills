#!/usr/bin/env python3
"""
Build bounded "smart context" for the single AI review pass, in priority
order: PR intent -> diff hunks -> enclosing changed function/class ->
signatures/imports -> direct callers/callees (bounded text search,
labeled candidate not verified) -> relevant tests -> trusted repo rules.

Everything is bounded by --max-tokens / --max-files / --hop-depth /
--max-snippet-chars. Every included item records why it was included;
every item left out because a bound was hit is recorded in `omitted`
with a reason. Coverage is "complete" only if nothing was cut for
budget reasons — never silently truncated and reported as complete.

Token counts are an approximation (~4 chars/token, no tokenizer
dependency) and are always labeled as estimates, never exact.

Usage:
  python3 build_context.py --repo <path> --diff-json <file> --risk-json <file>
                            [--metadata-json <file>] [--max-tokens N]
                            [--max-files N] [--hop-depth N] [--max-snippet-chars N]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RISK_TOKEN_DEFAULTS = {"low": 8000, "medium": 16000, "high": 28000}
DEFAULT_MAX_FILES = 25
DEFAULT_HOP_DEPTH = 1
DEFAULT_MAX_SNIPPET_CHARS = 4000
DEFAULT_MAX_CALLER_HITS_PER_SYMBOL = 15

DECLARATION_RE = re.compile(
    r"^\s*(?:(?:export|public|private|protected|static|async|default)\s+)*"
    r"(?:def|function|func|fn|class|interface|struct|impl)\s+([A-Za-z_][A-Za-z0-9_]*)"
)
IMPORT_RE = re.compile(r"^\s*(import\s|from\s+\S+\s+import|require\(|use\s+|#include|using\s+)")
TEST_FILE_RE = re.compile(r"(?i)(^|/)(test_|.*_test\.|.*\.test\.|.*\.spec\.|test/|tests/|spec/)")
EXCLUDE_DIR_RE = re.compile(r"(^|/)(node_modules|vendor|dist|build|\.git|__pycache__|target)/")

TRUSTED_RULE_FILENAMES = [".code-review-rules.md", "CODEREVIEW.md", "docs/code-review-rules.md"]


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def run_git(repo_path: str, args: list[str], timeout: int = 20) -> str:
    out = subprocess.run(["git", "-C", repo_path, *args], capture_output=True, text=True, timeout=timeout, check=False)
    return out.stdout if out.returncode == 0 else ""


def get_file_lines(repo_path: str, sha: str, path: str) -> list[str]:
    content = run_git(repo_path, ["show", f"{sha}:{path}"])
    return content.splitlines()


def parse_hunk_new_line_starts(hunk_text: str) -> list[int]:
    starts = []
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", hunk_text, flags=re.MULTILINE):
        starts.append(int(m.group(1)))
    return starts


def find_enclosing_block(lines: list[str], line_no: int, max_span: int = 200) -> dict | None:
    """line_no is 1-indexed. Scans backward for a declaration, then forward
    for its end via brace-balance (C-like) or indentation (Python-like)."""
    idx = min(line_no - 1, len(lines) - 1)
    decl_idx = None
    decl_name = None
    for i in range(idx, max(-1, idx - 400), -1):
        m = DECLARATION_RE.match(lines[i])
        if m:
            decl_idx = i
            decl_name = m.group(1)
            break
    if decl_idx is None:
        return None

    decl_indent = len(lines[decl_idx]) - len(lines[decl_idx].lstrip())
    uses_braces = "{" in "\n".join(lines[decl_idx:decl_idx + 3])

    end_idx = decl_idx
    truncated = False
    if uses_braces:
        depth = 0
        seen_open = False
        for i in range(decl_idx, min(len(lines), decl_idx + max_span)):
            depth += lines[i].count("{") - lines[i].count("}")
            if "{" in lines[i]:
                seen_open = True
            end_idx = i
            if seen_open and depth <= 0:
                break
        else:
            truncated = True
    else:
        for i in range(decl_idx + 1, min(len(lines), decl_idx + max_span)):
            stripped = lines[i].strip()
            if stripped and (len(lines[i]) - len(lines[i].lstrip())) <= decl_indent:
                break
            end_idx = i
        else:
            truncated = True

    return {
        "name": decl_name,
        "start_line": decl_idx + 1,
        "end_line": end_idx + 1,
        "text": "\n".join(lines[decl_idx:end_idx + 1]),
        "truncated": truncated,
    }


def extract_imports(lines: list[str], cap: int = 25) -> list[str]:
    found = []
    for line in lines[:200]:  # imports are almost always near the top
        if IMPORT_RE.match(line):
            found.append(line.strip())
            if len(found) >= cap:
                break
    return found


def search_repo_for_symbol(repo_path: str, symbol: str, exclude_paths: set[str], max_hits: int) -> list[dict]:
    pattern = rf"\b{re.escape(symbol)}\b"
    hits = []
    rg = subprocess.run(["which", "rg"], capture_output=True, text=True, check=False)
    if rg.returncode == 0:
        out = subprocess.run(
            ["rg", "-n", "--no-heading", pattern, repo_path],
            capture_output=True, text=True, timeout=30, check=False,
        )
        for line in out.stdout.splitlines():
            parts = line.split(":", 2)
            if len(parts) != 3:
                continue
            path = str(Path(parts[0]).relative_to(repo_path)) if Path(parts[0]).is_absolute() else parts[0]
            if path in exclude_paths or EXCLUDE_DIR_RE.search(path):
                continue
            hits.append({"path": path, "line": int(parts[1]), "text": parts[2].strip()[:200]})
            if len(hits) >= max_hits:
                break
        return hits

    # Fallback: pure-Python walk, used only when ripgrep isn't on PATH.
    compiled = re.compile(pattern)
    for p in Path(repo_path).rglob("*"):
        if len(hits) >= max_hits:
            break
        rel = str(p.relative_to(repo_path))
        if not p.is_file() or rel in exclude_paths or EXCLUDE_DIR_RE.search(rel):
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if compiled.search(line):
                hits.append({"path": rel, "line": i, "text": line.strip()[:200]})
                if len(hits) >= max_hits:
                    break
    return hits


def build(repo_path: str, diff: dict, risk: dict, metadata: dict | None,
          max_tokens: int, max_files: int, hop_depth: int, max_snippet_chars: int) -> dict:
    manifest = {"included": [], "omitted": [], "token_estimate": 0, "coverage": "complete"}
    budget_hit = False

    def add(kind: str, source: str, reason: str, content: str):
        nonlocal budget_hit
        tokens = estimate_tokens(content)
        if manifest["token_estimate"] + tokens > max_tokens:
            manifest["omitted"].append({"kind": kind, "source": source, "reason": "token budget exceeded"})
            budget_hit = True
            return
        manifest["included"].append({"kind": kind, "source": source, "reason": reason,
                                      "tokens_estimate": tokens, "content": content[:max_snippet_chars]})
        manifest["token_estimate"] += tokens

    # 1. PR intent / acceptance criteria
    if metadata and not metadata.get("error"):
        intent = f"Title: {metadata.get('title', '')}\n\n{metadata.get('description', '')}"
        add("pr_intent", metadata.get("url", "connector"), "PR title/description as stated intent", intent)
        if metadata.get("labels"):
            add("pr_labels", metadata.get("url", "connector"), "PR labels", ", ".join(metadata["labels"]))
    else:
        manifest["omitted"].append({"kind": "pr_intent", "source": "connector", "reason": "no connector metadata available"})

    non_excluded = [f for f in diff.get("files", []) if not f.get("excluded")]
    changed_paths = {f["path"] for f in non_excluded}
    head_sha = diff.get("head_sha")

    enclosing_names: dict[str, set[str]] = {}

    for f in non_excluded[:max_files]:
        path = f["path"]
        hunks = f.get("hunks") or f.get("lockfile_manifest_summary") or f.get("note", "")

        # 2. Diff hunks themselves
        add("diff_hunk", path, "direct change", hunks)

        # 3. Enclosing function/class, best-effort
        if f.get("hunks") and head_sha:
            lines = get_file_lines(repo_path, head_sha, path)
            if not lines:
                manifest["omitted"].append({"kind": "enclosing_block", "source": path,
                                             "reason": "could not read file at head SHA"})
            else:
                starts = parse_hunk_new_line_starts(f["hunks"])
                seen_spans = set()
                for line_no in starts:
                    block = find_enclosing_block(lines, line_no)
                    if not block:
                        manifest["omitted"].append({
                            "kind": "enclosing_block", "source": f"{path}:{line_no}",
                            "reason": "no recognizable declaration found within 400 lines backward — "
                                      "bounded text search only, not a real parser; language may not match "
                                      "the generic function/class patterns this script knows",
                        })
                        continue
                    span = (block["start_line"], block["end_line"])
                    if span in seen_spans:
                        continue
                    seen_spans.add(span)
                    enclosing_names.setdefault(path, set()).add(block["name"])
                    note = " (truncated at span cap)" if block["truncated"] else ""
                    add("enclosing_block", f"{path}:{block['start_line']}-{block['end_line']}",
                        f"encloses changed line {line_no}{note}", block["text"])

                # 4. Signatures/imports
                imports = extract_imports(lines)
                if imports:
                    add("imports", path, "file-level imports/signatures", "\n".join(imports))

    # 5. Direct callers/callees — bounded text search, one hop by default
    if hop_depth > 0 and not budget_hit:
        for path, names in enclosing_names.items():
            for name in names:
                hits = search_repo_for_symbol(repo_path, name, changed_paths, DEFAULT_MAX_CALLER_HITS_PER_SYMBOL)
                if hits:
                    rendered = "\n".join(f"{h['path']}:{h['line']}: {h['text']}" for h in hits)
                    add("caller_candidate", f"symbol:{name}",
                        "candidate reference found by bounded text search — NOT a verified call edge; "
                        "dynamic dispatch, reflection, and unresolved imports are not tracked", rendered)
                else:
                    manifest["omitted"].append({"kind": "caller_candidate", "source": f"symbol:{name}",
                                                 "reason": "no references found by bounded text search"})

    # 6. Relevant tests
    if not budget_hit:
        all_symbols = {n for names in enclosing_names.values() for n in names}
        for symbol in all_symbols:
            hits = search_repo_for_symbol(repo_path, symbol, set(), DEFAULT_MAX_CALLER_HITS_PER_SYMBOL)
            test_hits = [h for h in hits if TEST_FILE_RE.search(h["path"])]
            if test_hits:
                rendered = "\n".join(f"{h['path']}:{h['line']}: {h['text']}" for h in test_hits)
                add("relevant_test", f"symbol:{symbol}", "test file referencing a changed symbol", rendered)

    # 7. Trusted repo rules
    for rule_file in TRUSTED_RULE_FILENAMES:
        p = Path(repo_path) / rule_file
        if p.exists():
            add("trusted_rules", rule_file, "repo-provided review rules", p.read_text(errors="ignore"))
            break
    else:
        manifest["omitted"].append({"kind": "trusted_rules", "source": "repo root",
                                     "reason": f"none of {TRUSTED_RULE_FILENAMES} found"})

    if budget_hit or any(o["reason"] == "token budget exceeded" for o in manifest["omitted"]):
        manifest["coverage"] = "partial"

    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--diff-json", required=True)
    parser.add_argument("--risk-json", required=True)
    parser.add_argument("--metadata-json", default=None)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument("--hop-depth", type=int, default=DEFAULT_HOP_DEPTH)
    parser.add_argument("--max-snippet-chars", type=int, default=DEFAULT_MAX_SNIPPET_CHARS)
    args = parser.parse_args()

    repo_path = str(Path(args.repo).resolve())
    diff = json.loads(Path(args.diff_json).read_text())
    risk = json.loads(Path(args.risk_json).read_text())
    metadata = json.loads(Path(args.metadata_json).read_text()) if args.metadata_json else None

    max_tokens = args.max_tokens or RISK_TOKEN_DEFAULTS.get(risk.get("risk", "medium"), RISK_TOKEN_DEFAULTS["medium"])

    manifest = build(repo_path, diff, risk, metadata, max_tokens, args.max_files, args.hop_depth, args.max_snippet_chars)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
