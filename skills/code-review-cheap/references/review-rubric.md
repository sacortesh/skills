# Review rubric

## Contents
- Focus on
- Do not report
- Required fields (see schema.json)
- Output grouping
- What "no findings" means

This is the rubric handed to the single AI review pass — it's what makes
the review adversarial and bounded instead of a generic "looks good to me"
or a wall of style nitpicks.

## Focus on

- Incorrect behavior and edge cases the diff actually introduces.
- Security boundaries and permissions — auth/authz checks, trust
  boundaries crossed by the change.
- Contract mismatches between changed code and its actual consumers
  (signature changes, removed exports, altered return shapes).
- Data integrity and destructive operations (migrations, deletes, writes
  without the validation the surrounding code implies).
- Regressions in behavior the base ref actually supported.
- Missing validation or tests, but only when tied to a concrete failure
  scenario — not a generic "add more tests."
- Comments used as a justification for a shortcut (e.g. "doing it this
  way because X is slow/broken/flaky") — treat the comment as evidence
  of an admitted, unresolved risk in the category it describes, not as
  a reason to wave the change through. Verbose doc comments that narrate
  ticket/PM history instead of a non-obvious invariant are the same
  smell: they're usually covering for unclear code rather than
  documenting it, and that's worth a finding only if it's hiding or
  excusing the behavior above, not for the prose itself.

## Do not report

- Formatting or stylistic preferences — a linter's job, not this one's.
  This excludes comment *prose style*; a comment that justifies a
  shortcut or masks unclear code is reported under "Focus on" above,
  not here.
- Speculative architectural rewrites.
- Generic "add more tests" with no scenario attached.
- Unsupported assumptions about business requirements the diff doesn't
  state anywhere.
- Pre-existing defects the diff didn't introduce or touch — this is a
  diff review, not a codebase audit.

## Required fields (see schema.json)

Every finding needs: severity, category, file + exact line range + side
(base/head), a short title, triggering conditions, concrete consequence,
evidence connecting the change to the failure, a remediation direction
(not a prescribed diff), and a verification status (model-hypothesis /
statically-supported / reproduced-by-check). Model confidence is never a
substitute for a measured verification status — a finding the reviewer
feels strongly about but that no deterministic check corroborates stays
`model-hypothesis`.

## Output grouping

`render_report.py` groups validated findings into:

- **Potential blockers** — critical/high, needs human validation before
  merge.
- **Other actionable findings** — medium/low.
- **Questions and missing evidence** — from the `questions` array; real
  uncertainties, not findings in disguise.
- **Review coverage and limitations** — what was and wasn't inspected,
  carried over from the context manifest (`build_context.py`'s output).

## What "no findings" means

An empty `findings` array renders as:

> No actionable findings within the inspected scope.

It never renders as "this code is safe" or "approved" — the pipeline
doesn't know what it didn't look at, and `build_context.py`'s coverage
flag is the honest record of that. A clean report with `partial`
coverage must say so plainly in the same breath as "no findings."
