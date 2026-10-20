#!/usr/bin/env python3
"""
Run the repo's own configured lint/test/typecheck/Semgrep commands —
never invented ones — and report pass/fail/skipped/timeout/unavailable
per check, distinctly.

Execution is opt-in: without --execute, every configured check reports
"skipped (execution not enabled)" and nothing runs. This is the only
script in the pipeline that executes repo code, so it's the one place a
missing opt-in flag has to be respected literally.

Config format (JSON, see references in SKILL.md for where this comes
from — never invented by this script):
  {
    "checks": [
      {"name": "lint", "command": ["npm", "run", "lint"]},
      {"name": "typecheck", "command": ["npm", "run", "typecheck"]},
      {"name": "test", "command": ["npm", "test"]},
      {"name": "semgrep", "command": ["semgrep", "--config", "auto", "--json"]}
    ]
  }

Usage:
  python3 run_checks.py --repo <path> --config <config.json> [--execute] [--timeout 300]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMEOUT = 300
MAX_OUTPUT_CHARS = 8000  # truncate captured stdout/stderr before it ever reaches a report or a model.


def truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + f"\n...[TRUNCATED: {len(text) - MAX_OUTPUT_CHARS} more chars omitted]"


def run_one_check(repo_path: str, check: dict, execute: bool, timeout: int) -> dict:
    name = check.get("name", "unnamed-check")
    command = check.get("command")

    if not command:
        return {"name": name, "status": "unavailable", "summary": "no command configured"}

    if not execute:
        return {"name": name, "status": "skipped", "summary": "execution not enabled (pass --execute to run)"}

    try:
        result = subprocess.run(
            command, cwd=repo_path, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except FileNotFoundError:
        return {"name": name, "status": "unavailable", "summary": f"command not found: {command[0]}"}
    except subprocess.TimeoutExpired:
        return {"name": name, "status": "timeout", "summary": f"exceeded {timeout}s timeout"}

    status = "pass" if result.returncode == 0 else "fail"
    return {
        "name": name,
        "status": status,
        "exit_code": result.returncode,
        "stdout": truncate(result.stdout),
        "stderr": truncate(result.stderr),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--config", required=True, help="Path to a JSON config naming checks to run")
    parser.add_argument("--execute", action="store_true", help="Actually run the configured commands (default: report all as skipped)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    repo_path = str(Path(args.repo).resolve())
    config_path = Path(args.config)
    if not config_path.exists():
        print(json.dumps({"checks": [], "note": f"no config found at {args.config} — no checks configured"}, indent=2))
        return 0

    config = json.loads(config_path.read_text())
    checks = [run_one_check(repo_path, c, args.execute, args.timeout) for c in config.get("checks", [])]

    print(json.dumps({"checks": checks, "executed": args.execute}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
