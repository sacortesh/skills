#!/usr/bin/env python3
"""
Validate the AI review pass's output against references/schema.json,
verify every finding's file/line range actually exists in the inspected
diff snapshot, dedupe against deterministic-check output, and cap at 5
findings. Malformed input is reported as invalid_output — never silently
treated as "no findings."

Usage:
  python3 validate_findings.py --findings <model_output.json> --diff-json <file>
                                [--checks-json <file>]
"""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_FINDINGS = 5
REQUIRED_FINDING_FIELDS = {
    "severity", "category", "file", "line_start", "line_end", "side",
    "title", "trigger", "consequence", "evidence", "remediation", "verification_status",
}
VALID_SEVERITY = {"critical", "high", "medium", "low"}
VALID_SIDE = {"base", "head"}
VALID_VERIFICATION = {"model-hypothesis", "statically-supported", "reproduced-by-check"}
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def file_line_ranges_from_diff(diff: dict) -> dict:
    """path -> set of (start,end) line ranges touched, parsed from each file's hunk headers."""
    ranges = {}
    for f in diff.get("files", []):
        hunks = f.get("hunks")
        if not hunks:
            continue
        spans = []
        for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", hunks, flags=re.MULTILINE):
            start = int(m.group(1))
            length = int(m.group(2)) if m.group(2) else 1
            spans.append((start, start + max(length - 1, 0)))
        ranges[f["path"]] = spans
    return ranges


def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start <= b_end and b_start <= a_end


def validate(findings_payload: dict, diff: dict, checks: dict | None) -> dict:
    errors = []
    if not isinstance(findings_payload, dict) or "findings" not in findings_payload or "questions" not in findings_payload:
        return {"status": "invalid_output", "errors": ["top-level payload must have 'findings' and 'questions' keys"],
                "validated_findings": [], "rejected_findings": [], "questions": []}

    diff_ranges = file_line_ranges_from_diff(diff)
    known_paths = set(diff_ranges.keys())

    validated = []
    rejected = []

    for i, finding in enumerate(findings_payload.get("findings", [])):
        missing = REQUIRED_FINDING_FIELDS - set(finding.keys())
        problems = []
        if missing:
            problems.append(f"missing fields: {sorted(missing)}")
        if finding.get("severity") not in VALID_SEVERITY:
            problems.append(f"invalid severity: {finding.get('severity')!r}")
        if finding.get("side") not in VALID_SIDE:
            problems.append(f"invalid side: {finding.get('side')!r}")
        if finding.get("verification_status") not in VALID_VERIFICATION:
            problems.append(f"invalid verification_status: {finding.get('verification_status')!r}")

        path = finding.get("file")
        if path not in known_paths:
            problems.append(f"file {path!r} not present in the inspected diff snapshot")
        else:
            spans = diff_ranges.get(path, [])
            ls, le = finding.get("line_start"), finding.get("line_end")
            if not isinstance(ls, int) or not isinstance(le, int) or not any(overlaps(ls, le, s, e) for s, e in spans):
                problems.append(f"line range {ls}-{le} does not overlap any changed hunk in {path!r}")

        if problems:
            rejected.append({"index": i, "finding": finding, "problems": problems})
        else:
            validated.append(finding)

    # Dedup against deterministic-tool output: drop a finding whose title/evidence
    # closely restates a failing check's own output for the same file.
    if checks:
        failing_summaries = " ".join(
            (c.get("stdout", "") + " " + c.get("stderr", ""))
            for c in checks.get("checks", []) if c.get("status") == "fail"
        ).lower()
        deduped = []
        for finding in validated:
            title_words = set(re.findall(r"[a-z]{4,}", finding["title"].lower()))
            overlap_words = [w for w in title_words if w in failing_summaries]
            if len(overlap_words) >= 3:
                rejected.append({"index": None, "finding": finding,
                                  "problems": [f"duplicates deterministic check output (overlap: {overlap_words})"]})
            else:
                deduped.append(finding)
        validated = deduped

    validated.sort(key=lambda f: SEVERITY_ORDER.get(f["severity"], 99))
    overflow = []
    if len(validated) > MAX_FINDINGS:
        overflow = validated[MAX_FINDINGS:]
        validated = validated[:MAX_FINDINGS]

    return {
        "status": "ok",
        "errors": errors,
        "validated_findings": validated,
        "rejected_findings": rejected,
        "omitted_for_cap": [{"title": f["title"], "severity": f["severity"]} for f in overflow],
        "questions": findings_payload.get("questions", []),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", required=True)
    parser.add_argument("--diff-json", required=True)
    parser.add_argument("--checks-json", default=None)
    args = parser.parse_args()

    try:
        findings_payload = json.loads(Path(args.findings).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "invalid_output", "errors": [f"could not parse findings JSON: {e}"],
                           "validated_findings": [], "rejected_findings": [], "questions": []}, indent=2))
        return 1

    diff = json.loads(Path(args.diff_json).read_text())
    checks = json.loads(Path(args.checks_json).read_text()) if args.checks_json else None

    result = validate(findings_payload, diff, checks)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
