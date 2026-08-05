# AGENTS.md — sacortesh/skills

## Naming convention

Lead with the generic, searchable noun a stranger would actually type into
`npx skills find <query>` or skills.sh — not a brand, method name, or internal
project word. Narrow with what it does, and put anything project-specific or
branded last, only if it adds real information.

Pattern: `<searchable-noun>-<what-it-does>[-<variant>]`

**Good, don't change:**
- `book-shopping`, `book-hunt` — lead with "book," the word someone actually
  searches. The verb after it (shopping/hunt) distinguishes the two.

**Needs fixing when next touched:**
- `aspire-learning` → should lead with "learning" (e.g. `learning-aspire`).
  "ASPIRE" is the internal method name for the protocol, not what a stranger
  searches for.
- `project-portfolio-review` → should lead with "portfolio" (what people
  search), not "project." Also consider splitting by scope once the local
  and GitHub-repo modes diverge enough to be found independently —
  `portfolio-review-local` / `portfolio-review-github` — rather than one
  skill covering both behind an internal mode switch.

## When adding a new skill to this repo

1. Name it noun-first per the pattern above, before writing `SKILL.md`.
2. Reference bundled scripts/resources relative to the skill's own directory
   (`<skill_dir>/scripts/...`), never a hardcoded absolute path — this repo
   is meant to be installed on machines that aren't this one.
3. Add a `## Prerequisites` section if the skill shells out to anything
   (a runtime, a CLI, an API key) — state it up front, don't bury it in
   usage instructions further down.
4. Update the table in `README.md`.
