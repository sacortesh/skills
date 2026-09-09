---
name: avangarde-frontend-architect
description: Master flow for architecting a website or app's frontend from zero — requirements, information architecture, theming, component inventory, framework-specific structure (React first, extensible), a Tailwind-vs-CSS styling decision with maintainability practices, and a closing Gherkin/BDD journey report for external testing and handoff. Self-contained — no external knowledge base or MCP server required. Routes each request to the one phase(s) that apply instead of forcing a rigid pipeline. Every phase is grounded in established UI/UX methodology (About Face's goal-directed design, Atomic Design's component hierarchy, The Design of Everyday Things' affordances, Design for Hackers' visual grammar, The Image of the City's wayfinding, Hooked's habit loops), a 20-law UX checklist (Hick's, Fitts's, Jakob's, Miller's, etc.), and a tunable design-variance/motion-intensity/visual-density taste system, all gated against a mechanical anti-"AI slop" pre-flight checklist before anything is called done. Decisions are persisted to DESIGN.md/ARCHITECTURE.md/journeys/ as each phase completes, with an explicit checkpoint-and-resume protocol so a long build survives context compaction or a fresh session without losing prior decisions. Also handles the inherited-codebase case — auditing, critiquing, or modernizing a frontend this skill didn't build, via a preserve-vs-overhaul-vs-rebuild triage instead of blindly regenerating it. Also sanity-checks a frontend plan someone else already assembled — spec-kit's spec/plan/tasks output, or any Spec-Driven Development task breakdown — against this skill's own seven-phase checklist *before* anyone writes code against it, catching missing IA/theme/accessibility/acceptance-criteria coverage and bad task sequencing. Use this whenever the user wants to design or scaffold a new app/website's frontend from scratch, define its navigation/IA, pick a visual theme or design tokens, plan its component library, architect its React (or other framework) structure, decide between Tailwind and plain CSS, produce a BDD-style journey report for QA/handoff, review/modernize/take ownership of an existing frontend codebase, or sanity-check a spec-kit/SDD plan or task list before implementation starts. Also trigger for narrower asks that clearly map to one phase — "help me pick a theme," "what components do I need," "should this be Tailwind or CSS," "write Gherkin scenarios for this flow," "review my UI for AI slop," "audit this repo before I touch it," "did spec-kit plan this feature correctly," "sanity check these tasks before I start building" — without requiring the full pipeline.
---

# Avangarde Frontend Architect

A landing skill, not a monolith: this file routes intent to the one reference
doc that answers it. Each reference is self-contained — read only the ones the
request actually needs.

## Prerequisites

Self-contained by design — no external MCP server or personal knowledge
base required. Everything a phase needs to ground its decisions is already
written into that phase's reference doc.

- **WebFetch** — used by `references/taste-checklist.md` to pull Vercel's live
  Web Interface Guidelines rather than a vendored snapshot.
- Optional companion skill for deep React performance rules:
  `npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices`
  — not required; `references/05-architecture/react.md` covers the
  architecture-level decisions this skill is responsible for.
- If you maintain a personal UI/UX knowledge base or RAG, wiring a search
  call into the phase docs below (each one names the specific
  books/methodology it draws on) is a natural extension — deliberately left
  out of this shared version so the skill has no dependency on
  infrastructure only one person has access to.

## Persist decisions immediately — don't let context carry them

Every phase writes its decisions to disk as soon as they're made, into one
of three places. This isn't optional bookkeeping: a long build spans many
turns, context gets summarized, and a decision that only ever lived in
conversation is a decision that gets silently re-derived (and possibly
contradicted) two phases later.

- **`DESIGN.md`** — the product/UX decisions: phases 1-4 (requirements,
  navigation, theme, components). One file, one `##` section per phase,
  created on phase 1 and appended to by each subsequent phase — never
  recreated from scratch once it exists.
- **`ARCHITECTURE.md`** — the technical build decisions: phases 5-6
  (frontend architecture, styling approach). Same append-don't-recreate
  rule. Kept separate from `DESIGN.md` because these are engineering calls
  a different audience (a dev picking this up) reads independently of the
  design rationale.
- **`journeys/`** — phase 7's Gherkin output. Lowercase, matching the repo
  convention this skill otherwise follows.

Before starting any phase on a project that already has `DESIGN.md` or
`ARCHITECTURE.md`, read the existing file first — later phases build on
earlier ones' actual written decisions, not a fresh guess at what they
probably were.

