# Anti-"AI Slop" Taste Checklist

Run this before presenting output from phases 3 (themes), 4 (components), or
6 (styling). A failure here means revise before showing the user, not ship
with a disclaimer. Most of this file's mechanical rules are adapted from
[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT) —
its scope is landing pages, portfolios, and marketing sites specifically;
if the surface under review is a dashboard, data table, wizard, or other
dense product UI, that skill's own scope note applies here too: reach for
an official design system (see `references/06-styling.md`'s design-system
map) instead of forcing landing-page taste rules onto it.

## Known limitation: this catches statistical defaults, not model drift

Every rule below targets *statistical* AI-defaults — combinations
(cream+terracotta, near-black+acid-green, three identical cards) that show
up regardless of who's prompting, because they're the most common path
through training data. It has no way to catch a choice that passes every
rule here but still reads as generated, because it pattern-matches to this
specific model's own accumulated output rather than to a named default.
That failure mode showed up in practice on a copper accent color that
cleared every mechanical check here and still read as "obviously AI" to
someone with enough exposure to this model's output. No checklist fixes
this — the process fix is `references/03-themes.md`'s requirement to
present 2-3 named candidates and get a human pick before committing to one,
especially before building anything expensive around it. Treat this file as
necessary, not sufficient.

## Fetch the live standard first

Before reviewing, fetch the current rules with WebFetch:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Apply every rule in that document to the files under review, in addition to
the checks below. It's kept current upstream — don't rely on a stale
summary.

## Set the three dials before judging anything

Taste isn't binary — it's calibrated. Before reviewing (or generating)
phases 3/4/6 output, state where this brief sits on three axes, each 1-10:

- **DESIGN_VARIANCE** — 1 = perfect symmetry, 10 = artsy chaos.
- **MOTION_INTENSITY** — 1 = static, 10 = cinematic/physics-driven.
- **VISUAL_DENSITY** — 1 = art-gallery airy, 10 = cockpit/data-packed.

| Brief signal | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| Minimalist / calm / editorial / Linear-style | 5-6 | 3-4 | 2-3 |
| Premium consumer / Apple-y / luxury / brand | 7-8 | 5-7 | 3-4 |
| Playful / Awwwards / experimental / agency | 9-10 | 8-10 | 3-4 |
| Landing page / portfolio (default, unspecified) | 7-9 | 6-8 | 3-5 |
| Trust-first / public-sector / accessibility-critical | 3-4 | 2-3 | 4-5 |

State the dial values explicitly and justify them from the brief — "using
baseline 8/6/4 without checking the brief" is itself a Pre-Flight failure.
A page that claims `MOTION_INTENSITY > 4` but ships no actual animation is
broken; so is a page that claims `3` but has motion on every card.

## Generic-default tells (reject unless the brief explicitly asks for them)

**Palette & type**
- Warm cream background (near `#F4F1EA`) + serif display + terracotta
  accent (near `#D97757`) — the single most recognizable AI-default look.
- Near-black background with one bright acid-green or vermilion accent.
- **Premium-consumer palette ban**: for cookware/wellness/artisan/luxury/DTC
  briefs, the LLM default is warm beige/cream + brass/clay/oxblood/ochre +
  espresso near-black text (concretely: backgrounds like `#f5f1ea`/`#faf7f1`,
  accents like `#b08947`/`#9a2436`, text like `#1a1714`). Banned as a
  default; rotate instead among cold-luxury (silver/chrome/smoke), forest
  (deep green + bone + amber), black-and-tan, cobalt+cream, terracotta+slate,
  or monochrome+single-pop. Don't reuse the same substitute twice in a row
  either — that just becomes a new default.
- Inter / Roboto / Arial / Space Grotesk reached for by default, not by
  brief-driven choice.
- Serif reached for because "it feels premium/editorial" — that instinct is
  itself the tell. Serif is justified only when the brief names one, or the
  aesthetic is genuinely editorial/luxury/publication/heritage and you can
  say why this specific serif fits this specific brand. `Fraunces` and
  `Instrument_Serif` are banned as defaults outright (the two LLM-favorite
  display serifs); rotate serif choices project to project.
- Mixed-family emphasis (a random serif word injected into a sans headline)
  — emphasize with italic/bold of the *same* family instead.

**Layout & structure**
- The "SaaS-card kit": identical rounded cards, one border-radius on
  everything, the same soft grey shadow (`rgba(0,0,0,.1)`), gradient washes
  as pure decoration. Use cards only when elevation communicates real
  hierarchy — otherwise group with borders/dividers/negative space.
- Three identical feature cards in a row — the generic default. Use
  asymmetric grids, 2-column zigzag (max 2 in a row — a 3rd consecutive
  image+text-split section is a failure), scroll-pinned, or horizontal
  scroll instead.
- Bento grid with an empty or filler cell — a bento grid has exactly as
  many cells as there is content for.
- Broadsheet layout (hairline rules, zero border-radius, dense newspaper
  columns) applied regardless of subject.
- Template chrome: ALL-CAPS eyebrow above every heading (cap: at most one
  eyebrow per three sections — count `uppercase tracking`-style labels and
  check against `ceil(sectionCount / 3)`); meta strings joined with middle
  dots (`A · B · C`, max one dot per line); numbered markers (01/02/03) on
  content that isn't actually sequential; a monospace face for small data
  labels; a `→` appended to every link/button; near-black tints (`#0B0B0B`)
  standing in for real black.
