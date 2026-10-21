#!/usr/bin/env python3
"""
Posts validated findings as a single inline GitHub PR review via `gh api`.

One API call for the whole batch (POST pulls/{pr}/reviews with a
comments[] array, event=COMMENT) regardless of finding count — never one
call per finding, and never an approval/request-changes verdict. This
script never runs on its own; the skill's process only calls it after
the user has explicitly asked, for this run, to post comments — posting
to a shared PR is visible to others and hard to undo.

Usage:
  python3 post_comments.py --repo <path> --pr <number-or-url> --validated-findings <validated.json>
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def build_comments(findings: list[dict]) -> list[dict]:
    comments = []
    for f in findings:
        body = "\n".join([
            f"**[{f['severity']}/{f['category']}] {f['title']}**",
            "",
            f"**Trigger:** {f['trigger']}",
            f"**Consequence:** {f['consequence']}",
            f"**Evidence:** {f['evidence']}",
            f"**Remediation:** {f['remediation']}",
            "",
            f"_verification: {f['verification_status']} — posted by code-review-cheap_",
        ])
        comment = {"path": f["file"], "side": f["side"], "body": body}
        if f["line_start"] == f["line_end"]:
            comment["line"] = f["line_end"]
        else:
            comment["start_line"] = f["line_start"]
            comment["start_side"] = f["side"]
            comment["line"] = f["line_end"]
        comments.append(comment)
    return comments


def resolve_pr_number(repo_path: str, pr_ref: str | None) -> int | None:
    cmd = ["gh", "pr", "view"]
    if pr_ref:
        cmd.append(pr_ref)
    cmd += ["--json", "number"]
    try:
        out = subprocess.run(
            cmd, cwd=repo_path, capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)["number"]
    except (json.JSONDecodeError, KeyError):
        return None


def post_review(repo_path: str, pr_number: int, comments: list[dict]) -> dict:
    payload = {"event": "COMMENT", "comments": comments}
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/reviews",
             "-X", "POST", "--input", "-"],
            cwd=repo_path, input=json.dumps(payload), capture_output=True, text=True,
            timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"error": f"gh CLI call failed: {e}"}

    if out.returncode != 0:
        return {"error": f"gh api failed: {out.stderr.strip() or 'unknown error'}"}

    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError as e:
        return {"error": f"gh returned non-JSON output: {e}"}

    return {
        "posted": True,
        "comment_count": len(comments),
        "review_id": data.get("id"),
        "review_url": data.get("html_url"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--pr", default=None, help="PR number or URL; omit to use the current branch's PR")
    parser.add_argument("--validated-findings", required=True)
    args = parser.parse_args()

    validation = json.loads(Path(args.validated_findings).read_text())
    findings = validation.get("validated_findings", [])
    if not findings:
        print(json.dumps({"posted": False, "reason": "no validated findings to post"}, indent=2))
        return 0

    pr_number = resolve_pr_number(args.repo, args.pr)
    if pr_number is None:
        print(json.dumps({"error": "could not resolve a PR number via gh pr view"}, indent=2))
        return 1

    comments = build_comments(findings)
    result = post_review(args.repo, pr_number, comments)
    print(json.dumps(result, indent=2))
    return 0 if result.get("posted") else 1


if __name__ == "__main__":
    sys.exit(main())
