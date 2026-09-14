# Auditing an MCP tool description

Use this instead of `rubric.md`'s dimensions when the thing under audit
is a tool's `description` field and input schema (an MCP server tool, a
function-calling tool definition), not a skill or `CLAUDE.md`. The
underlying score (1-10) and shirt-size (XS-XL) scales from `rubric.md`
still apply — only the dimensions being judged change. Sourced from
Anthropic's "Writing effective tools for AI agents" (see `sources.md`).

Tool descriptions have a different failure shape than skill/prompt files:
the model doesn't just read a tool description, it has to pick *this*
tool over every other tool available in the same call, then get the
parameters right on (often) the first try with no chance to revise
before the call executes. That's a harder bar than a skill body, which
gets read start to end once triggered.

## Dimensions

1. **Selection & consolidation** — does this tool do one coherent,
   high-leverage thing, or is it a thin wrapper around a single API
   endpoint that overlaps with three other tools? Anthropic's own test:
   *"If a human engineer can't definitively say which tool should be
   used in a given situation, an AI agent can't be expected to do
   better."* A bloated tool set with ambiguous boundaries (`list_x` +
   `get_x` + `search_x` all slightly overlapping) scores low here even
   if each individual description is well-written — consolidating into
   one `search_x` with parameters often serves the agent better than
   three narrow tools.
2. **Namespacing** — when a server exposes many tools, are related ones
   grouped under a common, visually distinguishable prefix (e.g.
   `asana_projects_search`, `asana_users_search`, or the
   `ServerName:tool_name` fully-qualified form Claude Code itself uses)?
   Un-namespaced tools with similar names across servers are a common
   source of "tool not found" or wrong-tool-selected failures.
3. **Description quality** — written the way you'd brief a new hire who
   knows the domain but not this specific system: implicit context made
   explicit, edge cases named, and — as important as what it does —
   what it's *not* for, when that's a live confusion risk. Parameter
   names are unambiguous (`user_id`, not `user`).
4. **Response shaping** — does the tool return high-signal, semantic
   fields (`name`, `file_type`) rather than raw technical identifiers
   (UUIDs, internal row IDs) the model has no use for? For tools whose
   callers sometimes want more, sometimes less, is there a
   `response_format` (`concise`/`detailed`) parameter rather than always
   returning the maximum payload?
5. **Token efficiency** — pagination, range selection, filtering, or
   truncation with sensible non-arbitrary defaults, so one call can't
   blow the context budget. Claude Code's own convention (restricting
   tool responses to 25,000 tokens by default) is a reasonable anchor
   for "sensible default" if the tool has none. A tool with no size
   limit on its own output is a real finding here, not a nice-to-have.
6. **Error messages** — actionable and specific, not an opaque error
   code or a raw stack trace. Good errors point at the fix: *"Field
   'signature_date' not found. Available fields: customer_name,
   order_total, signature_date_signed"* tells the caller exactly what to
   retry with; a bare `400 Bad Request` doesn't.

## What a live evaluation would add (out of scope for a static audit)

This rubric judges the description and schema as written. Whether the
tool actually gets selected and used correctly under real multi-step
tasks is a different question, answered by running it — realistic
evals (not toy sandbox queries) tracking accuracy, tool-call count, and
token consumption per task, then reading transcripts for confusion
patterns. Anthropic's own note is worth repeating here: *"What agents
omit in their feedback and responses can often be more important than
what they include."* Flag this as a caveat in the report rather than
attempting to simulate it — this skill doesn't execute tool calls.

## Report

Use `rubric.md`'s same report template, substituting these six
dimensions for that file's seven. Score and shirt-size bands are
unchanged.
