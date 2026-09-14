#!/usr/bin/env python3
"""Deterministic structural findings for one instruction file (SKILL.md,
CLAUDE.md, AGENTS.md, a subagent .md, or any pasted system prompt saved
to a file).

This script only reports facts a regex can find — it does not score
quality or judge tone. It exists so the model doing the audit spends its
judgment on things that actually need judgment (is this description
clear? is this example well chosen?) instead of re-deriving things a
script does more reliably, like "does this file have two nearly-identical
paragraphs" or "is the frontmatter even valid."

Checks:
  - frontmatter HARD gate: the actual platform-enforced rules for `name`
    (<=64 chars, lowercase/digits/hyphens only, no reserved words) and
    `description` (<=1024 chars, no XML tags, third person) — sourced
    from Anthropic's own Skill authoring docs, not a heuristic
  - frontmatter soft guidance: description word-count sanity range
  - line/char count
  - shouting-word density: MUST / NEVER / ALWAYS / IMPORTANT / CRITICAL,
    in all-caps or bold — a proxy for brittle, unexplained imperatives
    (see references/levers.md on why this is a yellow flag, not a hard
    failure)
  - duplicate and near-duplicate paragraphs — the "nothing appears twice"
    pruning check
  - procedural paragraphs — long paragraphs (>=70 words) that pack >=4
    sentences into one block, a proxy for several distinct points bundled
    together instead of separated into a list. Advisory only: Anthropic's
    own prompting guidance says to use numbered/bulleted steps "when the
    order or completeness of steps matters," but plenty of long
    paragraphs are flowing rationale/exposition where prose is correct
    (see references/levers.md's degrees-of-freedom section) — this flags
    candidates for a human to judge, it does not fail them
  - leftover placeholders (TODO, FIXME, TBD, lorem ipsum, <placeholder>)
  - table-of-contents presence for files over 100 lines (Claude may only
    partially read long files, per the platform docs)
  - internal doc links, so a human can eyeball whether references nest
    more than one level deep from SKILL.md (not recommended)
  - heading outline, for a quick structural skim

Usage:
  lint_structure.py <file> [--json] [--near-dup-threshold 0.85]
"""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
SHOUT_WORDS = ["MUST", "NEVER", "ALWAYS", "IMPORTANT", "CRITICAL", "REQUIRED"]
# Case-insensitive: unambiguous markers that never appear in normal prose.
# TODO/FIXME exclude a trailing ".md" or "/Word" — "TODO.md" or "a TODO/NOTES
# file" are prose discussing the note-taking pattern (see levers.md), not a
# leftover marker.
PLACEHOLDER_PATTERNS_CI = [
    r"\bTODO\b(?!\.md|/[A-Za-z])", r"\bFIXME\b(?!\.md|/[A-Za-z])", r"\bXXX\b", r"\bTBD\b",
    r"lorem ipsum", r"<[\w \-]*placeholder[\w \-]*>",
    r"\{\{\s*\w+\s*\}\}", r"\[INSERT[ _]", r"\[YOUR[ _]",
]
# Case-sensitive: the bare word PLACEHOLDER only counts in shouting
# all-caps form (how unfilled template scaffolds actually write it) —
# lowercase "placeholder" is common in prose *about* placeholders (like
# this script's own docstring) and would otherwise false-positive.
PLACEHOLDER_PATTERNS_CS = [r"\bPLACEHOLDER\b"]
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

# Hard limits, from https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
MAX_NAME_CHARS = 64
MAX_DESCRIPTION_CHARS = 1024
NAME_FORMAT_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_NAME_WORDS = ["anthropic", "claude"]
FIRST_PERSON_RE = re.compile(r"\bI\s*(can|will|'ll|am|'m|help|use|detect|turn)\b")
SECOND_PERSON_RE = re.compile(r"\byou\s+(can\s+use|can\s+process|should\s+use)\b", re.IGNORECASE)
TOC_LINE_THRESHOLD = 100
TOC_HEADING_RE = re.compile(r"^#{1,3}\s*(table of contents|contents)\s*$", re.IGNORECASE | re.MULTILINE)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)[^)]*\)")


def parse_frontmatter(text: str):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    fm_text = m.group(1)
    body = text[m.end():]
    fields = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip().strip('"').strip("'")
    return fields, body


