# Reviewing GitHub repos (not just local folders)

Same taxonomy, same per-project state file, same rollup as the local
workflow in `SKILL.md` — the only thing that changes is where projects
come from and how much of each one you can see without cloning it. Read
this whole file before starting; it's short on purpose.

The point of this variant: local folders only show what you happened to
keep around. GitHub shows everything you ever pushed, plus a signal local
folders can never give you — real external interest (stars, forks, other
people's issues) instead of your own guess at market fit.

## Prerequisites

Requires the `gh` CLI, authenticated. Check with `gh auth status` before
starting — if it's not logged in, stop and ask the user to run
`gh auth login` themselves rather than trying to authenticate for them.

## Step 1: Scan and cross-reference

```
python3 <skill_dir>/scripts/scan_github_repos.py <owner> <target_dir>
```

`<owner>` is a GitHub username or org. If the user hasn't said which
account, default to the authenticated user (`gh api user --jq .login`);
ask if they might mean an org instead.

This fetches every repo for that owner and cross-references it against
`<target_dir>`'s local project folders (by matching each folder's git
remote URL, or by name if a folder has no remote configured yet). Output
is JSON with three buckets:

- **`matched`** — repo has a local folder with a matching remote. Already
  covered by a local scan; nothing new to write here, just enrich (see
  Step 3).
- **`possible_local_match`** — folder name matches a repo name but no
  remote URL confirmed it (e.g. the local folder was never pushed). Worth
  a quick manual look, not an automatic match.
- **`github_only`** — no local folder at all. This is the actual point of
  running this variant: repos that exist only on GitHub, some of which
  may be years old and completely forgotten.

## Step 2: Scope the github_only list with the user

Don't process all of `github_only` unasked — on an account with real
history this can easily be 40+ repos spanning a decade, and a lot of
that will be dead forks, abandoned tutorials, or one-off school/work
exercises that don't deserve the same treatment as a real side project.

Show the user the list (name, stars, pushed date, private/fork/archived
flags) and let them scope it — e.g. "everything," "skip forks and
archived," "only things with stars," "only the last N years." A
reasonable default suggestion: exclude pure forks with no stars
(`isFork: true` and `stargazerCount: 0`) unless the user wants everything,
since an untouched fork isn't really "your" project. State the exclusion
explicitly rather than silently dropping repos — the user should know
what was skipped and why, in case something they care about got filtered.

## Step 3: Enrich the `matched` repos (cheap, do this for all of them)

For each matched repo, open its existing `PROJECT_STATE.md` and add three
frontmatter fields if not already present: `github_stars`, `github_forks`,
`is_archived` (all straight from the scan JSON — no judgment needed). If
`github_stars > 0`, that's real signal worth a sentence in the Market
Position or Verdict section — a project with actual external stars is
meaningfully different from the same project with zero, regardless of
what the verdict already said. Don't mechanically bump the verdict up
just because of a star count, but do treat it as evidence to weigh, the
same way a market-research finding would be.

## Step 4: Write state files for in-scope `github_only` repos

There's no local folder for these, so don't invent one inside real
project directories. Instead, create a **shadow folder** directly under
`<target_dir>`, named `_gh-<repo-name>` (the underscore prefix signals
"not an actual local checkout — state file only"), and write
`PROJECT_STATE.md` there using the same template as the local flow
(`templates/PROJECT_STATE.md.template`). This keeps everything on one
rollup (`render_portfolio.py` already picks up any `*/PROJECT_STATE.md`
one level under the target directory, shadow folders included) without
polluting real project directories with files that don't belong to any
actual local code.

Gather purpose signal without cloning:

```
gh repo view <nameWithOwner>
```

This prints the description and rendered README directly — usually
enough to write the Purpose section. If it's genuinely too thin (no
README, one-line description, no obvious point), say so plainly, same
rule as the local flow — don't invent a purpose that isn't there.

Frontmatter differences from the local template:
- `git_is_repo` / `git_branch` / `uncommitted_changes` / `unpushed_commits`
  don't apply the same way — set `has_local_copy: false` instead, and use
  `pushedAt` for staleness.
- Add `github_stars`, `github_forks`, `is_fork`, `is_archived` from the
  scan JSON.
- `has_deploy_signals`: check `homepageUrl` from the scan JSON (a
  non-empty homepage is a real deployment signal) rather than scanning
  files.

Verdict, Usable As-Is, Effort, and Next Step follow the same rules as the
local flow, including `delete` as a valid verdict (see `SKILL.md`) — this
is where it comes up most: a decade of GitHub history tends to include
tutorial-following repos, dead-framework experiments, and one-off school
exercises that have no lasting value and aren't better served by staying
in git either. Don't reach for `delete` just because something is old —
plenty of old repos are fine as archives or still work — reach for it
when keeping it isn't actually doing anything for anyone. Three things
specific to this variant:
- **Weigh stars/forks as real evidence**, not just self-assessment — a
  repo with meaningful stars has already cleared a bar a local folder
  never had to.
- **"Next Step" for a promising github-only repo usually starts with
  cloning it** — you're writing this from a README and a description, not
  the actual code, so the honest next action is often "clone locally and
  actually look at the implementation" before deeper work makes sense.
- **`delete` here means the actual GitHub repo, not just this shadow
  file.** The Next Step for a `delete`-verdict repo is the real action —
  "delete `owner/repo` on GitHub (`gh repo delete owner/repo`)" or
  "archive it instead if there's any sentimental/reference value" — not
  just "remove the shadow file." Never run `gh repo delete` yourself:
  it's irreversible and affects the user's actual GitHub account, so it
  belongs in Next Step as a recommendation for the user to execute, the
  same way this skill never runs `rm` on a local project either.

## Step 5: Regenerate the rollup

Same command as always:

```
python3 <skill_dir>/scripts/render_portfolio.py <target_dir>
```

No changes needed to call it differently — it already globs one level
deep under the target directory, which covers both real project folders
and `_gh-*` shadow folders.

## What NOT to do

- Don't clone all 40+ `github_only` repos just to look — that's slow and
  defeats the point of using the GitHub API for cheap metadata first.
  Clone individually, later, only for repos that turn out to be worth a
  deeper look.
- Don't run this against an org with repos the user doesn't have context
  on (teammates' work, company repos) without checking scope first — this
  workflow is for personal portfolio triage, not auditing other people's
  projects.
