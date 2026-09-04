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

Data repositories get their own route (#1786). Their web pages answer a bot
challenge or a JavaScript shell -- Dataverse returns HTTP 202 with a ZERO-byte
body whatever user agent you send, and every OSF project page is the same 4.2kB
of CSS -- while their APIs return the record. OSF, Dataverse, figshare and
Mendeley are asked through their APIs instead, and where the deposit names the
paper it backs, that DOI is adopted and followed down the ordinary path, which
is where usable prose lives. Deposit metadata is returned only as a fallback and
is labelled `repository_metadata` so the caller can tell a catalogue record from
a paper.

OSF is the one that matters most by volume: 1,065 of the dictionary's 4,330 rows
name it, more than Dataverse, figshare and Mendeley combined.

Usage:
    python fetch_source.py TABLE --doi 10.1037/a0022874
    python fetch_source.py TABLE --url https://example.org/page
    python fetch_source.py TABLE --doi ... --force    # re-fetch even if cached
    python fetch_source.py TABLE --doi ... --no-oa    # skip the OpenAlex lookup

Cache lives in ../.cache/ next to this scripts/ dir, one file per table --
gitignored, not committed (see tags/.gitignore).
"""
import argparse
import os
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
# One cache per run when asked for one. Concurrent taggers share this directory
# by default, and it has no locking: during the 2026-09-03 two-path comparison
# two agents reported files appearing that they had not fetched, and one watched
# its own entry vanish between fetching it and reading it, because another agent
# had --force'd the same table. Both worked around it by hand.
#
# `--cache-dir`, or IRW_TAG_CACHE, gives a run its own namespace so that cannot
# happen. The default is unchanged, so a single-agent run keeps sharing the
# cache across sessions -- which is the point of it: a paywalled or rate-limited
# source is not re-hit on every retry.
CACHE_DIR = Path(os.environ.get("IRW_TAG_CACHE") or
                 (Path(__file__).resolve().parent.parent / ".cache"))
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


def write_cache(path, text):
    """Write the cache entry so a concurrent reader never sees half of it.

    `Path.write_text` truncates the file and then fills it, so a reader that
    opens it in between gets an empty or partial file and reads it as the
    source. Writing to a unique temporary in the same directory and then
    os.replace()-ing it over the target makes the swap atomic: a reader holds
    either the whole old entry or the whole new one, never a torn one.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8", errors="replace")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


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


# A page can be long, blocker-free, and still be furniture. Spain's CIS
# barometer pages return ~16kB of visible Liferay/React menu text with the
# survey itself loaded client-side; they clear MIN_USEFUL_CHARS and trip no
# BLOCKER_MARKERS, and three independent raters in the 2026-09-03 two-path
# comparison mistook them for reachable sources before reading them.
#
# What separates chrome from prose is not length but SENTENCE DENSITY. Menu
# labels and JSON-LD fragments are not sentences. Measured over the 101 cached
# pages with >=8000 chars of prose, every CIS page falls between 1.48 and 1.77
# sentences per 1000 characters, the next page up is 3.36, and real articles run
# 3.7-7.8. The threshold sits in that gap.
#
# This WARNS, it does not reject. The failure it catches is rare in the corpus
# that still needs tagging -- of the 1,427 untagged tables, 543 are PLOS and
# ~400 are the four repositories #1789 routed through APIs, and none is a
# government CMS -- so rejecting on a heuristic would risk turning usable
# fetches into failures to prevent a problem the reader can already see once
# told to look. The reason string is what tells them to look.
LOW_DENSITY_MIN_CHARS = 8000
LOW_DENSITY_PER_1K = 2.5


def sentence_density(prose):
    """Sentences per 1000 characters. A sentence is >=8 words before a stop."""
    if not prose:
        return 0.0
    n = sum(1 for seg in re.split(r"[.!?]+", prose) if len(seg.split()) >= 8)
    return 1000.0 * n / len(prose)


def merge_reasons(identity, content):
    """Combine the identity verdict with the content verdict.

    These answer different questions -- `is_the_right_work` says WHICH work this
    is, `classify` says whether the page is readable prose -- and both can be
    worth saying at once. The caller used to get only the identity string,
    because `reason` was reassigned before it was returned, which silently threw
    away the low-density warning added for #1704: it is computed, it is correct,
    and it never once reached the output. Found on 2026-09-03 when a tagging
    agent asked what `content=doi_in_text` meant and there was no answer,
    because that label had displaced everything else.

    Only the warning is carried through. An ordinary `N_chars_visible` adds
    nothing to `doi_in_text` and would just make the line noisier.
    """
    if content.startswith("low_prose_density"):
        return f"{identity}+{content}"
    return identity


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
    density = sentence_density(prose)
    if len(prose) >= LOW_DENSITY_MIN_CHARS and density < LOW_DENSITY_PER_1K:
        return True, (f"low_prose_density:{density:.2f}_sentences_per_1k:"
                      f"{len(prose)}_chars_visible")
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


def osf_api(doi, url):
    """(text, source, related_doi) from an OSF node or preprint, or None.

    OSF is the largest single source in the dictionary -- 1,065 of 4,330 rows
    name it, more than Dataverse, figshare and Mendeley combined -- and every
    one of its project pages is the same 4.2kB JavaScript shell, which the
    fetcher correctly rejects as `too_short` and then has nothing else to try.
    The API answers 200 with the record.
    """
    ident = None
    m = re.search(r"osf\.io/([A-Za-z0-9]{5})", url or "")
    if m:
        ident = m.group(1)
    elif doi and "10.17605/osf.io/" in (doi or "").lower():
        ident = doi.lower().split("10.17605/osf.io/", 1)[1].strip("/ ")
    if not ident:
        return None

    attrs = None
    for kind in ("nodes", "preprints"):
        api = f"https://api.osf.io/v2/{kind}/{ident}/"
        try:
            r = requests.get(api, headers=UA, timeout=30)
            if r.status_code != 200:
                continue
            attrs = (r.json().get("data") or {}).get("attributes") or {}
        except (requests.RequestException, ValueError, AttributeError):
            continue
        if attrs:
            break
    if not attrs:
        return None

    # A preprint record names the published article; a project sometimes does.
    related = None
    for key in ("doi", "article_doi", "original_publication_doi"):
        v = attrs.get(key)
        if isinstance(v, str) and v.strip().startswith("10.") and "osf.io" not in v.lower():
            related = v.strip()
            break

    keep = ("title", "description", "category", "tags", "subjects",
            "date_published", "node_license")
    parts = []
    for k in keep:
        v = attrs.get(k)
        if not v:
            continue
        if isinstance(v, (list, dict)):
            v = json.dumps(v)[:1500]
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
    """Try every repository API that applies. Never raises.

    The DOI is normalised again here rather than only in main(), so this stays
    correct for anything that imports and calls it directly. Every prefix test
    below is a startswith/substring check, and a `https://doi.org/`-prefixed DOI
    silently skips the Dataverse route and falls through to the 202 page.
    """
    doi = (doi or "").strip()
    for pre in ("https://doi.org/", "http://doi.org/", "doi.org/", "doi:"):
        if doi.lower().startswith(pre):
            doi = doi[len(pre):]
            break
    doi = doi or None
    for fn in (dataverse_api, figshare_api, mendeley_api, osf_api):
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
    ok, content = classify(text)
    if not ok:
        return None, content
    ok, identity = is_the_right_work(text, doi, title)
    if not ok:
        return None, identity
    return (text, r.url), merge_reasons(identity, content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--doi")
    ap.add_argument("--url")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--cache-dir",
                    help="write the cache here instead of ../.cache. Give each "
                         "agent in a concurrent run its own, or they will "
                         "--force over one another's entries.")
    ap.add_argument("--no-oa", action="store_true",
                    help="skip the OpenAlex lookup and resolve the DOI directly")
    args = ap.parse_args()

    if not args.doi and not args.url:
        ap.error("provide --doi or --url")

    # The dictionary stores some DOIs bare and others as
    # `https://doi.org/10.…`. Normalise ONCE here: every consumer below either
    # tests a prefix (the repository routes) or builds `https://doi.org/{doi}`
    # (the candidate list), and the prefixed form silently breaks both -- it
    # skipped the Dataverse route and produced a doubled, 404-ing URL. Caught
    # 2026-09-01 on feng2026_autonomy.
    if args.doi:
        d = args.doi.strip()
        for pre in ("https://doi.org/", "http://doi.org/", "doi.org/", "doi:"):
            if d.lower().startswith(pre):
                d = d[len(pre):]
                break
        args.doi = d

    global CACHE_DIR
    if args.cache_dir:
        CACHE_DIR = Path(args.cache_dir)
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
            ok, content = classify(text)
            reason = content
            if ok:
                ok, identity = is_the_right_work(text, args.doi, title)
                reason = merge_reasons(identity, content) if ok else identity
            if ok:
                write_cache(path, text)
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
        write_cache(path, text)
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
            write_cache(path, repo_text)
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
