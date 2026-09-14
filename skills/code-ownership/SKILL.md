---
name: code-ownership
description: Transfers real understanding of LLM-generated code to the human who'll own it, using a Socratic question-and-answer session instead of a passive summary the human just nods along to. Framework/language/agent agnostic — works on any diff from any coding agent, not just this session. Use this whenever the user explicitly asks to "transfer ownership," "make sure I understand this code," "quiz me on what we just built," "test my understanding," or wants a comprehension check before merging/shipping/relying on AI-generated code solo. Also trigger on "run code-ownership," "/code-ownership," or requests to verify a human can maintain code they didn't personally write line-by-line. Default scope is whatever this session changed; the user can instead name a file, glob, commit range, or area of the codebase as an argument.
argument-hint: "file/glob/commit-range/description of scope, or leave blank for this session's changes"
---

# Code Ownership

An LLM writing code and a human understanding that code are two different events. This skill closes the gap between them — deliberately, before the human walks away trusting code they only skimmed.

The method rests on two findings worth knowing the *why* of, because they shape every phase below:

- **The testing effect** (retrieval-practice research, e.g. *Make It Stick*): actively retrieving something from memory cements it far better than re-reading or being told it again. A summary the human reads passively barely touches this effect. A question the human has to actually answer does.
- **The Socratic method**: understanding is verified and deepened by questions that make the person reconstruct the reasoning themselves — never by the questioner supplying the answer. Telling someone "here's why" produces the *illusion* of understanding (the illusion-of-explanatory-depth problem); making them reconstruct it produces the real thing.

Everything below exists to put the human in the position of having to retrieve and reconstruct, not recognize and agree.

## When this runs

Only on deliberate invocation — this is a checkpoint the human asks for, not something to fire automatically after every edit.

**Resolving the argument:**
- No argument → default to whatever this conversation actually changed. Cross-check against `git status`/`git diff` where a repo exists, since your own memory of "what we did" can drift or get compacted — git is ground truth whenever it's available. If there's no git repo, or session context is gone and there's no git, fall back to whatever you can reconstruct and say plainly that confidence is lower.
- A file or glob → scope to that path via `git diff`/`git log` on it, or just read the files directly if there's no git history to diff against.
- A commit range (`HEAD~3..HEAD`, a branch name, etc.) → `git diff`/`git log` on that range.
- Free text ("the auth module," "the retry logic") → interpret it against the repo and recent history, and state your interpretation before continuing.

Always say the resolved scope back to the human before moving on — a wrong guess here wastes the whole session downstream.

## Phase 1: Summarize — what and where, not why

Produce a factual rundown: which files changed, what each change mechanically does, how the pieces connect to each other and to the rest of the codebase.

Deliberately hold back rationale and trade-offs here — why this approach was chosen, why an alternative was rejected, what breaks if an assumption is wrong. That material is the substance of Phase 3's questions. A summary that already explains the "why" hands the human a crib sheet and the whole exercise becomes theater.

Close this phase by telling the human to go read the actual files/diff themselves — not to treat this summary as a substitute for looking at the real code. The summary is a map to orient the reading, not the territory.

## Phase 2: Wait for the human to actually study it

Ask the human to say when they've gone through the material. Don't move on until they do — proceeding on a "sure, go ahead" without them having looked defeats the entire point, since there's nothing yet for Phase 3 to retrieve.

Passive reading barely helps here — retrieval practice only pays off when the study itself is active. Suggest something concrete rather than leaving "go read it" open-ended: sketch the flow by hand, mark up the actual diff (group related lines, circle the parts that surprised them), or restate each function's job in one line before moving to the next. These are Michael Feathers' notes/sketching and listing-markup techniques for building understanding of unfamiliar code (*Working Effectively with Legacy Code*, ch. 16) — low-tech, and they force the same kind of active engagement Phase 3 will later test.

Tell them explicitly that they can ask you clarifying "why" questions during this phase:
- For LLM-generated code, the rationale often lives only in the conversation that produced it — if nobody wrote it into a comment, commit message, or PR description, asking is the only way to get it.
- That's a legitimate and good use of this phase: the human pulling the reasoning out of you *now*, before the graded questions, is still them doing real work to build the mental model.
- What defeats the point is *you* volunteering the rationale unprompted in Phase 1's summary — waiting to be asked is the difference.

## Phase 3: Socratic questioning

One question at a time. Never multiple-choice or yes/no — the effortful, supply-your-own-answer form of retrieval is the one with the actual research backing (recognition tests barely move the needle by comparison). Scale the number of questions to how much is actually in the diff — a one-function fix might only need three; a multi-file feature might need seven or eight. Escalate through these tiers, skipping any that don't apply to this particular change:

