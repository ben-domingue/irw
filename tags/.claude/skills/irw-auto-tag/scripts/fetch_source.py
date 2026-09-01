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

Data repositories get their own route (#1786). Dataverse and figshare answer a
bot challenge on their web pages -- Dataverse returns HTTP 202 with a ZERO-byte
body whatever user agent you send -- while their APIs return the record. Some
Mendeley records serve a JavaScript shell. All three are asked through their API
instead, and where the deposit names the paper it backs, that DOI is adopted and
followed down the ordinary path, which is where usable prose lives. Deposit
metadata is returned only as a fallback and is labelled `repository_metadata`
so the caller can tell a catalogue record from a paper.

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
import json
import re
import sys
import time
from pathlib import Path

import requests

# OpenAlex asks for a contact address in the UA and gives faster, more
# reliable service to requests that carry one ("the polite pool").
UA = {"User-Agent": "irw-auto-tag/2.0 (research; ben.domingue@gmail.com)"}
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
OPENALEX = "https://api.openalex.org/works/doi:{}"
EPMC_SEARCH = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
               "?query=DOI:%22{}%22&format=json&resultType=core")
EPMC_FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"

# Courtesy pause between HTTP attempts. NCBI serves a reCAPTCHA to repeated
# unauthenticated hits, which is how a table that fetched cleanly on one run
# comes back "paywalled" on the next -- reachability was measurably
# rate-sensitive before this.
REQUEST_DELAY_S = 1.0

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
    """Return (oa_status, [urls], title) for a DOI: open locations, best first.

    Never raises -- OpenAlex being down or not knowing the DOI degrades to
    the old DOI-resolution behaviour rather than failing the fetch.
    """
    doi = doi.strip().removeprefix("https://doi.org/").removeprefix("doi.org/")
    try:
        r = requests.get(OPENALEX.format(doi), headers=UA, timeout=30)
        if r.status_code != 200:
            return f"openalex_http_{r.status_code}", [], None
        work = r.json()
    except (requests.RequestException, ValueError) as e:
        return f"openalex_error_{type(e).__name__}", [], None

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
    return oa_status, urls, work.get("title")