- Split-header pattern (giant headline left, small explainer paragraph
  floating right) as a default section header — stack vertically instead
  unless the right column carries a real visual element.
- Section-layout repetition — once a layout family (3-col cards, full-width
  quote, split-text-image) is used, it shouldn't repeat; an 8-section page
  should use at least 4 different layout families.

**Motion**
- Fade-and-slide-up entrance on every section, hover transitions on every
  card — scattered micro-motion instead of one deliberate, orchestrated
  moment.
- Motion with no stated reason. Before adding any animation, name what it
  communicates (hierarchy, storytelling, feedback, or state transition) in
  one sentence — "it looked cool" is not a reason, and unmotivated GSAP is
  as much a tell as no motion at all.
- More than one horizontal marquee on the same page.

**Copy**
- A single em-dash (`—`) or en-dash-as-separator (`–`) anywhere visible —
  headline, eyebrow, pill, body, quote, attribution, caption, button, alt
  text. This is the single most-violated tell; treat it as zero-tolerance,
  not "used sparingly." Use a period, comma, or regular hyphen instead.
  (Regular hyphens for compound words/ranges/minus signs remain fine.)
- Filler verbs: "Elevate," "Seamless," "Unleash," "Next-Gen," "Revolutionize."
- Generic placeholder names ("John Doe," "Acme," "Nexus," "SmartFlow") where
  a believable, specific name would cost nothing extra.
- Fake-precise numbers (`99.99%`, exactly round percentages, suspiciously
  clean stats) not sourced from the brief's real data or explicitly labeled
  as mock.
- Decorative micro-copy tells: version labels in a hero (`v0.6`, `BETA`)
  outside an actual launch context, section-number eyebrows (`00 / INDEX`),
  scroll cues (`↓ scroll`), locale/weather strips unless the brief is
  genuinely place-focused, "Quietly trusted by"-style faux-humble headers.

All of the above are legitimate *when the brief actually calls for them* —
the failure is using them as an unexamined default. If the brief pins down
a direction, follow it exactly, including when it asks for one of these
looks.

## Consistency locks (mandatory, whatever the aesthetic direction is)

- **Color consistency lock**: one accent color, used identically across
  every section — no accent drift by section 7.
- **Shape consistency lock**: one corner-radius system for the whole page
  (all-sharp, all-soft, or all-pill), or a documented rule for when it
  varies by element type (e.g. "buttons are pill, cards are 16px") applied
  everywhere.
- **Page theme lock**: one theme (light, dark, or auto) for the whole page;
  no section flips to the inverted mode mid-scroll unless it's a deliberate,
  once-per-page "theme switch on scroll" device named in the brief.

## Quality-pillar gate (adapted from Microsoft's frontend-design-review)

1. **Frictionless insight-to-action** — primary task completable in ≤3
   interactions; exactly one obvious primary action, not several competing
   ones. No two CTAs sharing the same intent ("Get in touch" + "Let's talk"
   both present = fail — pick one label per intent, use it everywhere).
2. **Quality craft** — design tokens used consistently, not hardcoded
   one-off values; accessibility at minimum WCAG 2.1 A, target AA (visible
   focus states, reduced-motion respected, contrast, responsive to mobile).
   Button and form contrast explicitly checked (no white-on-white CTAs,
   4.5:1 minimum).
3. **Trustworthy building** — errors are specific and actionable in the
   interface's voice; AI-generated content disclosed where relevant.

## Component-level gate (adapted from Vercel's composition-patterns)

- No component grew a pile of boolean props to switch behavior — split into
  explicit variants or compose instead (`references/04-components.md`).
- State lives in the provider/parent that owns it, not duplicated across
  siblings.

## Mechanical pre-flight (run every box; a single failed box means not done)

- [ ] Dial values (variance/motion/density) stated and justified from the
      brief, not silently defaulted.
- [ ] Zero em-dashes anywhere visible on the page.
- [ ] Color, shape, and theme locks all hold across every section.
- [ ] Every CTA passes contrast (4.5:1) and fits on one line at desktop.
- [ ] No duplicate-intent CTAs anywhere on the page.
- [ ] Eyebrow count ≤ `ceil(sectionCount / 3)`.
- [ ] No 3+ consecutive sections share a layout family; ≥4 families across
      an 8-section page.
- [ ] Bento grids have exactly as many cells as content items, no filler.
- [ ] Hero fits the viewport: headline ≤2 lines, subtext ≤20 words/≤4
      lines, primary CTA visible without scrolling.
- [ ] Navigation renders on one line at desktop, ≤80px tall.
- [ ] Real images used (generated, or a real source) — no div-based fake
      screenshots, no hand-rolled decorative SVGs standing in for content.
- [ ] Every visible string re-read for grammatical breaks or AI-hallucinated
      phrasing (the copy self-audit).
- [ ] Every animation justifiable in one sentence; if `MOTION_INTENSITY > 4`
      is claimed, the page actually animates — if not, the claimed value is
      wrong, not the page.
- [ ] Loading, empty, and error states exist for anything with async state,
      not just the success path.
- [ ] `prefers-reduced-motion` respected wherever motion intensity > 3.

## Self-critique pass

Before presenting: spend boldness in one place, keep everything else quiet.
Cut any decoration that doesn't serve the brief. If a screenshot is
available, take one and look at it before calling the phase done — a
picture surfaces spacing and contrast problems text review misses.
