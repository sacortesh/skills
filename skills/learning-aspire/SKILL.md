---
name: learning-aspire
description: Runs the ASPIRE self-learning protocol (Audit, Source, Probe, Ingest, Retrieve, Endure) for any skill or topic the user wants to learn — including coding skills. Use when the user invokes this skill directly, asks to start or resume a learning project, or references "the ASPIRE method" or "the download protocol."
argument-hint: "topic slug to resume/start, or leave blank for a status dashboard"
disable-model-invocation: true
---

# ASPIRE — Self-Learning Protocol

You are running a structured self-learning loop for the user. The method: **A**udit → **S**ource → **P**robe → **I**ngest → **R**etrieve → **E**ndure. Audit and Source happen once per topic. Probe, Ingest, and Retrieve+Endure repeat once per unit of the syllabus.

This is a stateful, multi-session tool. The filesystem under `~/aspire/` *is* the state — always read it before acting, never assume what session you're in.

---

## Data location

All data lives under `~/aspire/`. One folder per topic:

```
~/aspire/<topic-slug>/
  audit.md              — outcome, timeframe, current level (written once, in Audit)
  map.md                — the syllabus checklist (written in Source, updated every transition)
  knowledge.md           — rolling summary of every unit that has reached Endure
  units/
    to-source/<unit-slug>/     meta.md
    to-probe/<unit-slug>/      meta.md, sources.md
    ingesting/<unit-slug>/     meta.md, sources.md, probe.md, ingest-notes.md
    to-retrieve/<unit-slug>/   meta.md, sources.md, probe.md, ingest-notes.md
    endured/<unit-slug>/       meta.md, sources.md, probe.md, ingest-notes.md, diff.md, summary.md
```

A unit's folder location **is** its phase. Moving a unit forward means `mv`-ing its folder from one `units/<state>/` directory to the next and adding the file that phase produces. Never leave a unit's folder in two states at once.

State order: `to-source → to-probe → ingesting → to-retrieve → endured` (terminal).

---

## Invocation

**No argument, or argument doesn't match an existing topic slug:**

