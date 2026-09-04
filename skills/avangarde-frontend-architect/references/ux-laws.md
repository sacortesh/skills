# UX Laws Checklist

Twenty usability/psychology laws to check every design or architecture
decision against. Cite the specific law when it justifies a choice — "big
primary button, alone, per Fitts's + Von Restorff" is a real design
rationale; "looks good" is not. Source: user's own note summarizing a
@adam_ha_yes reel ("20 UX Laws to tell Claude for better Design").

1. **Hick's Law** — Decision time grows with the number/complexity of
   options. Reduce visible choices, group related ones, use progressive
   disclosure.
2. **Fitts's Law** — Time to reach a target depends on its size and
   distance. Make important buttons large and close; touch targets ≥44px.
3. **Jakob's Law** — Users expect your product to work like the ones they
   already know. Don't reinvent standard patterns without a reason.
4. **Law of Proximity** — Elements placed near each other read as a group.
   Use spacing to group and separate, not just borders or lines.
5. **Miller's Law** — Working memory holds ~7 (±2) items. Chunk long lists:
   phone numbers, wizard steps, menus.
6. **Doherty Threshold** — Interaction feels fluid when the system responds
   in <400ms. Give immediate feedback: skeletons, optimistic UI.
7. **Von Restorff Effect (isolation)** — The item that looks different gets
   remembered. One clearly distinct primary CTA per screen.
8. **Minimize Target Distance** — Shorten the cursor/finger travel between
   related actions (a corollary of Fitts's).
9. **Serial Position Effect** — The first and last items in a list are
   remembered best. Put key actions at the start or end of menus.
10. **Peak-End Rule** — An experience is judged by its peak moment and its
    ending. Invest in success moments and closing/final states.
11. **Zeigarnik Effect** — Unfinished tasks stick in memory. Use progress
    bars, onboarding checklists, "1 step left" nudges.
12. **Law of Prägnanz** — The eye resolves ambiguous shapes to the simplest
    interpretation. Keep layouts clean with recognizable forms.
13. **Law of Similarity** — Similar-looking elements read as related. Keep
    visual consistency across things of the same class.
14. **Uniform Connectedness** — Elements visually joined (lines, shared
    containers, shared background) read as more related than elements that
    are merely close together.
15. **Tesler's Law (conservation of complexity)** — Every app has irreducible
    complexity; someone has to absorb it. Make the system absorb it, not the
    user.
16. **Postel's Law (robustness)** — Be liberal in what you accept, precise in
    what you emit. Tolerant inputs (date formats, stray whitespace), clear
    outputs.
17. **Aesthetic-Usability Effect** — Designs perceived as beautiful are
    perceived as more usable, and their flaws are forgiven more readily.
18. **Parkinson's Law** — Work expands to fill the time available. Sensible
    defaults, autocomplete, and deadlines speed tasks up.
19. **Occam's Razor** — Between two designs that work, the simpler one wins.
    Keep removing elements until removing one more would break something.
20. **Pareto Principle (80/20)** — 80% of usage comes from 20% of features.
    Optimize that minority; de-emphasize or hide the rest.

## Where these apply most

- **Phase 1 (requirements)**: Tesler's, Pareto — scope what the system
  absorbs vs. the user, and which 20% of features actually matter.
- **Phase 2 (navigation)**: Hick's, Miller's, Jakob's, Serial Position —
  chunking, familiar patterns, placement of key nav items.
- **Phase 3 (themes)**: Aesthetic-Usability, Prägnanz, Similarity — cohesive,
  simple, consistent visual language.
- **Phase 4 (components)**: Fitts's, Von Restorff, Proximity, Uniform
  Connectedness — sizing, grouping, and isolating interactive elements.
- **Phase 6 (styling)**: Postel's, Occam's — tolerant, simple systems over
  clever, brittle ones.
- **Phase 7 (journeys)**: Doherty, Peak-End, Zeigarnik — the scenarios you
  write should test response time, closing states, and progress signaling.
