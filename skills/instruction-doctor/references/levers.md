# The methodology behind the audit

## Contents
- Two budgets, not one
- The Five Levers
- Right altitude and degrees of freedom
- Managing context over a long audit
- CLAUDE.md and AGENTS.md specifics
- How this cashes out during an audit
- Claude Code's own three-tier loading model

Two ideas do almost all the work here. Everything in `rubric.md` is a
restatement of these two ideas applied to specific dimensions.

## Two budgets, not one

Every instruction file spends against two different budgets, and they
trade off against each other:

- **Context load** — tokens that sit in the window whether or not they're
  used this turn. A verbose `CLAUDE.md`, a skill description that runs
  three paragraphs, a subagent file with a 200-line preamble — all of
  this is context load, paid on every single session regardless of task.
- **Cognitive load** — the burden on the *human* (or the model reading
  the file) of knowing which documents exist, what they're for, and when
  to go read them. A file that's too short to answer real questions
  pushes cognitive load onto whoever has to guess, ask, or improvise.

A short prompt isn't automatically good — it may just have shipped its
cost downstream as ambiguity. A long prompt isn't automatically thorough
— it may just be spending context load to avoid the design work of
deciding what actually needs to be said. The audit scores against both
failure modes, not just length.

## The Five Levers

A framework for where information should live and how it should be
worded, originally from aihero.dev's "Writing for Agents" and directly
corroborated by Anthropic's own "Effective context engineering for AI
agents" (see `sources.md`) — both converge on the same underlying idea,
so this skill treats it as validated rather than one blogger's opinion:

**Context pointers** — a reference that lives in the always-loaded file
and names something out-of-context (a `references/*.md`, a script, a
section further down). The pointer's *wording* is what makes it
reliable, not just its existence: "see `references/hierarchy.md`" is
weaker than "if scoring a skill with >2 domains/frameworks, read
`references/hierarchy.md` before continuing" — the second tells the
reader *when* to take the detour, not just that it exists.

