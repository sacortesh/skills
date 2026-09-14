---
name: playthrough-planner
description: Given a specific video game, plans how to actually play through it — a realistic schedule broken into daily/weekly sessions, what to advance each session, and a clear recommendation on whether to chase platinum/100% or stop at a defined "good enough" completion point. Use this when the user names a specific game and asks to plan sessions for it, schedule a playthrough, decide whether to go for platinum/completionist, or turn a backlog game into an actual daily loop ("help me plan my playthrough of X," "should I platinum X," "plan my sessions for X," "I want to actually finish X this time"). Do NOT use it for game recommendations, walkthroughs/puzzle help, or general "what should I play" questions — this is for planning the *pursuit* of a game already chosen, not choosing or beating it.
---

# Playthrough Planner

Takes one input — a specific game — and produces a session plan, a daily/weekly loop, and a platinum-vs-completion call, grounded in the game's actual length/trophy data rather than a generic "just play it" answer.

## Flow

**1. Get the game and the time budget.** The game name is required. If the user hasn't stated a time budget (hours/week or a target finish date), assume a default of ~5 hours/week across 2-3 sessions and say so in passing rather than asking — only ask if the wish contains a real fork you can't default around (e.g. "I have a hard deadline" vs. "no deadline" changes the whole pacing math).

**2. Get the game's real length data.** Look up (web search — HowLongToBeat-style sources, or your own knowledge if confident and the game is well-known) three numbers: Main Story hours, Main+Extras hours, Completionist/100% hours. State the source/estimate; don't invent precise numbers for an obscure game you're not confident about — say "estimate" openly instead.

**3. Get the platinum/completion feasibility signals.** Look up the community completion/rarity percentage and whatever trophy-guide structure is available (Steam achievement stats for non-PlayStation games) — see `references/platinum-decision.md`'s "Researching it" section for the search/fetch fallback chain and known site quirks (GameFAQs and PSNProfiles often block a direct fetch). Feed whatever you get into that file to produce a *provisional* recommendation, not just the raw numbers — the plan always also carries a **Decision Point** phase (after Phase 1/main story, before any platinum-grind phase) where this gets reconfirmed against firsthand experience rather than treated as final upfront. This decision-point section is mandatory in every plan, not optional flourish.

**4. Build the loop.** Use `references/pacing.md` to turn the hour totals and time budget into a concrete weekly loop (which sessions are main story, which are side/collectible, which are platinum-grind, sequenced to avoid replaying for missables) plus a minimum-viable-session fallback for low-motivation days. If the user wants session-level detail (not just "main story session"), fetch an actual chapter/level walkthrough (gamepressure/IGN/GameFAQs-style — see `references/platinum-decision.md`'s "Researching it" section for the same search/fetch fallback chain) and group real chapters/sections into session-sized chunks with a one-line summary of what happens in each, rather than inventing generic placeholders. If the user also wants missables/collectibles tracked (not just "collect along the way"), apply `references/missables-tracking.md`'s running-fraction-counter format per session — and flag explicitly if the game structurally requires multiple full playthroughs by design (that's a designed-phase situation, not an avoidable-replay failure).

**5. Output the plan.** Fill `assets/plan-template.md` and save it to `~/Documents/Game Plans/<Game Title>.md` (create the folder if needed). State the recommendation and the "stop line" (what counts as done) up front in the conversation — don't make the user open the file to find out whether they should platinum it.

## Terseness

One game, one time-budget question if genuinely unresolved, then act — no interview about play style, genre preference, or backlog history unless the user volunteers it. State assumptions in passing rather than asking when a reasonable default exists.
