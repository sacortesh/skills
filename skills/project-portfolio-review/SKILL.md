---
name: project-portfolio-review
description: Audits every project folder in a directory (and, on request, every GitHub repo for an account) and maintains a running assessment of each one's state — purpose, tech stack, git status, staleness, planning docs (PRDs/task lists/spec-kit), deployment readiness, and a verdict on whether it's closer to money (marketable, real gap), fame (portfolio/CV-worthy), private (a real edge worth keeping non-public), expand, merge, or neither yet. Writes a PROJECT_STATE.md per project plus a sorted PORTFOLIO.md rollup at the top. Use this whenever the user wants to review, audit, triage, or take stock of a folder full of side projects or repos — "what's the state of my projects", "which of these are worth finishing", "help me figure out what to work on", "portfolio review", "which of these could make money", "check my GitHub repos too, I bet I have stuff I forgot about", or anything about resurrecting old projects, deciding what to kill, or building a CV/portfolio from existing code. Also trigger for requests to just "update the project states" or "rescan" on a directory that already has PROJECT_STATE.md files from a prior run.
---

# Project Portfolio Review

Turns a directory of loosely-maintained side projects into a legible,
periodically-refreshed portfolio: one `PROJECT_STATE.md` per project, and a
`PORTFOLIO.md` rollup at the top that sorts everything by how actionable it
is. The point is triage, not busywork — don't re-write files that haven't
changed, and don't spend web-search quota on projects nobody's touched in a
year without asking first.

## Prerequisites

Python 3 available on PATH — `scripts/scan_project.py` and `scripts/render_portfolio.py`
are bundled with this skill (no separate install), but both are invoked as `python3 ...`.
For the optional GitHub-repo review mode (`references/github-repos.md`), the `gh` CLI
must be installed and authenticated (`gh auth status`). Market research (step 4) uses
whatever web-search tooling is already available in the session (WebSearch, Perplexity,
etc.) — nothing additional to install for that either.

## 0. Resolve the target directory and mode

Default target directory is the current working directory. If the user
names a different path, use that instead.

**If the user wants GitHub repos reviewed** — not just local folders,
e.g. "check my GitHub too," "I probably have money sitting in repos I
never cloned here" — stop and read `references/github-repos.md` before
doing anything else. It's a separate workflow (different data source, no
full codebase to read, an extra real-world-validation signal via
stars/forks) built on the same taxonomy and templates below, kept out of
this file so a normal local-folder run doesn't have to load it.

Parse the request for intent, not rigid flags — people will phrase this in
plain language:
- "rescan everything" / "force a full rescan" → treat every project as
  needing an update regardless of what `scan_project.py` reports.
- "rescan `<project-name>`" / "update just X" → only touch that one project
  (still run the rollup regeneration afterward so the table reflects it).
- Anything else / first run → incremental mode (the default): trust
  `needs_update` from the scan.

## 1. Find candidate projects

List immediate subdirectories of the target directory. Skip dotfile/dot-dir
entries (`.git`, `.claude`, etc.) and anything empty. Everything else that
looks like a self-contained project is a candidate — you don't need a
README or `.git` for a folder to count; that absence is itself a finding
worth recording (see Verdict below).

## 2. Scan each project (deterministic facts first)

For each candidate, run:

```
python3 <skill_dir>/scripts/scan_project.py <project_dir>
```

This returns JSON with everything that doesn't require judgment: file
listing, README/manifest excerpts, git plumbing (branch, dirty/clean,
unpushed count, has-remote), staleness in days, detected planning docs
(PRD/TODO/ROADMAP/spec-kit patterns), detected deploy signals (Dockerfile,
CI workflows, vercel.json, etc.), and a `needs_update` flag comparing the
project's last activity against the existing `PROJECT_STATE.md`'s
`last_scanned` field (if any).

**Skip projects where `needs_update` is `false`** (unless the user asked
for a full rescan) — nothing has changed since the last pass, so leave
their `PROJECT_STATE.md` alone. This is what keeps repeat runs fast across
a large portfolio.

If the portfolio has many projects needing updates (roughly 8+), it's
worth parallelizing: spawn a batch of general-purpose subagents, each
handling a handful of projects (run the scan script, then do step 3 for
those projects), rather than working through all of them serially in the
main context. Use judgment — for a handful of stale projects, just do it
inline.

## 3. Write the judgment call: Purpose and Verdict

For every project that needs an update, take the JSON from step 2 and
write the two sections a script can't produce:

- **Purpose** — 2-4 sentences on what the project does and its stack,
  grounded in the file listing, README excerpt, and manifest excerpt. If
  it's genuinely unclear (no README, cryptic file names, no manifest), say
  that plainly rather than inventing a plausible-sounding purpose.
- **Usable As-Is** — separate from the verdict: does this already provide
  real value to someone (often the user) in its current state, even if
  nothing more is ever built? A rough-but-working script counts; a
  well-planned repo with no working code doesn't, yet. This is about
  present value, not potential — don't conflate it with the verdict below.
