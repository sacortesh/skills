# Extending Wishing Wand

This skill is built to grow along three independent dimensions: new Da Rules, new intent-axis content, and new routing/dispatch targets. Each has its own file and its own low-friction way to add an entry — you shouldn't need to touch `SKILL.md` itself for any of these.

## Adding a new Da Rules entry

Add to `references/da-rules.md` when you notice a *pattern* of wish that keeps needing the same kind of redirect — not for a one-off. A good Da Rules entry has:

1. **Signal** — how to recognize it, written concretely enough that it doesn't require judgment calls every time (compare category 6's "urgency disproportionate to the stated goal" — a real tell, not a vague vibe).
2. **Why it's a rule** — the actual mechanism by which granting the literal wish fails or backfires. If you can't articulate this, it's probably not a real rule yet, just a hunch.
3. **Instead** — what to do, including whether a partial Direct Grant is still appropriate alongside the redirect. Most rules aren't "refuse everything" — they're "the literal ask is wrong, here's the adjacent thing that's right."

Numbering isn't meaningful — categories are matched by content, not by order. Feel free to insert a new one wherever it reads best.

## Adding a new intent-axis value or domain

`references/intent-axes.md` has one genuinely extensible piece: the true-desire table (currently autonomy / competence / relatedness / safety / meaning). Resist the urge to add rows casually — the value of that table is that it's short enough to actually hold in mind and check against. Only add a row if you've seen a category of wish that doesn't map cleanly onto the existing five and needs its own label.

If a whole *domain* keeps coming up (say, career-transition wishes, or parenting wishes) and the four generic axes feel like they're missing domain-specific texture, don't cram it into `intent-axes.md`. Instead:

1. Add a new file, `references/domains/<domain>.md`, following the pattern of the existing ones (`finance.md`, `psychology.md`, `learning.md`, `relationships.md`, `career.md`, `health.md`, `meaning.md`, `experience.md`): condensed, differentiated tenets keyed to a decision (e.g. "which framework fits which resource-gap read"), not generic advice restated. See "Sourcing a new domain file" below for how those were actually built.
2. Add one row to the domain-file table in `routing-guide.md`'s Direct Grant section — `SKILL.md` already points at `references/domains/` generically, so it doesn't need editing for a new file, only `routing-guide.md`'s index of what's in there.

## Finding out which domain files are missing in the first place

Don't just wait for a domain gap to become obvious through repeated wishes — it's worth periodically checking real research on what people actually wish for and comparing it against current domain-file coverage, the way `references/gap-research.md` was built. That file documents a real 5,000-person wish survey (Real Insurance/CoreData) plus Bronnie Ware's hospice-regret research, cross-referenced against this skill's coverage at the time — which is how `relationships.md`, `career.md`, `health.md`, `meaning.md`, and `experience.md` all got added in one pass (family/friends and experience wishes turned out to be the two highest-scoring wish categories in the real data, yet had zero domain coverage beforehand). If it's been a long time since `gap-research.md` was last refreshed, or a new large study on human desires/wishes surfaces, re-running that comparison is a legitimate way to find the next gap rather than waiting to notice it reactively.

## Sourcing a new domain file (or refreshing an existing one)

The existing domain files weren't written from general model knowledge — they were built by querying this user's own `avangarde-rag` knowledge base (via `mcp__avangarde-rag__search_knowledge_base`, at authoring time, in the conversation that built this skill) for the specific books already indexed there, and condensing genuinely substantive passages into decision-usable tenets. That's *why* they're worth more than generic advice: they're grounded in books the user has actually vetted and read, not plausible-sounding training-data recall.

This is a build-time step, not a runtime one — the shipped skill doesn't call out to that RAG (see `SKILL.md` step 5 and `routing-guide.md`'s research-priority section: it has to hold up in an environment with no RAG connected at all). But when it's time to add a new domain file, or refresh an existing one because the user's library has grown:

1. If a RAG-style knowledge-base tool is available in the authoring session, query it for the domain's core topics (the way this was done: search for each major book's central mechanism by name — "Atomic Habits identity based habits," not just "habits" — to get substantive chunks instead of index pages).
2. Distill what comes back into a **decision table or short set of named mechanisms**, each tied to a concrete "when to reach for this" condition — not a book report. A tenet is only useful here if a model reading it at runtime could immediately act on it without re-deriving the reasoning.
3. Name the source book/author inline for credibility and so a curious user can go find it, but the file's value is the condensed mechanism, not the citation.
4. Note explicit gaps ("known gap: nothing here on X") rather than stretching thin coverage to sound complete — a Redirect to a live web search is more honest than a fabricated-sounding tenet. If the RAG has nothing at all on a needed topic, that's also a legitimate signal to hand the user a short list of well-regarded real books on the subject (framed honestly as "not yet in your library" — a natural handoff to `book-hunt`/`book-shopping`) rather than distilling from thin or absent source material.
5. If no RAG or equivalent is available when refreshing, it's fine to distill from general knowledge instead — just hold it to the same bar (specific, real, decision-usable), since the whole point is quality of advice, not the source mechanism.

## Adding a new routing/dispatch target

When a new skill gets added to this environment that's a good landing spot for a class of wish, add one row to the "Known internal targets" table in `references/routing-guide.md` — wish shape on the left, skill name on the right. That's the entire integration point; `SKILL.md` already points here generically so it doesn't need editing.

When an *external* redirect category comes up often enough that you keep re-deriving the same "what kind of professional/resource" reasoning, it's a candidate for its own line in the routing guide's external-redirect guidance, or its own Da Rules entry if it's really about a hard limit rather than just a common case.

## A general note on scope discipline

The temptation with a skill like this is to keep adding rules and axes until it's trying to be a full psychology textbook. Resist that — the whole point of the four-axis structure is that it's small enough to run mentally on every wish without turning into a checklist ritual. If you find yourself wanting to add a sixth axis or a tenth Da Rules category, first check whether the new thing is actually a *new* consideration, or just a more specific instance of one that already exists (e.g. "wishes about winning the lottery" is not a new category — it's Da Rules category 6 plus Axis 1's resource-shaped gap, already covered).
