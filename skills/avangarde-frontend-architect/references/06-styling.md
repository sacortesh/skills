# Phase 6 — Styling Approach: Tailwind or Plain CSS

This is a user choice, not a default. Present the trade-off explicitly
(AskUserQuestion is appropriate here if it hasn't already been settled in
Phase 1's constraints) rather than picking silently.

## First check: does an official design system already own this problem?

Tailwind-vs-CSS is the right question only once you've ruled out that the
brief actually names (or clearly implies) a design system with an official
package — don't hand-roll what's already solved and accessibility-audited:

| Brief reads as… | Reach for | Why |
|---|---|---|
| Microsoft/enterprise SaaS, dashboards | `@fluentui/react-components` | Official Fluent, accessibility done |
| Material-flavored product | `@material/web` + Material 3 tokens | Official, theme-able |
| IBM-style B2B/analytics | `@carbon/react` | Mature data-density patterns |
| GitHub-style devtool/community page | `@primer/react` (or `@primer/react-brand` for marketing) | Official Primer |
| Public-sector (UK / US) | `govuk-frontend` / `uswds` | Often regulatorily expected |
| Modern accessible React foundation, own the styling | `@radix-ui/themes` | Primitives + polished theme |
| Modern SaaS, want to own the component code | shadcn/ui | You own it, customize freely — never ship in default state |
| **Solo/small-team product with its own bespoke identity — not a marketing/landing page, not enterprise B2B** | shadcn/ui or bare `@radix-ui/react-*` primitives + Phase 3's tokens | Unopinionated enough to carry a bespoke identity without fighting a system's visual language, while still getting accessible primitives for free. This is the common case that's neither of the two extremes above — name it explicitly here rather than reaching it by process of elimination. |

If one of these fits, install and use the **official** package rather than
recreating its CSS by hand, and don't import a system's tokens only to
override most of them. Use exactly one system per project — don't mix
Fluent and Carbon, or shadcn and Material, in the same tree. Only fall
through to the Tailwind-vs-CSS decision below when the brief is a bespoke
aesthetic direction with no owning system, or explicitly wants hand-rolled
styling.

**Note for the bespoke-product row above**: `references/taste-checklist.md`'s
mechanical rules (hero word counts, eyebrow caps, marquee limits, bento
cell counts) target marketing/landing surfaces specifically. A product app
that lands in this row still uses Phase 3's OKLCH/token process and the
taste checklist's consistency locks (color/shape/theme) and AI-tell list,
but its landing-page-specific mechanical checks mostly don't apply to a
dashboard-like or tool-like screen — use judgment on which sections of that
checklist actually fit the surface at hand.

## Decision inputs

| Signal | Favors Tailwind | Favors plain CSS |
|---|---|---|
| Team size / familiarity | Team already knows Tailwind, or is solo and wants speed | Team has strong CSS conventions already, or is CSS-first |
| Component reuse | High reuse across a component library (utility classes compose fast) | Few, highly bespoke components where semantic class names pay off |
| Design token maturity | Tokens defined in Phase 3 map cleanly to a Tailwind theme config | Tokens are better expressed as CSS custom properties consumed by hand-written rules |
| Long-term maintainability concern | Fine as long as components stay atomic (Phase 4) — utility soup is a symptom of skipping component extraction, not of Tailwind itself | Fine as long as a naming convention is enforced — unscoped globals are the equivalent failure mode |
| Longevity / portability | Locks into a build-time config but not a runtime framework | No build dependency; more portable across framework changes |

Neither is "correct" — reference `references/ux-laws.md`'s Postel's Law and
Occam's Razor here: pick the simpler system that's still tolerant of the
team's actual working style, and commit to the maintainability rules below
for whichever wins.

## If Tailwind wins

- Map every Phase 3 design token into `tailwind.config` (`theme.extend`) —
  no ad hoc hex values or magic numbers in `className` strings.
- Extract repeated utility combinations into components (Phase 4's atoms),
  not into `@apply` soup — `@apply` recreates the plain-CSS maintainability
  problem inside Tailwind.
- Keep responsive/state variants (`hover:`, `md:`, `dark:`) attached to the
  element they affect; don't scatter the same breakpoint logic across many
  unrelated components.
- Lint for arbitrary-value overuse (`w-[137px]`) — a real design token
  should exist for anything reused more than once.

## If plain CSS wins

- Use CSS custom properties for every Phase 3 token (`--color-primary`,
  `--space-4`, `--font-display`) at a single `:root` (or theme-scoped)
  source of truth — no repeated literal values.
- Scope styles per component (CSS Modules, `:where()`/`:is()` scoping, or a
  strict BEM-like naming convention) — global unscoped class names are the
  plain-CSS version of utility soup.
- Watch selector specificity carefully when composing section + element
  selectors (e.g. `.section` and `.cta` both touching padding/margin) —
  this is the most common source of styles silently cancelling each other
  out.
- Co-locate a component's styles with its file rather than one large
  global stylesheet, once the component inventory (Phase 4) is nontrivial.

## Output: styling decision

Write to `ARCHITECTURE.md` under a `## Styling` section (append — the
`## Frontend Architecture` section from Phase 5 stays intact above it):

```markdown
## Styling
### Approach
[Official design system name] / Tailwind / plain CSS — [why, from the
decision inputs above]
### Token mapping
[how DESIGN.md's `## Theme` tokens map to this approach's mechanism —
tailwind.config keys, or CSS custom-property names]
### Maintainability rules
[the specific rules from this file that apply — e.g. "no @apply soup,"
"CSS Modules per component," "no arbitrary Tailwind values over 1 use"]
```

## Either way: shared maintainability floor

- One source of truth for design tokens (Phase 3), consumed by name, never
  duplicated as raw values.
- Responsive down to mobile, visible focus states, `prefers-reduced-motion`
  respected — the same accessibility floor as Phase 3, now actually
  implemented.
- Document the choice and its rules in the project's own README so someone
  taking ownership later (Phase 7) knows which convention to follow.
