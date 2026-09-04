# Phase 7 — Journey Report (Gherkin/BDD)

This phase documents what was actually built — the real navigation (Phase
2), the real components (Phase 4), the real behavioral requirements (Phase
1) — not the original brief's assumptions. It's the handoff artifact: an
external tester or the user taking ownership of the code should be able to
read it and know what to verify, without reading the implementation.

If Phase 1 named behavioral requirements, ground scenario-writing in the
habit-loop thinking of Eyal's *Hooked* (trigger → action → reward) and the
target-behavior framing of Wendel's *Designing for Behavior Change* — so
the scenarios actually test whether the intended behavior occurs, not just
whether the screen renders.

## Format

Standard Gherkin: `Feature` → `Scenario` → `Given/When/Then`. One `.feature`
file per Phase 2 district or major flow, not one giant file for the whole
app.

```gherkin
Feature: <District or flow name, from Phase 2>
  As a <persona from Phase 1>
  I want to <job-to-be-done from Phase 1>
  So that <the outcome that matters to them>

  Scenario: <one primary path through this flow>
    Given <starting state — e.g. "I am on the dashboard node">
    When <action a user actually takes, via the components from Phase 4>
    Then <the observable, verifiable outcome>
    And <response time / feedback signal, if Doherty Threshold applies>

  Scenario: <an edge case or error path>
    Given <state>
    When <action that should fail or need correction>
    Then <the error is specific and actionable, per the taste checklist's trustworthy-building pillar>
```

## Deriving scenarios

1. Walk each primary path identified in Phase 2's navigation tree — each
   becomes at least one scenario.
2. For every organism in Phase 4 with interactive state (forms, wizards,
   toggles), write a scenario for its primary success path and at least one
   failure/validation path.
3. For every organism with async state, write scenarios covering the full
   interaction cycle, not just the success path: loading (does it show a
   layout-matching skeleton, not a generic spinner), empty state, error
   state (specific and actionable per the taste checklist's trustworthy-
   building pillar), and tactile feedback on the triggering action.
4. Where Phase 3's motion pass claimed a specific `MOTION_INTENSITY`
   (`references/taste-checklist.md`), write a scenario that verifies the
   claimed motion actually fires — a page claiming intensity `7` with no
   observable animation is a defect, not a style choice.
5. For every behavioral requirement named in Phase 1, write a scenario that
   verifies the target behavior, not just the UI state — e.g. for a habit
   loop, a scenario that the reward/feedback actually fires after the
   triggering action.
6. Check closing states against the Peak-End Rule (`references/ux-laws.md`)
   — a flow's last scenario should cover what the user sees at completion,
   since that's what they'll remember.

## Output

Write to `journeys/<district-or-flow>.feature` files (or a single
`journeys.feature` for a small app). Alongside them, write a short
`journeys/README.md` covering:

```markdown
## How to run these
[Whatever BDD runner fits the stack — Cucumber, Playwright-BDD, etc. — or,
if none is wired up yet, state plainly that these are currently
specification-only and name the runner that would execute them.]

## Coverage
- Scenarios: [count] across [count] features
- Districts covered: [list from Phase 2]
- Behavioral requirements verified: [list from Phase 1, or "none specified"]

## Known gaps
[Any Phase 2 path or Phase 4 component with no scenario yet — name it
rather than silently omitting it.]
```

This is the final deliverable of the full pipeline: at this point the user
(or an external tester) owns a navigable spec of the real, built product,
independent of this skill.
