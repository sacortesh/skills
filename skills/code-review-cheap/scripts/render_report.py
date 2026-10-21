#!/usr/bin/env python3
"""
Render review.json + review.md from the pipeline's validated outputs, and
append one line to usage.jsonl. Writes under <repo>/.code-review/ by
default — a tool-run-artifact directory, not living documentation.

Usage:
  python3 render_report.py --repo <path> --diff-json <file> --risk-json <file>
                            --context-manifest <file> --validated-findings <file>
                            [--checks-json <file>] [--runtime-seconds N] [--out-dir <path>]
"""
import argparse
import json
import sys
import time
from pathlib import Path

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def render_markdown(meta: dict, risk: dict, checks: dict | None, manifest: dict, validation: dict) -> str:
    lines = [f"# Code review — {meta['base_sha'][:12]}..{meta['head_sha'][:12]}", ""]
    lines.append(f"- Repo: `{meta.get('repo', '.')}`")
    lines.append(f"- Base: `{meta['base_sha']}`  Head: `{meta['head_sha']}`")
    lines.append(f"- Risk: **{risk['risk']}**" + (" — human review required" if risk["risk"] == "high" else ""))
    lines.append(f"- Pipeline status: **{meta['pipeline_status']}**  Disposition: **{meta['disposition']}**")
    lines.append("")

    if risk.get("reasons"):
        lines.append("## Risk reasons")
        lines += [f"- {r}" for r in risk["reasons"]]
        lines.append("")

    if checks and checks.get("checks"):
        lines.append("## Deterministic checks")
        for c in checks["checks"]:
            lines.append(f"- **{c['name']}**: {c['status']}" + (f" — {c.get('summary', '')}" if c.get("summary") else ""))
        lines.append("")

    blockers = [f for f in validation["validated_findings"] if f["severity"] in ("critical", "high")]
    others = [f for f in validation["validated_findings"] if f["severity"] in ("medium", "low")]

    lines.append("## Potential blockers")
    if blockers:
        for f in blockers:
            lines += render_finding(f)
    else:
        lines.append("No actionable findings within the inspected scope." if not validation["validated_findings"]
                      else "None at critical/high severity.")
    lines.append("")

    lines.append("## Other actionable findings")
    if others:
        for f in others:
            lines += render_finding(f)
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Questions and missing evidence")
    if validation.get("questions"):
        lines += [f"- {q}" for q in validation["questions"]]
    else:
        lines.append("None raised.")
    lines.append("")

    lines.append("## Review coverage and limitations")
    lines.append(f"- Context coverage: **{manifest['coverage']}**")
    if manifest["coverage"] == "partial":
        lines.append("  - Some context was omitted for budget reasons — see `review.json`'s `context_manifest.omitted` for exactly what.")
    for item in manifest.get("omitted", [])[:10]:
        lines.append(f"  - omitted: {item['kind']} ({item['source']}) — {item['reason']}")
    if meta.get("doc_triage_skips"):
        lines.append(f"- {len(meta['doc_triage_skips'])} verbose documentation file(s) sampled and skipped — not reviewed:")
        for item in meta["doc_triage_skips"][:10]:
            lines.append(f"  - `{item['path']}` ({item['changed_lines']} changed lines) — {item['reason']}")
    if validation.get("rejected_findings"):
        lines.append(f"- {len(validation['rejected_findings'])} candidate finding(s) rejected during validation (invalid, unverifiable location, or duplicate of a deterministic check) — see `review.json`.")
    if validation.get("omitted_for_cap"):
        lines.append(f"- {len(validation['omitted_for_cap'])} lower-priority finding(s) omitted past the 5-finding cap.")
    lines.append("")
    lines.append("_No findings is not the same as approved — it means nothing actionable turned up within the scope above._")

    return "\n".join(lines)


def render_finding(f: dict) -> list[str]:
    return [
        f"### [{f['severity'].upper()}] {f['title']}",
        f"- **File**: `{f['file']}:{f['line_start']}-{f['line_end']}` ({f['side']})",
        f"- **Category**: {f['category']}",
        f"- **Trigger**: {f['trigger']}",
        f"- **Consequence**: {f['consequence']}",
        f"- **Evidence**: {f['evidence']}",
        f"- **Suggested direction**: {f['remediation']}",
        f"- **Verification**: {f['verification_status']}",
        "",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--diff-json", required=True)
    parser.add_argument("--risk-json", required=True)
    parser.add_argument("--context-manifest", required=True)
    parser.add_argument("--validated-findings", required=True)
    parser.add_argument("--checks-json", default=None)
    parser.add_argument("--runtime-seconds", type=float, default=None)
    parser.add_argument("--out-dir", default=None, help="default: <repo>/.code-review")
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    out_dir = Path(args.out_dir) if args.out_dir else repo_path / ".code-review"
    out_dir.mkdir(parents=True, exist_ok=True)

    diff = json.loads(Path(args.diff_json).read_text())
    risk = json.loads(Path(args.risk_json).read_text())
    manifest = json.loads(Path(args.context_manifest).read_text())
    validation = json.loads(Path(args.validated_findings).read_text())
    checks = json.loads(Path(args.checks_json).read_text()) if args.checks_json else None

    pipeline_status = "failed" if validation["status"] != "ok" else ("partial" if manifest["coverage"] == "partial" else "completed")
    if validation["validated_findings"]:
        disposition = "findings"
    elif risk["risk"] == "high":
        disposition = "human-review-required"
    else:
        disposition = "no-findings"

    meta = {
        "repo": str(repo_path),
        "base_sha": diff["base_sha"],
        "head_sha": diff["head_sha"],
        "merge_base_sha": diff.get("merge_base_sha"),
        "pipeline_status": pipeline_status,
        "disposition": disposition,
        "doc_triage_skips": diff.get("doc_triage_skips", []),
    }

    review_json = {
        "metadata": meta,
        "risk": risk,
        "checks": checks,
        "context_manifest": manifest,
        "validation": validation,
        "call_count": 1,
    }

    (out_dir / "review.json").write_text(json.dumps(review_json, indent=2))
    (out_dir / "review.md").write_text(render_markdown(meta, risk, checks, manifest, validation))

    usage_record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo": str(repo_path),
        "base_sha": diff["base_sha"],
        "head_sha": diff["head_sha"],
        "call_count": 1,
        "risk": risk["risk"],
        "finding_counts": {
            sev: sum(1 for f in validation["validated_findings"] if f["severity"] == sev)
            for sev in ("critical", "high", "medium", "low")
        },
        "pipeline_status": pipeline_status,
        "disposition": disposition,
        "runtime_seconds": args.runtime_seconds,
    }
    with (out_dir / "usage.jsonl").open("a") as f:
        f.write(json.dumps(usage_record) + "\n")

    print(json.dumps({"out_dir": str(out_dir), "pipeline_status": pipeline_status, "disposition": disposition}, indent=2))
    return 0 if pipeline_status != "failed" else 1


if __name__ == "__main__":
    sys.exit(main())
