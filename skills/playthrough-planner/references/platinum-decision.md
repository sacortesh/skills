# Platinum vs. Completion Decision Framework

The question "should I go for platinum/100%?" isn't really a difficulty question — it's a cost-and-motive question. This checks both.

## Researching it

Start with WebSearch — PSNProfiles/TrueTrophies/TrueAchievements/PowerPyx-style sites usually surface a usable **roadmap** block or completion percentage straight from the search snippet, no fetch needed. If you need the full page (the detailed trophy list, or the roadmap block itself), try WebFetch next — but expect it to 403 on some of these sites (GameFAQs almost always; PSNProfiles often). When that happens, fall back to the browser tool (`navigate` + `get_page_text`) to render the page live instead. The same chain applies to walkthrough/chapter-guide pages (gamepressure/IGN/GameFAQs-style) when the main flow needs session-level detail for the pacing plan.

## Cost signals (look these up, don't guess)

If the game has a PSNProfiles-style **roadmap** block (most guide pages open with one — see "Researching it" above for how to get it), that single block usually answers most of the items below at once: estimated platinum difficulty (out of 10), estimated hours to platinum, minimum number of playthroughs required, # of missable trophies, # of glitched trophies, and whether difficulty setting affects any trophies. Look for it first before reconstructing the signals below one by one.

1. **Community completion rate.** PSNProfile/TrueTrophies/TrueAchievements publish the actual % of players who finished. Under ~5-10% is a real signal — it usually means at least one of the factors below is in play, not that the game is simply "hard." Above ~20-30% usually means the trophy list is reasonably grindable by anyone who finishes the main content.
2. **Missable trophies without chapter select.** If trophies can be permanently locked out mid-playthrough and the game has no chapter-select/checkpoint-replay feature, platinum effectively requires either meticulous mid-playthrough attention or a second full playthrough. This is the single biggest hidden time-cost most people don't budget for.
3. **Online/multiplayer-gated trophies.** Check whether the servers are still up and likely to stay up. A platinum that depends on a live population or a company's servers is a platinum with an expiration date — worth naming explicitly, especially for older or niche games.
4. **RNG/grind-gated trophies.** Rare drops, grind-heavy currency/level requirements, or "play N hours of multiplayer" trophies cost calendar time, not skill. These are the ones that blow up the hour estimate from step 2 of the main flow the most.
5. **Difficulty/skill-gated trophies.** Hardest-difficulty or no-hit/no-death runs cost skill-building time, not just hours — worth flagging as a different *kind* of cost (practice, frustration tolerance) than the others, which are mostly time cost.

## The motive check

Cost alone doesn't answer the question — plenty of people happily eat a 40-hour grind for a game they love. The actual fork:

- **Is the platinum itself the fun** (mastering the combat, exploring every corner, genuine attachment to the game)? Then the cost signals above are just planning inputs, not a reason to stop.
- **Or is it a collector-completionist compulsion** — "I always platinum games I start," "I'd feel like I wasted it if I don't 100% it," a felt obligation rather than a pull toward the specific content? This is the maximizer pattern (Schwartz — also covered in the wishing-wand `experience.md` domain file for hobby-selection): maximizers who chase the objectively "complete" outcome end up *less* satisfied and more prone to regret than people who define "good enough" and stop there, even when the maximizing effort produces a marginally better outcome on paper.

If the honest answer leans toward the second, the right output isn't "here's your platinum grind schedule" — it's naming a **stop line**: a specific, concrete definition of "done" that isn't platinum (e.g. "main story + all story-relevant side content, skip the multiplayer grind trophies") and treating that as the actual completion target, same move as the satisficer fix elsewhere in this skill set.

## What the plan should state explicitly

Whichever way it lands, the output plan names:
- The recommendation (platinum / full completion without the worst-offender trophies / main+extras only / main story only)
- The specific cost signals that drove it (not just "it's hard")
- The stop line — the concrete definition of done, so "should I keep going" isn't re-litigated every session