def check_frontmatter(text: str):
    fields, body = parse_frontmatter(text)
    if fields is None:
        return {"present": False, "fields": {}, "hard_issues": ["no frontmatter block found"], "soft_issues": []}

    hard = []
    soft = []

    name = fields.get("name")
    if name is None:
        hard.append("missing 'name' field")
    else:
        if len(name) > MAX_NAME_CHARS:
            hard.append(f"name exceeds the {MAX_NAME_CHARS}-char platform limit ({len(name)} chars)")
        if not NAME_FORMAT_RE.match(name):
            hard.append("name must contain only lowercase letters, numbers, and hyphens")
        if "<" in name or ">" in name:
            hard.append("name must not contain XML tags")
        if any(w in name.lower() for w in RESERVED_NAME_WORDS):
            hard.append(f"name contains a reserved word ({'/'.join(RESERVED_NAME_WORDS)}) — not allowed")

    description = fields.get("description")
    if description is None:
        hard.append("missing 'description' field")
    else:
        if len(description) > MAX_DESCRIPTION_CHARS:
            hard.append(f"description exceeds the {MAX_DESCRIPTION_CHARS}-char platform limit ({len(description)} chars) — will be rejected/truncated, not just 'long'")
        if "<" in description or ">" in description:
            hard.append("description must not contain XML tags")
        if FIRST_PERSON_RE.search(description) or SECOND_PERSON_RE.search(description):
            hard.append("description should be third person (\"Processes X\"), not first/second person (\"I can...\"/\"you can use...\") — platform docs are explicit about this")

        word_count = len(description.split())
        if word_count < 8:
            soft.append(f"description is very short ({word_count} words) — likely won't trigger reliably")
        elif word_count > 200:
            soft.append(f"description is on the long side ({word_count} words, {len(description)}/{MAX_DESCRIPTION_CHARS} chars) — this loads for EVERY session, consider tightening even though it's under the hard limit")

    return {"present": True, "fields": fields, "hard_issues": hard, "soft_issues": soft}


def check_toc(text: str, lines: int):
    if lines <= TOC_LINE_THRESHOLD:
        return {"required": False, "present": None}
    return {"required": True, "present": bool(TOC_HEADING_RE.search(text))}


def find_internal_md_links(text: str):
    return sorted(set(MD_LINK_RE.findall(text)))


def shout_word_density(text: str):
    counts = {}
    for w in SHOUT_WORDS:
        # count both literal all-caps occurrences and **bolded** exact-word matches
        plain = len(re.findall(rf"\b{w}\b", text))
        counts[w] = plain
    total = sum(counts.values())
    lines = max(1, text.count("\n") + 1)
    return {
        "counts": counts,
        "total": total,
        "per_100_lines": round(total / lines * 100, 2),
    }


INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def mask_inline_code(text: str) -> str:
    """Blank out inline `code spans` (same length, so positions still line
    up) before scanning for placeholders. A backtick-quoted "TODO:" or
    "PLACEHOLDER" is almost always prose illustrating the literal syntax
    (like this docstring does), not an actual leftover marker."""
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), text)


def find_placeholders(text: str):
    masked = mask_inline_code(text)
    hits = []
    for pat in PLACEHOLDER_PATTERNS_CI:
        for m in re.finditer(pat, masked, re.IGNORECASE):
            snippet_start = max(0, m.start() - 20)
            snippet = text[snippet_start:m.end() + 20].replace("\n", " ")
            hits.append({"pattern": pat, "context": f"...{snippet}..."})
    for pat in PLACEHOLDER_PATTERNS_CS:
        for m in re.finditer(pat, masked):
            snippet_start = max(0, m.start() - 20)
            snippet = text[snippet_start:m.end() + 20].replace("\n", " ")
            hits.append({"pattern": pat, "context": f"...{snippet}..."})
    return hits


def find_duplicate_paragraphs(text: str, near_dup_threshold: float):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 40]
    exact = []
    near = []
    seen = {}
    for i, p in enumerate(paragraphs):
        norm = re.sub(r"\s+", " ", p.lower())
        if norm in seen:
            exact.append({"first_index": seen[norm], "duplicate_index": i, "text": p[:120]})
        else:
            seen[norm] = i

    normed = [re.sub(r"\s+", " ", p.lower()) for p in paragraphs]
    for i in range(len(normed)):
        for j in range(i + 1, len(normed)):
            if normed[i] == normed[j]:
                continue  # already caught as exact
            ratio = SequenceMatcher(None, normed[i], normed[j]).ratio()
            if ratio >= near_dup_threshold:
                near.append({"index_a": i, "index_b": j, "similarity": round(ratio, 3), "text_a": paragraphs[i][:120]})

    return {"exact_duplicates": exact, "near_duplicates": near, "paragraph_count": len(paragraphs)}