**Information hierarchy** — the progression from steps written inline,
to references cited inline, to material fully disclosed only behind a
pointer. This is progressive disclosure: keep the top legible (metadata →
body → bundled resources, in Claude Code's own three-tier model), and
push anything conditional or domain-specific one level down rather than
inlining it for everyone. Anthropic's own platform docs add one sharp
constraint here worth enforcing mechanically: **keep references one
level deep from SKILL.md.** If a reference file itself links to another
reference file, Claude may only partially read the chain (previewing
with something like `head -100` instead of reading in full), and
information silently goes missing. `lint_structure.py` surfaces internal
`.md` links in a file so this is checkable rather than assumed.

**Completion criteria** — a clear, demanding statement of what "done"
looks like. Vague completion criteria ("clean up the code") invite
premature stopping; concrete ones ("all tests pass and no TODOs remain")
don't. Instruction files that never say what done looks like tend to
produce inconsistent runs.

**Leading words** — compact, pretraining-familiar phrases that anchor
both what the model does and when it recognizes to do it ("tracer
bullet," "red flag," "golden path"). These work *because* they're
already loaded with meaning from training — inventing bespoke jargon
does the opposite, forcing the reader to learn a private vocabulary
before the instructions even start.

**Pruning** — the discipline of cutting anything that fails the no-op
test: delete the sentence, ask whether the model's behavior would
actually change. If not, it was sediment — accumulated explanation that
felt necessary to add but isn't load-bearing. The default move when a
file is bloated is deletion, not softer rewording. Anthropic's platform
docs frame the same idea as a default assumption: **Claude is already
very smart** — before keeping a sentence, ask "does Claude really need
this explanation, or am I paying tokens to state the obvious?" Their own
before/after example cuts a ~150-token PDF-extraction explainer down to
~50 tokens by deleting everything a competent reader already knows about
what a PDF is.

## Right altitude and degrees of freedom

Anthropic's context-engineering guidance names the same failure mode
this skill's "right altitude" dimension checks for, verbatim: *"At one
extreme, we see engineers hardcoding complex, brittle logic in their
prompts... At the other extreme, engineers sometimes provide vague,
high-level guidance that fails to give the LLM concrete signals... The
optimal altitude strikes a balance: specific enough to guide behavior
effectively, yet flexible enough to provide the model with strong
heuristics."*

The platform docs give a more actionable lens for the same judgment call
— **degrees of freedom**, matched to how fragile and variable the task
actually is:

- **High freedom** (plain text-based instructions, a numbered list of
  considerations) — when multiple approaches are valid and heuristics
  should guide the call. A code-review checklist is high freedom.
- **Medium freedom** (pseudocode, a parameterized template/script) —
  when a preferred pattern exists but some variation is fine.
- **Low freedom** (an exact script/command, "run precisely this, don't
  modify it") — when the operation is fragile, error-prone, or must
  happen in a specific sequence. A database migration is low freedom.

Their own metaphor: think of the model as walking a path. A **narrow
bridge with cliffs on both sides** needs exact guardrails (low freedom)
— get it wrong and there's no recovery. An **open field with no
hazards** needs only general direction (high freedom) — many routes
succeed. Auditing a file for "right altitude" means asking which terrain
each instruction actually describes, not applying one house style
everywhere in the same file.

Freedom level has a formatting corollary, not just a content one.
Anthropic's own prompting guidance says to write instructions "as
sequential steps using numbered lists or bullet points when the order or
completeness of steps matters" — which is exactly the low-freedom,
must-happen-in-order case above. A paragraph that buries several
distinct conditions or ordered steps in flowing prose is a format/content
mismatch worth flagging, the same way a brittle enumerated if/else would
be flagged in the other direction. This isn't a blanket "bullets beat
prose" rule: high-freedom rationale and exposition are still better as
prose, and the effect is strongest for small models parsing multi-step
prompts (an arXiv study on small-model agents found bullet conversion
"significantly improves instruction-following" there) — frontier models
like Claude handle dense, well-written prose without losing track of
individual requirements nearly as often. Judge each paragraph against
the freedom level of what it's actually saying, don't convert a file to
bullets wholesale. `lint_structure.py`'s "procedural paragraphs" check
flags long, many-sentence paragraphs as candidates for this judgment
call — it's a rough proxy (sentence count, not semantic understanding of
whether order actually matters), so treat its hits as worth a look, not
an automatic fix.

## Managing context over a long audit

Anthropic's article also covers strategies for keeping an agent coherent
once a session runs long — directly relevant to `instruction-doctor`
itself when auditing a repo with many skills/agents, and to one specific
judgment call worth getting right:

- **Structured note-taking** (a `NOTES.md`, `TODO.md`, or Claude Code's
  own to-do list, persisted outside the context window and re-read
  later) is an explicitly endorsed agentic-memory pattern, not a smell.
  **Don't flag a maintainer-facing TODO/NOTES file as a structural
  problem just because it exists.** The legitimate finding is narrower:
  whether it's wired into the runtime flow when it shouldn't be (bloating
  the always-loaded or on-trigger path with build history no live
  session needs), not the file's mere presence.
- **Compaction** (summarizing a conversation nearing its context limit,
  keeping architectural decisions and discarding redundant tool output)
  is the pattern this skill's own workflow leans on implicitly: prefer
  condensed findings over pasting raw script JSON into the ongoing
  report.
- **Sub-agent delegation** — spawning a subagent to explore extensively
  (tens of thousands of tokens) and return only a condensed summary
  (Anthropic cites 1,000-2,000 tokens) — is the right move when a repo
  scan turns up many skill/agent bodies worth a closer look. This is why
  `SKILL.md`'s Step 1 says not to blindly deep-dive every flagged entry:
  past a handful, parallelize with subagents rather than reading
  everything serially in the main context.

## CLAUDE.md and AGENTS.md specifics

`AGENTS.md` is an open, multi-tool standard; Claude Code reads
`CLAUDE.md` instead. The common convention is symlinking them
(`ln -s AGENTS.md CLAUDE.md`) so every tool sees the same file —
`scripts/scan_hierarchy.py` detects this (or byte-identical copies kept
in sync by hand) and counts the always-loaded budget once, not twice.

Two calibration points specific to this file type, distinct from a
skill's `SKILL.md`:

- **Rough instruction-count budget**: frontier models can follow on the
  order of 150-200 instructions with reasonable consistency. Line count
  is a loose proxy, but for a file this dense (short, imperative lines)
  it's a more honest ceiling than "500 lines," which assumes a tier-3
  escape hatch `AGENTS.md`/`CLAUDE.md` doesn't have. Since there's
  nowhere to push detail down to, the escape hatch here is scope
  discipline, not hierarchy — trim what's in scope rather than deferring
  it to a reference file.
- **What shouldn't be in it**, per the same guidance: auto-generated
  boilerplate from a scaffolding tool, stale file paths likely to drift,
  redundant statements of things the model already knows, and
  language/framework-specific rules that belong in a nested,
  directory-scoped `CLAUDE.md` instead of the root file everyone always
  pays for.

## How this cashes out during an audit

- A file that's long because it inlines material only 10% of runs need →
  push that material behind a pointer (lever: information hierarchy +
  pointers). This is usually the fix for an oversized `SKILL.md` or
  `CLAUDE.md`.
- A file with repeated caveats, restated warnings, or the same idea in
  three places → prune (apply the no-op test paragraph by paragraph;
  `scripts/lint_structure.py` finds exact and near-duplicate paragraphs
  mechanically as a starting list).
- A file full of unexplained `MUST`/`NEVER`/`ALWAYS` → not automatically
  wrong, but a yellow flag worth checking: does the model actually need
  the *why*, or is the imperative alone enough? Brittle, unexplained
  imperatives break the moment a real case falls slightly outside what
  the author imagined; a stated reason lets the model extrapolate
  correctly to cases the author didn't enumerate.
- A file that's short but vague, forcing the model to guess at scope,
  output format, or when to stop → under-specified, not "efficiently
  terse." Add completion criteria and concrete examples, don't just leave
  it short.
- A skill/agent description that's generic ("helps with X") → weak
  context pointer at the metadata layer; the router (the model deciding
  whether to invoke this skill) can't act on it. Descriptions need to be
  concrete enough to match against, per skill-creator's own guidance:
  specific trigger phrases, named contexts, and — because models
  currently under-trigger skills — a bit of deliberate "pushiness."

## Claude Code's own three-tier loading model

This is the concrete instance of "information hierarchy" that
`scripts/scan_hierarchy.py` measures:

1. **Metadata** (skill/agent `name` + `description`) — always in context,
   for every skill and every subagent installed, whether or not they're
   used this turn. `name` and `description` are also subject to hard
   platform limits (64 chars, 1024 chars respectively) — see
   `rubric.md`'s hard-gate section.
2. **SKILL.md / agent body** — loaded only once that skill triggers or
   that subagent spawns. Target: under 500 lines; if approaching that,
   the fix is almost always an added layer of hierarchy (push detail to
   `references/`), not just trimming prose.
3. **Bundled resources** (`scripts/`, `references/`, `assets/`) — loaded
   only when the body explicitly points the reader there. Effectively
   unlimited size, because the cost is paid only on demand — this is
   where length stops being a problem, as long as the pointer to get
   there is clear, and it stays one level deep.

`CLAUDE.md` and `AGENTS.md` don't have a tier 3 by convention — they're
closer to always-loaded tier-1/tier-2 material, which is exactly why
their line-count threshold in the audit is stricter than a skill body's:
a bloated `CLAUDE.md` has no "on-trigger" escape hatch. Every token in it
is paid on every session in that repo, full stop.
