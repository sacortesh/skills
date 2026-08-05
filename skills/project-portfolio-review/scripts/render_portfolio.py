#!/usr/bin/env python3
"""Build the top-level PORTFOLIO.md rollup from each project's PROJECT_STATE.md
frontmatter. Pure aggregation — no judgment involved, so it's fully scripted
rather than left to the model.

The whole point of the rollup is triage: which project to actually pick up
next. So beyond just listing verdicts, this computes a priority label from
verdict (impact) x effort (cost of the next step), and sorts on it — high
value + low effort surfaces first, regardless of how each project's verdict
happened to alphabetize.
"""
import re
import sys
from pathlib import Path

STATE_FILENAME = "PROJECT_STATE.md"
ROLLUP_FILENAME = "PORTFOLIO.md"

# How much verdict a project has going for it. money/private are the two
# confirmed-value tiers (one public, one deliberately not); merge/expand
# both name a concrete next step; fame is realized but capped; neither is
# the least actionable/most uncertain.
IMPACT_TIER = {
    "money": 3, "private": 3, "merge": 2, "expand": 2, "fame": 1,
    "neither": 0, "delete": 0, "unassessed": 0,
}
EFFORT_SCORE = {"low": 2, "medium": 1, "high": 0}

VERDICT_EMOJI = {
    "money": "💰", "private": "🔒", "merge": "🔗", "expand": "🌱",
    "fame": "🏆", "neither": "🤷", "delete": "🗑️", "unassessed": "❔",
}
EFFORT_EMOJI = {"low": "🟢", "medium": "🟡", "high": "🔴"}


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = m.group(1)
    fields = {}
    for line in fm.splitlines():
        match = re.match(r"^(\w+):\s*(.*)$", line)
        if match:
            key, val = match.groups()
            fields[key] = val.strip()
    return fields


def bool_field(fields, key):
    return fields.get(key, "").strip() == "true"


def priority_label(score: int) -> str:
    # Bucket edges intentionally wide enough that effort only reorders
    # within a verdict tier — it never lets a low-effort "neither" project
    # outrank a high-effort "money" one. Impact leads; effort breaks ties.
    if score >= 30:
        return "🔥 do next"
    if score >= 20:
        return "⭐ worth doing"
    if score >= 10:
        return "🌤️ nice to have"
    return "💤 low priority"


def main():
    if len(sys.argv) != 2:
        print("usage: render_portfolio.py <target_dir>", file=sys.stderr)
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()
    rows = []

    for state_path in sorted(target_dir.glob(f"*/{STATE_FILENAME}")):
        folder_name = state_path.parent.name
        text = state_path.read_text(errors="replace")
        fm = parse_frontmatter(text)
        # Shadow folders (_gh-<repo>) hold the real name in frontmatter;
        # local folders match already, but fall back just in case.
        project_name = fm.get("project", folder_name).strip() or folder_name

        verdict = fm.get("verdict", "unassessed")
        effort = fm.get("effort", "medium")
        next_step = fm.get("next_step", "").strip() or "Not yet assessed"
        staleness = fm.get("staleness_days", "?")
        git_dirty = bool_field(fm, "uncommitted_changes")
        has_deploy = bool_field(fm, "has_deploy_signals")
        market_researched = bool_field(fm, "market_researched")
        usable_as_is = bool_field(fm, "usable_as_is")
        merge_with = fm.get("merge_with", "n/a")
        github_stars = fm.get("github_stars", "").strip()
        has_local_copy = fm.get("has_local_copy", "true").strip() == "true"

        impact = IMPACT_TIER.get(verdict, 0)
        effort_score = EFFORT_SCORE.get(effort, 1)
        score = impact * 10 + effort_score

        rows.append({
            "name": project_name,
            "folder": folder_name,
            "verdict": verdict,
            "merge_with": merge_with,
            "usable_as_is": usable_as_is,
            "effort": effort,
            "next_step": next_step,
            "staleness": staleness,
            "git_dirty": git_dirty,
            "has_deploy": has_deploy,
            "market_researched": market_researched,
            "github_stars": github_stars,
            "has_local_copy": has_local_copy,
            "score": score,
        })

    rows.sort(key=lambda r: (
        -r["score"],
        int(r["staleness"]) if str(r["staleness"]).isdigit() else 9999,
    ))

    lines = [
        "# Project Portfolio",
        "",
        f"Scanned {len(rows)} project(s) under `{target_dir}`.",
        "Regenerate with the `project-portfolio-review` skill; edit individual",
        "`PROJECT_STATE.md` files directly, they are the source of truth.",
        "Sorted by priority: verdict (impact) first, effort for the next step",
        "as the tiebreaker — quick wins within a tier surface above slow ones.",
        "",
        "| Priority | Verdict | Project | Next Step | Effort | Usable now | Stale | Flags |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        verdict_label = r["verdict"]
        if r["verdict"] == "merge" and r["merge_with"] not in ("n/a", "", None):
            verdict_label = f"merge → {r['merge_with']}"
        verdict_cell = f"{VERDICT_EMOJI.get(r['verdict'], '❔')} {verdict_label}"
        effort_cell = f"{EFFORT_EMOJI.get(r['effort'], '🟡')} {r['effort']}"
        usable_cell = "✅" if r["usable_as_is"] else "❌"

        flags = []
        if r["git_dirty"]:
            flags.append("🔧 dirty")
        if r["has_deploy"]:
            flags.append("🚀 deploy")
        if r["market_researched"]:
            flags.append("🔎 researched")
        if r["github_stars"].isdigit() and int(r["github_stars"]) > 0:
            flags.append(f"⭐{r['github_stars']}")
        if not r["has_local_copy"]:
            flags.append("☁️ github-only")
        flags_cell = " ".join(flags) if flags else "—"

        lines.append(
            f"| {priority_label(r['score'])} "
            f"| {verdict_cell} "
            f"| [{r['name']}]({r['folder']}/PROJECT_STATE.md) "
            f"| {r['next_step']} "
            f"| {effort_cell} "
            f"| {usable_cell} "
            f"| {r['staleness']}d "
            f"| {flags_cell} |"
        )

    out_path = target_dir / ROLLUP_FILENAME
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path} ({len(rows)} projects)")


if __name__ == "__main__":
    main()
