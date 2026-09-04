# Phase 3 — Assembling Themes

Ground this in the grid-systems/color-theory/type-pairing/proportion
grounding of Kadavy's *Design for Hackers* and the perceived-affordance
thinking of Norman's *The Design of Everyday Things*. Run
`references/taste-checklist.md` on the result before presenting it — this
is the phase most prone to generic-default output.

## Set the three dials first

Before planning tokens, state where this brief sits on
`references/taste-checklist.md`'s three dials — DESIGN_VARIANCE,
MOTION_INTENSITY, VISUAL_DENSITY (each 1-10) — using its brief-signal
table. Every choice below should trace back to these values: a `variance:
9` brief justifies an asymmetric, rule-breaking layout that a `variance: 4`
brief would not.

## Color: decide in OKLCH, commit as hex

Lock the brand anchor color before anything else in this phase — background,
surface, text, and accent all derive from it, so getting it right first
avoids re-deriving the rest of the palette later.

- **Why OKLCH, not HSL/RGB**: OKLCH's lightness axis is perceptually
  uniform — two colors at the same `L` actually look equally light, and
  `L` correlates predictably with contrast ratio. HSL doesn't have this
  property: `hsl(60 100% 50%)` (yellow) and `hsl(240 100% 50%)` (blue)
  share a lightness value but are wildly different in perceived brightness
  and in contrast against the same background. OKLCH is the right space to
  *reason* in — hit a target WCAG contrast ratio by moving `L` directly,
  step a tint/shade ramp at fixed `L` intervals without HSL's muddy
  midtones, and keep an accent visibly distinct from the primary by
  separating hue while holding `L`/`C` comparable so the distinction reads
  as intentional.
- **Process**:
  1. Define the brand anchor (usually `--color-primary`) as `oklch(L C H)`
     first — the one color the Phase 1 subject and mood should drive most
     directly.
  2. Derive the rest from it in OKLCH: background/surface by shifting `L`
     (holding `H`, dropping `C` toward zero for near-neutral surfaces),
     text by pushing `L` to the opposite end until the contrast math clears
     WCAG AA against its background, accent by rotating `H` (or picking a
     second anchor) while keeping `L`/`C` in a comparable range.
  3. **Convert every OKLCH value to hex deterministically — compute it,
     don't eyeball it.** Run an actual OKLCH→sRGB conversion (e.g. Node
     with `culori`'s `formatHex(oklch(...))`, or Python with `coloraide`)
     so the same OKLCH input always produces the exact same hex. If no
     conversion tool is available in the environment, say so explicitly
     rather than emitting an approximated hex — an eyeballed conversion
     defeats the point of choosing colors in a deterministic space.
  4. Record both forms in the output: OKLCH as the design intent (what to
     tweak if a color needs to change), hex as the committed token value
     everything downstream — Tailwind config, CSS custom properties,
     design tools — actually consumes. Hex stays the interchange format;
     OKLCH is how you got there, not a replacement for it in shipped
     tokens.

## Work in two passes (adapted from Anthropic's frontend-design)

**Pass 1 — plan.** Before writing any CSS, produce a compact token plan:

- **Color**: 4-6 named colors forming the core palette, decided per the
  OKLCH-first process above and committed as hex — not a default
  terracotta/cream or near-black/acid-green scheme unless the brief
  actually calls for that mood. Premium-consumer briefs (cookware,
  wellness, artisan, luxury) pull toward a specific banned default — warm
  beige/cream + brass/clay/oxblood/ochre + espresso text — hard enough
  that it's worth naming and deliberately avoiding; see
  `references/taste-checklist.md` for the exact hex families and rotation
  alternatives.
- **Type**: one or two typeface families and their roles (display vs. body).
  Two families should be clearly distinct from each other, not
  near-duplicates. Set a type scale with intentional weights and spacing —
  don't reach for Inter/Roboto/Arial/Space Grotesk by default. Serif is
  justified only when the brief names one or the aesthetic is genuinely
  editorial/luxury/heritage — reaching for serif because "it feels premium"
  is itself a tell (`references/taste-checklist.md`); `Fraunces` and
  `Instrument_Serif` are banned as defaults outright.
- **Layout**: a one-sentence layout concept plus an ASCII wireframe;
  state the alignment approach (left, centered, justified) explicitly.
- **Motion**: where the one deliberate moment of motion lives (a single
  page-load sequence, one reveal) — not scattered hover transitions.
- **Principles**: 2-3 sentences on what makes this palette/type/layout
  specific to *this* subject, not swappable with any other brief's.

**Pass 2 — review against the brief.** Ask: would this plan come out the
same for a different, unrelated brief? If yes, it's a default, not a choice
— revise it and note what changed and why. Only after this check, move to
implementation.

## Design tokens output

Write to `DESIGN.md` under a `## Theme` section (append — Phases 1-2's
sections stay intact above it):

```markdown
## Theme
Dials: variance [n], motion [n], density [n]

### Color
--color-bg: #______        (oklch(L C H))
--color-surface: #______   (oklch(L C H))
--color-text: #______      (oklch(L C H))
--color-primary: #______   (oklch(L C H))
--color-accent: #______    (oklch(L C H))

### Type
Display: [family], [weights used]
Body: [family], [weights used]
Scale: [base size + ratio, or explicit sizes]

### Layout
[one-sentence concept]
[ASCII wireframe]
Alignment: [left/center/justified]

### Motion
[the one deliberate moment, and what triggers it]
```

## Accessibility floor (non-negotiable regardless of aesthetic direction)

- Text contrast meets WCAG AA against its background — this should already
  be true by construction if step 2 of the OKLCH process above was
  followed, not something discovered after the fact by testing hex values.
- Visible keyboard focus states on every interactive element.
- `prefers-reduced-motion` respected for the motion pass above.
- The palette holds up in both the chosen theme and, if the product needs
  dark mode, its counterpart — don't design one and hope the other inverts
  cleanly.

Hand the finished token set to Phase 6 (styling) as the values that get
implemented as CSS custom properties or a Tailwind theme config, depending
on which approach wins that phase.
