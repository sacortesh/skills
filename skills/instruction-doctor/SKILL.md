---
name: instruction-doctor
description: Audits and corrects instructions written for an AI agent — a skill's SKILL.md, a project's CLAUDE.md or AGENTS.md, a subagent definition, an MCP tool description, or any raw agent/system prompt. Scores quality 1-10 and estimates a shirt-size (XS-XL) fix effort, checking Anthropic's own hard platform limits plus a progressive-disclosure/context-engineering rubric — a short prompt is under-specified just as often as a long one is bloated. Works on a single file or pasted prompt, or — invoked inside a repo — walks every file that lands in context IN LOAD ORDER, flagging always-loaded bloat first. Never translates the audited file's language unless asked. Use whenever the user wants to audit, review, score, or fix a prompt/skill/CLAUDE.md/AGENTS.md/subagent/MCP tool description; asks "is this skill too long," "how good are my instructions," "audita este prompt," "revisa este CLAUDE.md," "por qué no dispara este skill," or wants to know how much context window a file would consume.
argument-hint: "file path, pasted prompt, or leave blank to audit this repo's instruction hierarchy"
---

# Instruction Doctor

## Contents
- Prerequisites
- Step 0 — Resolve the mode
- Step 1 — Measure before judging
- Step 2 — Score and size
- Step 3 — Report
- Step 4 — Correct, only on request
- The never-translate rule

Audits instruction files the way a doctor reads a chart before
prescribing: measure first, diagnose against a known framework, then
treat — never skip straight to rewriting on instinct. The methodology
lives in `references/levers.md` (the two budgets: context load vs
cognitive load, and the five levers) and `references/rubric.md` (how
that turns into a 1-10 score and an XS-XL effort estimate, plus a hard
pass/fail gate for platform-enforced limits). Read both before the first
real audit in a session; they're short and everything below assumes
them. `references/mcp-tools.md` replaces `rubric.md` specifically when
auditing an MCP tool description (see Step 0). `references/sources.md`
lists exactly what was and wasn't researched to build this rubric, for
anyone who wants to check the originals or recalibrate a threshold.

## Prerequisites

