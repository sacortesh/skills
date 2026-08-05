---
name: book-shopping
description: Given one or more book titles (and optionally authors), produce links to actually find and acquire the book — Amazon, MercadoLibre Colombia, and BuscaLibre Colombia for buying, general search links (Google, Google Books, Open Library, WorldCat), and an Anna's Archive EPUB link for provisioning the avangarde-rag knowledge base. A single book gets a full grouped breakdown; multiple books (e.g. a whole shopping list) get a compact markdown table, one row per book. Use this whenever the user asks where to buy a book, wants a copy of a specific title, asks for shopping/purchase links for one or more books, or wants to acquire/provision a book for the RAG library. Also use it as the natural follow-up after the book-hunt skill produces a shopping list of titles — book-hunt rates and researches books, book-shopping finds where to actually get them. Trigger on requests like "where can I buy X", "find me a copy of these books", "get purchase links for this list", or "I need to provision these titles for the RAG."
---

# Book Shopping

Turns book titles into a ready-to-click set of links for buying, searching, or
provisioning the book — no manual URL construction needed.

## When to use this

- The user names one or more books and wants to know where to get them
  (buy, borrow, or download an EPUB to index into the RAG).
- The user just ran `/book-hunt` and has a 🛒 shopping list of titles —
  feed that list straight into this skill to get actionable links for each one.
- The user asks to "provision" a book for `avangarde-rag` (see the
  Provisioning workflow in the root `CLAUDE.md`) — this skill produces the
  Anna's Archive link that workflow starts from.

## Prerequisites

Bash and Python 3 available on PATH (the bundled `scripts/book-links.sh` shells out to
Python for URL-encoding and accent-stripped slug generation). No install step — nothing
external to fetch, no API keys. `rag-search.sh` is optional (see Edge cases below); its
absence degrades gracefully rather than blocking the skill.

## How to run it

Call the bundled script by its path relative to **this skill's own directory**
(`<skill_dir>/scripts/book-links.sh`) — do not rely on any shell alias, since
aliases defined in `.zshrc`/`.zprofile` are not reliably expanded in the
non-interactive shells tool calls run in. This mirrors how `rag-search` is
documented in the root `CLAUDE.md`: the alias is for humans at a terminal,
scripts and skills always call the underlying file directly. Don't hardcode a
specific machine's absolute path — resolve `<skill_dir>` to wherever this
skill is actually installed (it varies by machine and by install method).

**Single book — full grouped output:**
```bash
<skill_dir>/scripts/book-links.sh "Title" "Author"
```
Author is optional — omit it if unknown, the script still works, just with a
slightly less targeted search query.

**Multiple books — compact table (e.g. a book-hunt shopping list):**
Pipe one `Title|Author` pair per line (author optional, omit the `|` if you
don't have one):
```bash
printf 'Thinking, Fast and Slow|Daniel Kahneman\nSapiens|Yuval Noah Harari\n' | \
  <skill_dir>/scripts/book-links.sh
```
When chaining from a book-hunt output, pull the title (and author, if the
table includes one) out of each shopping-list row and build the batch input
from those — don't just paste the whole table in. Use the table format
whenever there's more than one book: a full block per book stops being
readable once the list grows past a couple of titles.

## What comes back

**Single book** — one block, grouped by intent:
- **🛒 Buy** — Amazon, MercadoLibre (Colombia), BuscaLibre (Colombia)
- **🔍 Search** — Google, Google Books, Open Library, WorldCat (library
  lookup, useful if the user would rather borrow than buy)
- **📚 Provision** — the Anna's Archive EPUB search link, built via
  `rag-search.sh` (the same script the Library's provisioning workflow uses),
  plus a one-line reminder of the next steps (drop the EPUB in
  `avangarde-rag/inbox/`, run `process.py`).

**Multiple books** — a markdown table, one row per book, columns `Book |
Amazon | MercadoLibre (CO) | BuscaLibre (CO) | Provision`. Each link cell
renders as clickable markdown (`[Get on Amazon →](url)`), not a bare URL —
that's what keeps a long list scannable instead of a wall of headers and
bullet lists. The general-search links (Google/Google Books/Open Library/
WorldCat) are intentionally left out of the table for compactness; if the
user wants those for one specific title from the list, run the single-book
form for just that title.

Present this output directly to the user — it's already formatted as
markdown. Don't paraphrase the links into prose; the point is clickable URLs,
not a summary.

## Why Amazon, MercadoLibre CO, and BuscaLibre CO (not Bookshop.org/AbeBooks)

The buy sources are tuned for a Colombia-based user: Bookshop.org and
AbeBooks mostly ship from the US/UK, which is often impractical to get to
Colombia. MercadoLibre and BuscaLibre both operate locally there and are
worth checking first. Don't reintroduce US/UK-only retailers into the Buy
group without asking — if a future user isn't Colombia-based, that's a real
config difference worth surfacing rather than guessing at.

The Amazon URL the script builds (`amazon.com/s?k=...`) is a plain,
functional search query. If you see a "real" Amazon URL with extra params
like `crid=`, `sprefix=`, or `__mk_es_US=`, those are session/tracking
artifacts Amazon's own UI appends after a live search — they aren't required
for the search to work, so don't try to replicate them.

## Edge cases

- If a title has unusual punctuation, accents, or non-Latin characters, pass
  it through as-is — the script handles URL-encoding (and, for MercadoLibre,
  accent-stripped slugs) via Python, it doesn't need pre-sanitizing.
- If `rag-search.sh` isn't present or isn't executable at the expected path,
  the script still returns every other link — for single-book output it falls
  back to a manually constructed Anna's Archive search URL; for table rows it
  shows `—` in the Provision cell instead of blocking on that one script.
- This skill only produces links; it never downloads, purchases, or opens
  anything automatically. The user (or a separate provisioning step) decides
  what to actually do with each link.
