#!/usr/bin/env python3
"""Fetch every GitHub repo for an owner and cross-reference against local
project folders, so the GitHub-repo review workflow (see
references/github-repos.md) only has to think about repos that don't
already have a local scan. Requires the `gh` CLI, authenticated.

Deterministic data-gathering only — matching by remote URL or folder name
is mechanical, no judgment involved. Purpose/verdict writing for the
github-only repos still happens in the model, same as the local flow.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_FIELDS = (
    "name,nameWithOwner,description,url,isPrivate,isFork,isArchived,"
    "stargazerCount,forkCount,pushedAt,primaryLanguage,homepageUrl"
)

IGNORED_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__"}
STATE_FILENAME = "PROJECT_STATE.md"
SHADOW_PREFIX = "_gh-"


def run(cmd, cwd=None):
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=15)
        return out.stdout.strip(), out.returncode
    except Exception:
        return "", 1


def normalize_remote(url: str):
    """https://github.com/owner/repo.git or git@github.com:owner/repo.git -> owner/repo"""
    if not url:
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(\.git)?/?$", url.strip())
    return m.group(1) if m else None


def main():
    if len(sys.argv) != 3:
        print("usage: scan_github_repos.py <owner> <target_dir>", file=sys.stderr)
        sys.exit(1)

    owner, target_dir = sys.argv[1], Path(sys.argv[2]).resolve()

    out, rc = run(["gh", "repo", "list", owner, "--limit", "1000", "--json", REPO_FIELDS])
    if rc != 0:
        print(json.dumps({"error": f"gh repo list failed: {out}"}))
        sys.exit(1)
    repos = json.loads(out)

    # Build normalized-remote -> local folder name map from every local
    # project directory (skip dotfiles and any pre-existing shadow folders
    # from a prior github-repo pass).
    remote_to_folder = {}
    name_to_folder = {}
    for entry in target_dir.iterdir():
        if not entry.is_dir() or entry.name.startswith(".") or entry.name.startswith(SHADOW_PREFIX):
            continue
        remote_url, rc = run(["git", "-C", str(entry), "remote", "get-url", "origin"])
        normalized = normalize_remote(remote_url) if rc == 0 else None
        if normalized:
            remote_to_folder[normalized.lower()] = entry.name
        name_to_folder[entry.name.lower()] = entry.name

    matched, possible_local_match, github_only = [], [], []
    for repo in repos:
        key = repo["nameWithOwner"].lower()
        shadow_path = target_dir / f"{SHADOW_PREFIX}{repo['name']}" / STATE_FILENAME
        repo["shadow_state_exists"] = shadow_path.exists()

        if key in remote_to_folder:
            repo["local_folder"] = remote_to_folder[key]
            matched.append(repo)
        elif repo["name"].lower() in name_to_folder:
            repo["local_folder"] = name_to_folder[repo["name"].lower()]
            possible_local_match.append(repo)
        else:
            github_only.append(repo)

    print(json.dumps({
        "owner": owner,
        "total_repos": len(repos),
        "matched": matched,
        "possible_local_match": possible_local_match,
        "github_only": github_only,
    }, indent=2))


if __name__ == "__main__":
    main()
