# Phase 1 — Capturing Requirements

The goal is a brief that names a real subject, a real audience, and a real
job — not a generic "modern, clean, responsive" placeholder. Ground this in
goal-directed design (name the persona's goal, not their tasks — the core
move from Cooper et al.'s *About Face*) and in mental-model thinking (does
the interface match what the user already expects, per Norman's *The
Design of Everyday Things*) before writing the brief.

## Interview questions

Ask what the brief doesn't already answer — don't invent these silently:

1. **Subject and industry.** What is this, concretely? A dashboard for
   financial analysts and a toy for 8-11-year-old girls demand entirely
   different visual and structural choices — identify the real subject
   before designing anything.
2. **Audience and their goal.** Not a demographic — a goal-directed persona
   (About Face): what is this person trying to accomplish, and what do they
   already know or expect (Jakob's Law) coming in?
3. **Primary job-to-be-done.** The one thing the product must let someone do
   well. Everything else is secondary until this is nailed down (Pareto:
   the 20% of features that drive 80% of use).
4. **Content inventory.** What real content exists or will exist — copy,
   data, media? A design brief without real content produces templated
   copy; ask for actual content or commit to writing placeholder content
   that's specific to the subject, not generic lorem-ipsum-adjacent filler.
   Placeholder or real, copy still has to clear
   `references/taste-checklist.md`'s copy tells: no filler verbs
   ("Elevate," "Seamless," "Unleash"), no generic names ("John Doe,"
   "Acme"), no fake-precise numbers unless sourced from real data.
5. **Primary rendering surface.** Where will this actually be used — mobile
   web (phone as the primary device), desktop web (large screens, dense
   information, mouse/keyboard as primary input), truly responsive-agnostic
   (a genuine even split), embedded/kiosk/TV, or wrapped-native
   (Electron/Tauri/Capacitor/React Native Web)? This isn't a decorative
   detail: it decides which breakpoint gets designed and tested first
   (Phase 3's breakpoint strategy), what's physically possible for
   interaction (hover states don't exist on touch; kiosk/TV needs larger
   targets and remote-friendly focus order per Fitts's Law), and caps the
   motion budget (a phone has to budget for battery and perf; a kiosk on a
   dedicated screen doesn't). Don't default to "responsive, works
   everywhere" without naming which surface is actually primary — treating
   every surface as equally primary is how none of them end up well-suited.
6. **Constraints.** Framework preference (defaults to React — see Phase 5),
   styling preference if already known (Tailwind vs. CSS — Phase 6 still
   makes the final call), performance/accessibility requirements, existing
   brand or design-system constraints.
7. **Behavioral requirements, if relevant.** If the product needs to build a
   habit or change behavior (subscription products, health apps, learning
   tools), name the target behavior explicitly and check it against
   *Hooked* and *Designing for Behavior Change* — this becomes a Phase 7
   journey scenario later.
8. **Irreducible complexity (Tesler's Law).** What complexity does this
   domain inherently have, and who should absorb it — the system, or the
   user? Decide this now; it shapes navigation (Phase 2) and component
   design (Phase 4) later.

## Output: requirements brief

Write to `DESIGN.md` under a `## Requirements` section (create the file if
it doesn't exist yet — this is the first phase to write to it):

```markdown
## Requirements
### Subject
### Audience & primary goal
### Primary job-to-be-done
### Content inventory
### Primary rendering surface
### Constraints (framework, styling, a11y, perf, brand)
### Behavioral requirements (if any)
### Complexity ownership (system vs. user)
```

Confirm this brief with the user before moving to Phase 2 — later phases
read this section back instead of re-deriving it, so an unconfirmed
assumption here compounds.
