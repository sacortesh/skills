# Scoring rubric

## Contents
- Hard gate (check first)
- Dimensions to weigh
- Score bands
- Shirt sizes
- What this rubric doesn't cover
- Report template

Score and effort are two different questions — keep them independent.
**Score (1-10)** answers "how good is this file right now?" **Shirt size
(XS-XL)** answers "how much work is fixing it?" A short, vague file can
score low but need only an XS/S fix (just add what's missing). A long,
well-organized-but-bloated file can also score low, yet need an L fix
(splitting it apart). Don't let one determine the other.

## Hard gate — check first, separately from the score

These are platform-enforced limits, sourced from Anthropic's own Skill
authoring docs, not style judgments — a violation is a bug, not a taste
disagreement, and caps the score regardless of how good everything else
is. `lint_structure.py` checks these mechanically for any file with
frontmatter (skills, subagents):

- `name`: max 64 characters, lowercase letters/numbers/hyphens only, no
  XML tags, must not contain "anthropic" or "claude" (reserved words).
- `description`: max 1,024 characters, non-empty, no XML tags, **third
  person** ("Processes X, generates Y" — not "I can help with X" or "you
  can use this for Y"). Anthropic is explicit that inconsistent
  point-of-view causes discovery problems, since the description is
  injected straight into the system prompt.

A file that fails the hard gate scores **4 or below**, no matter how
good the body is — a description over 1,024 characters may simply get
rejected or truncated by the platform, which makes every other quality
judgment moot until it's fixed. This is an XS/S fix almost always (trim
or reword the frontmatter), never a reason to redesign the body.

If the file under audit is an **MCP tool description** rather than a
skill/prompt file, stop here and use `references/mcp-tools.md` instead
of the dimensions below — tool descriptions are evaluated against a
different, Anthropic-sourced rubric (consolidation, namespacing, response
shaping, token budgets), not this one.

## Dimensions to weigh (not mechanically average)

Read `levers.md` first — these dimensions are that framework applied.
For any given file, judge each dimension that applies (some are N/A —
e.g. a plain system prompt has no frontmatter to check; a `CLAUDE.md`
has no "trigger description" the way a skill does), then form an overall
1-10 judgment. Don't average five numbers into a sixth; a single severe
problem (e.g. actively wrong instructions, or a 1500-line always-loaded
file) can cap the whole score even if other dimensions are fine.

1. **Trigger clarity** *(skills, subagents)* — does the description say
   both *what* it does and *when* to use it, with concrete phrasing the
   router can match against? Generic descriptions ("helps with X") score
   low even if the body is excellent, because the body never gets a
   chance to run.
2. **Right altitude** — specific enough to be actionable, not so rigid
   it breaks outside the exact cases the author imagined. Watch for
   brittle enumerated if/else logic where a stated principle would
   generalize better, and for vague hand-waving ("be careful," "use
   good judgment") with no actionable content behind it. Use the
   **degrees-of-freedom** lens from `levers.md` to make this concrete
   per-instruction rather than per-file: a fragile, must-happen-in-order
   operation earns low-freedom exact steps; a judgment call with several
   valid approaches earns high-freedom heuristics. A file scoring low
   here often has the freedom level backwards somewhere, not wrong
   everywhere. This extends to formatting: a long paragraph cramming
   several ordered steps or conditions into prose is a candidate for a
   list (`lint_structure.py`'s "procedural paragraphs" check flags these
   mechanically); see `levers.md`'s degrees-of-freedom section for why
   this isn't a blanket bullets-over-prose rule.
3. **Hierarchy & progressive disclosure** — is the always-loaded layer
   (frontmatter, or the whole file for a `CLAUDE.md`) thin, with
   conditional/domain-specific material pushed behind clear pointers?
   Or is everything inlined regardless of how often it's needed?
4. **Pruning** — run the no-op test mentally (or trust
   `lint_structure.py`'s duplicate-paragraph findings as a starting
   list): does anything restate a point already made? Sediment from
   incremental edits (a caveat added after each of three separate bugs,
   never consolidated) is the most common cause here.
5. **Completion criteria** — where the file describes a task with an end
   state, is "done" concrete and demanding, or vague enough to invite
   stopping early?
6. **Structural hygiene** — valid, complete frontmatter where required
   (see the hard gate above); no leftover placeholder text — but don't
   confuse a maintainer-facing `TODO.md`/`NOTES.md` (a legitimate
   agentic-memory pattern, see `levers.md`) with an actual unresolved
   `TODO:` marker left in runtime instructions; headings that actually
   aid navigation; examples present where the task benefits from one;
   reference files over 100 lines have a table of contents near the top
   (Claude may only partially read longer files); reference files stay
   one level deep from SKILL.md rather than linking to further reference
   files (`lint_structure.py` surfaces internal `.md` links as a
   starting point — a link doesn't automatically mean a violation, check
   whether the target is itself SKILL.md-adjacent or a further-nested
   reference); consistent terminology throughout (don't alternate
   between "endpoint"/"route"/"URL" for the same thing); no
   time-sensitive claims that'll silently go stale (a dated cutoff like
   "before August 2025, use X" belongs in a clearly labeled legacy/old-
   patterns section, not stated as current fact).
7. **Length calibration** — is the length proportional to the actual
   complexity of the task, in *both* directions? A 40-line `SKILL.md`
   for a genuinely multi-branch workflow is under-specified, not lean.
   A 700-line `CLAUDE.md` for a small repo is bloat, not thoroughness.

## Score bands

- **9-10 — Exemplary.** Thin always-loaded layer, clear pointers to
  conditional material, no duplication, length matches complexity in
  both directions, concrete completion criteria, trigger description
  (if applicable) a router could act on confidently.
- **7-8 — Solid.** Works reliably; one or two dimensions have minor
  gaps (a slightly generic phrase, one paragraph that could be pruned,
  a missing example). Nothing here would cause a real agent run to go
  wrong.
- **5-6 — Usable but frictional.** A real issue in at least one
  dimension — noticeable bloat, a vague completion criterion, a
  description too generic to trigger reliably. Works most of the time,
  wastes budget or produces inconsistent behavior some of the time.
- **3-4 — Poor.** Actively works against the agent: an always-loaded
  file large enough to tax every session regardless of task, or
  guidance vague/brittle enough to misfire regularly. Needs real
  rework, not touch-ups.
- **1-2 — Broken.** Missing required structure entirely (no
  frontmatter where one's required, no discernible instructions), or
  content that actively contradicts itself.

## Shirt sizes (effort to fix)

- **XS** — wording only. Tighten a sentence, fix a typo, sharpen one
  phrase. No restructuring, no new files. Under ~15 minutes.
- **S** — trim redundancy, rewrite a weak description, cut a handful of
  sentences that fail the no-op test. Still a single file, same shape.
- **M** — real restructuring within the same file (reorder sections,
  add missing completion criteria or an example), or extracting exactly
  one piece into a new `references/` file. Shape mostly holds.
- **L** — split material across multiple `references/`/`scripts/`
  files, rebuild the information hierarchy, rewrite large portions.
  The file's shape changes.
- **XL** — the scope or approach is wrong at the root (wrong altitude
  throughout, or trying to do too many unrelated things in one file).
  Needs a redesign. Worth running skill-creator's eval loop afterward —
  a rewrite this size should be validated against real test prompts,
  not just re-read for quality.

## What this rubric doesn't cover

This is a static-text audit — it judges the file, not how the file
performs in the model's hands. Anthropic's own authoring guidance is
explicit that real Skill quality comes from **evaluation-driven
development**: build a few realistic test scenarios, run them with and
without the file, test across the model sizes actually in use (a Skill
tuned for Opus can under-specify for Haiku), and iterate from observed
behavior. A 9/10 score here means the file is well-constructed by every
inspectable measure; it doesn't substitute for running it. If the user
wants that level of validation — especially after an XL rewrite — point
them at the `skill-creator` skill's eval-and-iterate loop rather than
trying to replicate it here.

## Report template

Use this shape when reporting an audit (single file or a repo scan):

```markdown
## Audit: <file or repo>

| File | Lines | Est. tokens | Score | Shirt size | Top issue |
|---|---|---|---|---|---|
| ... | ... | ... | .../10 | XS-XL | one line |

### <file path>
**Score:** X/10 — one-sentence verdict
**Shirt size:** <size> — one-sentence reason

**Strengths:**
- ...

**Issues (most severe first):**
- [dimension] specific problem, with a line reference where useful

**Proposed fix:** (only after the user asks to proceed — see SKILL.md's
correction workflow) a concrete diff, not just a restated complaint.
```

In repo-hierarchy mode, order the table by load priority (per
`scan_hierarchy.py`'s layer order), not by score — the point is that a
mediocre always-loaded `CLAUDE.md` matters more than a mediocre
on-trigger skill body, even if their scores are identical.
