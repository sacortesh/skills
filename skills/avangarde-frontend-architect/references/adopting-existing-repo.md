# Adopting and Critiquing an Existing Repo

Use this instead of running phases 1-7 fresh whenever the request is about a
codebase this skill didn't build — "review my site," "modernize this app,"
"take over this repo," "why does this feel off." Misclassifying this as a
greenfield build is the single biggest source of bad output here: it either
regenerates a working IA/brand from scratch (destroying real value) or
blindly bolts new phases onto code no one has actually looked at yet.
Adapted from Leonxlnx/taste-skill's Redesign Protocol (MIT).

## 1. Detect the mode first

Ask, or infer from the request, which of these is actually true:

- **Adopt as-is** — no redesign intent; the user wants to understand,
  extend, or take ownership of what exists. Audit only, no changes.
- **Evolve — preserve** — modernize without breaking the brand or IA. Audit
  first, extract what's already there, change gradually.
- **Overhaul** — new visual language on top of existing content and
  structure. Treat phases 3/4/6 as greenfield; preserve content and IA
  (phases 1/2) as constraints, not starting points to redo.
- **Rebuild** — the brand itself is changing, or the codebase is
  unsalvageable. Run the full phases 1-7 pipeline from `SKILL.md` instead
  of this file; the existing repo is reference material, not a foundation.

If ambiguous, ask **one** question: "Should this preserve the existing
[brand / IA / both], or are we starting fresh on [that axis]?" Don't guess
and don't ask more than one question — infer everything else from the code.

## 2. Audit before touching anything

**Check for `DESIGN.md` and `ARCHITECTURE.md` first.** If this skill (or a
prior session of it) already ran here, those files are the recorded
decisions — read them instead of reverse-engineering from scratch, and
treat any drift between what they say and what the code actually does as a
finding in its own right (the code changed without the docs, or vice
versa). If neither file exists yet — a genuinely fresh adoption — writing
them from this audit is itself valuable output, and per `SKILL.md`'s
persistence rules, creating `DESIGN.md` for the first time also means
adding the `AGENTS.md`/`CLAUDE.md` pointer stanza described there.

Otherwise, reverse-engineer each phase from what's actually there — this becomes the
baseline every later phase change gets diffed against, and the answer to
"what does this need" instead of "what would I build from zero."

| Phase | What to extract from the existing repo |
|---|---|
| 1. Requirements | Infer the real audience and job-to-be-done from what's built, not what a README claims — check which flows have the most polish/investment, which are neglected. |
| 2. Navigation | The actual page tree, primary nav, and conversion paths as they exist today — not the "ideal" IA from `references/02-navigation.md`. |
| 3. Themes | Extract the real design tokens in use: primary/accent colors, type stack, radii, logo treatment — even if applied inconsistently. Read the dial values (`references/taste-checklist.md`'s DESIGN_VARIANCE/MOTION_INTENSITY/VISUAL_DENSITY) the existing site is actually running at; that's the starting point, not the phase-3 baseline. |
| 4. Components | Inventory what exists (atoms/molecules/organisms per `references/04-components.md`), and flag existing boolean-prop proliferation, duplicated state, or missing compound structure — these are pre-existing debt, not new findings to silently fix. |
| 5. Architecture | Identify the actual framework, file layout, state management, and data-fetching pattern in use — compare against `references/05-architecture/react.md` (or the relevant framework file) and note deltas, don't assume the existing choice is wrong. |
| 6. Styling | Identify whether it's Tailwind, CSS, or a mix, and how consistently tokens are applied — this decides whether Phase 6 is even in scope or whether the existing choice stands. |
| 7. Journeys | If any tests, e2e specs, or documented flows exist, treat them as the current source of truth for what "working" means before writing new Gherkin scenarios. |

Also record, explicitly:

- **Patterns to preserve** — signature interactions, a recognizable hero,
  established copy voice, anything users already navigate by muscle memory.
- **Patterns to retire** — actual AI-slop tells (`references/taste-checklist.md`),
  broken layouts, dead links, generic stock imagery, obvious performance
  traps.
- **SEO baseline**, if this is a public site — current ranking pages, meta
  titles, structured data, OG cards. SEO regression is the single biggest
  risk in a redesign that isn't tracked anywhere else in this skill.

## 3. What never changes without explicit approval

Regardless of mode, these require the user to say yes explicitly — don't
fold them into a "modernization" pass silently:

- URL structure / route slugs.
- Primary nav labels (breaks muscle memory and SEO both).
- Form field names or order (breaks analytics and browser autofill).
- Brand logo or wordmark.
- Existing legal / consent / cookie copy.
- Existing accessibility wins — don't regress focus states, alt text,
  keyboard nav, or contrast while "modernizing" something else.

## 4. Modernization levers, in priority order (for evolve/overhaul modes)

Apply in order, stop as soon as the brief is satisfied — don't reach for
lever 6 when lever 2 would have done it:

1. **Typography refresh** — biggest visual lift for the least structural
   risk.
2. **Spacing and rhythm** — section padding, vertical rhythm consistency.
3. **Color recalibration** — desaturate, unify neutrals, keep the real
   brand accent (if the brand is already purple, it stays purple — the
   taste checklist's anti-purple-default rule is about unexamined
   defaults, not about brands that have earned the color).
4. **Motion layer** — add dial-appropriate micro-interactions to existing
   components, not a wholesale motion rewrite.
5. **Hero and key-section recomposition** — restructure top-of-funnel
   using the component/pattern vocabulary in `references/03-themes.md` and
   `references/04-components.md`.
6. **Full block replacement** — only once the above are exhausted and the
   existing block is genuinely unsalvageable.

## 5. Decide the scope of change

- IA, content, and SEO are sound, but the visuals feel dated → **targeted
  evolution** (levers 1-4 above). Most of the value, least of the risk.
- Visual debt is structural (no real design system, broken mobile, broken
  IA) → **full redesign**, but hold content and IA fixed unless the audit
  in step 2 specifically flagged them as broken.
- The brand itself is changing → treat as **greenfield**; run `SKILL.md`'s
  full phase pipeline, using this audit as historical reference only.

## 6. Report back

Before writing any code, present the audit (step 2's table plus preserve/
retire lists) and the proposed scope (step 5) to the user. This is a
checkpoint, not a formality — an audit that silently becomes a rewrite is
the exact failure mode this file exists to prevent.
