# Routing Guide

Once Da Rules is checked and the four axes are read, decide which output mode(s) apply. They combine — most non-trivial wishes get more than one.

## Direct Grant

Produce the actual thing now: a plan, a comparison, a document, code, a rewritten piece of text, a decision framework. This is the default when the resource gap is plan-shaped and the actionability is now-producible.

Keep it as concrete as the wish allows — a genie that grants "you'll be rich" with a vague motivational paragraph hasn't granted anything. If the wish is "I want to be rich" and the resource gap is plan-shaped (they have income/capital to redirect), the Direct Grant is an actual starting plan with numbers and next actions, not a lecture on the value of hard work.

Check `references/domains/` for a file matching the wish's topic before improvising from scratch — each one carries real, differentiated frameworks distilled from actual books, not generic advice:

| Domain file | Covers |
|---|---|
| `finance.md` | Wealth/money wishes — which framework (debt-first, conscious-spending, pay-yourself-first, behavior-check) matches the resource-gap read |
| `psychology.md` | Habit-shaped wishes, self-worth/identity wishes, confidence/social-anxiety wishes, wishes needing another person's cooperation |
| `learning.md` | Learning-a-skill wishes, including when to dispatch to `learning-aspire` vs. handle inline |
| `relationships.md` | Romantic/intimacy wishes, family/friends time wishes, reconciliation wishes |
| `career.md` | Job/work-life-balance/dream-job/career-change wishes |
| `health.md` | Physical fitness/wellbeing wishes |
| `meaning.md` | Legacy, contribution, altruism, "make a difference" wishes |
| `experience.md` | Travel, hobbies, "follow my passion," bucket-list wishes — mostly a router into the file that actually has the mechanism |

These were sourced by mining this user's own book library and real research on what people actually wish for (`gap-research.md`) — see `extending.md` for how to add or refresh one.

## Redirect

Name the real category of help, in one line, with the one-line why. Two flavors:

**Internal redirect** — the right executor is another skill already in this environment. Don't write a smaller, worse version of what that skill does; just say what you're dispatching to and why, then either hand off directly (invoke the skill within the same response if it's cheap and clearly right) or tell the user to invoke it themselves if it's a bigger, separate undertaking (e.g. `learning-aspire` is stateful and multi-session — point at it rather than trying to run its whole protocol inline).

Known internal targets (extend this list in `extending.md` as the environment's skill set grows):
| Wish shape | Target skill |
|---|---|
| Wants to learn a skill/topic and actually retain it, not just get a syllabus | `learning-aspire` |
| Wants book recommendations to learn or explore a subject | `book-hunt` (then `book-shopping` to actually acquire them) |
| Wants help turning experience into a resume/CV | `cv-builder-interview` |
| Wants to know if a content idea, video, or post will land | `virality-formula` |
| Wants to design, critique, or build an actual interface | `impeccable` or `avangarde-frontend-architect` |

**External redirect** — the right executor is a human professional, process, or community that doesn't have a skill here (therapist, financial advisor, doctor, lawyer, a specific kind of support group, a mentor). Name the *type* clearly enough to act on ("a CBT-oriented therapist," not just "therapy"; "a fee-only fiduciary financial planner," not just "a financial guy") and say briefly why that type fits what you read on the intent axes.

## Handout

Write a structured brief when the right executor is an external tool/model/professional that needs a clean, self-contained spec to act on — not just a pointer, an actual document they (or the user acting as courier) can use directly. Use `assets/handout-template.md`. Save it to `~/Documents/Wishing Wand/` (create the folder if needed — see `SKILL.md`'s Output shape section), tell the user where it landed and who it's for, and don't also paste the full contents inline — that defeats the terseness the genie framing asks for.

Good candidates for a Handout:
- Prep material for a professional appointment (symptom timeline for a doctor, questions for a financial advisor, documentation for HR/legal).
- A brief for a different AI tool/model with a capability this conversation doesn't have (image/video generation, a specialized coding agent, a different context window that needs the backstory this conversation already has).
- A spec for hiring someone (a freelancer brief, a commission brief for an artist/editor/contractor).

Don't produce a Handout when a Direct Grant would just do the job — the Handout is for when *someone or something else* has to be the one to execute, not a formatting exercise for content you could have written yourself.

## Research priority: baked-in tenets, then the open web, then a local knowledge base if one exists

This skill is meant to work the same way in any environment, including ones with no extra tools connected. So the order is:

1. **The domain reference files first.** `references/domains/{finance,psychology,learning}.md` are the default source for anything in those three areas — they're condensed from real, specific books, not generic training-data platitudes, and they don't require any tool call to use.
2. **A live web search second**, for anything current or specific the domain files don't cover — an actual local professional, today's pricing, a recent development, a topic outside finance/psychology/learning entirely. Use WebSearch or the `perplexity` MCP tools for this; it's the generally-available option regardless of what environment this skill runs in.
3. **A local knowledge-base tool, only if one happens to be available, as a bonus.** If this environment has something like an `avangarde-rag`-style MCP server connected, it's fine to check it for something unusually specific to the user's own library — but never assume it exists, never make it a required step, and never let its absence change the quality of the default answer.

Never fabricate a specific title/name/number you're not confident is real — say the category instead and offer to look one up ("a well-reviewed CBT workbook — happy to find a specific title if useful") rather than presenting a guess with the same confidence as a verified source.

## Saying which is which

Whatever combination you land on, make the seams visible in the output: a Direct Grant reads like an actual deliverable, a Redirect reads like a pointer with a reason, a Handout reads like "saved a brief to `<path>` for `<who>`." Don't let a Redirect masquerade as a Direct Grant (vague advice dressed up as a plan), and don't let a Direct Grant substitute for a Redirect the wish actually needed (a workout plan standing in for "talk to a doctor about this pain first").
