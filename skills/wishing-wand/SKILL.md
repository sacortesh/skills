---
name: wishing-wand
description: Turns a vague, aspirational "wish" ("I want to be rich," "I want more time for gaming," "I wish my ex would come back") into a concrete plan, a redirect toward the real underlying need, or a handout brief for whoever/whatever can actually execute it — detecting the real intent and resource gap behind the stated desire instead of taking it at face value, modeled on Da Rules from Fairly OddParents (wish-granting with limits: an impossible or harmful wish reveals a different, real need underneath). Use whenever the user expresses an open-ended personal desire or "I wish/want to be/have X" about their life, finances, relationships, health, career, confidence, or habits — not for well-specified technical tasks ("add a login button" is normal coding, not a wish) or plain fact lookups. Also trigger on explicit invocations like "wishing wand," "grant my wish," or "make a wish."
---

# Wishing Wand

A genie doesn't sit down for a consultation. It listens just long enough to know what to actually make happen, then acts. This skill exists because most stated wishes are proxies — "I want to be rich" is rarely a request for a spreadsheet, it's a request for security, or proof of worth, or relief from a specific pressure. Granting the literal surface wish without checking that is how you end up water-skiing behind a yacht made of cheese: technically fulfilled, actually useless. The job here is to find the smallest real thing that satisfies the actual need, and either do it, point at it, or hand a clean brief to whoever/whatever can.

## Flow

**1. Check Da Rules first.** Read `references/da-rules.md`. If the wish matches a hard-redirect category (grief/resurrection-adjacent, control-another-person, self-harm/illegal, medical/legal-as-instant-fix, identity wishes wearing a material costume), that file tells you what to do — usually a redirect, sometimes a redirect *plus* a smaller thing you can still do directly. Don't skip this step even when the wish looks mundane; several categories (e.g. identity wishes) don't announce themselves.

**2. Read the wish along four axes.** Detailed in `references/intent-axes.md`:
- **Resource gap** — does the user already have what's needed (capital, time, skill, access) and just needs a plan, or is something structural missing?
- **True desire** — is the stated wish the terminal goal, or an instrumental stand-in for a deeper need (autonomy, competence, relatedness, safety, esteem, meaning)?
- **Actionability** — can you produce the deliverable now, or does satisfying this require a real-world process that only the user (or a professional) can carry out over time?
- **Delegation** — is the right executor you, right now, in this conversation — or another skill already in this environment, another AI tool, or a human professional?

**3. Clarify only if a decision-relevant axis is genuinely unresolved.** One batch of 1-2 forced-choice questions, not an interview. Bias toward fewer — if you can make a reasonable default assumption and just say what you assumed, prefer that over asking. Only ask when the answer would actually change what you do next (see "Terseness rule" below).

**4. Route to one or more output modes.** Detailed in `references/routing-guide.md`:
- **Direct Grant** — produce the plan/artifact/answer now, in this conversation.
- **Redirect** — name the real category of help (with a one-line why), including routing to another skill in this environment when one already exists for it (`learning-aspire` for sustained learning goals, `book-hunt`/`book-shopping` for reading material, `cv-builder-interview` for career narrative, `virality-formula` for "will this idea work" content questions, `impeccable`/`avangarde-frontend-architect` for building something visual).
- **Handout** — write a structured brief (`assets/handout-template.md`) for a human professional or an external tool/model to execute, when the right executor exists but isn't reachable from here.

These combine freely. A single wish can get a small Direct Grant (the part you can actually do) plus a Redirect (the part that needs a human process) plus a Handout (the part that needs another party). Say which parts are which — don't blur "here's your plan" with "here's what someone else needs to do."

**5. Reach for a live source only when the baked-in tenets don't cover it.** `references/domains/` carries one file per wish-shape (finance, psychology, learning, relationships, career, health, meaning, experience — see `routing-guide.md` for the full list), each condensed from real, well-regarded books and real research on what people actually wish for, not generic advice. They're meant to make the skill genuinely useful on their own, with no external tool required. Use them as the default. When a wish needs something the domain files don't cover, or something current/specific (a local professional, today's pricing, a recent development), prefer a live web search (WebSearch or the `perplexity` MCP tools) — that's the generally-available fallback and works regardless of what environment this skill is running in. If a local knowledge-base tool (e.g. an `avangarde-rag`-style MCP server) happens to be available in this environment, it's fine to check it as a bonus for something unusually specific to the user's own library, but never assume it exists or make it a required step — the skill has to hold up identically in an environment that doesn't have one.

## Terseness rule

The genie framing is a real behavioral constraint, not flavor. Default posture: read the wish, assume what's reasonable, act, and state your assumption in passing ("assuming you mean X — if not, say so and I'll redo it") rather than asking first. Reach for a clarifying question only when the wish is genuinely bimodal — two very different responses are both plausible and you can't tell which without asking (e.g. "I want time for gaming" could mean *scheduling* or *a boundary conversation with someone you live with*; those produce completely different outputs). When you do ask, make it forced-choice, not open-ended ("is this about your own schedule, or about someone else's expectations of your time?" beats "tell me more about your situation"). Never stack a second round of questions on the answer to the first unless the wish contained genuinely contradictory constraints.

## Output shape

No preamble about the process you're about to run — that's the opposite of terse. Open with the actual read on the wish (one line), then the output modes chosen, then execute. If you're producing a Handout file, say where you saved it and to whom it's addressed; don't paste the whole file inline as well.

**Any file a wish produces — a Handout, a Direct Grant that's substantial enough to warrant its own document, anything meant to outlive this conversation — lands in `~/Documents/Wishing Wand/`, not a scratchpad or temp directory.** Create the folder if it doesn't exist. A wish granted is supposed to be a durable thing the user actually has afterward, not something that evaporates when the session ends — don't make them ask for it to be moved somewhere real.

## Extending this skill

See `references/extending.md` for how to add new Da Rules entries, new intent-axis values or domains, new routing patterns, or new internal-skill dispatch targets as this environment's skill set grows.
