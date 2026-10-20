#!/usr/bin/env python3
"""
Collect a git diff between two refs, resolved to immutable SHAs, with
generated/vendor/binary files excluded and lockfiles/manifests summarized
rather than dumped whole.

Never switches branches or touches the working tree — every read goes
through `git show`/`git diff <sha>..<sha>`, never `git checkout`.

Usage:
  python3 collect_diff.py --repo <path> --base <ref> --head <ref> [--merge-base]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

GENERATED_VENDOR_PATTERNS = [
    r"(^|/)node_modules/", r"(^|/)vendor/", r"(^|/)dist/", r"(^|/)build/",
    r"\.min\.(js|css)$", r"(^|/)\.git/", r"\.generated\.", r"(^|/)__pycache__/",
    r"(^|/)target/",  # rust/java build output
]

LOCKFILE_MANIFEST_PATTERNS = [
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock",
    "go.sum", "Gemfile.lock", "poetry.lock", "package.json", "go.mod",
    "Cargo.toml", "requirements.txt", "Pipfile.lock",
]

MAX_HUNK_CHARS = 20000  # per-file cap; oversized diffs get truncated with a note, never silently.


def run_git(repo_path: str, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", repo_path, *args],
        capture_output=True, text=True, timeout=timeout, check=False,
    )


def resolve_sha(repo_path: str, ref: str) -> str | None:
    out = run_git(repo_path, ["rev-parse", f"{ref}^{{commit}}"])
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def classify_path(path: str) -> tuple[bool, str | None, bool]:
    """Returns (excluded, exclusion_reason, is_lockfile_manifest)."""
    for pattern in GENERATED_VENDOR_PATTERNS:
        if re.search(pattern, path):
            return True, f"matches generated/vendor pattern: {pattern}", False
    basename = path.rsplit("/", 1)[-1]
    if basename in LOCKFILE_MANIFEST_PATTERNS:
        return False, None, True
    return False, None, False


def get_numstat(repo_path: str, base_sha: str, head_sha: str) -> dict:
    out = run_git(repo_path, ["diff", "--numstat", f"{base_sha}..{head_sha}"])
    stats = {}
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            added, removed, path = parts
            stats[path] = {
                "additions": None if added == "-" else int(added),
                "deletions": None if removed == "-" else int(removed),
                "binary": added == "-" and removed == "-",
            }
    return stats


def get_name_status(repo_path: str, base_sha: str, head_sha: str) -> dict:
    out = run_git(repo_path, ["diff", "--name-status", "--find-renames", f"{base_sha}..{head_sha}"])
    statuses = {}
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") and len(parts) == 3:
            statuses[parts[2]] = {"status": "renamed", "from": parts[1]}
        elif len(parts) == 2:
            kind = {"A": "added", "M": "modified", "D": "deleted"}.get(status[0], status)
            statuses[parts[1]] = {"status": kind, "from": None}
    return statuses


def get_file_hunks(repo_path: str, base_sha: str, head_sha: str, path: str) -> str:
    out = run_git(repo_path, ["diff", f"{base_sha}..{head_sha}", "--", path])
    text = out.stdout
    if len(text) > MAX_HUNK_CHARS:
        return text[:MAX_HUNK_CHARS] + f"\n...[TRUNCATED: {len(text) - MAX_HUNK_CHARS} more chars omitted]"
    return text


def summarize_lockfile_manifest(repo_path: str, base_sha: str, head_sha: str, path: str) -> str:
    """Line-level added/removed dependency entries, not the full file."""
    out = run_git(repo_path, ["diff", "--unified=0", f"{base_sha}..{head_sha}", "--", path])
    added = [l[1:].strip() for l in out.stdout.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:].strip() for l in out.stdout.splitlines() if l.startswith("-") and not l.startswith("---")]
    lines = []
    if added:
        lines.append(f"{len(added)} line(s) added, e.g.: " + "; ".join(added[:10]))
    if removed:
        lines.append(f"{len(removed)} line(s) removed, e.g.: " + "; ".join(removed[:10]))
    return "\n".join(lines) if lines else "(no line-level changes detected)"


def collect(repo_path: str, base_ref: str, head_ref: str, use_merge_base: bool) -> dict:
    base_sha = resolve_sha(repo_path, base_ref)
    head_sha = resolve_sha(repo_path, head_ref)
    if not base_sha or not head_sha:
        return {"error": f"could not resolve refs to SHAs (base={base_ref!r} -> {base_sha}, head={head_ref!r} -> {head_sha})"}

    compare_base_sha = base_sha
    merge_base_sha = None
    if use_merge_base:
        mb = run_git(repo_path, ["merge-base", base_sha, head_sha])
        if mb.returncode == 0 and mb.stdout.strip():
            merge_base_sha = mb.stdout.strip()
            compare_base_sha = merge_base_sha

    numstat = get_numstat(repo_path, compare_base_sha, head_sha)
    name_status = get_name_status(repo_path, compare_base_sha, head_sha)

    files = []
    exclusions = []
    for path in sorted(set(numstat) | set(name_status)):
        stat = numstat.get(path, {})
        status_info = name_status.get(path, {"status": "modified", "from": None})
        excluded, reason, is_lockfile = classify_path(path)

        entry = {
            "path": path,
            "renamed_from": status_info["from"],
            "status": status_info["status"],
            "additions": stat.get("additions"),
            "deletions": stat.get("deletions"),
            "binary": stat.get("binary", False),
            "excluded": excluded,
            "exclusion_reason": reason,
        }

        if excluded:
            exclusions.append({"path": path, "reason": reason})
            files.append(entry)
            continue
        if entry["binary"]:
            entry["note"] = "binary file — content not diffed"
            files.append(entry)
            continue
        if is_lockfile:
            entry["lockfile_manifest_summary"] = summarize_lockfile_manifest(repo_path, compare_base_sha, head_sha, path)
            files.append(entry)
            continue

        entry["hunks"] = get_file_hunks(repo_path, compare_base_sha, head_sha, path)
        files.append(entry)

    return {
        "base_ref": base_ref,
        "head_ref": head_ref,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "merge_base_sha": merge_base_sha,
        "compared_against": compare_base_sha,
        "files": files,
        "exclusions": exclusions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--merge-base", action="store_true",
                         help="Compare head against merge-base(base, head) instead of base directly — the default for PR-style review.")
    args = parser.parse_args()

    repo_path = str(Path(args.repo).resolve())
    result = collect(repo_path, args.base, args.head, args.merge_base)
    print(json.dumps(result, indent=2))
    return 1 if "error" in result else 0


if __name__ == "__main__":
    sys.exit(main())
