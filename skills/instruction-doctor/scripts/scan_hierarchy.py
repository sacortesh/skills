#!/usr/bin/env python3
"""Enumerate, in load-priority order, every file that lands in an agent's
context window for a given repo — and estimate the token cost of each.

The point: some files load on EVERY session regardless of task (global
CLAUDE.md, project CLAUDE.md, every skill's frontmatter, every subagent's
frontmatter). Others load only when triggered (a skill body, an agent
body). Bloat in the first group taxes every single conversation; bloat in
the second only taxes the sessions that actually use that skill/agent.
Fixing the wrong one first is a common, avoidable mistake — this script
makes the distinction visible instead of leaving it to guesswork.

Layers, in the order they're accounted for:
  1. global_claude_md   ~/.claude/CLAUDE.md                — always loaded
  2. project_claude_md  <repo>/CLAUDE.md                    — always loaded
  3. nested_claude_md   any other CLAUDE.md under the repo   — loaded when
                        Claude Code operates in that subtree
  4. agents_md          any AGENTS.md found                 — flagged for
                        possible duplication with CLAUDE.md
  5. skill_frontmatter  name+description of every SKILL.md  — always loaded
  6. skill_body         the rest of each SKILL.md            — on-trigger
  7. subagent_frontmatter  name+description of every agent .md — always loaded
  8. subagent_body      the rest of each agent .md            — on-spawn

Bundled resources (scripts/references/assets referenced BY a skill) are not
walked here — they cost ~0 until the model chooses to read them, which is
the entire point of progressive disclosure.

Usage:
  scan_hierarchy.py [repo_path] [--json]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from count_tokens import heuristic_tokens, tiktoken_tokens  # noqa: E402

IGNORED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build",
    ".next", ".turbo", "target", ".cache", "coverage", ".pytest_cache",
}

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


def estimate(text: str):
    tk = tiktoken_tokens(text)
    return tk if tk is not None else heuristic_tokens(text)


def parse_frontmatter(text: str):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text, ""
    fm_text = m.group(1)
    body = text[m.end():]
    fields = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip().strip('"').strip("'")
    return fields, body, fm_text


def repo_root(start: Path) -> Path:
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except Exception:
        pass
    return start


def find_files(root: Path, filename: str):
    hits = []
    for p in root.rglob(filename):
        if any(part in IGNORED_DIRS for part in p.parts):
            continue
        hits.append(p)
    return hits


def find_skill_dirs(root: Path):
    dirs = set()
    for candidate in [root / ".claude" / "skills", root / "skills"]:
        if candidate.is_dir():
            dirs.add(candidate)
    home_skills = Path.home() / ".claude" / "skills"
    if home_skills.is_dir():
        dirs.add(home_skills)
    return dirs


def find_agent_files(root: Path):
    files = []
    for candidate in [root / ".claude" / "agents", Path.home() / ".claude" / "agents"]:
        if candidate.is_dir():
            files.extend(sorted(candidate.glob("*.md")))
    return files


def entry(layer: str, scope: str, path: Path, text: str, name=None, synced_with=None):
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    tokens = estimate(text)
    return {
        "layer": layer,
        "scope": scope,
        "path": str(path),
        "name": name,
        "lines": lines,
        "estimated_tokens": tokens,
        # True when this file is a symlink to (or byte-identical copy of)
        # another entry already counted — e.g. the common `ln -s AGENTS.md
        # CLAUDE.md` pattern. Kept in the list for visibility, excluded
        # from the budget sum so the same content isn't paid for twice.
        "synced_with": synced_with,
        "counts_toward_budget": synced_with is None,
    }


def files_are_synced(a: Path, b: Path) -> bool:
    """True if `a` and `b` are the same file on disk (symlink) or have
    byte-identical content (a plain copy kept in sync by hand)."""
    try:
        if a.resolve() == b.resolve():
            return True
    except OSError:
        pass
    try:
        return a.read_bytes() == b.read_bytes()
    except OSError:
        return False


def scan(root: Path):
    entries = []

    global_claude = Path.home() / ".claude" / "CLAUDE.md"
    if global_claude.is_file():
        text = global_claude.read_text(errors="replace")
        entries.append(entry("global_claude_md", "always", global_claude, text))

    project_claude = root / "CLAUDE.md"
    if project_claude.is_file():
        text = project_claude.read_text(errors="replace")
        entries.append(entry("project_claude_md", "always", project_claude, text))

    for p in find_files(root, "CLAUDE.md"):
        if p in (project_claude,):
            continue
        text = p.read_text(errors="replace")
        entries.append(entry("nested_claude_md", "conditional (directory-scoped)", p, text))

    claude_md_candidates = [e for e in entries if e["layer"] in ("global_claude_md", "project_claude_md", "nested_claude_md")]
    for p in find_files(root, "AGENTS.md"):
        text = p.read_text(errors="replace")
        synced_with = None
        for c in claude_md_candidates:
            if files_are_synced(p, Path(c["path"])):
                synced_with = c["path"]
                break
        entries.append(entry("agents_md", "always (if tool honors AGENTS.md)", p, text, synced_with=synced_with))

    seen_skills = set()
    for skills_dir in find_skill_dirs(root):
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            if skill_md in seen_skills:
                continue
            seen_skills.add(skill_md)
            text = skill_md.read_text(errors="replace")
            fields, body, fm_text = parse_frontmatter(text)
            name = fields.get("name", skill_md.parent.name)
            entries.append(entry("skill_frontmatter", "always", skill_md, fm_text, name=name))
            entries.append(entry("skill_body", "on-trigger", skill_md, body, name=name))

    seen_agents = set()
    for agent_md in find_agent_files(root):
        if agent_md in seen_agents:
            continue
        seen_agents.add(agent_md)
        text = agent_md.read_text(errors="replace")
        fields, body, fm_text = parse_frontmatter(text)
        name = fields.get("name", agent_md.stem)
        entries.append(entry("subagent_frontmatter", "always", agent_md, fm_text, name=name))
        entries.append(entry("subagent_body", "on-spawn", agent_md, body, name=name))

    is_always = lambda e: e["scope"].startswith("always")  # catches "always" and "always (if tool honors AGENTS.md)"
    budgeted_always = [e for e in entries if is_always(e) and e["counts_toward_budget"]]
    skipped_synced = [e for e in entries if is_always(e) and not e["counts_toward_budget"]]
    always_tokens = sum(e["estimated_tokens"] for e in budgeted_always)
    conditional = [e for e in entries if not is_always(e)]

    return {
        "repo_root": str(root),
        "entries": entries,
        "summary": {
            "always_loaded_token_budget": always_tokens,
            "always_loaded_file_count": len(budgeted_always),
            "synced_pairs_excluded": len(skipped_synced),
            "conditional_entry_count": len(conditional),
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo_path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--line-threshold", type=int, default=500)
    args = ap.parse_args()

    root = repo_root(Path(args.repo_path).resolve())
    result = scan(root)

    for e in result["entries"]:
        e["over_line_threshold"] = e["lines"] > args.line_threshold

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"repo root: {result['repo_root']}\n")
    layer_order = [
        "global_claude_md", "project_claude_md", "nested_claude_md", "agents_md",
        "skill_frontmatter", "skill_body", "subagent_frontmatter", "subagent_body",
    ]
    for layer in layer_order:
        rows = [e for e in result["entries"] if e["layer"] == layer]
        if not rows:
            continue
        print(f"## {layer}  ({rows[0]['scope']})")
        for r in rows:
            flag = "  [OVER LINE THRESHOLD]" if r["over_line_threshold"] else ""
            if not r["counts_toward_budget"]:
                flag += f"  [SYNCED with {r['synced_with']} — not double-counted]"
            label = f" ({r['name']})" if r["name"] else ""
            print(f"  {r['path']}{label} — {r['lines']} lines, ~{r['estimated_tokens']} tokens{flag}")
        print()

    s = result["summary"]
    print("## summary")
    print(f"  always-loaded token budget (every session, regardless of task): ~{s['always_loaded_token_budget']} tokens")
    print(f"  always-loaded file/section count: {s['always_loaded_file_count']}")
    if s["synced_pairs_excluded"]:
        print(f"  synced CLAUDE.md/AGENTS.md pairs excluded from budget (symlink or identical content): {s['synced_pairs_excluded']}")
    print(f"  conditional (on-trigger/on-spawn) entries: {s['conditional_entry_count']}")


if __name__ == "__main__":
    main()
