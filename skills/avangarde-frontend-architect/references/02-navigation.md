# Phase 2 — Assembling Navigation Architecture

Ground this phase in Kevin Lynch's *The Image of the City*: a legible city
and a legible site share the same problem — someone unfamiliar with the
place needs to build a working mental map fast.

## Lynch's five elements, mapped to site IA

| Lynch's urban element | Site/app equivalent |
|---|---|
| **Paths** | The primary flows a user travels — the main nav, the checkout flow, the onboarding sequence |
| **Edges** | Section boundaries — where "marketing site" ends and "app" begins, where a wizard's steps are bounded |
| **Districts** | Distinct areas with their own identity — "Settings," "Dashboard," "Docs" — each recognizably itself |
| **Nodes** | Decision points and hubs — a dashboard home, a search results page, a cart |
| **Landmarks** | Fixed, unmistakable reference points — logo/home link, a persistent "you are here" indicator |

A site with clear paths, honest edges, distinct districts, useful nodes, and
a couple of landmarks is navigable the way a legible city is — you build a
mental map after one visit instead of getting lost every time.

## Build the sitemap

1. List every screen/page implied by the Phase 1 brief's job-to-be-done and
   content inventory.
2. Group them into districts. If a district needs more than ~7 direct
   children, chunk it further (Miller's Law) rather than listing them flat.
3. Identify nodes — pages more than one path leads to — and make sure they
   answer "where am I, what can I do here" without relying on the browser
   back button.
4. Place the highest-value actions at the start or end of any nav list, not
   buried in the middle (Serial Position Effect).
5. Don't invent a navigation pattern the audience hasn't seen before unless
   the brief specifically calls for it (Jakob's Law) — breadcrumbs, tab
   bars, and sidebar nav are underused not because they're boring but
   because they work.
6. **Mechanical constraints for the primary nav** (from
   `references/taste-checklist.md`): it must render on a single line at
   desktop — condense labels, drop secondary items, or move to a hamburger
   before letting it wrap to two lines — and stay ≤80px tall (default
   64-72px). An "agency" nav bar eating 15% of the viewport fails this on
   sight, independent of how good the visual design is.

## Output: navigation tree

Write to `DESIGN.md` under a `## Navigation` section (append — don't
overwrite the `## Requirements` section Phase 1 already wrote):

```markdown
## Navigation
### Sitemap
- Home (landmark)
  - District A
    - Page
    - Page
  - District B
    ...

### Primary paths
1. [Flow name]: Home → ... → completion
### Nodes
- [Page]: reachable from X, Y; primary action: ...
### Landmarks
- [Element]: persistent across all districts
```

Feed this directly into Phase 4 (components) — every node and district
implies at least a nav component and a landing/index component.
