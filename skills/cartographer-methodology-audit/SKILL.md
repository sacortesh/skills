---
name: cartographer-methodology-audit
description: Audits a project's actual development methodology and flags gaps, risks, and mismatches between its actual complexity/risk profile and its actual process rigor — spec-driven complexity with no specs anywhere, agentic/AI tooling configured but unused, inconsistent commit/branch conventions, missing CI where the risk surface would want one. Prescriptive, not descriptive — reads docs/cartography/METHODOLOGY.md (the companion cartographer-explore skill's descriptive index) as input where it exists, or runs its own lightweight discovery when it doesn't. Use whenever the user wants to know if their process has real risk, asks "are we doing this right," wants a methodology health-check before formalizing a process decision (adopting spec-driven development, adding CI, writing specs), or wants that decision grounded in what's actually true of the project today. Trigger also on "audit our methodology," "review our workflow," "is our process solid enough for X."
---

# Cartographer: Methodology Audit

## Contents
- When this is worth running
- Inputs
- What to flag
- Output
- What this doesn't do

`cartographer-explore`'s Step 1.5 indexes what's discoverable about a
project's development methodology — deliberately descriptive, never
judging whether it's enough. This skill is the other half: given that
index (or its own quick discovery pass, if no index exists yet), judge
whether the project's actual process rigor matches its actual complexity
and risk — and flag it plainly where it doesn't. Mixing descriptive
indexing and prescriptive judgment in one pass makes a skill's job
ambiguous, so this stays separate and reads the index as input rather than
reinventing the discovery step.

## When this is worth running

- Before formalizing a process decision (adopting spec-driven development,
  phase-based planning, more CI) — use this audit to ground the decision in
  what's actually true of the project today, not to retrofit justification
  for a decision already made.
- When something already went wrong that smells process-shaped — a drift
  `cartographer-spec-drift` found, a bug that slipped through because
  nothing enforced a check, an onboarding dev confused by inconsistent
  conventions.
- **Not** worth running reflexively on every small project — a two-person
  side project with five files doesn't need a methodology audit. Say so
  and skip it if the project's actual scale doesn't warrant process
  ceremony, the same "when this is worth the cost" judgment the rest of
  the cartography family applies to documentation effort, applied here to
  process rigor instead.

## Inputs

1. `docs/cartography/METHODOLOGY.md`, if it exists (written by
   `cartographer-explore`'s Step 1.5) — read it as the starting index of
   what's discoverable. If it doesn't exist, run that same discovery
   inline first (skim `.claude/`, `AGENTS.md`/`CLAUDE.md`, planning-doc
   naming patterns, `git log` for commit/branch conventions, an agentic
   tooling inventory) rather than requiring the user to run
   `cartographer-explore` first — this skill works standalone.
2. The project's actual complexity signals: size (file/LOC count as a
   rough proxy, not precision), number of contributors (`git log`
   authors), how many distinct containers/surfaces exist (from
   `cartographer-explore`'s Context doc if present, or a quick Step-0-style
   skim if not), and whether the project touches anything high-stakes
   (auth, billing, data integrity).

## What to flag

For each dimension below, state the actual observed practice, then judge:
is the current level of rigor under-matched, well-matched, or
over-matched to this project's actual risk/complexity? Only flag a
mismatch — don't restate what's already fine just to look thorough.

- **Spec/planning discipline vs. actual complexity** — e.g. multiple
  cross-cutting features with no written spec anywhere, or heavy
  spec/ritual on a project too small to need it.
- **Test/CI coverage vs. risk surface** — no CI on a project with
  billing/auth/data-integrity logic is a flag; no CI on a static site is
  not.
- **Agentic tooling inventory vs. actual use** — skills/MCP servers/
  subagents configured in the repo (`.claude/agents/`, `.claude/skills/`,
  committed MCP configs) that nothing in git history or `AGENTS.md` shows
  evidence of actually being invoked, or conversely, real reliance on an
  agent/skill that no documentation anywhere tells a new contributor
  exists.
- **Commit/branch convention consistency** — a convention stated somewhere
  (`CONTRIBUTING.md`, a PR template) that `git log` doesn't actually
  follow, or a de facto convention in `git log` that's never written down
  anywhere a newcomer would find it.
- **Documentation-to-practice gap** — anything `cartographer-explore` or
  `cartographer-spec-drift` already surfaced as drift that's
  process-shaped rather than code-shaped (the same kind of claim going
  stale repeatedly suggests a process gap, not a one-off mistake) — note
  it here with a pointer to the specific drift entry, don't re-investigate
  it from scratch.

## Output

Write `docs/cartography/METHODOLOGY_AUDIT.md`:

```yaml
---
audited_against: METHODOLOGY.md | inline discovery, no file
last_audited_revision: <git sha or date>
---
```

Then one entry per flagged mismatch (skip dimensions with nothing to flag —
say so in one line, don't pad):

- **Dimension** — one of the five above (or a new one, named plainly, if
  something real doesn't fit the list).
- **Observed vs. expected** — what's actually true vs. what the project's
  own risk/complexity would call for.
- **Severity** — low/medium/high, the same scale `cartographer-spec-drift`
  uses, for consistency across the cartography family.
- **Suggested next step** — concrete and small (e.g. "add a CI job that
  runs the existing test suite on PR," not "improve testing culture").

If `docs/cartography/README.md` exists, link this file from its body
alongside the other always-present docs, the same way `cartographer-
explore`'s Step 1 links Methodology/Deployment/Entrypoint. If
`cartographer-explore` hasn't been run on this project, just report
findings directly in chat instead of inventing a Context doc to link from.

## What this doesn't do

Doesn't fix anything — same "flag it, let the human decide" principle as
`cartographer-spec-drift`. Doesn't replace `cartographer-explore`'s
Step 1.5 (purely descriptive indexing) — if both are run, Step 1.5 should
run first and this skill should read its output rather than re-discovering
from scratch. Doesn't invent process ceremony a project hasn't asked for —
recommending "adopt spec-driven development" or "add a formal spec
process" is only in scope as a flagged *option* with a stated reason,
never as an unprompted mandate.
