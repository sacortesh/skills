---
name: cartographer-spec-drift
description: Finds and triages disagreements between a written claim (a spec, PRD, comment, prior doc, an earlier AI agent's "done" note) and what the code actually does, then persists a triaged list — category (bug/technical-debt/refactor/architectural-decision/spec-staleness), severity, and delegation strategy (agent-solo/ai-assisted-session/manual-user-task) — to docs/cartography/DRIFT.md. Works standalone against an existing map or a bare codebase, or gets invoked by cartographer-explore once, aggregated across every feature touched, during its Step 4. Use whenever the user suspects a spec or a prior agent's "done" claim doesn't match the code, wants a drift report, asks "does this still match the spec," "has this gone stale," or wants a persisted, triaged list of spec-vs-code disagreements rather than an ad-hoc check. Trigger also on "audit this against the spec," "check for drift," "/spec-drift."
---

# Cartographer: Spec Drift

## Contents
- Two ways this gets invoked
- Finding drift
- Not checked
- Output
- What this skill doesn't do

If a spec, comment, or prior doc claims something the code doesn't actually
do, that mismatch is usually the single most valuable thing an
investigation can surface — more valuable than any diagram. This skill's
job is to find that mismatch and triage it, nothing more:

- Report it plainly.
- Don't quietly "fix" the doc to match the spec's claim.
- Don't quietly fix the code either.
- Flag it and let the user decide which one was actually wrong.

The delegation-strategy field (below) classifies *how* a finding could be
resolved — it does not resolve it.

## Two ways this gets invoked

1. **Standalone** — the user hands you a feature (or the whole project)
   directly and wants a drift check right now, with or without a
   pre-existing `docs/cartography/` map.
2. **Delegated from `cartographer-explore`** — called exactly once per run,
   aggregated across every feature touched, during that skill's Step 4
   (never per-feature — a single invocation is the only point it's called
   from a fresh run). Each feature's purpose, layers touched, and rules
   table are already known from the caller's own Step 1-3 work — use
   what's handed to you rather than re-deriving it from scratch.

## Finding drift

For each feature in scope (or the whole project, if run standalone with no
feature named), actively search for a written claim to check against
before concluding none exists:

- A spec, PRD, user story, or BDD feature file
- A code comment describing intended behavior
- A prior `docs/cartography/<feature>.md` from an earlier
  `cartographer-explore` run
- An earlier AI coding agent's "done"/"implemented"/completion note (commit
  messages, PR descriptions, session logs if accessible)
- Adjacent `specs/`, `docs/`, or `.claude/`-style planning directories

Read whatever you find, verify it against the actual code — never the
spec's own prose, never inferred, always the real implementation — and
report agreement or disagreement plainly. Treat the code as ground truth
for "what happens now." The point isn't to shame the discrepancy; it's to
give the user a decision: was this a misunderstood intent (fix the code to
match), or did the intent change and the spec's just stale (fix the spec)?

Never write "no spec exists" as an unqualified fact — either name
specifically what you checked, or record the gap in **Not checked** (below)
rather than asserting a negative you didn't actually verify.

Also catch drift that isn't spec-vs-code at all — any code-level finding
worth a human decision even without a competing written claim: dead code, a
missing implementation behind an advertised feature, inconsistent
fail-open/fail-closed behavior, a tier/permission gate enforced in only one
layer, and so on.

## Not checked

Same discipline as the rest of the cartography family: a short, explicit
list of what you chose not to verify further — a reference you confirmed
was irrelevant but didn't trace fully, a risk you noticed but didn't chase,
a directory you didn't search. Required, even if short — it's what makes
every other claim here honest and checkable instead of a silent gap or an
unfalsifiable negative.

## Output

Write (or update) `docs/cartography/DRIFT.md`. Each entry needs:

- **What** — the concrete disagreement or finding, stated plainly, with
  file/line pointers.
- **Triage category** — `bug` | `technical-debt` | `refactor` |
  `architectural-decision` | `spec-staleness`. Pick whichever names *what
  kind of thing* this is, not how bad it is.
- **Severity** — however you'd naturally rank it (low/medium/high, or a
  one-line "why this matters").
- **Delegation strategy** — who or what can actually resolve it:
  `agent-solo` (a subagent could just fix it, no judgment call needed),
  `ai-assisted-session` (needs a human-in-the-loop AI session — there's a
  tradeoff or missing context only the human has), or `manual-user-task`
  (needs the human directly — a product/business decision, external
  coordination, something outside what any agent can act on).

If a run finds zero disagreements, still write the file saying so plainly —
an explicit "nothing found" is worth more than a missing file someone has
to guess the meaning of. If `docs/cartography/DRIFT.md` already exists,
read it first and update rather than discard prior entries that are still
accurate; only drop an entry once it's actually been resolved or
re-verified as no longer present.

Surface the same findings as a distinct, scannable list in your report to
the user too — that's often the most actionable part of the whole run —
but the persisted file is now the record of truth, not just the chat
message. `docs/cartography/README.md` (if it exists) doesn't need its own
link to `DRIFT.md` — it's regenerated per-run rather than a stable
reference doc, so it's mentioned in-report instead of linked from the
Context doc. Keep that convention if `cartographer-explore` has already
been run on this project.

## What this skill doesn't do

Doesn't fix anything — flags only, same principle as
`cartographer-methodology-audit`. Doesn't replace `cartographer-explore`'s
"paintable" filter — if a feature was already judged not worth a dedicated
map, running a drift check on it anyway is a standalone-mode judgment call
here, not something that happens automatically as part of a full
`cartographer-explore` run. Doesn't generate diagrams or rules tables —
that's `cartographer-explore`'s Step 3; this skill consumes that output
when it's available rather than re-deriving it.
