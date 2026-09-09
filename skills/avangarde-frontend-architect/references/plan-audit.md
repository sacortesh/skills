# Auditing a Spec-Kit / SDD Plan Before It's Built

Use this instead of (or before) running phases 1-7 fresh, whenever the
request is to sanity-check a plan someone else already assembled — spec-kit's
`/specify`/`/plan`/`/tasks` output, or any Spec-Driven Development task
breakdown — for a frontend feature, before anyone writes code against it.
This audits the *plan*, not a codebase or a person's understanding of one —
that second thing is a different skill's job, not this file's.

The failure mode this exists to catch: a task list that *looks* complete —
has tasks, file paths, checkboxes — but silently skips a phase's real work.
No one actually decided the IA. No one considered accessibility. The
component list came from guessing at screen names instead of checking what
already exists. There's no acceptance criteria anywhere, so "done" only ever
meant "the code compiles."

## 1. Locate the plan

Spec-kit's own convention is `specs/<NNN-slug>/` containing `spec.md` (the
what/why), `plan.md` (the how), `tasks.md` (the actual checklist), plus
`research.md`, `data-model.md`, `quickstart.md`, `contracts/` as needed.
Other SDD flows vary — don't assume this exact layout; if the files aren't
where expected, ask the user to point at them rather than guessing a
structure that isn't really there.

Read `spec.md`, `plan.md`, and `tasks.md` fully before judging anything. A
phase that looks missing might just be covered under a task name that
doesn't obviously map to it — check before flagging.

## 2. Determine which phases actually apply

Not every feature needs all seven phases — a small addition to an existing
IA doesn't need Phase 2 revisited, a feature with no new visual surface
doesn't need Phase 3. Read `DESIGN.md`/`ARCHITECTURE.md` first if they exist
(this skill's own persistence files, per `SKILL.md`) to know what's already
decided project-wide, and only check the plan against phases actually in
scope for *this* feature.

## 3. Cross-check coverage, phase by phase

| Phase | What a complete plan should show | Where to look |
|---|---|---|
| 1. Requirements | A real audience and job-to-be-done, not an assumed "why." | `spec.md`'s rationale/why section |
| 2. Navigation | If this feature adds or changes navigation, an explicit task for it — not something that only appears implicitly inside a component task. | `plan.md`, `tasks.md` |
| 3. Theme | If the plan introduces any new visual choice, a task to define or extend design tokens — not colors invented ad hoc inside an implementation task. | `plan.md`; compare against `DESIGN.md`'s `## Theme` if it exists |
| 4. Components | New components distinguished from reuse of existing ones. A plan that names a new component per screen without checking what already exists (`references/04-components.md`'s inventory logic) is heading for duplication. | `tasks.md`; compare against `DESIGN.md`'s `## Components` |
| 5. Architecture | A file/module layout that matches this project's actual `ARCHITECTURE.md` decisions, not a new pattern invented for this one feature. | `plan.md`, `ARCHITECTURE.md` |
| 6. Styling | Consistency with whatever `ARCHITECTURE.md` already decided (Tailwind vs. CSS) — not a task quietly reaching for something else. | `plan.md`, `ARCHITECTURE.md` |
| 7. Journeys | A task, anywhere, that defines acceptance criteria or a testable user flow — not "done" meaning only "the code compiles." A plan with nothing equivalent to this has no way to know when the feature is actually finished from the user's point of view. | `spec.md`, `tasks.md` |

## 4. Check sequencing, not just coverage

A plan can name every task and still be ordered wrong. Flag:

- A build/implementation task scheduled before the design decision it
  depends on (e.g., "build ProfileCard component" listed before "define
  theme tokens," when no tokens exist yet).
- A testing/acceptance task with no earlier task that actually defines what
  "correct" looks like.
- Tasks marked independently parallelizable that actually share a
  dependency (two tasks both touching the same shared component or token
  file).

## 5. Catch AI-slop before it's built, not after

If the plan already commits to specific visual or copy choices — a task
says "use a blue gradient hero," a task description contains filler copy —
run those choices against `references/taste-checklist.md` now. Catching a
bad default while it's still a sentence in a plan is far cheaper than
catching it once Phase 4's own gate sees it as built code.

## 6. Report back

Same discipline as `adopting-existing-repo.md`'s audit: don't silently fix
the plan yourself. Present:

- A coverage table — phase by phase, covered / partially covered / missing,
  naming which task (if any) covers it.
- Sequencing issues, named specifically (which task, which dependency it
  jumps ahead of).
- A verdict: **Ready to build** (proceed with `tasks.md` as-is), **Needs
  revision** (name the specific tasks to add, split, or reorder), or **Too
  incomplete to assess** (enough of section 3's checks came back missing
  that judging sequencing is premature — recommend rerunning spec-kit's
  `/plan` or `/tasks` step, or the equivalent in whatever SDD tool produced
  this, before auditing again).

Let the user decide whether to fix the plan in its own tooling or hand it
back for a redo. This file audits someone else's plan; it doesn't rewrite it.
