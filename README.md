# skills

Personal collection of [Claude Skills](https://github.com/vercel-labs/skills), installable via:

```bash
npx skills add sacortesh/skills
```

## Layout

Flat layout — one folder per skill under `skills/`:

```
skills/
  cv-builder-interview/
    SKILL.md
```

## Available skills

| Skill | What it does |
|---|---|
| [`cv-builder-interview`](skills/cv-builder-interview/SKILL.md) | Builds résumé/CV bullet points through a structured interview (problem → what you did → quantified result → tools), instead of guessing or inventing content. Includes reference material: formatting rules, action verb bank, and a demonstrable/relevant/finished filter for which personal projects are worth including. |

## Adding a new skill

Create `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`) followed by the
skill's instructions. See the existing skill for the expected format.
