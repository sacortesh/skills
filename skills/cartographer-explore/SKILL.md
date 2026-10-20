---
name: cartographer-explore
description: Generates unbloated, diagram-first "living map" documentation for a software system — a Context-level overview plus one self-contained doc per feature (state or data-flow diagram, exact rule/threshold table, cross-layer breakdown) — then walks the user through verifying it against their own knowledge (Adoption mode). Use whenever the user wants to document, map, or understand a system before a rewrite/migration/port, onboard into an unfamiliar codebase, asks for an "architecture map," "system map," or "living documentation," or wants to review, correct, or "adopt" a previously generated map. Delegates spec-vs-code drift triage to `cartographer-spec-drift` and methodology risk judgment to `cartographer-methodology-audit` rather than duplicating either. Works via a conversational questionnaire, not a required upfront spec.
---

# Cartographer: Explore

## Contents
- Why this shape, briefly
- When this is worth the cost
- Related skills
- The process (Steps 0-6)
- Output conventions
- What this skill doesn't do yet

Produces documentation shaped like a **map**, not a **manual** — something
checked daily under pressure, not read once and filed away. The distinction
matters: a spec document is written once for alignment before work starts; a
map is consulted repeatedly *while* working, and stays trustworthy only if
every claim in it can be checked against something real (usually the code
itself).

## Why this shape, briefly

Four tensions, each resolved by a specific choice this skill makes:

- **Hierarchical (C4-style zoom levels) vs. self-contained topics (EPPO)** —
  use a hierarchy only at the slow-changing top (one Context doc), then let
  each feature be its own linked, standalone page. Nobody reads a system
  doc front-to-back; they land on the one page that answers today's
  question.
- **Generate from code vs. hand-write** — where a fact lives in code,
  extract it exactly (thresholds, formulas, transition rules — copy them,
  don't paraphrase). Where a fact is a human decision or rationale, say so
  explicitly and don't invent code that doesn't exist to justify it.
- **Trust, not just coverage** — every non-trivial claim should be
  checkable. If a spec, comment, or prior doc claims something the code
  doesn't actually do, that mismatch is the single most valuable thing this
  skill can surface — more valuable than the diagram itself. That check is
  `cartographer-spec-drift`'s job (see Step 3 and Step 4 below); don't
  reimplement it inline here.
- **Seed, not cage** — if whoever invoked this skill hands over pointers or
  pre-resolved facts (files to look at, a module boundary, an entry point),
  treat that as a head start, never as the boundary of what to look at.
  Always still probe outward — glob for adjacent specs/docs/comments, follow
  an unresolved reference — whenever coverage looks incomplete. A claim like
  "no spec exists" or "no prior doc exists" is only honest if you actually
  searched for one; if you didn't look broadly enough to know, that belongs
  in **Not checked** (below), not stated as fact.

## When this is worth the cost

A real investigation pass here costs real tokens and time — doing it
properly means full discovery on top of whatever head start you were given,
not a shortcut.

- **Worth paying for**: a change touches a contract this system didn't just
  write for itself — billing, entitlements, auth, or any logic another part
  of the codebase already depends on.
- **Not worth it**: a small, uniform addition to a codebase whose existing
  conventions are already cheap to read directly (e.g. copying the pattern
  from two sibling files) — say so and recommend skipping a dedicated map
  rather than generating one just because you were asked to.

The point is catching what a task-focused read would miss on something that
matters, not documenting everything on principle.

## Related skills

- **`cartographer-spec-drift`** — owns the spec-vs-code check (Step 3) and
  the triaged `DRIFT.md` aggregation (Step 4). Invoke it rather than
  re-deriving that logic here; it also runs standalone against an existing
  map, outside a fresh `cartographer-explore` pass.
- **`cartographer-methodology-audit`** — a prescriptive audit of the
  project's actual development process (spec discipline, test/CI coverage,
  agentic-tooling usage, convention drift), reading this skill's
  `METHODOLOGY.md` (Step 1.5) as its starting input. Step 1.5 here stays
  purely descriptive — indexing what's discoverable, never judging it;
  invoke the audit skill separately when the user wants that judgment.

## The process

### Step 0 — Figure out what shape of system this is

Before anything else, work out what kind of thing you're documenting — this
determines what "layers" or "containers" even mean here. Don't assume a
web-app's Data/Domain/Interface split applies to everything.

