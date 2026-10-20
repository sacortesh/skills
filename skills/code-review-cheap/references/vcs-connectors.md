# VCS connectors

## Contents
- Why this is pluggable
- The connector interface
- GitHub (implemented)
- Bitbucket (not implemented — how to add it)
- GitLab (not implemented — how to add it)
- Detection order and fallback

## Why this is pluggable

PR metadata (title, description, labels, linked issues) is useful input
to risk assessment and context building, but it's optional — this skill
works entirely from local git with no connector at all. Keeping the
connector behind a thin, explicit interface means adding a new host
later is additive (one new file + one new entry in
`detect_connector.py`'s registry), not a rewrite of the core pipeline.

## The connector interface

Every connector is a Python module under `scripts/connectors/` exposing
exactly two functions:

```python
def detect(repo_path: str) -> bool:
    """True if this connector applies to the repo's remote(s)."""

def fetch_metadata(repo_path: str, pr_ref: str | None) -> dict:
    """
    Returns:
      {
        "title": str,
        "description": str,
        "labels": list[str],
        "linked_issues": list[str],   # e.g. ["#123"], best-effort parse
        "base_ref": str,              # branch/ref name, not a SHA
        "head_ref": str,
        "url": str,
      }
    """
```

Connectors never resolve refs to commit SHAs themselves — that stays
`collect_diff.py`'s job (`git rev-parse <ref>^{commit}` against the local
clone), so every connector only has to know how to name a ref, not pin
one. Connectors never fetch the diff itself either — only metadata; the
diff always comes from local git so the pipeline never depends on a
host's API rate limits for the part that actually matters.

## GitHub (implemented)

`scripts/connectors/github.py`.

- **Detect**: `git remote -v` contains `github.com`.
- **Fetch**: shells out to `gh pr view [<pr_ref>] --json
  title,body,labels,baseRefName,headRefName,url`. Requires the `gh` CLI
  already authenticated in the environment — matches this environment's
  standing preference for `gh` over hand-rolled GitHub API calls. No
  separate API token is requested or stored by this skill.
- **Linked issues**: best-effort regex over the PR body for GitHub's
  closing keywords (`close`/`closes`/`closed`/`fix`/`fixes`/`fixed`/
  `resolve`/`resolves`/`resolved` followed by `#<number>`), plus bare
  `#<number>` mentions as a weaker signal. Never asserted as a complete
  list — `build_context.py` records it as "linked issues found," not
  "the linked issues."

## Bitbucket (not implemented — how to add it)

- **Detect**: `git remote -v` contains `bitbucket.org` (cloud) or a
  configured self-hosted hostname (Bitbucket Server/Data Center doesn't
  have a fixed domain).
- **Fetch**: Bitbucket has no first-party CLI equivalent to `gh`/`glab`
  with the same metadata coverage — would need the Bitbucket REST API
  (`/repositories/{workspace}/{repo}/pullrequests/{id}`) directly, which
  means handling an API token/app password, unlike the GitHub connector.
  Flag that credential requirement explicitly to the user before
  implementing — it changes this skill's "no separate credentials"
  property.
- Add `scripts/connectors/bitbucket.py` implementing the same two
  functions, then register it in `detect_connector.py`'s connector list.

## GitLab (not implemented — how to add it)

- **Detect**: `git remote -v` contains `gitlab.com`, or a configured
  self-hosted hostname (GitLab is commonly self-hosted, so the hostname
  can't be hardcoded the way `github.com` can — needs a config value or
  an env var for the self-hosted case).
- **Fetch**: `glab mr view --json title,description,labels,sourceBranch,
  targetBranch,webUrl` mirrors the GitHub connector's shape closely —
  `glab` plays the same role `gh` does, and unlike Bitbucket needs no
  separate credential handling, so this is the easier of the two to add.
  Same addition steps as Bitbucket above (new connector module, new
  registry entry).

## Detection order and fallback

`detect_connector.py` tries each registered connector's `detect()` in a
fixed order (github, bitbucket, gitlab) and stops at the first match. If
none match, or a match is found but not implemented (today: bitbucket,
gitlab), the pipeline falls back to local-only mode: no PR metadata, refs
come only from the `--base`/`--head` flags, and the context manifest
records "no PR metadata connector available" as a coverage limitation
rather than failing the run.
