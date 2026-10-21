# Risk heuristics

## Contents
- Why heuristics, not a model call
- The dimensions
- What risk level controls
- Stated limitations

## Why heuristics, not a model call

`assess_risk.py` is pure pattern-matching — keyword/path/regex checks
against the diff, never a model call. Two reasons: it has to run before
any context budget decision exists (so it can't depend on the thing it's
sizing), and letting risk level be judged by the same kind of call it's
meant to budget would make the budget self-referential. Risk output
decides how much context `build_context.py` is worth spending and
whether `render_report.py` should mark the run as needing human review —
it never triggers a bigger model, a second call, or any other spend on
its own.

## The dimensions

- **Auth/authz, secrets, payments** — changed files under common
  auth/session/permission paths, added/removed calls to permission-check
  functions, diffs touching anything matching secret-like patterns
  (API key, token, password, credential identifiers) even if the value
  itself is redacted before it ever reaches this script.
- **Data deletion, migrations, persistence** — migration files, DROP/
  DELETE/TRUNCATE-shaped SQL, schema files, ORM model changes.
- **Shared state, concurrency, infrastructure** — lock/mutex/semaphore
  usage, queue/worker config, infra-as-code files, env/config files that
  fan out to multiple services.
- **Public API/schema/signature changes** — exported function signatures
  changed, public schema/contract files (OpenAPI, GraphQL schema, proto)
  touched, a removed export.
- **Shared utilities with many callers** — a changed file whose exports
  show up in a bounded reference search (see `build_context.py`) above a
  configurable caller-count threshold.
- **Size and test coverage** — large diffs (line/file count thresholds),
  diffs touching source files with no corresponding test file touched in
  the same change, unresolved merge-conflict markers or newly added
  TODO/FIXME left in the diff.

## What risk level controls

- `low` — tight context budget, no human-review flag by default.
- `medium` — standard context budget (the defaults `build_context.py`
  ships with).
- `high` — widened context budget (more hop depth, more per-file
  snippet room, within the same single-call limit) and the rendered
  report is marked "human review required" regardless of what the AI
  pass finds — a clean AI review on a high-risk diff is not the same
  claim as a clean AI review on a low-risk one.

Risk level never changes the model, the effort level, or the call count
— those stay fixed (sonnet, medium, one call) regardless of risk. Risk
only reallocates the fixed budget and sets the human-review flag.

## Documentation triage (collect_diff.py, not assess_risk.py)

A sibling deterministic heuristic, same spirit, different script: a
`.md`/`.mdx`/`.rst`/`.adoc` file under `DOC_LARGE_LINE_THRESHOLD` changed
lines goes through untouched, exactly like any other file — no triage,
no special-casing. Past that threshold, `collect_diff.py` samples only
the first `DOC_SAMPLE_LINES` *added* lines for decision-shaped content
(a table, a code/schema block, normative language, a concrete numeric
limit, an API/contract noun, an HTTP route) before deciding whether the
full diff earns a place in Step 4's context budget. No signal in the
sample → the full hunks are swapped for a short note, the sample
excerpt is kept for audit, and the skip is recorded in
`doc_triage_skips` — surfaced in `review.md`'s coverage section, never
silently dropped. The point isn't "docs don't matter"; it's that a
400-line narrative rewrite and a 400-line spec change cost the same
tokens to review but not the same tokens to skip, and pure
ticket-narration prose is the case this exists to catch cheaply.

This is a sampling heuristic, not a full read — a load-bearing
invariant past line 60 of an otherwise-prose-shaped doc will be missed.
That's the explicit trade for keeping this at zero model cost; see
review-rubric.md's note on comments for the related judgment that a
verbose doc narrating process instead of invariants is itself a smell,
not just a cost problem.

## Stated limitations

These are keyword/path heuristics, not static analysis — they will miss
risk expressed only in logic with no recognizable keyword or path match,
and will occasionally flag a file as higher-risk than it is (a test
fixture named `secrets_test_data.json`, a file merely importing a crypto
library without touching an auth boundary). `render_report.py` always
prints the specific reasons a risk level was assigned, so a human can
discount a flag that's clearly a false positive — the heuristic output
is never presented as a verdict on its own.
