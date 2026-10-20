#!/usr/bin/env python3
"""
Heuristic risk assessment — no model call. See references/risk-heuristics.md
for the dimensions and what risk level controls downstream.

Usage:
  python3 assess_risk.py --diff-json <collect_diff.py output>
"""
import argparse
import json
import re
import sys
from pathlib import Path

AUTH_SECRETS_PATTERNS = [
    r"(^|/)(auth|session|permission|acl)s?(/|\.)", r"(?i)api[_-]?key",
    r"(?i)\btoken\b", r"(?i)\bpassword\b", r"(?i)\bcredential",
    r"(^|/)payments?/", r"(?i)\bstripe\b", r"(?i)\bbilling\b",
]
DATA_PATTERNS = [
    r"(^|/)migrations?/", r"(?i)\bDROP\s+TABLE\b", r"(?i)\bDELETE\s+FROM\b",
    r"(?i)\bTRUNCATE\b", r"(^|/)schema\.(sql|prisma|graphql)$",
]
INFRA_CONCURRENCY_PATTERNS = [
    r"(?i)\bmutex\b", r"(?i)\bsemaphore\b", r"(?i)\block\(", r"(^|/)(terraform|k8s|helm)/",
    r"(^|/)docker-compose\.ya?ml$", r"(^|/)Dockerfile$",
]
PUBLIC_API_PATTERNS = [
    r"(^|/)openapi\.ya?ml$", r"(^|/)schema\.graphql$", r"\.proto$",
]
LARGE_DIFF_FILE_THRESHOLD = 20
LARGE_DIFF_LINE_THRESHOLD = 800
CALLER_COUNT_HIGH_THRESHOLD = 10  # used only if a caller count is supplied via --caller-counts


def match_any(patterns: list[str], text: str) -> str | None:
    for p in patterns:
        if re.search(p, text):
            return p
    return None


def has_test_sibling(changed_paths: list[str]) -> bool:
    for p in changed_paths:
        name = p.rsplit("/", 1)[-1]
        if re.search(r"(?i)(test|spec)", name):
            return True
    return False


def assess(diff: dict, caller_counts: dict[str, int] | None = None) -> dict:
    files = [f for f in diff.get("files", []) if not f.get("excluded")]
    reasons = []
    limitations = [
        "Keyword/path heuristics only, not static analysis — risk expressed purely in "
        "logic with no recognizable keyword or path match will be missed.",
    ]

    for f in files:
        path = f["path"]
        haystack = path + "\n" + (f.get("hunks", "") or f.get("lockfile_manifest_summary", ""))

        hit = match_any(AUTH_SECRETS_PATTERNS, haystack)
        if hit:
            reasons.append(f"auth/secrets/payments pattern in {path} (matched: {hit})")

        hit = match_any(DATA_PATTERNS, haystack)
        if hit:
            reasons.append(f"data deletion/migration pattern in {path} (matched: {hit})")

        hit = match_any(INFRA_CONCURRENCY_PATTERNS, haystack)
        if hit:
            reasons.append(f"shared-state/concurrency/infra pattern in {path} (matched: {hit})")

        hit = match_any(PUBLIC_API_PATTERNS, haystack)
        if hit:
            reasons.append(f"public API/schema file touched: {path}")

    if caller_counts:
        for path, count in caller_counts.items():
            if count >= CALLER_COUNT_HIGH_THRESHOLD:
                reasons.append(f"{path} has {count} referencing locations found — shared-utility risk")

    all_paths = [f["path"] for f in files]
    total_changed_lines = sum((f.get("additions") or 0) + (f.get("deletions") or 0) for f in files)
    if len(all_paths) >= LARGE_DIFF_FILE_THRESHOLD or total_changed_lines >= LARGE_DIFF_LINE_THRESHOLD:
        reasons.append(f"large diff: {len(all_paths)} files, ~{total_changed_lines} changed lines")

    source_changed = any(not re.search(r"(?i)(test|spec)", p) for p in all_paths)
    if source_changed and all_paths and not has_test_sibling(all_paths):
        reasons.append("source files changed with no test file touched in the same diff")

    if not reasons:
        level = "low"
    elif any(r.startswith(("auth/secrets", "data deletion")) for r in reasons):
        level = "high"
    else:
        level = "medium"

    return {"risk": level, "reasons": reasons, "limitations": limitations}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diff-json", required=True, help="Path to collect_diff.py's JSON output")
    parser.add_argument("--caller-counts", default=None,
                         help="Optional path to a JSON object mapping changed file path -> reference count found elsewhere in the repo")
    args = parser.parse_args()

    diff = json.loads(Path(args.diff_json).read_text())
    caller_counts = None
    if args.caller_counts:
        caller_counts = json.loads(Path(args.caller_counts).read_text())

    result = assess(diff, caller_counts)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
