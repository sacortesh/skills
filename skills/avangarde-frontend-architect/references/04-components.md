# Phase 4 — Identifying Components

Primary method: **Atomic Design** (Brad Frost). Cross-check interaction
patterns against Cooper et al.'s *About Face* and affordance/signifier
guidance against Norman's *The Design of Everyday Things*.

## Build the inventory bottom-up

1. **Atoms** — the smallest indivisible pieces: a button, an input, a label,
   an icon, a color swatch, a type style. These map directly to the Phase 3
   design tokens — an atom's states (default/hover/focus/disabled/error)
   should be enumerated now, not discovered mid-build.
2. **Molecules** — small groups of atoms functioning as a unit: a labeled
   input with validation message, a search field with its button, a nav
   item with its icon.
3. **Organisms** — larger, distinct sections composed of molecules and
   atoms: a header, a card grid, a form, a nav bar. Every district and node
   from Phase 2's sitemap implies at least one organism.
4. **Templates** — page-level layout skeletons showing where organisms sit,
   without real content.
5. **Pages** — templates filled with the Phase 1 content inventory's real
   content, for actual pages in the Phase 2 sitemap.

## Visual discipline while identifying organisms

These are identification-time decisions, not review-time fixes — get them
right here and `references/taste-checklist.md`'s gate becomes a formality
instead of a rewrite:

- **Cards only when elevation communicates real hierarchy.** Don't default
  every organism to a rounded card with a soft shadow; group with borders,
  dividers, or negative space when there's no actual elevation to signal.
- **No three identical feature cards in a row.** If Phase 1/2 imply three
  parallel items, identify an asymmetric grid, a 2-column zigzag (max two
  in a row), or a scroll-pinned organism instead of defaulting to the
  three-card row.
- **Bento organisms get exactly as many cells as there is content for** —
  identify the cell count from the actual content inventory, not a
  round number, and flag if fewer than ~2-3 cells will need real visual
  variation (image/gradient/pattern) rather than text-only.
- **Shape-consistency lock**: decide the corner-radius system (all-sharp,
  all-soft, all-pill, or an explicit per-element-type rule) while
  identifying atoms — don't leave it to be discovered inconsistently once
  organisms are built.

## Composition rules (adapted from Vercel's composition-patterns)

Apply these while identifying components, not after — a component identified
with the wrong shape now becomes the boolean-prop pile the taste checklist
flags later:

- **Avoid boolean-prop proliferation.** If a component's behavior varies
  along an axis (`isCompact`, `isDisabled`, `showIcon`, `variant`...),
  identify it as an explicit variant component or a composable slot instead
  of a single component gaining more booleans over time.
- **Compound components for anything with internal structure.** A component
  with clearly related sub-parts (a `Tabs` with `Tabs.List`/`Tabs.Panel`, a
  `Menu` with `Menu.Item`) should be identified as a compound family sharing
  context, not one monolithic component with a dozen props controlling
  sub-parts.
- **State ownership.** For any organism with shared state across its
  molecules (a form, a multi-step wizard), identify which component is the
  provider — state should be lifted to the nearest common parent and read
  down, not duplicated across siblings.
- **Children over render props** where composition is the goal — favor
  slotting real children into a component over a `renderX` prop.

## Output: component inventory

Write to `DESIGN.md` under a `## Components` section (append — this is the
last of the four `DESIGN.md` sections; Phase 5 starts a separate file):

```markdown
## Components
### Atoms
- Button (variants: primary, secondary, danger; states: default/hover/focus/disabled)
- Input (states: default/focus/error/disabled)
...

### Molecules
- SearchField (Input + Button)
...

### Organisms
- SiteHeader (uses: Logo atom, NavItem molecules) — appears on: all pages (landmark, Phase 2)
- [OrganismName] — implements: [district/node from Phase 2]
...

### Compound families
- Tabs → Tabs.List, Tabs.Tab, Tabs.Panel — shared context: activeTab
...

### Templates → Pages
- [Template] → [Page(s) from Phase 2 sitemap]
```

Feed this inventory directly into Phase 5 — the framework architecture
phase turns each atom/molecule/organism into an actual file, and the
compound families above dictate where context providers live.