1. **Recall** — "What does this do, in your own words?" Surfaces whether they have even a working mental model, and exposes the illusion-of-explanatory-depth immediately if they don't.
2. **Rationale** — "Why this approach, and not [a plausible alternative]?" This is the Socratic "challenge assumptions" move — it's also exactly the part Phase 1 held back, so there's no way to answer it from the summary alone.
3. **Mechanism** — walk through one genuinely non-trivial piece of logic, step by step.
4. **Edge cases / failure modes** — "What happens if [a specific input/condition]? How would this fail?"
5. **Consequences** — "What else in the codebase does this touch? What could this break elsewhere?"
6. **Maintenance** — "If this broke in production tomorrow with no LLM to ask, where would you start?"

**Prefer predict-then-verify over pure verbal Q&A whenever the code is actually runnable.** For mechanism and edge-case questions especially, ask the human to predict a concrete output or behavior first — then actually run it and check. This borrows Michael Feathers' characterization-test algorithm (*Working Effectively with Legacy Code*, ch. 13): write the assertion you expect, run it, let the result tell you the truth. It turns the question from "did the human's explanation sound plausible to me" into an objective check against the running code, which is both a stronger test and immune to the human (or you) being persuasive but wrong.

**Never state the answer, even when the human gets it wrong or gets stuck.** Respond only with a further question that points back at a specific place in the actual code — a file, a line, a function — for them to go look at again. This is the whole discipline of the Socratic method: the questioner stays a "humble inquirer," not a lecturer.

**When stuck, scaffold before you give up on the question.** A wrong or vague answer usually doesn't mean the human needs the answer handed over — it often means the question is too big a jump from where they currently are.
- Break it into a smaller, more structured step that still requires them to supply the final piece themselves: walk through one concrete case together, lay out a pattern and ask them to complete it, or narrow "how does this work" down to "what does this one variable equal right after this one line." That's still retrieval, just scaffolded down to a size they can actually reach — it's a legitimate Socratic move, not a concession.
- Only after scaffolding has also failed a couple of times should you stop: log it plainly as a gap, name the exact lines worth re-studying, and move to the next question. A gap that's honestly surfaced is far more useful than a false pass bought by quietly explaining it away.

**Exception — check whether the question is even answerable first.** Rationale questions only work if the rationale was actually externalized somewhere the human could have found it: a comment, a commit message, a PR description, or something discussed earlier in this conversation.
- If a human pushes back that there's genuinely nothing to retrieve — and you check and find they're right, nothing documents this decision anywhere — that's not a comprehension gap, it's a process gap: the decision should have been written down and wasn't.
- This isn't a special rule invented for this skill — it's John Ousterhout's named principle that "comments should describe things that aren't obvious from the code" (*A Philosophy of Software Design*, ch. 13), and he specifically calls out "the rationale for a particular design decision" as exactly the kind of thing that can *only* live in a comment, never in the code itself.
- If it's not there and it's not anywhere else either, the code failed that standard before the human ever had a chance to. Say so plainly, explain the rationale yourself since there was never a fair way for them to get it otherwise, and note the missing documentation in the log instead of a gap against the human.
- Don't let this become an easy escape hatch, though — first genuinely check that the information really is unrecoverable before granting the exception.

## Phase 4: Verdict and log

Conclude with one of three verdicts:
- **Owned** — answered the substantive questions with real reconstruction, not just recognition.
- **Partial** — got the mechanics but had real gaps on rationale, edge cases, or consequences. List the gaps plainly.
- **Not yet** — struggled broadly. Recommend re-studying before relying on this code solo, and name what to focus on.

Write the session to a per-project log so this doesn't evaporate with the conversation:

```
.claude/code-ownership/
  log.md                          — rolling index, one line per session
  sessions/<timestamp>-<slug>.md  — full transcript for that session
```

`log.md` — append one line per session, newest at the top:

```md
# Code Ownership Log

| Date | Scope | Verdict | Session |
|---|---|---|---|
| 2026-09-09 | src/auth/refresh.ts | Partial | sessions/2026-09-09-auth-refresh.md |
```

`sessions/<timestamp>-<slug>.md`:

```md
# Code Ownership — <scope>

**Date:** <date>
**Scope:** <resolved files/diff>
**Verdict:** Owned / Partial / Not yet

## Summary given
<the Phase 1 summary>

## Questions and answers
1. <question> → <human's answer> [gap noted, if any]
...

## Gaps to revisit
- <specific file:line — what to re-study, if any>

## Undocumented decisions found
- <specific file:line — decision that had no accessible rationale anywhere; explained live instead of tested, per the Phase 3 exception>
```

If `.claude/code-ownership/` isn't already tracked in the repo, mention once that it's worth adding to `.gitignore` — this is a personal study record, not something every session necessarily wants committed.

## A note on scope creep

If the human answers a question by revealing they actually want to change the code (a real bug, a better approach they now see), that's a legitimate and good outcome of them actually understanding it — but it's a different task. Note it, don't silently fix it mid-session, and let them decide whether to pause the ownership check to go fix it or finish the check first.