# A paragraph that crams several independent sentences/clauses into one
# block is a candidate for a list, regardless of whether it uses narrative
# transition words ("first," "then") — those turned out to be a weak
# signal (see the sentence this replaced: it missed both paragraphs that
# motivated this check). Sentence count is a rougher but more reliable
# proxy for "several distinct points bundled together." Paragraphs that
# already contain a markdown list, or the frontmatter block, are skipped
# — they're either already a list or not prose to begin with.
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z*\"“])")
LIST_MARKER_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s", re.MULTILINE)
PROCEDURAL_MIN_WORDS = 70
PROCEDURAL_MIN_SENTENCES = 4


def find_procedural_paragraphs(text: str):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 40]
    hits = []
    for i, p in enumerate(paragraphs):
        if p.startswith("---") or LIST_MARKER_RE.search(p):
            continue
        word_count = len(p.split())
        if word_count < PROCEDURAL_MIN_WORDS:
            continue
        sentence_count = len(SENTENCE_SPLIT_RE.split(p))
        if sentence_count >= PROCEDURAL_MIN_SENTENCES:
            hits.append({"index": i, "word_count": word_count, "sentence_count": sentence_count, "text": p[:120]})
    return hits


def heading_outline(text: str):
    return [{"level": len(m.group(1)), "text": m.group(2).strip()} for m in HEADING_RE.finditer(text)]


def analyze(path: Path, near_dup_threshold: float):
    text = path.read_text(errors="replace")
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    return {
        "file": str(path),
        "lines": lines,
        "chars": len(text),
        "frontmatter": check_frontmatter(text),
        "shout_words": shout_word_density(text),
        "placeholders": find_placeholders(text),
        "duplicates": find_duplicate_paragraphs(text, near_dup_threshold),
        "procedural_paragraphs": find_procedural_paragraphs(text),
        "toc": check_toc(text, lines),
        "internal_md_links": find_internal_md_links(text),
        "headings": heading_outline(text),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--near-dup-threshold", type=float, default=0.85)
    args = ap.parse_args()

    p = Path(args.file)
    if not p.is_file():
        print(f"error: not a file: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = analyze(p, args.near_dup_threshold)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"{result['file']} — {result['lines']} lines, {result['chars']} chars\n")

    fm = result["frontmatter"]
    print(f"frontmatter: {'present' if fm['present'] else 'MISSING'}")
    for issue in fm["hard_issues"]:
        print(f"  [HARD] {issue}")
    for issue in fm.get("soft_issues", []):
        print(f"  [soft] {issue}")

    sw = result["shout_words"]
    print(f"\nshouting words: {sw['total']} total ({sw['per_100_lines']} per 100 lines)")
    for w, c in sw["counts"].items():
        if c:
            print(f"  {w}: {c}")

    ph = result["placeholders"]
    if ph:
        print(f"\nplaceholders/leftovers found: {len(ph)}")
        for h in ph[:10]:
            print(f"  - {h['context']}")
    else:
        print("\nplaceholders/leftovers: none found")

    dup = result["duplicates"]
    print(f"\nparagraphs analyzed: {dup['paragraph_count']}")
    if dup["exact_duplicates"]:
        print(f"  exact duplicates: {len(dup['exact_duplicates'])}")
        for d in dup["exact_duplicates"][:5]:
            print(f"    - paragraphs {d['first_index']} & {d['duplicate_index']}: \"{d['text']}...\"")
    if dup["near_duplicates"]:
        print(f"  near-duplicates (>={args.near_dup_threshold}): {len(dup['near_duplicates'])}")
        for d in dup["near_duplicates"][:5]:
            print(f"    - paragraphs {d['index_a']} & {d['index_b']} (similarity {d['similarity']}): \"{d['text_a']}...\"")
    if not dup["exact_duplicates"] and not dup["near_duplicates"]:
        print("  no duplicate/near-duplicate paragraphs found")

    proc = result["procedural_paragraphs"]
    if proc:
        print(f"\nprocedural paragraphs (candidates for bulleting, see rubric.md dimension 2): {len(proc)}")
        for h in proc[:5]:
            print(f"  - paragraph {h['index']} ({h['word_count']} words, {h['sentence_count']} sentences): \"{h['text']}...\"")

    toc = result["toc"]
    if toc["required"]:
        status = "present" if toc["present"] else "MISSING (file is over 100 lines)"
        print(f"\ntable of contents: {status}")

    links = result["internal_md_links"]
    if links:
        print(f"\ninternal .md links found: {len(links)} — verify these stay one level deep from SKILL.md")
        for link in links:
            print(f"  - {link}")

    print(f"\nheadings: {len(result['headings'])}")
    for h in result["headings"]:
        print(f"  {'  ' * (h['level'] - 1)}{'#' * h['level']} {h['text']}")


if __name__ == "__main__":
    main()