def visible_text(html_or_text):
    """Strip markup and collapse whitespace, so what is measured is prose."""
    try:
        import warnings

        from bs4 import BeautifulSoup

        with warnings.catch_warnings():
            # Europe PMC returns JATS XML; html.parser handles it fine for
            # text extraction, and bs4's "that looks like XML" warning is
            # noise on stderr the skill would otherwise have to read past.
            warnings.simplefilter("ignore")
            soup = BeautifulSoup(html_or_text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text(" ")
    except Exception:
        text = re.sub(r"<[^>]*>", " ", html_or_text)
    return re.sub(r"\s+", " ", text).strip()


def _squash(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def is_the_right_work(text, doi, title):
    """Does this text actually belong to the work we asked for?

    A page can be real prose and still be the wrong page -- a journal's
    article *listing* has thousands of words, no blocker markers, and
    nothing to do with the article. An article's own page or PDF almost
    always carries its DOI or its title, so require one of them.

    Returns (ok, reason). Unknown identity (no DOI and no title) passes:
    with nothing to check against, refusing would reject every --url-only
    fetch, which is the data-portal case.
    """
    if not doi and not title:
        return True, "identity_unchecked"
    squashed = _squash(text)
    if doi and _squash(doi) in squashed:
        return True, "doi_in_text"
    # Titles get typeset with line breaks, entities and smart quotes, so
    # compare on a squashed prefix rather than the whole string.
    if title:
        probe = _squash(title)[:60]
        if len(probe) >= 20 and probe in squashed:
            return True, "title_in_text"
    return False, "wrong_work:doi_and_title_absent"


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


def europepmc_fulltext(doi):
    """Full text via the Europe PMC API, or None.

    Preferred over scraping a PMC article page: it is a real API, returns
    JATS XML rather than a rendered page, and does not challenge repeat
    callers. Only open-access records expose fullTextXML -- everything else
    404s and falls through to the URL candidates.
    """
    doi = doi.strip().removeprefix("https://doi.org/").removeprefix("doi.org/")
    try:
        r = requests.get(EPMC_SEARCH.format(doi), headers=UA, timeout=30)
        if r.status_code != 200:
            return None
        hits = r.json().get("resultList", {}).get("result", [])
        if not hits or not hits[0].get("pmcid"):
            return None
        pmcid = hits[0]["pmcid"]
        r = requests.get(EPMC_FULLTEXT.format(pmcid), headers=UA, timeout=40)
        if r.status_code != 200:
            return None
    except (requests.RequestException, ValueError):
        return None
    return visible_text(r.text), f"https://europepmc.org/article/PMC/{pmcid}"


# Repository landing pages that answer a bot challenge instead of content, and
# the APIs that answer properly (#1786). Both were measured 2026-09-01: the
# Dataverse dataset page returns HTTP 202 with a ZERO-byte body regardless of
# user agent, while api/datasets/:persistentId returns 200 and 8.5kB of JSON for
# the same record; figshare's article page challenges while api.figshare.com
# does not. This cost w2 70% of its reachability in the 2.3 blind run -- nine of
# ten failures there were this, not paywalls, with OpenAlex reporting the
# records openly available.
#
# The metadata is thin on its own. Its real value is the RELATED PUBLICATION:
# a deposit usually names the paper it backs, and that DOI goes back through the
# ordinary OpenAlex/Europe PMC path, which is where usable prose lives. Deposit
# metadata is returned only when there is no such pointer, and is labelled so
# the caller can tell a paper from a catalogue record.
DATAVERSE_DOI_PREFIXES = ("10.7910/dvn",)
FIGSHARE_DOI_MARKERS = ("figshare",)
MIN_METADATA_CHARS = 300


def _dv_fields(payload):
    """Flatten a Dataverse citation metadata block to {typeName: value}."""
    blocks = (((payload.get("data") or {}).get("latestVersion") or {})
              .get("metadataBlocks") or {})
    fields = (blocks.get("citation") or {}).get("fields") or []
    return {f.get("typeName"): f.get("value") for f in fields}


def _dv_text(value):
    """Dataverse values are strings, lists, or compound dicts of dicts."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ; ".join(_dv_text(v) for v in value)
    if isinstance(value, dict):
        if "value" in value and not isinstance(value["value"], (dict, list)):
            return str(value["value"])
        return " ; ".join(_dv_text(v) for v in value.values())
    return ""


def dataverse_api(doi, url):
    """(text, source, related_doi) from a Dataverse record, or None."""
    host = "dataverse.harvard.edu"
    m = re.search(r"https?://([^/]+)/dataset\.xhtml", url or "")
    if m:
        host = m.group(1)
    elif not (doi or "").lower().startswith(DATAVERSE_DOI_PREFIXES):
        return None
    if not doi:
        m = re.search(r"persistentId=(doi:[^&\s]+)", url or "")
        doi = m.group(1).removeprefix("doi:") if m else None
    if not doi:
        return None
    api = f"https://{host}/api/datasets/:persistentId/?persistentId=doi:{doi}"
    try:
        r = requests.get(api, headers=UA, timeout=30)
        if r.status_code != 200:
            return None
        fields = _dv_fields(r.json())
    except (requests.RequestException, ValueError, AttributeError):
        return None
    if not fields:
        return None

    related = None
    for entry in (fields.get("publication") or []):
        if not isinstance(entry, dict):
            continue
        idn = _dv_text(entry.get("publicationIDNumber") or "")
        typ = _dv_text(entry.get("publicationIDType") or "").lower()
        if idn and ("doi" in typ or idn.startswith("10.")):
            related = idn.replace("https://doi.org/", "").strip()
            break

    parts = [f"{k}: {_dv_text(v)}" for k, v in fields.items() if v]
    return "\n".join(parts), api, related


def figshare_api(doi, url):
    """(text, source, related_doi) from a figshare record, or None.

    Covers figshare-hosted institutional repositories too -- York St John's
    10.25421/yorksj.* resolves through the same API.
    """
    art_id = None
    if doi and any(m in doi.lower() for m in FIGSHARE_DOI_MARKERS):
        m = re.search(r"figshare\.(\d+)", doi)
        art_id = m.group(1) if m else None
    if art_id is None:
        m = re.search(r"figshare\.com/articles/[^/]*/?(\d+)", url or "")
        art_id = m.group(1) if m else None
    try:
        if art_id is None and doi:
            r = requests.get("https://api.figshare.com/v2/articles",
                             params={"doi": doi}, headers=UA, timeout=30)
            if r.status_code != 200 or not r.json():
                return None
            art_id = r.json()[0]["id"]
        if art_id is None:
            return None
        api = f"https://api.figshare.com/v2/articles/{art_id}"
        r = requests.get(api, headers=UA, timeout=30)
        if r.status_code != 200:
            return None
        art = r.json()
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None

    related = (art.get("resource_doi") or "").replace("https://doi.org/", "").strip() or None
    keep = ("title", "description", "citation", "resource_title", "tags",
            "categories", "funding", "defined_type_name", "license")
    parts = []
    for k in keep:
        v = art.get(k)
        if not v:
            continue
        if isinstance(v, list):
            v = " ; ".join(x.get("title", "") if isinstance(x, dict) else str(x)
                           for x in v)
        elif isinstance(v, dict):
            v = v.get("name") or str(v)
        parts.append(f"{k}: {v}")
    return "\n".join(parts), api, related


def mendeley_api(doi, url):
    """(text, source, related_doi) from a Mendeley Data record, or None.

    Mendeley serves a JavaScript shell to an unauthenticated GET on some
    records but not others -- two of ten in the 2.3 run -- which reads as
    `too_short` rather than as a block. `public-api` answers for both.
    `api.data.mendeley.com` needs OAuth and 401s; this one does not.
    """
    ident = None
    m = re.search(r"data\.mendeley\.com/datasets/([A-Za-z0-9]+)", url or "")
    if m:
        ident = m.group(1)
    elif doi and "10.17632/" in doi.lower():
        ident = doi.lower().split("10.17632/", 1)[1].split(".")[0].strip("/")
    if not ident:
        return None
    api = f"https://data.mendeley.com/public-api/datasets/{ident}"
    try:
        r = requests.get(api, headers=UA, timeout=30)
        if r.status_code != 200:
            return None
        rec = r.json()
    except (requests.RequestException, ValueError):
        return None

    related = None
    for art in (rec.get("articles") or []):
        cand = (art.get("doi") or {})
        cand = cand.get("id") if isinstance(cand, dict) else cand
        if cand and str(cand).startswith("10."):
            related = str(cand)
            break

    keep = ("name", "description", "doi", "categories", "data_licence",
            "articles", "contributors", "institutions", "versions")
    parts = []
    for k in keep:
        v = rec.get(k)
        if not v:
            continue
        if isinstance(v, (list, dict)):
            v = json.dumps(v)[:2000]
        parts.append(f"{k}: {v}")
    return "\n".join(parts), api, related


# NOT a route: DataCite (api.datacite.org/dois/<doi>) answers 200 for every one
# of these DOIs and would look like a universal fallback, but its records are
# too thin to tag from -- 73 and 109 characters of description for the two
# Mendeley and Dataverse records measured, against a 300-character floor, and
# zero for the third. It would convert an honest UNREACHABLE into a success
# carrying nothing but a title. Each repository's own API is what has the
# description and the related-publication pointer.
def repository_api(doi, url):
    """Try every repository API that applies. Never raises."""
    for fn in (dataverse_api, figshare_api, mendeley_api):
        try:
            got = fn(doi, url)
        except Exception:                                  # noqa: BLE001
            got = None
        if got:
            return got
    return None


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


def try_url(url, doi=None, title=None):
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
    ok, reason = is_the_right_work(text, doi, title)
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
    title = None
    candidates = []
    if args.doi and not args.no_oa:
        oa_status, candidates, title = openalex_locations(args.doi)
    if args.doi:
        candidates.append(f"https://doi.org/{args.doi}")
    if args.url:
        candidates.append(args.url)

    attempted = []
    rejected = []

    # A repository API, before anything that could be challenged (#1786). If the
    # deposit names the paper it backs, that DOI is worth far more than the
    # deposit record, so adopt it and carry on down the ordinary path -- OpenAlex
    # locations, Europe PMC, then URLs -- exactly as if it had been passed in.
    repo = repository_api(args.doi, args.url)
    repo_text = repo_source = None
    if repo:
        repo_text, repo_source, related = repo
        if related and related != args.doi:
            print(f"NOTE {repo_source} names a related publication: {related}",
                  file=sys.stderr)
            args.doi = related
            oa_status, oa_urls, title = ("not_checked", [], None)
            if not args.no_oa:
                oa_status, oa_urls, title = openalex_locations(related)
            candidates = oa_urls + [f"https://doi.org/{related}"] + candidates

    # Europe PMC first: an API beats scraping a page that may be a captcha.
    if args.doi and not args.no_oa:
        got = europepmc_fulltext(args.doi)
        if got:
            text, source = got
            ok, reason = classify(text)
            if ok:
                ok, reason = is_the_right_work(text, args.doi, title)
            if ok:
                CACHE_DIR.mkdir(exist_ok=True)
                path.write_text(text, encoding="utf-8", errors="replace")
                print(f"OK oa_status={oa_status} source={source} "
                      f"final_url={source} content={reason} attempts=1 -> {path}")
                return
            rejected.append(f"{source} -> {reason}")
            attempted.append(source)

    for url in candidates:
        if url in attempted:
            continue
        attempted.append(url)
        time.sleep(REQUEST_DELAY_S)
        got, reason = try_url(url, args.doi, title)
        rejected.append(f"{url} -> {reason}")
        if got is None:
            continue
        text, final_url = got
        CACHE_DIR.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8", errors="replace")
        print(f"OK oa_status={oa_status} source={url} final_url={final_url} "
              f"content={reason} attempts={len(attempted)} -> {path}")
        return

    # Nothing else worked, but a repository record was readable. It is a
    # catalogue entry rather than a paper, so it is labelled as one and held to a
    # lower floor -- a deposit description is legitimately short. The tagger is
    # expected to leave fields blank rather than infer a sample or an age range
    # from this; vocab.md already says so, and the reason string is what tells it
    # which kind of source it is holding.
    if repo_text:
        prose = visible_text(repo_text)
        if len(prose) >= MIN_METADATA_CHARS:
            CACHE_DIR.mkdir(exist_ok=True)
            path.write_text(repo_text, encoding="utf-8", errors="replace")
            print(f"OK oa_status={oa_status} source={repo_source} "
                  f"final_url={repo_source} "
                  f"content=repository_metadata:{len(prose)}_chars_visible "
                  f"attempts={len(attempted) + 1} -> {path}")
            return
        rejected.append(f"{repo_source} -> repository_metadata_too_short:"
                        f"{len(prose)}_chars")

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
