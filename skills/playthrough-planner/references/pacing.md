# Pacing: Turning Hours Into a Loop

Converting "this game takes ~35 hours" into an actual schedule fails for the same reason most habit plans fail (see wishing-wand's `psychology.md` habit-loop tenet, if that skill is present) — a plan sized for a motivated week collapses the first bad week. Two things fix that: sequencing and a floor.

## Sequencing: do missable/collectible content during the pass it belongs to

The single biggest avoidable time cost is discovering post-game that a trophy or 100%-completion item needed to happen mid-story and now requires a second playthrough. Default sequencing:

- **Main story sessions** carry side content and collectibles *in the area/chapter they're found in*, not "I'll go back for it later" — unless the game explicitly supports chapter-select/free-roam replay of earlier areas.
- **Platinum-grind content** (multiplayer hours, farming, difficulty runs) gets its own separate session type, scheduled after or alongside the main pass, not interleaved — grinding mid-story just slows the story down without saving any time.
- **Postgame-only content** (NG+, superbosses, DLC) stays its own phase at the end, only scheduled if it's inside the chosen stop line.

## The weekly loop template

A default 3-session/week loop (adjust session count to the stated time budget, keep the *shape*, not necessarily 3):

| Session type | What it advances | Cadence |
|---|---|---|
| Main story | Story progress + area-local side content/collectibles | Most sessions |
| Side/collectible catch-up | Anything missed, exploration, non-missable extras | ~Weekly |
| Platinum-grind (only if platinum is the recommendation) | The specific grind/online/difficulty trophies | Its own slot, not blended into story sessions |

## The floor: a minimum-viable session for bad days

Borrowing the tiny-habits shrink-the-behavior move: define the smallest session that still counts as "showed up" — e.g. 15 minutes of story progress — for the days motivation is low, rather than an all-or-nothing "full session or it doesn't count" that produces the two-week dropout pattern. A day that only hits the floor still keeps the loop alive; that matters more than any single session's length.

## Session-level detail: name the actual missions, not a chapter-arc summary

A loop that just says "main story session" three times a week is a schedule, not a plan. But a one-line vibes summary per chapter ("story escalates, new district opens up") is *also* too generic once the user has asked for mission-level detail — confirmed directly: a chapter-arc-summary version of this section was rejected as "too generic... that is not my wish." The bar is: each session line names the **exact mission and side-quest titles** to do that session, not a paraphrase of what happens.

To get real names, don't summarize the walkthrough prose — look for the walkthrough's own list/index structure, which is usually more compact and reliable than reconstructing names from narrative text:
- Many long-form guides (GameFAQs-style) put a bulleted mini table-of-contents right under each chapter heading (e.g. lines starting with `o ` or `-`) naming that chapter's missions in order — pull the list from there.
- If the page is too large for a single fetch/read, use the browser tool's `javascript_tool` to run a targeted extraction (regex for the chapter-heading pattern, then grab the bullet lines immediately following each heading) rather than trying to read the whole page as prose — this stays well under output-size limits and gets cleaner data than prose-summarizing would.
- Distinguish real named side quests (unique, one-off, often tied to a specific karma/choice branch) from generic repeatable side-activity *types* (a game may have "stop a mugging"/"defuse a bomb"-style filler that repeats indefinitely rather than a finite named quest) — list the former by name per session; for the latter, say plainly that they're ambient/optional rather than inventing a fake finite checklist for them.
- If a real per-chapter mission list can't be found for a game, say so openly rather than inventing mission names.

## Milestone checkpoints

Tie 2-4 checkpoints to % of Main Story hours (e.g. 25%/50%/75%/100%) rather than calendar dates alone — calendar dates drift, but "am I roughly a quarter through the main story" is a check the user can self-assess mid-session and adjust pace against.
