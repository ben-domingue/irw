#!/usr/bin/env python3
"""Fetch and locally cache the source text for a table (paper via DOI, or
data-page URL), so repeated runs don't re-hit paywalled or rate-limited
sources.

Given a DOI, this asks OpenAlex where an openly readable copy lives and
tries those locations before falling back to resolving the DOI itself.
That matters because publisher landing pages frequently refuse an
unauthenticated GET even when the article is fully open access -- the old
single-GET behaviour reported those as unreachable, and the tagger read
that as "paywall". Of the nine tables the 2.2 scoring run called paywalled
(#1744), six had a legally open version.

It still does not decide whether content is a paywall -- but it now reports
OpenAlex's asserted `oa_status`, so that judgement has evidence behind it
rather than being inferred from a blocked fetch. PDFs are extracted to text.

Usage:
    python fetch_source.py TABLE --doi 10.1037/a0022874
    python fetch_source.py TABLE --url https://example.org/page
    python fetch_source.py TABLE --doi ... --force    # re-fetch even if cached
    python fetch_source.py TABLE --doi ... --no-oa    # skip the OpenAlex lookup

Cache lives in ../.cache/ next to this scripts/ dir, one file per table --
gitignored, not committed (see tags/.gitignore).
"""
import argparse
import io
import re
import sys
from pathlib import Path

import requests

# OpenAlex asks for a contact address in the UA and gives faster, more
# reliable service to requests that carry one ("the polite pool").
UA = {"User-Agent": "irw-auto-tag/2.0 (research; ben.domingue@gmail.com)"}
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
OPENALEX = "https://api.openalex.org/works/doi:{}"

# Minimum *visible prose* (not raw bytes) for a page to count as source text.
# Raw byte count cannot distinguish an article from a challenge page: the
# reCAPTCHA interstitial Google served for a fully open-access PeerJ paper was
# 21kB, and OSF's JavaScript shell is a consistent 4.2kB of pure CSS.
MIN_USEFUL_CHARS = 1500

# Substrings that identify a page as a blocker rather than the source. Matched
# against the visible text, lowercased. Kept explicit rather than clever --
# each one was observed on a real table in the #1744 pool.
BLOCKER_MARKERS = (
    "recaptcha",
    "captcha",
    "unusual traffic",
    "verify you are a human",
    "are you a robot",
    "enable javascript",
    "javascript is disabled",
    "your web browser is no longer supported",
    "ya no se admite tu navegador",
    "checking your browser",
    "cloudflare",
    "access denied",
    "403 forbidden",
    "sign in to continue",
    "purchase this article",
    "get access to the full version",
)


def cache_path(table):
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in table.lower())
    return CACHE_DIR / f"{safe}.txt"


def openalex_locations(doi):
    """Return (oa_status, [urls]) for a DOI: open locations, best first.

    Never raises -- OpenAlex being down or not knowing the DOI degrades to
    the old DOI-resolution behaviour rather than failing the fetch.
    """
    doi = doi.strip().removeprefix("https://doi.org/").removeprefix("doi.org/")
    try:
        r = requests.get(OPENALEX.format(doi), headers=UA, timeout=30)
        if r.status_code != 200:
            return f"openalex_http_{r.status_code}", []
        work = r.json()
    except (requests.RequestException, ValueError) as e:
        return f"openalex_error_{type(e).__name__}", []

    oa_status = (work.get("open_access") or {}).get("oa_status", "unknown")
    urls = []
    locations = [work.get("best_oa_location")] + (work.get("locations") or [])
    for loc in locations:
        if not loc or not loc.get("is_oa"):
            continue
        # PDF first: publisher HTML landing pages are the thing that blocks.
        for key in ("pdf_url", "landing_page_url"):
            u = loc.get(key)
            if u and u not in urls:
                urls.append(u)
    return oa_status, urls


def visible_text(html_or_text):
    """Strip markup and collapse whitespace, so what is measured is prose."""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_or_text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(" ")
    except Exception:
        text = re.sub(r"<[^>]*>", " ", html_or_text)
    return re.sub(r"\s+", " ", text).strip()


def classify(text):
    """Is this the source, or something standing in front of it?

    Returns (ok, reason). The caller keeps trying other locations when not ok.
    """
    prose = visible_text(text)
    low = prose.lower()
    for marker in BLOCKER_MARKERS:
        if marker in low:
            return False, f"blocker:{marker.replace(' ', '_')}"
    if len(prose) < MIN_USEFUL_CHARS:
        return False, f"too_short:{len(prose)}_chars_visible"
    return True, f"{len(prose)}_chars_visible"


def extract(response):
    """Text of a response -- PDFs decoded, everything else left as-is."""
    ctype = response.headers.get("Content-Type", "").lower()
    looks_pdf = "pdf" in ctype or response.content[:5] == b"%PDF-"
    if not looks_pdf:
        return response.text
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(response.content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"[PDF extraction failed: {type(e).__name__}: {e}]"


def try_url(url):
    """Fetch one candidate. Returns ((text, final_url) | None, reason)."""
    try:
        r = requests.get(url, headers=UA, timeout=30, allow_redirects=True)
    except requests.RequestException as e:
        return None, f"error:{type(e).__name__}"
    if r.status_code != 200:
        return None, f"http_{r.status_code}"
    text = extract(r)
    ok, reason = classify(text)
    if not ok:
        return None, reason
    return (text, r.url), reason


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--doi")
    ap.add_argument("--url")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-oa", action="store_true",
                    help="skip the OpenAlex lookup and resolve the DOI directly")
    args = ap.parse_args()

    if not args.doi and not args.url:
        ap.error("provide --doi or --url")

    path = cache_path(args.table)
    if path.exists() and not args.force:
        print(f"CACHED {path} ({path.stat().st_size} bytes)")
        return

    oa_status = "not_checked"
    candidates = []
    if args.doi and not args.no_oa:
        oa_status, candidates = openalex_locations(args.doi)
    if args.doi:
        candidates.append(f"https://doi.org/{args.doi}")
    if args.url:
        candidates.append(args.url)

    attempted = []
    rejected = []
    for url in candidates:
        if url in attempted:
            continue
        attempted.append(url)
        got, reason = try_url(url)
        rejected.append(f"{url} -> {reason}")
        if got is None:
            continue
        text, final_url = got
        CACHE_DIR.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8", errors="replace")
        print(f"OK oa_status={oa_status} source={url} final_url={final_url} "
              f"content={reason} attempts={len(attempted)} -> {path}")
        return

    # Nothing readable. oa_status is the useful half of this message: a
    # closed status corroborates a paywall, while an open one means the
    # article is readable and something else -- a WAF, a bad link -- blocked
    # us, which is not the same finding and should not be staged as one.
    # Each rejection carries its reason, so "blocked by a captcha" is
    # distinguishable from "genuinely behind a paywall" -- the distinction
    # #1744 found the tagger was collapsing.
    print(f"UNREACHABLE oa_status={oa_status} tried={len(attempted)}",
          file=sys.stderr)
    for line in rejected:
        print(f"  rejected {line}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