Python 3 on PATH. The scripts in `scripts/` run standalone — no install
needed. `tiktoken` and the `anthropic` package sharpen the token
estimate if present, but every script degrades gracefully without them
(see each script's docstring for its fallback).

## Step 0 — Resolve the mode

**Single-artifact mode**: the user names or pastes one thing — a file
path, a skill directory, or raw prompt text pasted into chat. If it's
pasted text with no file behind it, save it to a file under the
scratchpad directory first (e.g. `pasted_prompt.md`) so the scripts below
have something to run against — don't try to eyeball token/line counts
by hand when a script can do it exactly.

**Repo-hierarchy mode**: the user asks about "this repo," "my
instructions," "why doesn't this skill trigger," or gives no specific
target while working inside a repo. Confirm the resolved target and mode
back to the user in one line before running anything — a wrong guess
here wastes the whole audit.

A skill directory (SKILL.md plus its `references/`/`scripts/`) is a
middle case: audit the SKILL.md itself in full, then skim any reference
file for the same issues — especially duplication *between* SKILL.md and
its own references (the same point made twice across files is still a
pruning violation), and check that any reference file over 100 lines has
a table of contents near the top (`lint_structure.py` checks this).

**MCP tool description mode**: the target is a tool's `description`
field and schema, not a skill/prompt file (e.g. "is this tool
description good," "why does the agent keep picking the wrong tool").
Skip `references/rubric.md`'s dimensions and use `references/mcp-tools.md`
instead — tool descriptions fail differently (tool selection ambiguity,
namespacing, response shaping) than skill/prompt files do.

## Step 1 — Measure before judging (deterministic, always run these)

Single-artifact mode:
```
python3 <skill_dir>/scripts/count_tokens.py <file>
python3 <skill_dir>/scripts/lint_structure.py <file>
```

Repo-hierarchy mode:
```
python3 <skill_dir>/scripts/scan_hierarchy.py <repo_path>
```
This alone answers "how much context window would loading this file
consume" and, critically, separates **always-loaded** cost (global
CLAUDE.md + project CLAUDE.md + every skill's and subagent's
description — paid every session, regardless of task) from
**conditional** cost (skill/agent bodies — paid only when that
skill/agent actually triggers). The `always_loaded_token_budget` in its
summary is the single most useful number for deciding what to fix first:
fixing an oversized body that triggers rarely matters far less than
trimming 50 tokens off a description that loads in every session.

Then run `lint_structure.py` on each entry worth a closer look — in
practice: everything in the always-loaded layer, plus anything
`scan_hierarchy.py` flagged `OVER LINE THRESHOLD`. If a repo has many
skills/subagents, don't blindly deep-dive every body — that's expensive
and most are fine. Tell the user how many entries exceeded the
threshold and ask which (if any) beyond that they want inspected, unless
the count is small enough (a handful) that just doing all of them is
obviously cheaper than asking.

These scripts report facts, not verdicts — line counts, token estimates,
duplicate paragraphs, missing frontmatter fields, placeholder leftovers.
The verdict is Step 2.

## Step 2 — Score and size

Check `references/rubric.md`'s hard gate first (name/description format
and length — `lint_structure.py` already flags violations as `[HARD]`).
A hard-gate failure caps the score at 4 regardless of everything else,
and is an XS/S fix on its own — don't let it block scoring the rest of
the file. Then apply the rubric's dimensions to reach a 1-10 score and
an XS-XL shirt size **per file**, informed by (not mechanically derived
from) Step 1's findings. A file can measure short and still score low
(under-specified) or measure long and still score high (genuinely
complex task, well hierarchized) — length is one input, not the
verdict.

## Step 3 — Report

Use the table + per-file template in `references/rubric.md`'s "Report
template" section. In repo-hierarchy mode, order the table by load
priority (always-loaded layer first), not by score — a mediocre
always-loaded CLAUDE.md matters more than a mediocre on-trigger skill
body with an identical score, because of who pays for it and how often.

## Step 4 — Correct, only on request, always as a proposed diff

Audits report findings; don't jump to editing files unless the user asks
for the fix. When they do:

1. Draft the corrected version, applying `levers.md`'s principles
   directly: prune first (delete, don't soften), push conditional
   material behind a pointer rather than inlining it, replace bare
   `MUST`/`NEVER` with the reasoning behind them where it's missing, add
   concrete completion criteria where the task has an end state that
   isn't currently stated.
2. Show the proposed change as a diff — via `Edit`'s old/new pairs, or a
   clear before/after in chat — with a one-line rationale per
   substantive change, tied to a lever ("pruned — restates the
   duplicate-paragraph point flagged in Step 1", "moved behind a
   pointer — only needed for the multi-domain case").
3. **Wait for explicit approval before writing.** This holds even for
   trivial XS fixes — the file may be in use by other sessions or
   agents, and an unreviewed edit to a CLAUDE.md or SKILL.md silently
   changes behavior for everyone who loads it next.

## The never-translate rule

Never change the language an instruction file is written in as part of
a "fix," and never suggest a rewrite in a different language than the
original — not English-to-Spanish, not the reverse, regardless of which
language you're chatting with the user in right now. Whether English or
Spanish (or a mix) prompts a given model better is genuinely unsettled;
changing language is a real, separate experiment the user hasn't asked
to run, and silently bundling it into an unrelated structural fix would
confound any comparison they might want to make later. Only translate if
the user explicitly asks for a translation, as its own request — and
treat that as a distinct task, not part of an audit.

The audit report itself (scores, findings, commentary) can be written in
whatever language the conversation is already in — that's a different
question from the audited file's own language, which stays untouched.
