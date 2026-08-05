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
  aspire-learning/
    SKILL.md
  book-shopping/
    SKILL.md
    scripts/book-links.sh
    evals/evals.json
  cv-builder-interview/
    SKILL.md
  project-portfolio-review/
    SKILL.md
    scripts/
    references/
    templates/
```

## Available skills

| Skill | What it does |
|---|---|
| [`aspire-learning`](skills/aspire-learning/SKILL.md) | Runs the ASPIRE (Audit, Source, Probe, Ingest, Retrieve, Endure) self-learning protocol for any topic or skill — a stateful, multi-session learning loop tracked on the filesystem under `~/aspire/`. |
| [`book-shopping`](skills/book-shopping/SKILL.md) | Turns book titles into ready-to-click links — buy (Amazon, MercadoLibre CO, BuscaLibre CO), search (Google Books, Open Library, WorldCat), and provision (Anna's Archive EPUB link for RAG indexing). Handles single books or a whole shopping list as a compact table. |
| [`cv-builder-interview`](skills/cv-builder-interview/SKILL.md) | Builds résumé/CV bullet points through a structured interview (problem → what you did → quantified result → tools), instead of guessing or inventing content. Includes reference material: formatting rules, action verb bank, and a demonstrable/relevant/finished filter for which personal projects are worth including. |
| [`project-portfolio-review`](skills/project-portfolio-review/SKILL.md) | Audits a folder of side projects (or a GitHub account's repos) and maintains a running `PROJECT_STATE.md` per project plus a sorted `PORTFOLIO.md` rollup — verdict (money/fame/private/expand/merge/delete/neither), staleness, planning docs, deploy signals, and one concrete next step per project. |

All bundled scripts reference their own skill directory (`<skill_dir>/...`), not a
hardcoded absolute path — they work wherever the skill actually gets installed.

## Adding a new skill

Create `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`) followed by the
skill's instructions. See the existing skill for the expected format.
