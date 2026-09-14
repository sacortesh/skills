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
- `learning-aspire` (renamed 2026-08-05, was `aspire-learning`) — leads with
  "learning" now; "ASPIRE" is the internal method name, kept as the suffix.
- `portfolio-review` (renamed 2026-08-05, was `project-portfolio-review`) —
  leads with "portfolio" now. Splitting by scope (local vs. GitHub-repo
  mode) was considered and rejected — `references/github-repos.md` already
  handles that branch cleanly within one skill.

## When adding a new skill to this repo

1. Name it noun-first per the pattern above, before writing `SKILL.md`.
2. Reference bundled scripts/resources relative to the skill's own directory
   (`<skill_dir>/scripts/...`), never a hardcoded absolute path — this repo
   is meant to be installed on machines that aren't this one.
3. Add a `## Prerequisites` section if the skill shells out to anything
   (a runtime, a CLI, an API key) — state it up front, don't bury it in
   usage instructions further down.
4. Update the table in `README.md`.

## Deploying local edits

**This repo is the only place a skill's source ever gets edited — no
exceptions, including when the editing is done through `skill-creator`
or any other tool.** Edit here first, then push out with:

```bash
npx skills add . -g -s <skill-name> -y   # one skill
npx skills add . -g --all                # everything
```

Never hand-edit a deployed copy under `~/.agents/skills/` or
`~/.claude/skills/` directly — some of those are symlinks back into this
repo and some are plain copies the CLI overwrites per-agent (not every
agent supports symlinking), so an edit made there is invisible to git
and gets silently clobbered by the next `add`. Treat everything outside
this repo as build output.

**`skill-creator` specifically is a trap here.** It's a generic tool
with no awareness of this repo's convention, and when asked to "edit
skill X" it will happily resolve and write to whatever copy it finds
first — typically a deployed one under `~/.claude/skills/` or
`~/.agents/skills/`, since that's what's actually loaded and discoverable
in a live session, not the repo path. This already happened once: an
`instruction-doctor` edit session landed entirely in
`~/.agents/skills/instruction-doctor` (reached via a symlink from
`~/.claude/skills/`) and the repo copy went stale until caught later by
hand. Before invoking `skill-creator` (or pointing any other editing
tool) at a skill that lives in this repo, explicitly pass it the path
under `skills/<name>/` — never let it resolve the name on its own.
