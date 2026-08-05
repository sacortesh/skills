#!/usr/bin/env python3
"""Gather deterministic facts about one project folder as JSON.

Everything here is cheap and objective (file listing, git plumbing, mtimes,
pattern matching for known filenames). Anything that requires judgment
(summarizing purpose, writing the verdict) is left to the calling model —
this script only decides WHETHER a project needs that judgment applied,
via the `needs_update` flag, so repeated runs across a large portfolio
don't re-burn tokens on projects that haven't changed.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

IGNORED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build",
    ".next", ".turbo", "target", ".cache", "coverage", ".pytest_cache",
}

README_NAMES = ["README.md", "README.rst", "README.txt", "README"]
MANIFEST_NAMES = [
    "package.json", "pyproject.toml", "requirements.txt", "Cargo.toml",
    "go.mod", "Gemfile", "composer.json", "pom.xml", "build.gradle",
]
PLANNING_PATTERNS = [
    r"^PRD.*", r"^TASKS?[_.].*", r"^TASKS?\.md$", r"^TODO.*", r"^ROADMAP.*",
    r"^SPEC.*", r"^\.specify$", r"^spec-kit.*", r"^PLAN.*", r"^IDEA.*",
    r"^NOTES?.*", r"^BACKLOG.*",
]
DEPLOY_FILES = [
    "vercel.json", "netlify.toml", "Dockerfile", "docker-compose.yml",
    "Procfile", "fly.toml", "render.yaml", "wrangler.toml", "app.yaml",
]
DEPLOY_DIRS = [".vercel", ".netlify"]

STATE_FILENAME = "PROJECT_STATE.md"


def run(cmd, cwd):
    try:
        out = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip(), out.returncode
    except Exception:
        return "", 1


def git_info(project_dir: Path):
    if not (project_dir / ".git").exists():
        return {"is_repo": False}

    branch, _ = run(["git", "branch", "--show-current"], project_dir)
    status, _ = run(["git", "status", "--porcelain"], project_dir)
    last_commit_iso, rc = run(
        ["git", "log", "-1", "--format=%cI"], project_dir
    )
    remotes, _ = run(["git", "remote"], project_dir)
    has_remote = bool(remotes.strip())

    unpushed = None
    if has_remote and branch:
        upstream, urc = run(
            ["git", "rev-parse", "--abbrev-ref", f"{branch}@{{u}}"],
            project_dir,
        )
        if urc == 0:
            count, crc = run(
                ["git", "rev-list", "--count", f"{branch}@{{u}}..{branch}"],
                project_dir,
            )
            if crc == 0 and count.isdigit():
                unpushed = int(count)

    return {
        "is_repo": True,
        "branch": branch or None,
        "uncommitted_changes": bool(status),
        "last_commit_iso": last_commit_iso or None,
        "has_remote": has_remote,
        "unpushed_commits": unpushed,
        "has_no_commits": rc != 0,
    }


def newest_mtime(project_dir: Path):
    newest = 0.0
    for p in project_dir.rglob("*"):
        if any(part in IGNORED_DIRS for part in p.parts):
            continue
        # Exclude the state file itself — otherwise every scan "touches"
        # the project and staleness resets to 0 on the next run.
        if p.name == STATE_FILENAME:
            continue
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime > newest:
            newest = mtime
    return newest


def find_first(project_dir: Path, names):
    for name in names:
        p = project_dir / name
        if p.exists():
            return p
    return None


def read_truncated(path: Path, max_chars=4000):
    try:
        return path.read_text(errors="replace")[:max_chars]
    except Exception:
        return None


def detect_planning_docs(project_dir: Path):
    hits = []
    try:
        entries = list(project_dir.iterdir())
    except OSError:
        entries = []
    for entry in entries:
        for pat in PLANNING_PATTERNS:
            if re.match(pat, entry.name, re.IGNORECASE):
                hits.append(entry.name)
                break
    # also check one level of docs/ if present
    docs_dir = project_dir / "docs"
    if docs_dir.is_dir():
        for entry in docs_dir.iterdir():
            for pat in PLANNING_PATTERNS:
                if re.match(pat, entry.name, re.IGNORECASE):
                    hits.append(f"docs/{entry.name}")
                    break
    return hits


def detect_deploy_signals(project_dir: Path):
    hits = [name for name in DEPLOY_FILES if (project_dir / name).exists()]
    hits += [f"{name}/ (local deploy CLI state)" for name in DEPLOY_DIRS if (project_dir / name).is_dir()]
    workflows = project_dir / ".github" / "workflows"
    if workflows.is_dir():
        hits += [f".github/workflows/{f.name}" for f in workflows.glob("*.yml")]
        hits += [f".github/workflows/{f.name}" for f in workflows.glob("*.yaml")]
    return hits


def parse_existing_state(state_path: Path):
    """Pull just the frontmatter fields we need to decide staleness."""
    if not state_path.exists():
        return None
    text = state_path.read_text(errors="replace")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {"last_scanned": None}
    fm = m.group(1)
    scanned = re.search(r"^last_scanned:\s*(.+)$", fm, re.MULTILINE)
    researched = re.search(r"^market_researched:\s*(\w+)$", fm, re.MULTILINE)
    return {
        "last_scanned": scanned.group(1).strip() if scanned else None,
        "market_researched": (researched.group(1).strip() == "true") if researched else False,
    }


def main():
    if len(sys.argv) != 2:
        print("usage: scan_project.py <project_dir>", file=sys.stderr)
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.is_dir():
        print(json.dumps({"error": f"not a directory: {project_dir}"}))
        sys.exit(1)

    top_files = sorted(
        p.name + ("/" if p.is_dir() else "")
        for p in project_dir.iterdir()
        if p.name not in IGNORED_DIRS and not p.name.startswith(".DS_Store")
    )

    readme_path = find_first(project_dir, README_NAMES)
    manifest_path = find_first(project_dir, MANIFEST_NAMES)

    git = git_info(project_dir)
    newest = newest_mtime(project_dir)
    newest_iso = (
        datetime.fromtimestamp(newest, tz=timezone.utc).isoformat()
        if newest else None
    )

    last_activity_candidates = [t for t in [newest_iso, git.get("last_commit_iso")] if t]
    last_activity = max(last_activity_candidates) if last_activity_candidates else None
    staleness_days = None
    if last_activity:
        dt = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
        staleness_days = (datetime.now(timezone.utc) - dt).days

    state_path = project_dir / STATE_FILENAME
    existing = parse_existing_state(state_path)
    needs_update = existing is None or existing.get("last_scanned") is None or (
        last_activity and existing["last_scanned"] and last_activity > existing["last_scanned"]
    )

    planning_docs = detect_planning_docs(project_dir)
    deploy_signals = detect_deploy_signals(project_dir)

    result = {
        "project_name": project_dir.name,
        "project_path": str(project_dir),
        "top_level_entries": top_files,
        "readme_excerpt": read_truncated(readme_path) if readme_path else None,
        "readme_file": readme_path.name if readme_path else None,
        "manifest_file": manifest_path.name if manifest_path else None,
        "manifest_excerpt": read_truncated(manifest_path, 2000) if manifest_path else None,
        "git": git,
        "last_activity_iso": last_activity,
        "staleness_days": staleness_days,
        "planning_docs": planning_docs,
        "deploy_signals": deploy_signals,
        "state_file_exists": state_path.exists(),
        "market_previously_researched": bool(existing and existing.get("market_researched")),
        "needs_update": needs_update,
        # Deliberately NOT staleness-gated: how long ago someone touched a
        # project says something about their attention/time, not about
        # whether the idea itself is any good. A project idle for a year is
        # just as worth a market check as one from this morning — staleness
        # is surfaced to the human as context, not used to filter them out.
        "has_purpose_signal": bool(readme_path or planning_docs or manifest_path),
        "promising_candidate": bool(
            (readme_path or planning_docs or manifest_path)
            and not (existing and existing.get("market_researched"))
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
