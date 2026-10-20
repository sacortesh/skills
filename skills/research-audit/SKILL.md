---
name: research-audit
description: Audits the research quality behind a written piece — article, blog post, report, essay, book chapter — checking whether claims are cited, whether citations are trustworthy (CRAP test — Current, Relevance, Authority, Accuracy, Purpose), whether key claims rest on more than one source, and whether the piece engages with disconfirming evidence or only confirms its own thesis. Use when the user wants to check research quality, verify claims, audit sourcing, fact-check a draft, or asks "is this well-researched," "check my sources," "audit this article's research," or invokes "research-audit" directly. Works with or without a RAG/knowledge-base or live web-search tool — degrades gracefully to structural-only analysis (citation presence, source diversity, one-sidedness) when no verification tool is available, and clearly labels which findings were live-verified vs. structural-only.
argument-hint: "file path or pasted text of the piece to audit"
---

# Research Audit

You diagnose the research quality behind a written piece. You do not rewrite it, and you do not grade prose craft (clarity, voice, rhythm — that's a different job). You check whether what the piece *claims* is actually *earned* by its sourcing.

## Input

A file path or pasted text. If the piece has an existing citation convention (footnotes, inline `(Author, Year)`, a bibliography, markdown links), note the format before starting — you'll need to recognize it during extraction.

---

## Phase 0 — Tool Check

Before auditing anything, check what verification tooling this session actually has (don't assume). Priority order, same reasoning as elsewhere in this skill set — a vetted local corpus outranks a live web query, which outranks nothing:

1. **A custom/internal knowledge-base or RAG tool, if one exists** — check it first (list what's indexed, then query it).
2. **Perplexity (or similar research MCP), if available** — for live verification of claims/sources on the open web. Respect that tool's own quota rules (cheapest/quickest mode first).
3. **WebSearch/WebFetch** — fallback when neither of the above exists, or for a direct lookup (e.g. confirming a cited URL actually says what the piece claims it says).
4. **None available** — say so up front, and run **structural-only mode**: you can still check citation presence, source diversity, and one-sidedness (Phases 2, 4, 6 below), but skip live source verification (Phase 3) and label every output row from this run `STRUCTURAL-ONLY — not live-verified`.

Never claim a source was verified if no tool call actually confirmed it.

---

## Phase 1 — Extract Claims

Scan the piece. Pull out every sentence that makes a factual, statistical, historical, or attributed claim — i.e. anything that could be *wrong*, as opposed to opinion, narrative, or the author's own stated experience. List them:

```
[CLAIM 1] "The average knowledge worker loses 2.5 hours per day to context switching." — Para 3
[CLAIM 2] "McCloskey argues economy of prose is a moral obligation, not just a style choice." — Para 7
...
```

Note whether each claim already carries a citation inline.

---

## Phase 2 — Citation Presence

For every claim from Phase 1 with no attached citation, flag it:

```
[UNCITED] "<claim>" — <location> — no source given
```

A claim framed as the author's own direct experience or opinion does not need a citation — don't flag those. When ambiguous, ask which it's meant to be rather than guessing.

---

## Phase 3 — Source Verification (CRAP test)

Skip this phase entirely in structural-only mode (Phase 0 fallback).

For every cited claim, verify the source using whatever tool Phase 0 selected, then score it against CRAP:

| Letter | Checks |
|---|---|
| **C**urrent | Is the source recent enough to still be valid for this claim? Flag if the field moves fast and the source is stale. |
| **R**elevance | Does the source actually address this specific claim, or just the same general topic? |
| **A**uthority | Is the author/publication/institution credible on this subject? Peer-reviewed, recognized expert, primary source — or an anonymous blog with no credentials? |
| **A**ccuracy | Does the source make its argument with real evidence and acknowledge its own limitations, or does it just assert? |
| **P**urpose | Why was this made — to inform, or to sell/persuade/promote? Does that compromise the claim being borrowed from it? |

Classify each citation:

| Status | Meaning |
|---|---|
| `CONFIRMED` | Source checked out, supports the claim, passes CRAP without major flags |
| `WEAK` | Source exists and is nominally relevant, but fails one or more CRAP checks (e.g. outdated, low-authority, promotional) |
| `MISMATCH` | Source exists but doesn't actually say what the claim attributes to it — see Phase 5 |
| `NOT FOUND` | Source couldn't be located/accessed to verify |

---

## Phase 4 — Source Diversity

For claims central to the piece's thesis (not minor supporting detail), check whether they rest on more than one independent source. A single book, single study, or single author backing a load-bearing claim is a risk — one source can be wrong, biased, or outdated with nothing to catch it.

```
[SINGLE-SOURCE] "<claim>" — only source: <source> — no corroborating source found
```

This isn't a defect in every case (some claims genuinely have one authoritative source), but it must be surfaced so the author can decide if it's acceptable.

---

## Phase 5 — Claim–Evidence Match

For every citation, don't just confirm the source *exists* — confirm it actually *supports the specific inference* the piece draws from it. A source can be real, relevant, and authoritative, and still be stretched to support more than it actually says (overgeneralizing a narrow study, citing a counterpoint as if it were agreement, etc.). Flag these as `MISMATCH` with a one-line explanation of the gap between what the source says and what the piece claims it says.

---

## Phase 6 — One-Sidedness / Confirmation-Bias Check

Read the piece's overall argument. Check: does it anywhere engage with evidence, sources, or interpretations that complicate or disagree with its own thesis — or does every cited source happen to agree with the author?

```
[ONE-SIDED] No disconfirming evidence or counterargument found anywhere in the piece.
```

This is a structural read of the whole piece, not a per-claim check — run it once, not per citation.

---

## Output — Research Quality Report

```markdown
## Research Quality Report — <title/slug>

**Mode:** <tool used for verification, or "STRUCTURAL-ONLY — no verification tool available">

### Verdict: <Rigorous / Adequate / Thin / Unverifiable>

### Verified
- [CONFIRMED] "<claim>" — <source>
...

### Needs Attention
| # | Type | Location | Issue | Action |
|---|------|----------|-------|--------|
| 1 | UNCITED | Para 3 | Statistic has no source | Verify or remove |
| 2 | WEAK | Para 5 | Source is a promotional blog, fails Authority/Purpose | Find a stronger source |
| 3 | MISMATCH | Para 7 | Cited study is about a different population than claimed | Correct the claim or find a matching source |
| 4 | SINGLE-SOURCE | Para 9 | Thesis-level claim rests on one book | Corroborate or caveat |

### One-Sidedness
<finding from Phase 6, or "No issue found — piece engages with counterevidence at <location>">
```

**Verdict scale** (pick one, state why in one line):
- **Rigorous** — claims cited, sources check out, thesis-level claims corroborated, counterevidence engaged.
- **Adequate** — mostly sound, a few WEAK/SINGLE-SOURCE flags on non-critical claims.
- **Thin** — multiple UNCITED or WEAK flags on claims the argument depends on.
- **Unverifiable** — structural-only mode, or too many NOT FOUND results to assess rigor.

---

## Rules

- Never invent a `CONFIRMED` status. If no tool call actually checked a source, the status is `NOT FOUND` or the whole run is `STRUCTURAL-ONLY`.
- Do not rewrite or remove claims/citations — only flag them. The author decides what to do with each finding.
- `WEAK` is not the same as `wrong` — a low-authority source can still be the best available for an obscure claim. Flag it; let the author judge.
- A `MISMATCH` is more serious than a `NOT FOUND` — it means the piece is actively misrepresenting a real source, not just missing one.
- Run Phase 6 (one-sidedness) even in structural-only mode — it needs no external verification, just a careful read.
- If the piece already has a citation-verification process of its own (e.g. a project-specific citation checker against a private corpus), don't duplicate its exact mechanics — this skill is for pieces that don't have one, or for a second, source-quality-focused pass on top of one that only checks "is it indexed."