1. `ls ~/aspire/` (create the directory with `mkdir -p` if it doesn't exist yet — this may be the first run).
2. For each topic folder, read `map.md` and count units per state.
3. Show a compact dashboard: topic name, outcome (one line from `audit.md`), and a per-state unit count (e.g. `oil-painting: 2 endured, 1 ingesting, 4 to-source`).
4. If no topics exist, or the user's argument looks like a new topic description, offer to start a new one — proceed to **Phase: Audit**.
5. If topics exist, ask which one to resume, or whether to start a new one.

**Argument matches an existing topic slug:**

1. Read `map.md` and scan `units/` to find what's in flight.
2. If any unit is in `to-probe`, `ingesting`, or `to-retrieve`, resume that unit at its current phase — jump straight to the matching phase section below. Don't re-ask questions already answered in that unit's files; read them first.
3. If every unit that has been sourced is `endured`, and there are still units in `to-source`, continue sourcing the next batch.
4. If every unit on the map is `endured`, congratulate the user, show the `knowledge.md` summary, and ask if they want to add units to the map or close out the topic.

---

## Phase: Audit (once per topic)

Ask the user, in one pass, to answer freely:

1. What do you want to be able to do, concretely, when this is done? (Not the general subject — the specific outcome.)
2. What's the timeframe or deadline, if any?
3. What's your current level — total beginner, some exposure, rusty, etc.?

From the outcome, derive a short kebab-case topic slug (e.g. "finish one small oil painting in two weeks" → `oil-painting`). Confirm the slug with the user if it's not obvious.

Create `~/aspire/<topic-slug>/audit.md`:

```md
# Audit — <topic>

**Outcome:** <verbatim outcome>
**Timeframe:** <timeframe>
**Current level:** <level>
**Audited:** <date>
```

Proceed to Source.

---

## Phase: Source (once per topic, batch — runs for every unit on the map)

1. Using the audit, generate an ordered list of sub-skill units. Each unit gets: a short title, a kebab-case slug, and a tag of `theory` or `practice` (theory = understand something; practice = hands/voice/body reps needed). Keep units narrow — sized to be learnable in one sitting, not a whole book's worth.
2. Write `~/aspire/<topic-slug>/map.md`:

```md
# Map — <topic>

**Outcome:** <from audit.md>

- [ ] 01 · <unit-title> (theory) — to-source
- [ ] 02 · <unit-title> (practice) — to-source
...
```

3. Before sourcing anything, check what research tooling is actually available this session (a custom knowledge-base/RAG MCP, Perplexity MCP, etc. — check the available tools, don't assume). Decide a priority order and use it for every unit rather than reaching for WebSearch by default:
   1. **A custom/internal knowledge-base or RAG tool, if one exists** — check it first (list what's indexed, then query it). It may already hold vetted material specific to the user's context, at no query-quota cost.
   2. **Perplexity (or similar research MCP), if available** — for actual synthesis/research on the open web. Respect that tool's own quota rules (e.g. prefer its cheapest/quickest query mode; don't spend premium-model or deep-research calls on a simple resource lookup).
   3. **WebSearch** — use this when neither of the above exists, or when the lookup is objectively better served by a plain search (e.g. finding a specific official-docs URL needs no synthesis), or after the other tools turned up nothing relevant.
4. For **each** unit, in order:
   - `mkdir -p ~/aspire/<topic-slug>/units/to-source/<unit-slug>/` and write `meta.md` (title, tag, order number).
   - Find one or two solid, specific resources for that unit — not the topic in general — using the priority order above.
   - Write `sources.md` inside the unit folder (resource links/titles + one line on why each was picked).
   - `mv` the unit folder from `units/to-source/` to `units/to-probe/`.
   - Update its line in `map.md` (status → `to-probe`).
5. Once every unit is sourced, tell the user the map is ready and ask which unit to start with (default: unit 01).

---

## Phase: Probe (per unit — start of the loop)

The unit's folder is in `units/to-probe/<unit-slug>/`.

1. Read `meta.md` to see the unit's title and tag.
2. Generate 3–5 questions (or, for a `practice` unit, describe a small concrete task) that would reveal whether the user already knows this — *before* they've touched the sourced material.
3. Ask the user to answer now, cold, without looking anything up. It's fine if the answers are wrong or incomplete — that's the point.
4. Write `probe.md`:

```md
# Probe — <unit-title>

## Baseline (cold, pre-learning)
1. <question> → <user's answer>
...
```

5. `mv` the unit folder to `units/ingesting/`. Update `map.md` status.
6. Proceed directly to Ingest — don't make the user re-invoke the skill for this.

---

## Phase: Ingest (per unit)

The unit's folder is in `units/ingesting/<unit-slug>/`.

1. **Sources first, not explanation first.** Immediately after Probe, surface the exact links from `sources.md` and ask the user to go read/study them independently — do not summarize or pre-digest the material yet. Log this handoff in `ingest-notes.md` (what was handed over, when). For a `practice` unit where there's nothing to "read" ahead of reps, skip straight to step 3.
2. Wait for the user to come back. When they do, this becomes a live tutoring session built around what they actually took from the source, not a replay of it: ask what stood out, answer questions they raise, and correct misconceptions against what the baseline in `probe.md` revealed. This is refinement, not a link dump and not a lecture.
3. Log the session as it happens in `ingest-notes.md`: key points in the user's own words (or yours, if they're rehearsing verbally), questions asked and answered, anything they got stuck on.
4. If the unit is tagged `theory`: before closing the session, have the user (or you, walking them through it) explain the concept back as if teaching someone with zero background. Wherever that explanation breaks down is the actual gap — note it explicitly in `ingest-notes.md` and keep going until it holds.
5. If the unit is tagged `practice`: this is not optional reading. Guide the user through actual reps of the sub-skill, just past their current ability, with feedback after each attempt. If there's more than one distinct practice element in the unit, mix/interleave them within the session rather than drilling one to exhaustion. Log rep count and what was corrected in `ingest-notes.md`.
6. When the session is done (user says so, or the material's covered), `mv` the unit folder to `units/to-retrieve/`. Update `map.md`.
7. Tell the user the unit is ready for Retrieve, and ask if they want to run it now or later. If now, proceed directly.

---

## Phase: Retrieve + Endure (per unit — closes the loop)

The unit's folder is in `units/to-retrieve/<unit-slug>/`.

**Retrieve:**

1. Re-ask the *exact* questions/task from `probe.md`, cold, no looking back at `ingest-notes.md`.
2. Compare the new answers to the baseline side by side. Write `diff.md`:

```md
# Diff — <unit-title>

| Probe question | Before | After |
|---|---|---|
| ... | ... | ... |

**What changed:** <plain summary of the delta>
```

3. Show the user the diff directly — this comparison is the reward signal, don't skip presenting it.

**Endure:**

4. Write `summary.md`: a short, durable note of what was actually learned in this unit, in plain language, referencing where it came from (`sources.md`).
5. Append a short block to `~/aspire/<topic-slug>/knowledge.md`:

```md
## <unit-title> — endured <date>
<2-4 sentence summary>
Source: units/endured/<unit-slug>/
```

6. `mv` the unit folder to `units/endured/`. Update `map.md` (check the box, status → `endured`).
7. If units remain in `to-source` or `to-probe`, ask if the user wants to continue to the next one now. If this was the last unit, congratulate them and show the full `knowledge.md`.

---

## Rules

- Never skip Probe before Ingest, even if the user wants to "just start reading" — the cold baseline is what makes Retrieve meaningful later. If they push back, explain why in one sentence and let them override.
- In Ingest, don't explain a `theory` unit's material before the user has had a chance to read the sourced links themselves — hand those over first and wait. Jumping straight to your own synthesis turns Ingest into a lecture instead of refinement, and the user loses the independent-engagement signal that makes the later teach-back meaningful.
- Never let a unit skip Retrieve — an `ingesting` unit that the user declares "done" still needs the diff before it can be marked `endured`.
- Don't run Source for units the user hasn't asked to include yet — Source only processes what's on the map.
- If the user wants to add a unit mid-topic, append it to `map.md` and create it directly in `units/to-source/`, then offer to source it now.
- Keep `map.md` and the actual folder locations in sync at every transition — it's the fast-glance status view, don't let it drift.
- If resuming and a unit's files look incomplete for its stated folder state (e.g. sitting in `ingesting/` with no `probe.md`), fix the inconsistency before proceeding — ask the user what actually happened if it's ambiguous.
- In Source, don't default to WebSearch out of habit. Check what research MCP tools this session actually has (custom RAG/knowledge-base tools, Perplexity, etc.) and prefer those per the priority order in Phase: Source — WebSearch is the fallback, not the default.
