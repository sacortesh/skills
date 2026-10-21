---
name: code-review-cheap
description: Runs a cheap, targeted code review against a git diff — deterministic evidence first (existing lint/test/typecheck results, heuristic risk scoring, bounded "smart context" built outward from the diff), then exactly one independent AI review pass (Sonnet, medium effort) validated against a strict output schema before anything is reported. Finds concrete correctness, security, contract-mismatch, and regression problems with evidence and a verification status; never approves, merges, or auto-fixes, and never posts PR comments unless the user explicitly asks for that in the same request. Detects a GitHub/Bitbucket/GitLab remote via a pluggable connector (GitHub implemented) to pull PR intent and, on request, post findings as inline review comments, or works local-only without one. Use when the user wants a quick, low-cost review of a diff, PR, or branch instead of — or before — a full multi-agent review, or asks to "review this PR," "review this diff," or "review these changes cheaply."
---

# Code Review — Cheap

## Contents
- Why this shape
- Non-goals
- Prerequisites
- The process
  - Step 0 — Resolve inputs and connector
  - Step 1 — Collect the diff
  - Step 2 — Deterministic evidence
  - Step 3 — Assess risk
  - Step 4 — Build smart context
  - Step 5 — One independent AI review
  - Step 6 — Validate and render
  - Step 7 — Post comments (opt-in, GitHub only)
- Output conventions
- What this doesn't do yet

## Why this shape

A full agentic code review (separate subagents, broad codebase search,
a strong model) is the right tool when the stakes justify the cost. Most
diffs don't. This skill's whole premise: spend on determinism first
(diff parsing, existing lint/test/typecheck, keyword-level risk
heuristics — all free, all exact), bound the context by actual relevance
rather than dumping files, and spend exactly **one** model call — a
fixed model (Sonnet), fixed effort (medium), fixed count (one) — doing
the one thing determinism can't: judging whether the code actually does
what it claims to. Evidence-backed findings over broad coverage; a
validated "I didn't look at X" over a silent guess.

## Non-goals

Carried over deliberately, not because they're hard but because they
change what this tool is:

- Autonomous approval, merging, or code fixes.
- Posting PR comments *without being asked for it in that request* —
  Step 7 exists, but it never runs by default, and it is never chained
  automatically after a plain "review this PR."
- Full-codebase embedding/indexing or a complete cross-language call
  graph — `build_context.py`'s caller/callee search is bounded text
  search, always labeled "candidate," never asserted as verified or
  complete.
- Multiple parallel reviewers or automatic escalation to a stronger
  model — one call, fixed model and effort, every time.
- Style commentary, commit-squashing, or merge-strategy advice.
- A dashboard or persistent background service — this is a one-shot
  pipeline, run on demand.

## Prerequisites

- `git`, `python3` (stdlib only — no `pip install` required for the
  bundled scripts).
- `rg` (ripgrep) is used by `build_context.py` for the caller/callee
  search if present on PATH; it degrades to a slower pure-Python walk
  if not, so it's a speed optimization, not a hard requirement.
- `gh` CLI, already authenticated, if the repo has a `github.com`
  remote and PR metadata should be pulled in — see
  `references/vcs-connectors.md`. Not required for local-only review.
- The model call in Step 5 uses this environment's own `Agent` tool
  (`model: sonnet`, `effort: medium` — fixed, never scaled up to a
  stronger/pricier model like opus or fable, never scaled down either)
  — no separate API key, no external billing to configure.

## The process

### Step 0 — Resolve inputs and connector

Ask (or infer from context) the base ref and head ref — default to
comparing the current branch's HEAD against its upstream's default
branch if the user didn't say otherwise. Run:

```
python3 scripts/detect_connector.py --repo <repo>
```

If it returns an implemented connector (today: `github`), fetch PR
metadata:

```
python3 scripts/connectors/github.py --repo <repo> [--pr <number-or-url>]
```

If the connector isn't implemented (bitbucket, gitlab) or none matched,
proceed local-only — this is expected, not an error, and gets recorded
as a coverage note later, not surfaced as a failure now.

Never switch branches or otherwise modify the working tree at any point
in this pipeline — every read goes through `git show`/`git diff <sha>..
<sha>`.

### Step 1 — Collect the diff

```
python3 scripts/collect_diff.py --repo <repo> --base <base_ref> --head <head_ref> --merge-base
```