- **Verdict** — pick exactly one: **money** (plausible market, the gap
  looks real, far enough along to matter), **fame** (technically solid or
  interesting, good CV/portfolio material, not a business), **private**
  (gives a real edge — trading, scraping, job-hunting, competitive
  advantage of some kind — that depends on staying non-public; a
  confident "keep this back" call, not a hedge), **expand** (real
  potential and a visible direction, just needs more built before
  money/fame can be honestly judged — the hopeful cousin of "neither"),
  **merge** (more valuable combined with another project in *this same
  scan* than continued alone — see below), **delete** (an active
  recommendation to remove it — obsolete tech with no path forward, a
  pure learning/tutorial exercise with no lasting value, or a repo that's
  simply the wrong medium for what it holds; different from "neither,"
  which stays open rather than closing the case), or **neither** (thin,
  unclear, or stalled with no visible next step). Don't hedge into "could
  be either" — pick what's actually true right now, given what's on disk.
  One or two honest sentences on why.

  If a project genuinely doesn't fit any of these categories — not a
  strained approximation, an actual gap — pick the closest one so the row
  still sorts, and add a "**Suggested new category:**" line in the
  Verdict explaining what's missing. This taxonomy grew out of exactly
  that kind of feedback already (private, merge, and delete all started
  as "none of these quite fit"); don't silently force a bad fit instead
  of flagging it.

A `private` verdict is still worth a market-research pass if the user
opts in at step 4 — the question there isn't "how do I sell this," it's
"does this edge actually exist, or does this already exist elsewhere and
the edge is imagined." Finding a crowded market for a `private` project
is a real, useful result: it means the verdict was wrong, not that the
research was pointless.

- **Next Step + Effort** — the whole point of this exercise is deciding
  what to actually do, so name one concrete, imperative next action per
  project ("Build the NestJS API skeleton," not "keep developing it"),
  and rate the effort for *just that step* as low/medium/high. Effort is
  about the next action, not the whole remaining project — a big eventual
  vision shouldn't inflate the estimate for what's actually next. The
  rollup script combines this with the verdict to rank projects by
  effective priority (high value + low effort surfaces first), so a lazy
  or inflated effort rating will visibly distort someone else's — i.e.
  your own — sense of what to work on next.

**Watch for merge candidates while you write purposes.** As you read each
project's README/idea docs, you'll sometimes see explicit cross-references
("I have a sister project that...") or two projects that are obviously
solving adjacent problems. Don't assign `verdict: merge` speculatively —
only use it when you can name the specific other project (in `merge_with`)
*and* it's actually present in this scan. If a project's own notes mention
a sibling that isn't part of this run, say so in the Verdict prose instead
("references a tarot-card project not found in this scan — worth checking
if/when it's included") rather than forcing a merge verdict you can't back
up. Once you've drafted every project's Purpose section, it's worth a
quick second look across all of them together — full portfolios especially
tend to have a couple of overlapping ideas that aren't obvious from any
one project in isolation.

Fill in the rest of the template (`templates/PROJECT_STATE.md.template`)
directly from the JSON: git state, staleness, planning artifacts, deploy
signals. The frontmatter fields are structured on purpose so
`render_portfolio.py` can aggregate them later — keep them exactly as
typed in the template (`true`/`false` lowercase, ISO dates, etc; `merge_with`
is a project name or `n/a`). Leave `market_researched: false` and the
Market Position section as "Not yet assessed" for now — that's step 4.

Write the file to `<project_dir>/PROJECT_STATE.md`.

## 4. Market research — ask before spending quota

After the per-project pass, collect every project where the scan JSON
marked `promising_candidate: true` (has *some* purpose signal — a README,
a planning doc, or a dependency manifest — and hasn't been researched
yet). This is deliberately **not** filtered by staleness: how long ago a
project was last touched reflects the person's time and attention, not
whether the idea is good. A project idle for a year deserves the same
shot at a market check as one from this morning. Staleness is shown to
the user as context alongside each candidate, never used to silently drop
one from the list.

**Before running any search**, show the user that shortlist and ask which
ones (if any) they want researched now. Use `AskUserQuestion` with
multi-select if there's more than a couple — don't just go do it. Web
search quota (and especially Perplexity's, which is small — check
`pplx_usage` if you're considering it) is worth spending deliberately, not
on autopilot across a whole portfolio.

For confirmed projects:
- Default to the plain `WebSearch` tool — "does X already exist", "is
  there a product like Y" — that's free and usually enough to tell if a
  space is crowded.
- Only reach for Perplexity if the user specifically asks for deeper
  research on a project, or `WebSearch` results are too thin to judge.
- Update that project's `PROJECT_STATE.md`: fill in **Market Position**
  with what you found and how crowded/gapped the space looks, set
  `market_researched: true`, and reconsider the **Verdict** in light of
  it — a "neither yet" can become "money" or firmly "fame" once you know
  whether the idea is original.

Projects the user declines to research keep `market_researched: false` and
"Not yet assessed" — that's a valid, honest state, not a gap to fill later
in the same run.

## 5. Regenerate the rollup

Once all updates for this run are written, run:

```
python3 <skill_dir>/scripts/render_portfolio.py <target_dir>
```

This reads every `PROJECT_STATE.md`'s frontmatter and rewrites
`PORTFOLIO.md` at the top of the target directory — sorted by a priority
score combining verdict (impact) and effort (cost of the next step), so
high-value/low-effort projects surface first. It's pure aggregation from
already-written frontmatter, so always run it after any project update,
even if you only touched one project (per a targeted rescan) — the table
needs to reflect the whole portfolio, not just what changed this run. This
also picks up any `_gh-*` shadow folders from a GitHub-repo pass (see
`references/github-repos.md`) automatically — no separate rollup needed.

## 6. Report back

Summarize what changed this run in the chat: how many projects were
scanned vs. skipped (already current), what moved verdict category (if
anything), and point at `PORTFOLIO.md`. Don't paste the full rollup table
into the chat unless the user asks — they can read the file.
