# skills

Personal collection of [Claude Skills](https://github.com/vercel-labs/skills), installable via:

```bash
npx skills add sacortesh/skills
```

## Layout

Flat layout — one folder per skill under `skills/`, each with its own bundled scripts/
references/templates as needed:

```
skills/
  learning-aspire/
    SKILL.md
  book-shopping/
    SKILL.md
    scripts/book-links.sh
    evals/evals.json
  cv-builder-interview/
    SKILL.md
  portfolio-review/
    SKILL.md
    scripts/
    references/
    templates/
```

## Available skills

| Skill | What it does |
|---|---|
| [`learning-aspire`](skills/learning-aspire/SKILL.md) | Runs the ASPIRE (Audit, Source, Probe, Ingest, Retrieve, Endure) self-learning protocol for any topic or skill — a stateful, multi-session learning loop tracked on the filesystem under `~/aspire/`. |
| [`book-shopping`](skills/book-shopping/SKILL.md) | Turns book titles into ready-to-click links — buy (Amazon, MercadoLibre CO, BuscaLibre CO), search (Google Books, Open Library, WorldCat), and provision (Anna's Archive EPUB link for RAG indexing). Handles single books or a whole shopping list as a compact table. |
| [`cv-builder-interview`](skills/cv-builder-interview/SKILL.md) | Builds résumé/CV bullet points through a structured interview (problem → what you did → quantified result → tools), instead of guessing or inventing content. Includes reference material: formatting rules, action verb bank, and a demonstrable/relevant/finished filter for which personal projects are worth including. |
| [`portfolio-review`](skills/portfolio-review/SKILL.md) | Audits a folder of side projects (or a GitHub account's repos) and maintains a running `PROJECT_STATE.md` per project plus a sorted `PORTFOLIO.md` rollup — verdict (money/fame/private/expand/merge/delete/neither), staleness, planning docs, deploy signals, and one concrete next step per project. |
| [`avangarde-frontend-architect`](skills/avangarde-frontend-architect/SKILL.md) | Self-contained master flow for architecting a website/app frontend from zero — requirements, navigation IA, theme tokens, atomic-design component inventory, React (extensible) architecture, a Tailwind-vs-CSS decision, and a closing Gherkin/BDD journey report — or auditing/modernizing an inherited codebase, or sanity-checking a spec-kit/SDD plan's phase coverage and task sequencing before any code exists. Persists decisions to `DESIGN.md`/`ARCHITECTURE.md`/`journeys/` with a checkpoint-and-resume protocol so a long build survives context compaction. Grounded in a 20-law UX checklist, a Persuade/Operate/Read/Experience visitor-mode taxonomy, and a tunable variance/motion/density taste system, gated by a mechanical anti-"AI slop" pre-flight checklist. |
| [`code-ownership`](skills/code-ownership/SKILL.md) | Transfers real understanding of LLM-generated code to the human who'll own it — a Socratic question-and-answer session instead of a passive summary. Withholds rationale in its initial summary, waits for the human to actively study the change, then escalates through recall/rationale/mechanism/edge-case/consequence/maintenance questions, scaffolding when stuck and never revealing an answer outright. Logs each session's verdict (Owned/Partial/Not yet) to `.claude/code-ownership/`. Framework/language/agent agnostic. |
| [`wishing-wand`](skills/wishing-wand/SKILL.md) | Turns a vague, aspirational "wish" into a concrete plan, a redirect toward the real underlying need, or a handout brief for whichever tool/professional/skill can actually execute it — modeled on Da Rules from Fairly OddParents (a wish for something impossible or harmful reveals a real need underneath). Reads every wish along four axes (resource gap, true desire, actionability, delegation), stays terse and genie-like (1-2 forced-choice questions at most, then acts), and grounds its domain advice (finance, psychology, learning, relationships, career, health, meaning, experience) in real books and real research on what people actually wish for rather than generic advice. Saves any granted artifact to `~/Documents/Wishing Wand/`. |
| [`research-audit`](skills/research-audit/SKILL.md) | Audits the research quality behind a written piece — checks citation presence, runs a CRAP test (Current/Relevance/Authority/Accuracy/Purpose) on sources, flags thesis-level claims resting on a single source, catches claim-evidence mismatches (source is real but doesn't say what the piece claims), and checks for one-sidedness/confirmation bias. Prefers a RAG/knowledge-base or Perplexity tool for live verification when available; degrades to structural-only analysis (clearly labeled) otherwise. |
| [`cartographer-explore`](skills/cartographer-explore/SKILL.md) | Generates unbloated, diagram-first "living map" documentation for a software system — a Context-level overview plus one self-contained doc per feature (state or data-flow diagram, exact rule/threshold table, cross-layer breakdown) — then walks the user through verifying the map against their own knowledge of the system (Adoption mode). Delegates spec-vs-code drift to `cartographer-spec-drift` and methodology judgment to `cartographer-methodology-audit` rather than duplicating either. |
| [`cartographer-methodology-audit`](skills/cartographer-methodology-audit/SKILL.md) | Audits a project's actual development methodology and flags gaps/risks — spec discipline vs. actual complexity, CI coverage vs. risk surface, unused or undocumented agentic tooling, inconsistent commit/branch conventions — reading `cartographer-explore`'s descriptive `METHODOLOGY.md` as input where it exists. Prescriptive, not descriptive; flags only, doesn't fix. |
| [`cartographer-spec-drift`](skills/cartographer-spec-drift/SKILL.md) | Finds and triages disagreements between a written claim (spec, PRD, comment, prior doc, an earlier AI agent's "done" note) and what the code actually does, persisting a triaged `DRIFT.md` (category, severity, delegation strategy). Runs standalone or gets invoked by `cartographer-explore` per feature during a mapping run. |
| [`code-review-cheap`](skills/code-review-cheap/SKILL.md) | Cheap, targeted code review: deterministic evidence first (diff parsing, existing lint/test/typecheck, heuristic risk scoring, bounded "smart context"), then exactly one Sonnet/medium-effort AI review pass validated against a strict schema. Pulls PR intent via a pluggable VCS connector (GitHub implemented; Bitbucket/GitLab documented) or runs local-only. Never approves, merges, or auto-posts comments. |

All bundled scripts reference their own skill directory (`<skill_dir>/...`), not a
hardcoded absolute path — they work wherever the skill actually gets installed.

## Adding a new skill

Create `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`) followed by the
skill's instructions. See the existing skill for the expected format.
