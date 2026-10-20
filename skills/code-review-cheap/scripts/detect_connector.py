#!/usr/bin/env python3
"""
Detect which VCS host connector (if any) applies to this repo's remotes.

Degrades gracefully: no git repo, no remotes, or an unrecognized/
unimplemented host all fall back to {"connector": "local"} rather than
raising — see references/vcs-connectors.md for the full interface and
detection order this implements.

Usage:
  python3 detect_connector.py [--repo <path>]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# Registry: (name, hostname substrings, implemented)
# Order matters — first match wins. See references/vcs-connectors.md
# before adding an entry here; a new entry also needs a matching module
# under connectors/ to actually be usable, not just detected.
CONNECTOR_REGISTRY = [
    ("github", ["github.com"], True),
    ("bitbucket", ["bitbucket.org"], False),
    ("gitlab", ["gitlab.com"], False),
]


def get_remote_urls(repo_path: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", repo_path, "remote", "-v"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return []
    if out.returncode != 0:
        return []
    urls = []
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            urls.append(parts[1])
    return urls


def detect(repo_path: str) -> dict:
    urls = get_remote_urls(repo_path)
    if not urls:
        return {
            "connector": "local",
            "implemented": True,
            "remote_urls": [],
            "note": "No git remotes found (or not a git repo) — local-only mode.",
        }

    for name, hostnames, implemented in CONNECTOR_REGISTRY:
        for url in urls:
            if any(h in url for h in hostnames):
                return {
                    "connector": name,
                    "implemented": implemented,
                    "remote_urls": urls,
                    "note": (
                        None if implemented
                        else f"'{name}' remote detected but no connector module "
                             f"implemented yet — falling back to local-only mode "
                             f"for PR metadata. See references/vcs-connectors.md."
                    ),
                }

    return {
        "connector": "local",
        "implemented": True,
        "remote_urls": urls,
        "note": "No recognized host in remotes — local-only mode.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Path to the git repo (default: cwd)")
    args = parser.parse_args()

    repo_path = str(Path(args.repo).resolve())
    result = detect(repo_path)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