Skim the project (package manifests, entry points, folder structure, how
it's invoked/deployed) and form a hypothesis: client app, server/backend,
worker or background-job system, embedded system, middleware, or a
CI/CD-style pipeline. State the hypothesis to the user and let them correct
it — don't silently commit to a wrong shape.

Read `references/container-shapes.md` for a suggested starting container set
per shape. These are starting points to offer, never a forced taxonomy — if
the real project's structure disagrees with the suggestion, the real
structure wins. The point of Step 0 is discovering the actual containers,
not filling in a template.

### Step 0.25 — Size check before committing to a pass

Before reading everything, get a rough sense of how much there actually is
to read, scoped to what Step 2 will settle as on-demand vs. whole-feature-set.

Cheaply filter out what's never worth reading regardless of size — lockfiles,
`node_modules`/`vendor`/`dist`, minified bundles, binary assets, anything
`.gitignore` already excludes. Then judge, relative to what's actually
available in this session (never a hardcoded token constant carried over
from a different tool or model): is this small enough to read and map in one
continuous pass, or large enough that it needs splitting into sub-passes?

If it needs splitting, split along the container/module boundaries Step 0
just found — never by an arbitrary file count or byte cutoff. A module's
natural edge should decide where a sub-pass starts and ends. State the
chosen approach (single pass, or split and how) before proceeding, the same
way Step 0's shape hypothesis gets stated rather than silently assumed.

### Step 0.5 — First run: how should this map be kept current?

Ask this only once per project — skip it entirely if `docs/cartography/
README.md` already exists and already has a `maintenance_mode` field in its
frontmatter (Step 1). When it's genuinely the first run, ask the user how
they want this map maintained going forward:

1. **Manual** — "I'll re-invoke this skill myself when something changes
   enough to warrant an update."
2. **Agent-maintained** — a dedicated subagent watches for boundary-crossing
   or breaking changes and re-invokes this skill itself, scoped to just the
   affected feature. If chosen, write (into the *target* project, never into
   this skill's own folder):
   - `.claude/agents/cartography-maintainer.md` — template below.
   - An addendum to the project's `AGENTS.md` (create it if absent, append
     if it exists) noting the maintainer agent exists and what triggers it,
     so any other agent or human working in the repo knows a map exists and
     who keeps it current.
3. **Something else, proposed by you, not hardcoded here** — look at what
   the project already has before suggesting a third option: CI config
   present → suggest a PR-CI regeneration step; git hooks already in active
   use → suggest a pre-commit/pre-push hook; neither → suggest a plain,
   low-ceremony periodic-reminder note instead of inventing infrastructure
   the project has no other instance of. Don't default to option 2 just
   because it sounds most capable — match the project's existing level of
   automation, don't exceed it uninvited.

Record the answer in the Context doc's frontmatter (`maintenance_mode:
manual | agent | <short description>`) so this is never asked twice.

**`cartography-maintainer.md` template, for option 2** (fill in the
project's actual containers/paths from Step 0 before writing):

```markdown
---
name: cartography-maintainer
description: Use proactively after any change that crosses a module/
  container boundary or alters an existing feature's documented rules —
  new or changed API routes, schema migrations, new cross-cutting
  dependencies, or a breaking change to behavior docs/cartography/
  already describes. Not for small, uniform, same-pattern additions.
tools: Read, Edit, Write, Bash, Grep, Glob
---

Re-invoke the `cartographer-explore` skill, scoped only to the feature(s)
affected by the change that triggered you — never a full project re-run.
Follow that skill's own "Seed, not cage" and "When this is worth the cost"
guidance exactly as written there; don't duplicate or diverge from it here.
```

Keep this template pointing at `cartographer-explore`'s own guidance, not a
restated copy of it — a copy can drift out of sync with the real rules.

### Step 1 — Build the Context doc (once per project)

Write `docs/cartography/README.md`, starting with a YAML frontmatter block:

```yaml
---
maintenance_mode: manual | agent | <short description>
containers: [<names from Step 0>]
methodology_doc: METHODOLOGY.md
deployment_doc: DEPLOYMENT.md
entrypoint_doc: ENTRYPOINT.md
drift_doc: DRIFT.md
---
```

followed by one Mermaid diagram showing the containers found in Step 0 and
how they call/depend on each other, a one-paragraph purpose statement for
the system, and a feature index table (feature name → doc link → status).
A feature with no code yet — one that only exists in a spec or plan — gets
a row with `status: planned` and a link to that plan, **not** a generated
feature file; see Step 2's note on this. This is the slow-changing top
layer — per C4's own guidance, it shouldn't need to change often, so it's
fine to hand-maintain.

Link the Methodology, Deployment, and Entrypoint docs (Steps 1.5 and 1.75)
from the body here too, not only in frontmatter — frontmatter is for other
tools to parse, the prose is for the human reading this file to actually
click through. `DRIFT.md` (generated by `cartographer-spec-drift`) doesn't
need a link here since it's regenerated per-run; mention it in that skill's
own report instead.

If `docs/cartography/README.md` already exists from a previous run, read it
first and update it rather than starting over — containers rarely change,
features do.

### Step 1.5 — Index the methodology (once per project)

Write `docs/cartography/METHODOLOGY.md`: an index, not a narrative, and
deliberately descriptive only — this step reports what's discoverable, it
never judges whether it's enough. List what's actually discoverable about
how this project has been built and worked on:

- Skills/agents/tools with real evidence of use (`.claude/`, `AGENTS.md`,
  `CLAUDE.md`, planning-doc naming patterns like phase- or prompt-build-style
  files), and what development methodology the project's own artifacts imply
  (spec-driven, phase-based, ad-hoc, agentic-loop-driven) — as links to the
  real files found, with one line of context each.
- **Git/collaboration conventions** — skim `git log` for a real commit
  message pattern (Conventional Commits, ticket-prefixed, freeform) rather
  than assuming one; note branch-naming conventions and any PR template or
  CI check that enforces one. Report the pattern actually observed in
  history, not a style guide that happens to exist unused.
- **Agentic capabilities inventory**, scoped to *this* project, not a full
  machine dump:
  - Repo-local tooling actually checked in — `.claude/agents/`,
    `.claude/skills/` (if present), MCP server configs committed to the repo.
  - Machine-wide tooling relevant to someone working on this project —
    skills, MCP servers, or RAG/knowledge-base indexes worth knowing about,
    named specifically (never "there are skills installed"), and only
    included when there's a concrete reason they're relevant here (matches
    this project's stack, domain, or an already-discovered pain point).

Same trust rule as everywhere else in this skill: if you didn't find it, it
doesn't go in. If nothing is discoverable for a given bullet, say that
plainly and keep the file short rather than padding it. If the user wants
this turned into a judgment — is the process actually good enough for this
project — that's `cartographer-methodology-audit`, not this step.

### Step 1.75 — Always-present docs (once per project)

Some facts aren't feature-shaped — they carry no state and no business
rule, so Step 2's "paintable" filter would reject them — but every real
system has them structurally, so write them unconditionally rather than
waiting for them to earn a slot. Same trust rule as everywhere else: only
write what's discoverable; if a project genuinely has nothing beyond the
obvious for one of these, say so in one line rather than padding it out.

- `docs/cartography/DEPLOYMENT.md` — env vars (what's required, where
  declared — `.env.example`, config schemas, secrets-manager references),
  the build/package process, and how the thing actually gets deployed or
  run in each environment that's discoverable (dev, CI, prod). Copy exact
  variable names and defaults from the real config files; don't paraphrase
  them.
- `docs/cartography/ENTRYPOINT.md` — the first thing a user or dev actually
  sees or runs: for a client app, the landing route; for a backend, the
  health/docs endpoint; for a CLI, the help output or first command.
  Include a **Quickstart** — the actual commands/scripts/ports to run it
  locally, pulled from the project's own package manifest, scripts folder,
  or README, never invented. If the project already documents this clearly
  and correctly, link to that doc instead of duplicating it; only write
  original content for what's missing or wrong.

Git/branching conventions belong in Step 1.5's Methodology doc, not here —
they're about how the project is worked on, not what a newcomer runs first.

### Step 2 — Enumerate candidate features, then filter by "paintable"

**First, settle scope — on-demand or whole-feature-set.** These are
different triggers and shouldn't default silently into one or the other:

- **On-demand, single feature** — triggered by a real question ("I need to
  touch X, how does it actually work") or a change about to cross a
  contract boundary. The default for incremental work, and the cheaper of
  the two.
- **Whole-feature-set** — triggered by onboarding into an unfamiliar
  codebase, a pre-rewrite/port audit, or an explicit request for full
  coverage. Still legitimate, and still what "When this is worth the cost"
  allows for — that section is about skipping ceremony for *small, uniform
  changes*, not about banning full-project mapping when that's genuinely
  the job.

If it isn't obvious from context which one applies, ask rather than assume.

Pull candidate features from whatever's available: existing specs/PRDs/user
stories, code module boundaries, or direct conversation with the user if
they're still vibing something without written specs yet. Don't force the
user to have a formal list ready — asking "what are the 5-10 things this
system actually *does*?" is a fine way to start the questionnaire.

**Specs/PRDs/plans are an input here, never a merged document type.** A
feature that exists only in a plan, with no code yet, does not get a
cartography doc — there's nothing to extract, and writing one anyway means
inventing content shaped like real documentation. List it in the Context
doc's feature index with `status: planned` and a link to the plan instead;
generate its actual doc once code exists to read.

Not every feature earns its own map. A feature is **paintable** — worth a
dedicated doc — if it has any of:

- **State** that changes over time, with rules governing the transitions
  (the strongest signal — this maps directly to a state diagram)
- **Non-trivial rules** — a formula, threshold, or precedence order that
  isn't obvious from the feature's name alone
- **Cross-layer footprint** — touches more than one container, so no single
  glance shows the whole picture
- **Non-obvious failure modes** — race conditions, retries, ordering
  dependencies, things that could silently break

If none of these apply — pure styling, static config, a CRUD passthrough
with no rule beyond "save this record" — don't paint it. Say so, and suggest
a one-line bullet in the Context doc instead of forcing a diagram. Building
a map for something with no state and no rules is exactly the bloat this
skill exists to avoid; resist the urge to make every feature feel
document-worthy just because you're already in documentation mode.

### Step 3 — For each paintable feature, write its own doc

One file per feature at `docs/cartography/<feature-slug>.md`. Read the
actual implementation before writing anything — every number and threshold
in the doc must be copied from real code, not inferred from a spec's prose
or the feature's name. Start with frontmatter:

```yaml
---
feature_id: <slug>
surface: api | page | cli | event | internal
status: structurally_current | semantically_reviewed | behaviorally_verified | blocked
last_verified_revision: <git sha or date>
---
```

Then the body:

1. **Purpose** — one or two sentences, what this feature is for and who/what
   it serves.
2. **State machine or data-flow diagram** — pick whichever actually matches
   the feature's nature, don't force both. If the feature has real state
   that persists and transitions over time, a Mermaid `stateDiagram-v2` of
   the actual states and transitions. If instead its defining characteristic
   is a flow across layers with no meaningful at-rest state (a request path,
   an auth check, a pipeline stage sequence), a Mermaid `sequenceDiagram`
   showing the actual participants and call order is usually the truer
   picture. Skip this section entirely only if the feature has neither.
3. **Rules table** — every threshold, formula, and precondition, copied
   exactly from source. Flag anything that reads as an odd or arbitrary
   number in the code (e.g. two different files independently encoding "1
   tick = 15 minutes") — these are exactly the values most likely to drift
   silently during a rewrite.
4. **Layer breakdown** — for each container from Step 0 that this feature
   actually touches, describe what the feature looks like there (its data
   shape, its logic, its interface surface, its API contract — whichever
   containers are real for this project). Skip containers the feature
   doesn't touch; never write a placeholder section for a layer that
   doesn't exist. A client-only app has no backend section, full stop —
   don't invent one to look thorough.
5. **Spec vs. code** — leave this section as a placeholder for now:
   `cartographer-spec-drift` fills it in during Step 4's single aggregated
   pass across every feature touched this run, not once per feature here —
   see Step 4 for why. If that skill isn't available in the current
   environment, perform the same check described there directly, right
   now, rather than leaving the placeholder unresolved.
6. **Migration/porting notes** (only relevant if the user mentioned a
   rewrite/port/migration as their reason for wanting this documentation) —
   ambiguities worth resolving deliberately rather than porting silently
   (e.g. "this state never transitions back — is that intentional or an
   oversight?").
7. **Not checked** — a short, explicit list of what you chose not to verify
   further (a reference you confirmed was irrelevant but didn't trace
   fully, a risk you noticed but didn't chase, a directory you didn't
   search). This section is required, even if short. A structured
   disclosure here is what makes every other section's claims trustworthy —
   it turns "I didn't find X" into an honest, checkable statement instead of
   a silent gap or an unfalsifiable negative.

### Step 4 — Close the loop

Tell the user which features got docs, which were judged not paintable (and
why). Then invoke `cartographer-spec-drift` exactly once, scoped to every
feature touched this run together:

- This is the single point where that check actually runs, not once per
  feature — a single aggregated invocation is cheaper, and it's what fills
  in each feature doc's placeholder "Spec vs. code" section from Step 3.
- It writes `docs/cartography/DRIFT.md`: a persisted, triaged aggregation
  of every finding surfaced while writing docs — not just the "Spec vs.
  code" disagreements, but any code-level finding worth a human decision
  (dead code, a missing implementation behind an advertised feature,
  inconsistent fail-open/fail-closed behavior, a tier gate enforced in
  only one layer, and so on).
- This is what makes that check durable: "that mismatch is the single most
  valuable thing this skill can surface" shouldn't evaporate when the chat
  scrolls past it.
- See `cartographer-spec-drift`'s own file for the entry format and triage
  categories — don't restate them here.

Surface the same findings as a distinct, scannable list in your report to
the user too — that's often the most actionable part of the whole run — but
the chat message is now a pointer to the persisted file, not the only place
it lives. Then move into Step 5 — a freshly generated map hasn't been
checked against the one source of truth no cartography skill can read: what
the human actually knows about the system.

### Step 5 — Adoption: verify the map against the human's own knowledge

Step 3's "Spec vs. code" check catches disagreement between a *written*
claim and the code. It can't catch the third kind of drift: something the
human knows — intent, tribal knowledge, a decision that was never written
down anywhere — that neither the code nor any spec reflects. Only the human
can catch that, and only if you make it easy to localize, not just "does
this look right?"

**Walk them through in a specific order, not all at once:**

1. **The Context doc first.** If the discovered shape or container set is
   wrong, every feature doc inherits that error. Ask plainly: "Does this
   match how you think about the system? Are these the right containers?"
   Don't proceed to individual features until this is confirmed — a
   container-set correction here can invalidate work already reviewed
   downstream.
2. **The always-present docs next** (`DEPLOYMENT.md`, `ENTRYPOINT.md`,
   `METHODOLOGY.md`, if Step 1.75/1.5 wrote them) — these are quick to
   confirm and, like the Context doc, other things can hang off them (an
   onboarding dev reads `ENTRYPOINT.md` first; wrong env var docs send
   someone debugging in the wrong place).
3. **Then each feature doc**, in the order the Context doc's feature index
   lists them — foundational features (ones others depend on or reference)
   before the features that build on them.
4. **`DRIFT.md`'s findings last**, as their own pass. These are claims about
   claims; they're easier to evaluate with a clear head after the
   structural review is already settled.

**When the user flags a problem, don't ask "what's wrong?"**

An unscoped "what's wrong?" makes the human reconstruct the doc's entire
scope from memory before they can even name the problem. Instead, reflect
the doc's own declared scope back at them and build a targeted question out
of it — pull its **Purpose** line, the **layers/containers** it claims to
cover, and anything it **links to** — then ask something shaped like:

> "This document maps [purpose] across [layers]. [Related functionality]
> lives in [linked doc]. Given that scope: is what's missing a state or
> transition, a threshold value, a layer that's missing or shouldn't be
> here, or an interaction with [linked feature] that isn't captured?"

This does two things at once: it gets a localized, actionable correction
instead of a vague complaint, and it surfaces — for free — the most valuable
kind of correction there is: the human realizing the doc's *scope itself*
was wrong ("actually this touches layer Z too, and that's not even in the
container list"). That's a Step 0/Step 1 problem wearing a Step 3 costume —
treat it as one. Fix the Context doc first, then recheck any feature docs
that inherited the old container set, rather than patching the symptom in
the one file where it happened to surface.

**Applying a correction:** make a small, targeted edit to the specific
section that was wrong — don't regenerate the whole file from scratch unless
the doc's actual scope changed. Regenerating everything on every correction
makes the human warier of flagging small things, which defeats the point of
this step.

### Step 6 — Optional: choose a render target

Everything so far is plain Markdown + YAML frontmatter + Mermaid — it
already works as-is in any text editor, GitHub, or VS Code with a Mermaid
extension. Only go further if the user actually wants the map rendered as
a browsable site, and ask rather than assume which of these they mean:

- **Docsify** — generate `docs/cartography/index.html` and
  `docs/cartography/_sidebar.md` (Docsify's real sidebar convention —
  `_index.md` from **Output conventions** stays as the plain-folder skim
  file, it is not what Docsify itself reads). Known gotcha, found the hard
  way: the `docsify-mermaid` plugin is unmaintained and breaks against
  modern Mermaid, because it targets the `.init()` API that Mermaid removed
  in v10+. Don't use it. Instead wire Mermaid directly: load
  `mermaid.min.js`, call `mermaid.initialize({ startOnLoad: false })` once,
  override `$docsify.markdown.renderer.code` so a ` ```mermaid ` fence
  renders as `<div class="mermaid">...</div>`, and call
  `mermaid.run({ querySelector: '.mermaid' })` inside a `$docsify.plugins`
  `doneEach` hook. Serve with `npx docsify-cli serve docs/cartography`.
- **Obsidian vault** — no extra scaffolding needed. The frontmatter and
  wiki-style markdown links this skill already produces (see **Output
  conventions**) are exactly what Obsidian's Properties pane and graph view
  expect — just point the user at the folder as a vault, or as a folder
  inside one they already have.
- **Plain folder** — the default; no action needed, `_index.md` is already
  the nav aid.

Skip this step silently if the user never asks to view the map rendered —
don't offer it unprompted on every run, and don't let it block Steps 0-5.

## Output conventions

- Everything lives under `docs/cartography/` in the target project.
- All diagrams are Mermaid, inline in the Markdown — plain text, works in
  any Mermaid-aware renderer (Obsidian, GitHub, VS Code with the right
  extension), diffable in git, and directly editable by an agent later
  without re-generating from scratch. This is a deliberate trade of visual
  polish for portability and diffability — Mermaid's layout engine is what
  it is, and that's not a bug to fix here. If a user wants hand-tuned SVG
  diagram aesthetics, that's a different, heavier pipeline than this skill
  runs; say so rather than quietly swapping renderers mid-map.
- Each feature file is self-contained (Every-Page-Is-Page-One style): a
  reader should be able to open just that one file and get their answer,
  without needing to have read the Context doc first. Link back to it, don't
  require it.
- Every file's YAML frontmatter (Steps 1 and 3) is deliberately the only
  structured-metadata mechanism used — it's what Obsidian's Properties
  pane, Dendron, and MkDocs all read natively, so the output degrades
  gracefully into a wiki under any of them without this skill committing to
  one. Don't add a second, competing metadata format.
- Also write `docs/cartography/_index.md`: a flat, one-line-each list of
  everything generated so far (including `DEPLOYMENT.md`, `ENTRYPOINT.md`,
  and `DRIFT.md`). It doubles as a plain-folder skim aid and as the data
  source if Step 6 generates a renderer-specific sidebar file. Regenerate
  it whenever a feature doc is added or removed — it's cheap and has no
  other state to drift.
- Any reference from one file in `docs/cartography/` to another — Context
  doc ↔ feature doc, feature doc ↔ feature doc, planned-feature entries,
  methodology links — is a real markdown link (`[text](relative/path.md)`),
  never a bare filename or prose mention. This isn't cosmetic: it's what
  makes the EPPO cross-references (and any wiki rendering from Step 6)
  actually navigable, not just readable.

## What this skill doesn't do yet

This version works from conversation + reading the actual code — it does
not yet auto-parse a formal specification document end-to-end into a full
feature set unattended. If the user hands over a spec doc, read it as one
input among several (alongside the code and the conversation), not as a
document to mechanically transform. A future version may add a dedicated
spec-document parsing mode; don't claim that capability exists today.

Screenshot support for `surface: page` features — capturing a real app
screenshot via the `run` skill plus browser automation, embedded in the
relevant feature doc — was considered and deliberately deferred. It needs a
real design pass before it's worth building: where screenshots live on
disk, a staleness/invalidation policy (a screenshot is a snapshot, and
nothing today tracks whether the UI has drifted from it), and which pages
actually warrant one versus which would just be clutter. Don't improvise
this inside a single run; if a user wants it, treat it as its own small
design question first, not a quick addition to Step 3.
