#!/usr/bin/env python3
"""Fetch and locally cache the source text for a table (paper via DOI, or
data-page URL), so repeated runs don't re-hit paywalled or rate-limited
sources.

Prefers resolving https://doi.org/{doi} when a DOI is given; falls back to
the raw URL otherwise. Does not try to detect paywalls itself -- it fetches
what it can and reports the HTTP status, final URL, and byte count. The
skill (Claude, reading the cached text with the Read tool) decides whether
the content is actually the paper/data page or a paywall/login wall, per the
brief's instruction not to guess content from a blocked fetch.

Usage:
    python fetch_source.py TABLE --doi 10.1037/a0022874
    python fetch_source.py TABLE --url https://example.org/page
    python fetch_source.py TABLE --doi ... --force    # re-fetch even if cached

Cache lives in ../.cache/ next to this scripts/ dir, one file per table --
gitignored, not committed (see tags/.gitignore).
"""
import argparse
import sys
from pathlib import Path

import requests

UA = {"User-Agent": "irw-auto-tag/1.0 (research; contact your-email)"}
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"


def cache_path(table):
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in table.lower())
    return CACHE_DIR / f"{safe}.txt"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--doi")
    ap.add_argument("--url")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not args.doi and not args.url:
        ap.error("provide --doi or --url")

    path = cache_path(args.table)
    if path.exists() and not args.force:
        print(f"CACHED {path} ({path.stat().st_size} bytes)")
        return

    target = f"https://doi.org/{args.doi}" if args.doi else args.url
    try:
        r = requests.get(target, headers=UA, timeout=30, allow_redirects=True)
    except requests.RequestException as e:
        print(f"FETCH_ERROR {target} :: {e}", file=sys.stderr)
        sys.exit(1)

    CACHE_DIR.mkdir(exist_ok=True)
    path.write_text(r.text, encoding="utf-8", errors="replace")
    print(f"OK status={r.status_code} final_url={r.url} bytes={len(r.text)} -> {path}")


if __name__ == "__main__":
    main()
