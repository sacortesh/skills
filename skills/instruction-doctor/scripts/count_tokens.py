#!/usr/bin/env python3
"""Deterministic line/char/token estimate for one or more files.

Why this exists: "is this file too long" is a judgment call an LLM will
happily rationalize either way. A repeatable number takes that off the
table so the audit's length verdict rests on a measurement, not a vibe.

Estimation tiers (best available is used automatically, and reported):
  1. tiktoken (cl100k_base), if installed — a decent cross-model proxy.
     Not Claude's actual tokenizer, so still an approximation, but a
     tighter one than a character count.
  2. chars / 3.5 heuristic — always available, no dependencies, fully
     offline. Calibrated for English/code-mixed markdown; pure code or
     pure CJK text will skew this.

Exact counts (Claude's real tokenizer) require a network call to the
Anthropic API and are deliberately NOT automatic — pass --exact to opt
in. Default behavior stays offline and deterministic.

Usage:
  count_tokens.py <file> [<file> ...]
  count_tokens.py <file> --json
  count_tokens.py <file> --exact          # calls Anthropic API if configured
  count_tokens.py <file> --line-threshold 500 --token-threshold 8000
"""
import argparse
import json
import sys
from pathlib import Path

DEFAULT_LINE_THRESHOLD = 500
DEFAULT_TOKEN_THRESHOLD = 8000


def heuristic_tokens(text: str) -> int:
    return max(1, round(len(text) / 3.5))


def tiktoken_tokens(text: str):
    try:
        import tiktoken
    except ImportError:
        return None
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text, disallowed_special=()))


def exact_tokens(text: str, model: str):
    """Calls the Anthropic Messages API token-counting endpoint. Returns
    None (with a warning on stderr) if the SDK or API key isn't available —
    callers should fall back to the estimate rather than fail the run."""
    try:
        import anthropic
    except ImportError:
        print("warning: --exact requested but `anthropic` package not installed; falling back to estimate", file=sys.stderr)
        return None
    try:
        client = anthropic.Anthropic()
        result = client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": text}],
        )
        return result.input_tokens
    except Exception as e:
        print(f"warning: --exact call failed ({e}); falling back to estimate", file=sys.stderr)
        return None


def analyze(path: Path, use_exact: bool, model: str):
    text = path.read_text(errors="replace")
    lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    chars = len(text)

    method = "heuristic (chars/3.5)"
    tokens = heuristic_tokens(text)

    tk = tiktoken_tokens(text)
    if tk is not None:
        tokens = tk
        method = "tiktoken cl100k_base (approximate proxy, not Claude's tokenizer)"

    if use_exact:
        exact = exact_tokens(text, model)
        if exact is not None:
            tokens = exact
            method = f"anthropic API count_tokens (exact, model={model})"

    return {
        "file": str(path),
        "lines": lines,
        "chars": chars,
        "estimated_tokens": tokens,
        "method": method,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    ap.add_argument("--exact", action="store_true", help="attempt an exact count via the Anthropic API (needs ANTHROPIC_API_KEY)")
    ap.add_argument("--model", default="claude-sonnet-5", help="model id to use for --exact counting")
    ap.add_argument("--line-threshold", type=int, default=DEFAULT_LINE_THRESHOLD)
    ap.add_argument("--token-threshold", type=int, default=DEFAULT_TOKEN_THRESHOLD)
    args = ap.parse_args()

    results = []
    for f in args.files:
        p = Path(f)
        if not p.is_file():
            print(f"warning: skipping {f} (not a file)", file=sys.stderr)
            continue
        r = analyze(p, args.exact, args.model)
        r["over_line_threshold"] = r["lines"] > args.line_threshold
        r["over_token_threshold"] = r["estimated_tokens"] > args.token_threshold
        results.append(r)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    for r in results:
        flags = []
        if r["over_line_threshold"]:
            flags.append(f"OVER {args.line_threshold} LINES")
        if r["over_token_threshold"]:
            flags.append(f"OVER {args.token_threshold} TOKENS")
        flag_str = f"  [{', '.join(flags)}]" if flags else ""
        print(f"{r['file']}")
        print(f"  lines: {r['lines']}  chars: {r['chars']}  est_tokens: {r['estimated_tokens']}  ({r['method']}){flag_str}")


if __name__ == "__main__":
    main()
