# Phase 5 — Frontend Architecture: React

React is the default framework because it's the market-preferred choice, not
because it's assumed — confirm this against Phase 1's constraints before
applying this doc. To support a different framework, add a sibling file in
this same directory (see the template note at the bottom); nothing in
`SKILL.md` is React-specific beyond routing here by default.

Grounded in Vercel's composition-patterns skill (MIT) for architecture and
state, and vercel-react-best-practices for performance categories (installed
separately if deeper detail is needed — see `SKILL.md` prerequisites).

## File layout

Structure by feature/domain, not by file type, once the Phase 4 component
inventory is nontrivial:

```
src/
  components/          # shared atoms/molecules (Phase 4) used across features
  features/
    <feature>/
      components/       # organisms specific to this feature
      hooks/
      api.ts
  routes/ or pages/      # maps 1:1 to Phase 2's sitemap
  lib/                   # framework-agnostic utilities
  styles/ or theme.ts     # Phase 3 tokens as CSS custom properties or Tailwind config
```

A flat `components/` folder is fine only while the Phase 4 inventory is
small; once organisms start being feature-specific, colocate them with the
feature instead of growing one giant shared folder.

## Component architecture

- **Compound components** (identified in Phase 4) get their own folder with
  an `index.tsx` exporting the family and a shared context — `Tabs/`,
  `Menu/`, not a single `Tabs.tsx` with a dozen props.
- **No boolean-prop proliferation** — a component identified in Phase 4 as
  needing variants gets explicit variant props (`variant="danger"`) or
  separate composed components, not a growing set of `is*`/`show*` booleans.
- **React 19+**: use `use()` instead of `useContext()`; don't use
  `forwardRef` — refs are regular props. Skip this if the project targets
  React 18 or earlier.

## Server/client boundary (Next.js / RSC)

- Default to Server Components; global state and context providers work
  only inside Client Components, so wrap providers in a dedicated
  `"use client"` component rather than marking whole trees client-side.
- **Interactivity isolation**: any component using animation, scroll
  listeners, or pointer physics (identified in Phase 4 as needing motion)
  must be an isolated client leaf — Server Components render static layout
  only. This keeps the bulk of the tree server-rendered even on a
  motion-heavy page.
- Never track continuous, high-frequency values (mouse position, scroll
  progress, pointer physics) in `useState` — it re-renders the React tree
  on every change and degrades badly on mobile. Use a motion library's
  dedicated value primitives (e.g. Motion's `useMotionValue`/`useTransform`/
  `useScroll`) outside the render cycle instead. Reach for scroll-driven
  CSS animations or `IntersectionObserver`-based reveal before wiring a raw
  `window.addEventListener('scroll')`.

## State management

- **Decouple implementation from interface.** A provider component should be
  the *only* place that knows how state is actually managed (`useState`,
  `useReducer`, external store) — consumers see a generic interface
  (`{ state, actions, meta }`), not the implementation detail. This makes
  swapping the state mechanism later a one-file change.
- **Lift state to the nearest common parent** that needs it — a provider
  component, not prop-drilling through unrelated intermediate components or
  duplicating state across siblings.
- **Define a generic state-context interface** (`state`, `actions`, `meta`)
  for anything injected via context, so the same interface could be swapped
  for a different implementation without touching consumers.

## Data fetching

- Fetch at the route/page level where possible, not scattered across every
  organism that happens to need data — this avoids waterfalls and makes
  loading states predictable.
- Parallelize independent fetches; only sequence fetches that actually
  depend on each other's result.
- Wrap slow or independently-loading sections in Suspense boundaries scoped
  to that section, not one boundary around the whole page.

## Rendering strategy

- Defer non-critical work off the initial render path (dynamic imports for
  below-the-fold organisms, `requestIdleCallback`/`useTransition` for
  low-priority updates).
- Memoize expensive derived values, but don't wrap trivial expressions in
  `useMemo` — memoization has its own cost and should target measured, not
  assumed, hotspots.

## Testing hook points

Structure components so Phase 7's journey scenarios can actually drive them:
stable `data-testid` or accessible roles/labels on every interactive element
identified in Phase 4, and route-level components that can be rendered in
isolation for scenario-level tests.

## Output: architecture decisions

Write to `ARCHITECTURE.md` under a `## Frontend Architecture` section
(create the file if it doesn't exist — `DESIGN.md` stays a separate
document from this point on):

```markdown
## Frontend Architecture
### Framework
React [version] — [reason, if non-default]
### File layout
[the chosen structure, adapted from the template above]
### State management
[provider/context strategy actually chosen, and why]
### Data fetching
[route-level vs. component-level, parallelization notes]
### Rendering strategy
[what's deferred, memoized, or Suspense-boundaried, and why]
### Testing hook points
[how Phase 7's scenarios will drive these components]
```

Then implement the real file layout and components accordingly — this
section is the record of *why*, the source tree is the *what*.

## Adding a new framework

Create `references/05-architecture/<framework>.md` with the same six
sections as this file (file layout, component architecture, state
management, data fetching, rendering strategy, testing hook points), and
route to it from `SKILL.md` when the brief names that framework instead of
React.
