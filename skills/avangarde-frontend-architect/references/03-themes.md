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

**Read `DESIGN.md`'s Primary Rendering Surface (Phase 1) before setting
MOTION_INTENSITY and VISUAL_DENSITY** — it caps both, independent of what
the aesthetic mood alone would suggest:

- Mobile-first: MOTION_INTENSITY has a real battery/perf ceiling regardless
  of mood — an "Awwwards/experimental" brief still can't spend a 9 here the
  way the same brief could on desktop. VISUAL_DENSITY also has a practical
  ceiling from screen size.
- Desktop-first (tools, dashboards, dense B2B): VISUAL_DENSITY can run
  higher than the brief-signal table's defaults suggest, since there's
  physical room and the audience expects information density.
- Kiosk/TV: MOTION_INTENSITY depends entirely on context — an ambient
  display wants near-zero incidental motion; an attract-loop screen may
  want to max it out. State which case this is; don't assume.
- Touch-primary surfaces (mobile, kiosk, tablet) can't rely on hover for
  anything load-bearing — any interaction planned around a hover state
  needs a touch-equivalent named now, not discovered during Phase 4.

## Breakpoint strategy

Decide this from Primary Rendering Surface, not by habit:

- **Mobile-first** (design and test the primary rendering surface's base
  styles first, then progressively enhance upward with `min-width` media
  queries) when the named primary surface is mobile or touch-first.
- **Desktop-first** (base styles target the desktop layout, then adapt
  downward) when the named primary surface is desktop — common for
  internal tools and dense dashboards where the mobile view is a secondary
  concession, not the main experience.
- State which one this brief uses in the token output below — Phase 6
  implements the actual breakpoint values, but which direction is
  "designed first" is a Phase 3 decision, because it changes which layout
  gets the most design attention.

## Color: decide in OKLCH, commit as hex

The brand anchor color drives everything else in this phase — background,
surface, text, and accent all derive from it — so it's worth getting right
before anything else, and "right" here specifically means **user-confirmed,
not self-confirmed**.

**Present 2-3 named candidates before committing to one — never pick
silently and build around it.** This is not optional even when a candidate
seems obviously correct. `references/taste-checklist.md`'s mechanical
checks catch *statistical* AI-defaults — the cream+terracotta or
near-black+acid-green combinations that show up regardless of who's
prompting. They have no way to catch a color that passes every mechanical
rule but still reads as generated, because it pattern-matches to this
model's own accumulated output specifically rather than to a named,
checklist-encoded default. That failure mode is only catchable by a human
comparing named options side by side — not by a better rule, and not by a
more careful self-review. Name each candidate (e.g. "Slate Cobalt," "Warm
Graphite," "Deep Teal"), give each a one-line character note, and get an
explicit pick before deriving the rest of the palette or building anything
around it — especially before building a flagship/hero screen, where the
cost of an unconfirmed miss compounds fastest.

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
  1. Propose 2-3 named anchor-color candidates as `oklch(L C H)`, per the
     presentation requirement above, and get an explicit pick before
     continuing.
  2. Derive the rest from the chosen anchor in OKLCH: background/surface by
     shifting `L` (holding `H`, dropping `C` toward zero for near-neutral
     surfaces), text by pushing `L` to the opposite end until the contrast
     math clears WCAG AA against its background, accent by rotating `H`
     (or picking a second anchor) while keeping `L`/`C` in a comparable
     range.
  3. **Convert every OKLCH value to hex deterministically — compute it,
     don't eyeball it, and don't reconstruct the conversion from memory as
     a substitute for actually running it.** In order:
     a. Install a real conversion library on the spot and use it — `npm
        install culori` (or a one-off `npx`-based script) or `pip install
        coloraide` — this is the default path and works in any environment
        with network/package-manager access. Prefer a conversion tool
        already present in the project if one exists.
     b. If installation genuinely isn't possible (no network, sandboxed,
        no package manager), **say so explicitly to the user and label the
        resulting hex values as unverified.** Do not hand-transcribe the
        OKLab/OKLCH conversion matrices from memory into a throwaway
        script and present the output as computed — a transcription error
        is invisible and looks exactly as plausible as a correct
        conversion. That silent-failure risk is precisely what "compute
        it, don't eyeball it" exists to prevent; reconstructing the math
        from memory reintroduces the same risk with extra steps, not less.
  4. Record both forms in the output: OKLCH as the design intent (what to
     tweak if a color needs to change), hex as the committed token value
     everything downstream — Tailwind config, CSS custom properties,
     design tools — actually consumes. Hex stays the interchange format;
     OKLCH is how you got there, not a replacement for it in shipped
     tokens.

## Work in two passes (adapted from Anthropic's frontend-design)

**Pass 1 — plan.** Before writing any CSS, produce a compact token plan:

- **Color**: 4-6 named colors forming the core palette, derived from the
  user-confirmed anchor per the OKLCH-first process above and committed as
  hex — not a default terracotta/cream or near-black/acid-green scheme
  unless the brief actually calls for that mood. Premium-consumer briefs
  (cookware, wellness, artisan, luxury) pull toward a specific banned
  default — warm beige/cream + brass/clay/oxblood/ochre + espresso text —
  hard enough that it's worth naming and deliberately avoiding; see
  `references/taste-checklist.md` for the exact hex families and rotation
  alternatives.
- **Type**: same candidate-presentation requirement as color — **propose
  2-3 named type-pairing candidates and get an explicit user pick before
  locking one in**, for the same reason: avoiding the specific named tells
  (Inter/Roboto/Arial/Space Grotesk as defaults; Fraunces/Instrument_Serif
  as display serifs) filters out the *known* AI-defaults, but the next
  font down the list of "safe alternatives" can just as easily become the
  new tell once enough tools converge on recommending it — a banned-list
  approach only ever chases the last generation of default, it doesn't
  prevent the next one. A human picking between named, distinct-looking
  candidates is what actually catches that; a longer ban list doesn't. Each
  candidate: one or two families with clear display/body roles (or a
  single family with distinct weights, if that's the direction), a
  one-line character note, and a type scale with intentional weights and
  spacing. Serif is justified only when the brief names one or the
  aesthetic is genuinely editorial/luxury/heritage.
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
Dials: variance [n], motion [n], density [n] (capped/set by: [primary
rendering surface from DESIGN.md Requirements])
Breakpoint strategy: [mobile-first / desktop-first], because [primary
rendering surface]

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
