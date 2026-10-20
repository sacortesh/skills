#!/usr/bin/env python3
"""
GitHub connector — fetches PR metadata via the `gh` CLI.

Implements the two-function interface from references/vcs-connectors.md.
Never resolves refs to SHAs (collect_diff.py's job) and never fetches the
diff itself (always local git) — this module only answers "what does the
PR say about itself."

Usage (standalone, for debugging):
  python3 github.py [--repo <path>] [--pr <number-or-url>]
"""
import argparse
import json
import re
import subprocess
import sys

CLOSING_KEYWORDS = r"(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)"
ISSUE_REF = r"#(\d+)"


def detect(repo_path: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "-C", repo_path, "remote", "-v"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return out.returncode == 0 and "github.com" in out.stdout


def _parse_linked_issues(body: str) -> list[str]:
    if not body:
        return []
    strong = set(re.findall(rf"{CLOSING_KEYWORDS}\s+{ISSUE_REF}", body, flags=re.IGNORECASE))
    weak = set(re.findall(ISSUE_REF, body))
    # Strong (closing-keyword) matches first, then any remaining bare mentions.
    ordered = [f"#{n}" for n in strong] + [f"#{n}" for n in weak if n not in strong]
    return ordered


def fetch_metadata(repo_path: str, pr_ref: str | None = None) -> dict:
    cmd = ["gh", "pr", "view"]
    if pr_ref:
        cmd.append(pr_ref)
    cmd += ["--json", "title,body,labels,baseRefName,headRefName,url"]

    try:
        out = subprocess.run(
            cmd, cwd=repo_path, capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"error": f"gh CLI call failed: {e}"}

    if out.returncode != 0:
        return {"error": f"gh pr view failed: {out.stderr.strip() or 'unknown error'}"}

    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError as e:
        return {"error": f"gh returned non-JSON output: {e}"}

    body = data.get("body") or ""
    return {
        "title": data.get("title", ""),
        "description": body,
        "labels": [l.get("name") for l in data.get("labels", []) if l.get("name")],
        "linked_issues": _parse_linked_issues(body),
        "base_ref": data.get("baseRefName", ""),
        "head_ref": data.get("headRefName", ""),
        "url": data.get("url", ""),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--pr", default=None, help="PR number or URL; omit to use the current branch's PR")
    args = parser.parse_args()

    if not detect(args.repo):
        print(json.dumps({"error": "no github.com remote detected"}, indent=2))
        return 1

    print(json.dumps(fetch_metadata(args.repo, args.pr), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