This resolves both refs to immutable SHAs (recorded in every later
output), excludes generated/vendor/binary files, summarizes
lockfile/manifest diffs instead of dumping them, and — for a
`.md`/`.mdx`/`.rst`/`.adoc` file past `DOC_LARGE_LINE_THRESHOLD` changed
lines — samples the first lines for decision-shaped content before
deciding whether the full diff is worth reviewing (see
`references/risk-heuristics.md`'s "Documentation triage" section).
Report both the exclusions and any doc-triage skips (`doc_triage_skips`)
to the user in one line each — don't bury either.

### Step 2 — Deterministic evidence

Look for an existing, repo-native way to lint/typecheck/test this
change (`package.json` scripts, a `Makefile` target, a CI config file)
rather than inventing a command. If one exists and the user has opted
into execution for this run, build a config JSON (see
`run_checks.py`'s docstring for the shape) and run:

```
python3 scripts/run_checks.py --repo <repo> --config <config.json> --execute
```

Without explicit opt-in, skip execution — every configured check
reports `skipped`, which stays visible in the final report rather than
silently vanishing. A missing or skipped check is never treated as
proof the code is fine.

### Step 3 — Assess risk

```
python3 scripts/assess_risk.py --diff-json <diff.json>
```

Transparent heuristics only — see `references/risk-heuristics.md`. This
never triggers a bigger model or an extra call; it only sizes Step 4's
budget and sets whether Step 6 marks the run as needing human review.

### Step 4 — Build smart context

```
python3 scripts/build_context.py --repo <repo> --diff-json <diff.json> --risk-json <risk.json> [--metadata-json <metadata.json>]
```

Builds the bounded context manifest in priority order (PR intent → diff
hunks → enclosing function/class → signatures/imports → candidate
callers/callees → relevant tests → trusted repo rules — see the
script's docstring). If the budget is hit partway through, the manifest
says so explicitly (`coverage: partial`) with the specific omissions —
never a silent truncation reported as a complete pass.

### Step 5 — One independent AI review

Spawn exactly one `Agent` call — `model: sonnet`, `effort: medium`,
default `subagent_type` (general-purpose is fine; this pass only
reasons over what it's handed, it doesn't need any tool access beyond
that), **not** a fork (this needs a fresh session with no access to
whatever conversation produced the diff, per
`templates/review-prompt.md`'s own framing). Feed it:

- `templates/review-prompt.md` as the instruction body.
- The context manifest from Step 4.
- The risk level and reasons from Step 3.
- The deterministic check results from Step 2, if any ran.

Require its reply to be the raw JSON described in
`references/schema.json` — nothing else. Save that reply to a file;
Step 6 validates it from disk rather than trusting it inline.

### Step 6 — Validate and render

```
python3 scripts/validate_findings.py --findings <model_output.json> --diff-json <diff.json> [--checks-json <checks.json>]
python3 scripts/render_report.py --repo <repo> --diff-json <diff.json> --risk-json <risk.json> \
  --context-manifest <context.json> --validated-findings <validated.json> [--checks-json <checks.json>]
```

`validate_findings.py` rejects anything that doesn't match the schema,
confirms every cited file/line range actually exists in the inspected
diff snapshot, dedupes against failing deterministic checks, and caps
at 5 findings without padding to reach that number. Malformed model
output becomes `status: invalid_output` and an explicit `failed`
pipeline status in the rendered report — never a silently "clean"
review.

`render_report.py` writes `review.json` and `review.md` under
`.code-review/` and appends one line to `.code-review/usage.jsonl`
(timestamp, SHAs, call count, finding counts by severity, pipeline
status — a measurement record, not a cost ledger, since there's no
separate billing to track here).

Then call this environment's own `ReportFindings` tool with the
validated findings list (most-severe first) so the review also renders
natively in this session, in addition to the persisted files.

### Step 7 — Post comments (opt-in, GitHub only)

Only run this step if the user's request explicitly asked for findings
to be posted to the PR (e.g. "review this PR and comment," "post the
findings") — never because a GitHub connector was detected, never
because the run found findings, and never on a plain "review this PR."
Posting to a shared PR is visible to everyone on it and not cleanly
reversible, so confirm with the user before running this even when
they asked for it in the same message, unless they've already stated a
standing preference to skip that confirmation.

If `validated_findings` is non-empty and the connector is `github`:

```
python3 scripts/post_comments.py --repo <repo> --pr <number-or-url> --validated-findings <validated.json>
```

This posts exactly one GitHub review (`gh api .../pulls/<n>/reviews`,
`event: COMMENT`) containing one inline comment per validated finding,
anchored to its file/line/side — one API call for the whole batch, not
one per finding, and never an approval or change request. Not available
for Bitbucket/GitLab — no connector there yet (see
`references/vcs-connectors.md`); tell the user and fall back to the
rendered report only.

## Output conventions

- `.code-review/review.json` — full machine-readable report (metadata,
  risk, checks, context manifest, validation result, findings).
- `.code-review/review.md` — the human-readable version, grouped into
  Potential blockers / Other actionable findings / Questions and
  missing evidence / Review coverage and limitations.
- `.code-review/usage.jsonl` — one append-only line per run.
- Pipeline status (`completed` / `partial` / `failed`) is always
  reported separately from review disposition (`findings` /
  `no-findings` / `human-review-required`) — a failed pipeline is never
  mistaken for a clean review, and "no findings" never means "safe" or
  "approved."

## What this doesn't do yet

- No Bitbucket or GitLab connector — documented in
  `references/vcs-connectors.md` as the next thing to add, not
  implemented here.
- No local result cache keyed by SHAs/prompt-version/config — every run
  does its own Step 5 call. Worth adding if repeated re-reviews of an
  unchanged diff turn out to be common; not built until that's actually
  true.
- No monetary cost ledger or multi-provider adapter — this skill runs
  inside an existing Claude Code session rather than as a
  separately-billed CLI, so call-count (fixed at 1) and context/token
  bounding are the real cost controls, not a dollar estimate.
- No bounded second-pass verification step for specific candidate
  findings — the spec this skill was adapted from describes one as
  optional future work, separately budgeted; same here.