**The first time `DESIGN.md` is created on a project**, also add a short
section to the project's own `AGENTS.md` (or `CLAUDE.md` if that's the
convention already in use there — prefer `AGENTS.md` if neither exists yet,
since it's the more tool-agnostic convention) pointing back at this skill.
Without it, someone who clones the repo later — a person or a fresh agent
session with no memory of this conversation — has no way to know these
files aren't just handwritten docs, or how to keep working with the same
workflow. Check first whether the section already exists (search for
"avangarde-frontend-architect") — this is written once, not re-appended on
every phase. Use this shape:

```markdown
## Frontend architecture: avangarde-frontend-architect

This frontend's structure and decisions are tracked by the
`avangarde-frontend-architect` skill, not only by the source code:

- `DESIGN.md` — requirements, navigation, theme, and component decisions.
- `ARCHITECTURE.md` — frontend framework and styling decisions.
- `journeys/` — Gherkin/BDD specs of the actual built user journeys.

Read `DESIGN.md` and `ARCHITECTURE.md` before making frontend changes —
they're the durable record of what was decided and why; don't re-derive a
decision that's already written down there. To keep extending the project
with the same skill (evolve the design, add a phase, audit before a
redesign), reinstall it with `npx skills add <source-repo> --skill
avangarde-frontend-architect` — check `skills-lock.json` or your skills
manifest for `<source-repo>` if it isn't already obvious from how this
skill was installed here. Don't hardcode a specific repo path if it can't
be determined; leave the placeholder and say so instead of guessing.
```

## Checkpointing and resuming across sessions

A seven-phase build will often outlast a single context window, and long
sessions degrade — accumulated back-and-forth crowds out earlier reasoning,
and a summarized conversation can quietly drop or blur an earlier decision.
`DESIGN.md`, `ARCHITECTURE.md`, and `journeys/` are the fix, not just a
paper trail: since every phase's decision is already on disk, the
conversation itself becomes disposable.

- **Resuming** — at the start of a session (fresh, or right after a
  `/compact`), check the project root for `DESIGN.md` and `ARCHITECTURE.md`
  before doing anything else. If they exist, read them fully and infer
  which phase to resume from the sections already present (e.g. `DESIGN.md`
  has `## Requirements` and `## Navigation` but no `## Theme` → resume at
  phase 3). Never restart a phase whose section already exists unless the
  user explicitly asks for a redo.
- **Checkpointing** — right after writing a phase's section, say so in one
  line: "Phase 3 written to `DESIGN.md`. Safe to `/compact` or start a new
  session before phase 4 — it reads this file, not this conversation."
  This makes compaction a deliberate, safe checkpoint instead of a risk,
  which is the actual fix for context degradation on a long build: not
  avoiding compaction, but making sure nothing load-bearing depends on the
  conversation surviving it.

## The seven phases

| # | Phase | Reference | Writes to |
|---|-------|-----------|----------|
| 1 | Capture requirements | `references/01-requirements.md` | `DESIGN.md` — `## Requirements` |
| 2 | Navigation architecture | `references/02-navigation.md` | `DESIGN.md` — `## Navigation` |
| 3 | Theme | `references/03-themes.md` | `DESIGN.md` — `## Theme` |
| 4 | Components | `references/04-components.md` | `DESIGN.md` — `## Components` |
| 5 | Frontend architecture | `references/05-architecture/react.md` | `ARCHITECTURE.md` — `## Frontend Architecture`, plus real source files |
| 6 | Styling approach | `references/06-styling.md` | `ARCHITECTURE.md` — `## Styling`, plus real source/config files |
| 7 | Journey report | `references/07-journey-report.md` | `journeys/*.feature` + `journeys/README.md` |

One more reference is an alternate entry point, not a phase:

- `references/adopting-existing-repo.md` — use this **instead of** running
  phases 1-7 fresh whenever the request is about a codebase this skill
  didn't build ("review my site," "modernize this app," "take over this
  repo"). It triages adopt-as-is / evolve-preserve / overhaul / rebuild,
  audits each phase's current state before proposing changes, and names
  what must never change without explicit approval (URLs, nav labels, form
  field names, brand logo, legal copy).
- `references/plan-audit.md` — use this **instead of** running phases 1-7
  fresh whenever the request is to sanity-check a plan someone else already
  assembled (spec-kit's spec/plan/tasks output, or any Spec-Driven
  Development task breakdown) *before* code gets written against it. Checks
  the plan's task list for phase coverage (did anyone actually decide IA,
  theme, accessibility, acceptance criteria — or just assume it) and
  sequencing (is a task scheduled before the decision it depends on),
  reporting Ready to build / Needs revision / Too incomplete to assess. This
  audits the plan artifact itself — it is not a comprehension check on a
  person, which is a different tool's job entirely.

