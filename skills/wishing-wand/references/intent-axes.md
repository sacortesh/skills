# Intent Axes

Four questions to run every wish through, after the Da Rules check. Not a form to fill out loudly — read the wish, make a call on each axis, and only surface a question to the user when a call is genuinely ambiguous *and* the two possible answers would lead to different output.

## Axis 1: Resource gap

What does the user actually have already, versus what's structurally missing?

- **Plan-shaped gap** — they have the resources (time, money, skill, access) and just lack a concrete plan or the confidence to start. → a Direct Grant (the plan itself) is probably sufficient.
- **Resource-shaped gap** — something concrete is missing (capital to invest, a credential, physical access, a skill that takes real time to build). → the plan has to include acquiring the missing resource, or the wish needs reframing around what's reachable now.
- **Structural/relational gap** — the blocker is someone else's behavior, a living situation, a system they don't control (e.g. "I want time for gaming" but they share a house with someone who has different expectations). → this is not a scheduling problem, it's a boundaries/communication problem, and the plan has to address the actual constraint, not pretend it's a time-management issue.
- **Confidence/fear-shaped gap** — the resources and the plan both exist, but the person hasn't started. Real barrier data (`references/gap-research.md`) found "fear of defeat/lack of confidence in self" (27.5%) and "waiting to feel ready" (20.1%) among the most commonly cited reasons wishes don't get acted on — distinct from not having a plan at all. → the Direct Grant here is a *first step small enough to remove the excuse to wait*, not a more detailed plan (a bigger plan can actually make this gap worse).
- **Orientation-shaped gap** — the person doesn't know what to actually do, independent of confidence or resources ("not knowing exactly what to do to get there" — 20.0% per the same data). → the Direct Grant is a map/sequence, and confidence-building isn't the bottleneck.

This axis is often where the *ambiguity worth asking about* lives — e.g. "I want to be rich" resolves completely differently depending on whether the user has capital to invest, income to redirect, or neither. It's also worth a quick check against which of these five shapes actually matches before defaulting to "give them a plan," since a plan is the fix for exactly one of them.

## Axis 2: True desire

Is the stated wish the terminal goal, or an instrumental stand-in for one of a small set of underlying needs? Borrowed from Self-Determination Theory (autonomy, competence, relatedness) plus two practical additions (safety, meaning) — deliberately a short, stable list so this doesn't turn into freelance amateur psychoanalysis on every request.

| Underlying need | What it looks like surfacing as a wish |
|---|---|
| **Autonomy** — wanting control over one's own choices/time | "I want to be rich" (freedom from a boss), "I want time for gaming" (control over how a day is spent) |
| **Competence** — wanting to feel effective/capable | "I want to learn X," "I want to be good at Y" |
| **Relatedness** — wanting connection/belonging | wishes about being liked, being missed, romantic wishes, wanting to matter to a specific person |
| **Safety** — wanting security against a real or feared loss | "I want to be rich" (buffer against precarity), health-anxiety-adjacent wishes |
| **Meaning** — wanting one's life/work to matter | career wishes, legacy wishes, "I want to make an impact" |

Same surface wish can map to different needs for different people — this table is a lookup to check against, not a lookup to assert. When the mapping is ambiguous and would change the output (plan vs. redirect vs. both), that's a candidate for one of your 1-2 clarifying questions. When it's not ambiguous — most of the time — just proceed on the most likely read and say so in passing.

**Worked examples from the brief:**
- *"I want to be rich"* — check resource gap first (do they have capital/income/skills to invest, or not?). Then check true-desire: is the urgency proportionate to a real financial gap, or does it sound more like safety/autonomy/esteem anxiety? If the latter, this is also Da Rules category 6 (identity wishes) — pair a real financial starting plan with a light redirect toward examining the anxiety directly.
- *"I want time for gaming"* — check resource gap: is this really about their own schedule (plan-shaped), or about someone else's expectations of their time (structural/relational)? That's the one genuinely bimodal fork worth a forced-choice question if it's not clear from context.

**A cross-check worth knowing about:** real research converges from two independent directions — a 5,000-person consumer survey and decades of hospice-patient testimony (Bronnie Ware) — on *staying connected to people* and *living authentically/following one's own path* being among the most commonly regretted gaps, ahead of money or achievement (`references/gap-research.md`). If a wish's true-desire read is genuinely unclear, and it plausibly touches relatedness or autonomy, those two are worth weighting a little higher than a snap read might suggest — not because every wish is secretly about connection or authenticity, but because those are the two places people most reliably discover, in hindsight, that they under-invested.

## Axis 3: Actionability

- **Now-producible** — the deliverable is something you can just write/generate/compute in this conversation (a plan, a document, code, a comparison, a schedule, a rewritten bullet point).
- **Requires a real-world process** — satisfying the wish requires the user (or someone else) to do something repeatedly over real time that no amount of planning substitutes for (get fit, get sober, learn a skill to fluency, repair a relationship, grieve). See Da Rules category 5 — these still get a Direct Grant (the starting plan), but be honest that the plan isn't the wish fulfilled.

## Axis 4: Delegation

Who is actually the right executor, once you know what's needed?

- **You, here, now** — most "now-producible" cases.
- **Another skill already in this environment** — check before writing something from scratch. Known dispatch targets: `learning-aspire` (sustained learning goals), `book-hunt` + `book-shopping` (reading material on a subject), `cv-builder-interview` (turning experience into career narrative), `virality-formula` (whether a content/creative idea has real traction), `impeccable` / `avangarde-frontend-architect` (building or critiquing an actual interface). See `routing-guide.md` for how to hand off to one of these mid-response.
- **An external AI tool/model** — the task needs a capability this conversation doesn't have (image/video generation, a different context window, a specialized agent). → Handout.
- **A human professional or process** — therapist, financial advisor, lawyer, doctor, coach, or just another named person (a mentor, a friend). → Redirect, possibly with Handout-style prep material (see Da Rules category 4).
