#!/usr/bin/env bash
# Build a set of "where to find this book" links: retailers (Amazon +
# Colombia-specific stores), general search, library lookup, and the Anna's
# Archive provisioning link used to feed the avangarde-rag knowledge base.
#
# Usage (single book — full grouped output):
#   book-links.sh "Title" ["Author"]
#
# Usage (batch, one book per line on stdin, "Title|Author" — author optional
# — compact table output, meant for a whole book-hunt shopping list):
#   printf 'Thinking, Fast and Slow|Daniel Kahneman\nThe Innovator'"'"'s Dilemma\n' | book-links.sh
#
# Anna's Archive link is delegated to rag-search.sh so both skills stay in
# sync on how that URL is built — always called by absolute path, never by
# the `rag-search` shell alias, since aliases aren't reliably available to
# non-interactive shells.
set -euo pipefail

RAG_SEARCH="/Users/skraheux/Workspace/Code/personal/avangarde-rag/rag-search.sh"

# Space -> %20. Used for Google/Google Books/Open Library/WorldCat/Anna's
# Archive fallback, which all accept this form fine.
encode() {
  python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))" "$1"
}

# Space -> +. Matches Amazon's and BuscaLibre's own search URLs.
encode_plus() {
  python3 -c "import sys, urllib.parse; print(urllib.parse.quote_plus(sys.argv[1]))" "$1"
}

# MercadoLibre Colombia builds its search path as a hyphenated, accent-
# stripped slug (e.g. "El Dios Menos Malo" -> "el-dios-menos-malo").
slugify() {
  python3 -c "
import sys, unicodedata, re
s = unicodedata.normalize('NFKD', sys.argv[1]).encode('ascii', 'ignore').decode('ascii')
s = re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')
print(s)
" "$1"
}

anna_link_for() {
  local title="$1"
  if [[ -x "$RAG_SEARCH" ]]; then
    "$RAG_SEARCH" "$title" 2>/dev/null || true
  fi
}

# Full grouped output for a single book.
emit_single() {
  local title="$1"
  local author="${2:-}"
  local query="$title"
  if [[ -n "$author" ]]; then
    query="$title $author"
  fi
  local qp q enc_title anna_link
  qp=$(encode_plus "$query")
  q=$(encode "$query")
  enc_title=$(encode "$title")
  anna_link=$(anna_link_for "$title")

  echo "## ${title}${author:+ — $author}"
  echo ""
  echo "🛒 Buy"
  echo "- Amazon: https://www.amazon.com/s?k=${qp}&i=stripbooks"
  echo "- MercadoLibre (Colombia): https://listado.mercadolibre.com.co/$(slugify "$query")"
  echo "- BuscaLibre (Colombia): https://www.buscalibre.com.co/libros/search/?q=${qp}"
  echo ""
  echo "🔍 Search"
  echo "- Google: https://www.google.com/search?q=${q}+book"
  echo "- Google Books: https://www.google.com/search?tbm=bks&q=${q}"
  echo "- Open Library: https://openlibrary.org/search?q=${q}"
  echo "- WorldCat (library lookup): https://search.worldcat.org/search?q=${q}"
  echo ""
  echo "📚 Provision (for RAG indexing)"
  if [[ -n "$anna_link" ]]; then
    echo "- Anna's Archive (EPUB): ${anna_link}"
  else
    echo "- Anna's Archive (EPUB): rag-search.sh unavailable — search manually at https://annas-archive.gl/search?q=${enc_title}"
  fi
  echo "  (download the EPUB, drop it in avangarde-rag/inbox/, then run \`uv run python process.py\` from avangarde-rag/)"
}

# Compact table row for batch mode (many books at once, e.g. a book-hunt
# shopping list) — one row per book, one link per source.
emit_table_header() {
  echo "| Book | Amazon | MercadoLibre (CO) | BuscaLibre (CO) | Provision |"
  echo "|---|---|---|---|---|"
}

emit_table_row() {
  local title="$1"
  local author="${2:-}"
  local query="$title"
  if [[ -n "$author" ]]; then
    query="$title $author"
  fi
  local qp anna_link label
  qp=$(encode_plus "$query")
  anna_link=$(anna_link_for "$title")
  label="${title}${author:+ — $author}"

  local amazon_url="https://www.amazon.com/s?k=${qp}&i=stripbooks"
  local ml_url="https://listado.mercadolibre.com.co/$(slugify "$query")"
  local bl_url="https://www.buscalibre.com.co/libros/search/?q=${qp}"
  local provision_cell="—"
  if [[ -n "$anna_link" ]]; then
    provision_cell="[Anna's Archive →](${anna_link})"
  fi

  echo "| ${label} | [Get on Amazon →](${amazon_url}) | [Search →](${ml_url}) | [Search →](${bl_url}) | ${provision_cell} |"
}

if [[ $# -ge 1 ]]; then
  emit_single "$1" "${2:-}"
else
  emit_table_header
  while IFS='|' read -r title author || [[ -n "$title" ]]; do
    [[ -z "$title" ]] && continue
    emit_table_row "$title" "${author:-}"
  done
fi