Two more references support every phase rather than owning one:

- `references/ux-laws.md` — 20 UX/psychology laws (Hick's, Fitts's, Jakob's,
  Miller's, Von Restorff, Tesler's, Postel's, Aesthetic-Usability, Pareto,
  etc.). Check relevant laws against every decision in phases 1-4 and cite
  which law justifies which choice — this is a "show your work" requirement,
  not decoration.
- `references/taste-checklist.md` — the anti-"AI slop" gate. Run it before
  presenting output from phases 3, 4, and 6: generic palette/type/motion
  defaults, boolean-prop-driven components, and hardcoded style values all
  fail this gate and must be revised, not shipped with a caveat. It also
  carries the three tunable taste dials (DESIGN_VARIANCE, MOTION_INTENSITY,
  VISUAL_DENSITY) that phases 3, 4, and 7 calibrate against — state these
  explicitly per brief rather than defaulting silently.

## How to route a request

0. **Building on top of a codebase this skill didn't create?** Stop here and
   read `references/adopting-existing-repo.md` instead of starting phase 1
   — auditing what already exists comes before deciding what changes.
   **Sanity-checking a plan before any code exists yet** (spec-kit, SDD, or
   any pre-written task breakdown)? Read `references/plan-audit.md` instead
   — same "audit before acting" instinct, one phase earlier in the
   lifecycle.
1. **Identify which phase(s) the request maps to.** A "build me a new app"
   request runs all seven in order, each phase's output feeding the next. A
   narrower request ("what should the nav look like," "pick a theme," "is
   this React structure sane") only needs its one reference — don't force the
   rest of the pipeline on someone who didn't ask for it.
2. **Apply `references/ux-laws.md`** to whatever choice the phase is making
   — cite which law justifies which choice; this is a "show your work"
   requirement, not decoration.
3. **For phases 3, 4, and 6**, run the output against
   `references/taste-checklist.md` before presenting it. If something fails,
   fix it before showing the user, not after. Verify in one bounded pass, not
   an open-ended loop: build the phase fully, inspect once against the
   checklist, fix everything it flags in one batch, and confirm with at most
   one more round. Open-ended self-QA after that point burns turns doing
   worse what the user's own review of the presented output does better —
   the checklist's job is to catch defects before presenting, not to chase
   diminishing improvements after.
4. **Write the phase's decisions to `DESIGN.md` or `ARCHITECTURE.md`**
   (see above) before moving on, and say so in one line per the
   checkpointing note above — rather than carrying decisions only in
   conversation, where later phases would have to re-derive them from
   memory instead of reading them back.
5. **Only at phase 7**, produce the Gherkin journey report — it documents
   what was actually built, so it must come last and reflect the real nav,
   components, and flows, not the original brief's assumptions.

## Extending to a new framework

Phase 5 ships with `references/05-architecture/react.md` because React is the
market default, but the phase is not React-specific. To add another
framework, create `references/05-architecture/<framework>.md` following the
same section structure (file layout, state management, data fetching,
rendering strategy, testing hook points) and route to it when the brief
names that framework.

## Acknowledgments

Aesthetic-direction and anti-slop guidance adapted from
[Anthropic's frontend-design skill](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
(Apache-2.0) and
[Microsoft's frontend-design-review skill](https://github.com/microsoft/skills/tree/main/.github/skills/frontend-design-review).
React composition guidance adapted from
[Vercel's composition-patterns skill](https://github.com/vercel-labs/agent-skills)
(MIT). The taste-dial system, mechanical pre-flight checklist, and the
adopt/evolve/overhaul/rebuild triage in `references/adopting-existing-repo.md`
are adapted from [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)
(MIT) — a scope note there is worth repeating here: its rules target
landing pages, portfolios, and marketing sites, not dashboards or dense
product UI, which is why `references/06-styling.md` routes those toward an
official design system instead. UX laws sourced from the user's own note,
itself summarizing a @adam_ha_yes reel. The visitor-mode taxonomy (Phase 1),
the refinement-preserves/redesign-replaces framing and "evidence and
anti-reference" phrasing (`references/adopting-existing-repo.md`), and the
bounded-pass verification principle (`SKILL.md` step 3) are adapted from
the commercial `impeccable` skill — no open-source license is claimed for
these; the concepts and phrasing are paraphrased from observed usage, not
copied from its source files verbatim.
