# Sources and further reading

This skill's methodology comes from a small, traceable set of sources —
documented here so anyone extending or second-guessing the rubric can go
to the originals instead of trusting the compressed version in
`levers.md`/`rubric.md`/`mcp-tools.md`. Built in two rounds; the second
round exists specifically because the first one under-researched and
this file says so plainly rather than quietly patching it over.

## Contents
- Round 1: initial build
- Round 2: post-build research pass (corrects round 1)
- What still hasn't been checked

## Round 1: initial build

One live external lookup, via `WebFetch`, on the page the user pointed
at as the model to build from:

- **aihero.dev — "Writing for Agents"**
  https://www.aihero.dev/skills-writing-for-agents
  Source of the two-budget framing (context load vs. cognitive load) and
  the original statement of the "Five Levers."

No RAG, Perplexity, or `WebSearch` calls were made in round 1. The rest
came from Claude Code's own bundled `skill-creator` skill (progressive
disclosure's three-tier model, the ~500-line guideline, a >300-line
reference-TOC convention that round 2 corrected — see below) plus
general model knowledge for the specific thresholds (score bands, XS-XL
sizes, the 0.85 paragraph-similarity cutoff). That knowledge was never
verified against Anthropic's own current documentation, which turned out
to matter.

## Round 2: post-build research pass (corrects round 1)

Triggered by the user directly asking why `avangarde-rag` and Perplexity
weren't used, and asking for a proper pass to make the tool as solid as
possible.

**Correction: the RAG assumption in round 1 was wrong.** Round 1 assumed
`avangarde-rag` held nothing relevant, based on what other skills in this
repo use it for (design/UX/trope books), and skipped checking. It should
have checked. `mcp__avangarde-rag__search_knowledge_base` turned up:

- **"Effective context engineering for AI agents"** (Anthropic
  engineering blog, indexed in full as a 32-chunk PDF) —
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  The first-party source for "right altitude" (quoted verbatim in
  `levers.md`), compaction, structured note-taking, and sub-agent
  delegation for long-horizon context management. This is the primary
  source `levers.md`'s Five Levers should have been traced to from the
  start — aihero.dev's version was a compatible but secondhand
  restatement of ideas Anthropic had already published.
- **"Writing effective tools for AI agents"** (Anthropic engineering
  blog, found and fetched via `WebSearch` + `WebFetch`, not indexed in
  the RAG at the time of this pass) —
  https://www.anthropic.com/engineering/writing-tools-for-agents
  Entirely new dimension this skill was missing despite claiming to
  audit MCP tool descriptions: tool consolidation, namespacing, response
  shaping, token-efficiency defaults, actionable error messages. Now
  `references/mcp-tools.md`.

Also fetched directly via `WebFetch` (not RAG-indexed):

- **platform.claude.com — "Skill authoring best practices"**
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  The canonical, current spec — more authoritative than the bundled
  `skill-creator` skill for exact numbers. Source of every hard-gate
  check in `lint_structure.py` (name/description format and length
  limits, third-person requirement), the "keep references one level
  deep" rule, the degrees-of-freedom framework, and the correction from
  >300 lines to >100 lines for when a reference file needs a table of
  contents (skill-creator's bundled note had the older/looser number;
  this page is the current official one, so it wins).
- **aihero.dev — "A Complete Guide to AGENTS.md"**
  https://www.aihero.dev/a-complete-guide-to-agents-md
  Source of the `CLAUDE.md`/`AGENTS.md` symlink convention (which
  motivated the synced-pair detection added to `scan_hierarchy.py` so a
  symlinked pair isn't double-counted), the ~150-200-instruction budget
  heuristic, and the explicit "what should NOT go in it" list for
  root-level agent-instruction files.

`WebSearch` was used several times in this round (to locate the pages
above); Perplexity was not — `WebSearch` found the exact canonical pages
on the first or second query each time, so spending Perplexity's more
limited quota wasn't warranted. That's a judgment call each time, not a
standing rule to skip Perplexity.

## What still hasn't been checked

Being honest about the boundary of this research, not just what's in
it: no academic literature search was done beyond what these sources
cite in passing (e.g. the RAG's "A Survey of Context Engineering for
LLM.pdf" surfaced in searches but wasn't read closely — it's a broader
academic survey that likely has more on memory-augmented agents than
was pulled in here). If a future audit finding seems to need more than
`levers.md`/`rubric.md`/`mcp-tools.md` cover, that survey is a
reasonable next place to check before assuming the gap needs original
research.
