"""
irw_discover.py
===============
Discovery-only pipeline for finding candidate datasets to contribute to the
Item Response Warehouse (IRW). No scoring, no validation, no coercion — its one
job is to cast a wide net across open-data repositories and hand you a clean,
deduplicated list of candidates to review by hand.

Three things this does that a naive search doesn't:
  - SOURCES   : queries 5 repositories, not 1 (breadth = recall)
  - PAGINATION: walks every page per source, so you don't miss results
  - DEDUP     : merges by DOI across sources, falls back to title
  - EXCLUDE   : automatically skips datasets already in the IRW and datasets
                already queued for processing. Both exclusion sets are fetched
                live from Google Sheets on every run (_load_auto_exclusions())
                — the IRW dictionary sheet and the processing queue sheet.
                No local file to maintain.

The processing queue is a Google Sheet maintained manually — add a row whenever
you decide to process a candidate from the triage output. Future discovery runs
will fetch the sheet and exclude those DOIs automatically.

Run:
    python irw_discover_updated.py "self-efficacy scale" "reading assessment"
    python irw_discover_updated.py --all "questionnaire"   # disable relevance filter
"""

from __future__ import annotations

import os
import sys
import re
import csv
import time
import argparse
from dataclasses import dataclass, asdict

import requests

UA = {"User-Agent": "irw-discovery-scout/1.0 (research; contact your-email)"}

# ---------------------------------------------------------------------------
# RELEVANCE FILTER (tiered)
# ---------------------------------------------------------------------------
# IRW membership is STRUCTURAL (person x item x ordinal response), not topical,
# and a title can't reveal structure — so this filter's job is RECALL: let real
# data through and only block the obvious noise. The triage stage does the
# precision work (content gate + format validator).
#
# How matching works:
#   * a title with ANY strong or construct term  -> PASS
#   * ambiguous terms ("test", "scale", "survey") do NOT pass on their own,
#     because alone they match geology surveys, stress tests, soil scales, etc.
#     They only add confidence alongside a strong/construct term.
#
# To tune: add the construct words for the domains you care about, or move a
# word between tiers. To turn the filter off entirely, run with --all.

STRONG_TERMS = [          # psychometric structure/method — rarely outside the field
    "item response", "item-level", "item response theory", "irt", "rasch",
    "psychometric", "questionnaire", "likert", "self-report", "factor analysis",
    "latent trait", "test battery", "item bank", "polytomous", "dichotomous",
    "construct validity", "measurement invariance", "response data",
    "reaction time", "response latency", "curriculum-based measurement",
]
CONSTRUCT_TERMS = [       # things the IRW actually measures (its construct_type tags)
    # education / ability
    "ability", "aptitude", "achievement", "proficiency", "numeracy", "literacy",
    "vocabulary", "reading comprehension", "grammar", "arithmetic", "spelling",
    "intelligence", "cognitive", "working memory", "knowledge test",
    "phonological awareness", "reading fluency", "mathematics achievement",
    "science achievement",
    # executive function / cognitive control
    "executive function", "inhibitory control", "cognitive flexibility",
    "task switching", "set shifting", "processing speed",
    # personality / clinical
    "personality", "big five", "depression", "anxiety", "well-being", "wellbeing",
    "self-esteem", "mood", "affect", "temperament", "psychopathology",
    "quality of life", "fear of missing out",
    # attitudes / other
    "attitude", "partisanship", "preference",
]
AMBIGUOUS_TERMS = [       # match too much alone; only count WITH a term above
    "test", "scale", "survey", "assessment", "rating", "inventory",
    "responses", "measure", "score", "battery",
]

# EXCLUSIONS: clinical/epidemiology study language. A construct word like
# "depression" pulls in huge amounts of MEDICAL research that studies the
# outcome without measuring it via item responses (e.g. "aspirin and risk of
# depression"). A title with any of these is blocked even if it names a
# construct, because it's a study ABOUT a condition, not item-response data.
EXCLUDE_TERMS = [
    "risk of", "cross-sectional", "case-control", "cohort study",
    "odds ratio", "hazard ratio", "relative risk", "prevalence", "incidence",
    "mortality", "meta-analysis", "systematic review", "biomarker",
    "comorbidit", "all-cause", "etiology", "aetiology", "pathogenesis",
    "association between",
]

# WIDELY-USED INSTRUMENTS — named scales used across thousands of studies.
# An instrument name is the highest-precision signal there is: a title saying
# "PHQ-9" or "Rosenberg" is almost certainly real item-response data. These
# pass on their own and also catch acronym-only titles (TROG, WAIS) that the
# construct terms miss. Add the instruments for the constructs you care about.
INSTRUMENT_TERMS = [
    # personality
    "big five inventory", "bfi", "neo-pi", "neo-ffi", "ipip", "hexaco",
    "eysenck personality", "epq", "16pf", "mbti", "dark triad", "sd3",
    "dirty dozen",
    # depression
    "beck depression", "bdi", "phq-9", "phq", "ces-d", "hamilton depression",
    "madrs", "geriatric depression", "gds",
    # anxiety
    "gad-7", "state-trait anxiety", "stai", "beck anxiety", "bai",
    "hospital anxiety and depression", "hads",
    # affect / well-being / life satisfaction
    "panas", "positive and negative affect", "satisfaction with life", "swls",
    "warwick-edinburgh", "wemwbs", "ryff",
    # self-esteem / stress / resilience / burnout / loneliness
    "rosenberg", "rses", "perceived stress scale", "pss", "brief cope",
    "connor-davidson", "cd-risc", "maslach burnout", "mbi", "ucla loneliness",
    # cognitive ability / intelligence
    "raven's progressive matrices", "progressive matrices", "wechsler", "wais",
    "wisc", "icar", "stanford-binet",
    # executive function tasks
    "stroop", "trail making", "flanker", "stop signal", "n-back",
    "brixton", "wisconsin card sorting", "tower of london", "tower of hanoi",
    "behavior rating inventory of executive function", "brief-a",
    # educational achievement / reading
    "woodcock-johnson", "dibels", "aimsweb", "kaufman assessment", "kabc",
    "dynamic indicators of basic early literacy",
    # values / language / large-scale assessments
    "schwartz values", "portrait values", "peabody picture vocabulary", "ppvt",
    "test for reception of grammar", "trog",
    "pisa", "timss", "pirls", "naep",
]

# Compile word-boundary matchers so short acronyms are safe (e.g. "irt" won't
# match inside "shirt", "bai" won't match inside "bait").
def _matcher(terms):
    return re.compile(r"\b(?:" + "|".join(re.escape(t) for t in terms) + r")\b")

_RE_INSTRUMENT = _matcher(INSTRUMENT_TERMS)
_RE_STRONG     = _matcher(STRONG_TERMS)
_RE_CONSTRUCT  = _matcher(CONSTRUCT_TERMS)
_RE_EXCLUDE    = _matcher(EXCLUDE_TERMS)

# Supplementary-file titles: journal papers upload individual tables, figures,
# and data sheets as repository items. These are never standalone datasets and
# reliably have no downloadable tabular file. Block them unconditionally.
_RE_SUPPLEMENTARY = re.compile(
    r"^(?:table\s+\d+[_\s]|data\s+sheet\s+\d+[_\s]|"
    r"supplementary\s+(?:file|material|table|figure|data)\b|"
    r"figure\s+\d+[_\s]|appendix\s*\d*[_:\s])"
    # DataCite-specific: SAGE/Springer supplemental files named "sj-ext-N-jrnl-doi"
    r"|^sj-[a-z]+-\d+-"
    # Anything flagged mid-title as supplemental material for a paper
    r"|\bsupplemental\s+material\s+for\b"
    # Software/package files accidentally filed as datasets (.tar, version strings)
    r"|_\d+\.\d+\.\d+\.tar$",
    re.IGNORECASE
)


@dataclass
class Hit:
    source: str
    title: str
    url: str
    doi: str = ""
    published: str = ""


def norm_doi(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi:\s*", "", s)
    return s


def is_relevant(h: Hit, enabled: bool) -> bool:
    """Relevant if the title names an instrument, or carries a strong/construct
    signal — and isn't clinical/epi study language. Word-boundary matched so
    short acronyms don't match inside other words. Ambiguous words don't pass.
    Named instruments override the exclusion gate: a validation study of the
    PHQ-9 in a clinical cohort still has the item-response data we want."""
    if not enabled:
        return True
    # Supplementary file naming convention — never a standalone dataset, always
    # blocked regardless of content or instrument mentions.
    if _RE_SUPPLEMENTARY.search(h.title):
        return False
    text = h.title.lower()
    # Named instrument always passes — validation studies have the data.
    if _RE_INSTRUMENT.search(text):
        return True
    # Epi/medical study language blocks everything else.
    if _RE_EXCLUDE.search(text):
        return False
    return bool(_RE_STRONG.search(text) or _RE_CONSTRUCT.search(text))


# ---------------------------------------------------------------------------
# Source connectors — each yields Hit objects, paginating to exhaustion.
# ---------------------------------------------------------------------------

def from_dataverse(query: str, max_pages: int = 5, per: int = 50):
    start = 0
    for _ in range(max_pages):
        try:
            r = requests.get(
                "https://dataverse.harvard.edu/api/search",
                params={"q": query, "type": "dataset", "per_page": per, "start": start},
                headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json().get("data", {})
            items = data.get("items", [])
        except Exception as e:
            print(f"[dataverse] {e}", file=sys.stderr); return
        if not items:
            return
        for it in items:
            yield Hit("dataverse", it.get("name", ""), it.get("url", ""),
                      norm_doi(it.get("global_id", "")), it.get("published_at", ""))
        start += per
        if start >= data.get("total_count", 0):
            return
        time.sleep(0.5)


def from_zenodo(query: str, max_pages: int = 5, per: int = 25):
    query = query.replace("-", " ")   # Zenodo returns 400 on hyphenated queries
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://zenodo.org/api/records",
                params={"q": query, "size": per, "page": page, "type": "dataset"},
                headers=UA, timeout=30)
            r.raise_for_status()
            hits = r.json().get("hits", {}).get("hits", [])
        except Exception as e:
            print(f"[zenodo] {e}", file=sys.stderr); return
        if not hits:
            return
        for h in hits:
            md = h.get("metadata", {})
            yield Hit("zenodo", md.get("title", ""),
                      h.get("links", {}).get("html", ""),
                      norm_doi(h.get("doi", "")), md.get("publication_date", ""))
        time.sleep(0.5)


def from_osf(query: str, max_pages: int = 5, per: int = 50):
    url = "https://api.osf.io/v2/nodes/"
    params = {"filter[tags]": query, "page[size]": per}
    for _ in range(max_pages):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=30)
            r.raise_for_status()
            body = r.json()
        except Exception as e:
            print(f"[osf] {e}", file=sys.stderr); return
        for node in body.get("data", []):
            a = node.get("attributes", {})
            yield Hit("osf", a.get("title", ""),
                      node.get("links", {}).get("html", ""),
                      "", a.get("date_created", ""))
        nxt = body.get("links", {}).get("next")
        if not nxt:
            return
        url, params = nxt, {}
        time.sleep(0.5)


def from_dryad(query: str, max_pages: int = 5, per: int = 50):
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://datadryad.org/api/v2/search",
                params={"q": query, "per_page": per, "page": page},
                headers=UA, timeout=30)
            r.raise_for_status()
            sets = r.json().get("_embedded", {}).get("stash:datasets", [])
        except Exception as e:
            print(f"[dryad] {e}", file=sys.stderr); return
        if not sets:
            return
        for d in sets:
            yield Hit("dryad", d.get("title", ""),
                      f"https://datadryad.org/dataset/{d.get('identifier','')}",
                      norm_doi(d.get("identifier", "")),
                      d.get("publicationDate", ""))
        time.sleep(0.5)


def from_figshare(query: str, max_pages: int = 5, per: int = 50):
    for page in range(1, max_pages + 1):
        try:
            r = requests.post(
                "https://api.figshare.com/v2/articles/search",
                json={"search_for": query, "page_size": per, "page": page,
                      "item_type": 3},  # 3 = dataset
                headers=UA, timeout=30)
            r.raise_for_status()
            arts = r.json()
        except Exception as e:
            print(f"[figshare] {e}", file=sys.stderr); return
        if not arts:
            return
        for a in arts:
            yield Hit("figshare", a.get("title", ""), a.get("url_public_html", ""),
                      norm_doi(a.get("doi", "")), a.get("published_date", ""))
        time.sleep(0.5)


def from_gesis(query: str, max_pages: int = 5, per: int = 25):
    """GESIS Vitrine API — Elasticsearch-backed social/behavioral science archive."""
    for page in range(max_pages):
        try:
            r = requests.get(
                "https://api.vitrine.gesis.org/search/gesis-soda/_search",
                params={"q": query, "size": per, "from": page * per},
                headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json()
            hits = data.get("hits", {}).get("hits", [])
        except Exception as e:
            print(f"[gesis] {e}", file=sys.stderr); return
        if not hits:
            return
        for h in hits:
            s = h.get("_source", {})
            title_obj = s.get("title", {})
            title = title_obj.get("en") or title_obj.get("pref", "")
            handles = s.get("handles", [])
            doi = handles[0].get("notation", "") if handles else ""
            url = handles[0].get("url", "") if handles else ""
            pubs = s.get("publications", [{}])
            published = pubs[0].get("startDate", "") if pubs else ""
            yield Hit("gesis", title, url, norm_doi(doi), published)
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        if (page + 1) * per >= total:
            return
        time.sleep(0.5)


# Publishers already covered by other connectors — skip their DataCite records
# to avoid duplicate candidates (DOI dedup catches exact matches, but publisher
# filtering avoids pulling in thousands of Zenodo/Figshare records we already have).
_DATACITE_SKIP = {
    "zenodo", "figshare", "dryad data", "harvard dataverse",
    "open science framework", "osf",
}

def from_datacite(query: str, max_pages: int = 5, per: int = 25):
    """DataCite REST API — aggregates datasets from ICPSR, UK Data Service, DANS,
    and hundreds of other repositories not covered by the other connectors."""
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://api.datacite.org/dois",
                params={"query": query, "resource-type-id": "dataset",
                        "page[size]": per, "page[number]": page},
                headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json()
            items = data.get("data", [])
        except Exception as e:
            print(f"[datacite] {e}", file=sys.stderr); return
        if not items:
            return
        for item in items:
            a = item.get("attributes", {})
            publisher = a.get("publisher", "").lower()
            if any(s in publisher for s in _DATACITE_SKIP):
                continue
            titles = a.get("titles", [{}])
            title = titles[0].get("title", "") if titles else ""
            doi = a.get("doi", "")
            url = a.get("url", "") or f"https://doi.org/{doi}"
            published = str(a.get("publicationYear", ""))
            # Strip version suffixes (e.g. 10.3886/icpsr21661.v3) for cleaner dedup
            doi_norm = re.sub(r"\.v\d+$", "", norm_doi(doi))
            yield Hit("datacite", title, url, doi_norm, published)
        meta = data.get("meta", {})
        if page >= meta.get("totalPages", 1):
            return
        time.sleep(0.5)


def _dataverse_connector(name: str, base_url: str):
    """Generate a Dataverse-compatible source function for a given instance."""
    def fn(query: str, max_pages: int = 5, per: int = 50):
        start = 0
        for _ in range(max_pages):
            try:
                r = requests.get(
                    f"{base_url}/api/search",
                    params={"q": query, "type": "dataset", "per_page": per, "start": start},
                    headers=UA, timeout=30)
                r.raise_for_status()
                data = r.json().get("data", {})
                items = data.get("items", [])
            except Exception as e:
                print(f"[{name}] {e}", file=sys.stderr); return
            if not items:
                return
            for it in items:
                yield Hit(name, it.get("name", ""), it.get("url", ""),
                          norm_doi(it.get("global_id", "")), it.get("published_at", ""))
            start += per
            if start >= data.get("total_count", 0):
                return
            time.sleep(0.5)
    fn.__name__ = f"from_{name}"
    return fn


from_scholars_portal = _dataverse_connector(
    "scholars_portal", "https://dataverse.scholarsportal.info")
from_surf            = _dataverse_connector("surf", "https://dataverse.nl")
from_aussda          = _dataverse_connector("aussda", "https://data.aussda.at")


def from_openaire(query: str, max_pages: int = 5, per: int = 25):
    """OpenAIRE — European open research aggregator (EU-funded datasets)."""
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                "https://api.openaire.eu/search/datasets",
                params={"keywords": query, "size": per, "page": page, "format": "json"},
                headers=UA, timeout=30)
            r.raise_for_status()
            data = r.json()
            results = data.get("response", {}).get("results", {}).get("result", [])
            total = int(data.get("response", {}).get("header", {}).get("total", {}).get("$", 0))
        except Exception as e:
            print(f"[openaire] {e}", file=sys.stderr); return
        if not results:
            return
        for res in results:
            md = res.get("metadata", {}).get("oaf:entity", {}).get("oaf:result", {})
            t = md.get("title", [])
            if isinstance(t, list) and t:
                title = t[0].get("$", "")
            elif isinstance(t, dict):
                title = t.get("$", "")
            else:
                title = ""
            pids = md.get("pid", [])
            doi = ""
            for p in (pids if isinstance(pids, list) else [pids]):
                if isinstance(p, dict) and p.get("@classid") == "doi":
                    doi = p.get("$", "")
                    break
            url_obj = md.get("url", {})
            url = url_obj.get("$", "") if isinstance(url_obj, dict) else ""
            if not url and doi:
                url = f"https://doi.org/{doi}"
            dates = md.get("dateofacceptance", {})
            published = dates.get("$", "")[:10] if isinstance(dates, dict) else ""
            yield Hit("openaire", title, url, norm_doi(doi), published)
        if page * per >= total:
            return
        time.sleep(0.5)


# Also update skip list so DataCite doesn't duplicate our new Dataverse instances
_DATACITE_SKIP.update({"scholars portal", "scholars portal dataverse", "surf",
                        "aussda", "austrian social science data archive"})


SOURCES = [from_dataverse, from_zenodo, from_osf, from_dryad, from_figshare,
           from_datacite, from_scholars_portal, from_surf]

SOURCE_MAP = {fn.__name__.replace("from_", ""): fn for fn in SOURCES}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Processing queue: DOIs decided for processing but not yet landed in the IRW.
# Managed manually in this Google Sheet (must be shared "anyone with link can view"):
QUEUE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8/export?format=csv&gid=0"
)

# IRW dictionary: authoritative list of what is already in the warehouse.
DICT_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/export?format=csv&gid=0"
)


def _extract_doi_from_url(url: str) -> str | None:
    """Best-effort extraction of a normalised DOI from a data repository URL."""
    if not url:
        return None
    # doi.org resolver
    m = re.search(r'doi\.org/(.+?)(?:\s|$)', url)
    if m:
        return norm_doi(m.group(1))
    # Harvard Dataverse persistent ID
    m = re.search(r'persistentId=doi:(.+?)(?:&|$)', url, re.I)
    if m:
        return norm_doi(m.group(1))
    # OSF project page
    m = re.search(r'osf\.io/([a-z0-9]+)/?$', url, re.I)
    if m:
        return norm_doi(f'10.17605/osf.io/{m.group(1)}')
    # Zenodo record page
    m = re.search(r'zenodo\.org/record/(\d+)', url)
    if m:
        return norm_doi(f'10.5281/zenodo.{m.group(1)}')
    # Figshare article page (any subdomain)
    m = re.search(r'figshare\.com/articles/[^/]+/(\d+)', url)
    if m:
        return norm_doi(f'10.6084/m9.figshare.{m.group(1)}')
    return None


def _load_queued_from_sheet() -> set:
    """Fetch queued DOIs from the IRW processing queue Google Sheet."""
    try:
        r = requests.get(QUEUE_SHEET_URL, timeout=15)
        r.raise_for_status()
        dois = set()
        for row in csv.reader(r.text.splitlines()):
            for cell in row:
                d = norm_doi(cell)
                if "/" in d and d.count(" ") == 0:
                    dois.add(d)
        return dois
    except Exception as e:
        print(f"[warn] Could not fetch processing queue from Google Sheet: {e}",
              file=sys.stderr)
        return set()


def _load_existing_irw_dois() -> set:
    """Fetch DOIs of datasets already in the IRW dictionary Google Sheet."""
    try:
        r = requests.get(DICT_SHEET_URL, timeout=15)
        r.raise_for_status()
        reader = csv.DictReader(r.text.splitlines())
        dois = set()
        for row in reader:
            url_doi = _extract_doi_from_url(row.get("URL (for data)", ""))
            if url_doi:
                dois.add(url_doi)
            paper_doi = norm_doi(row.get("DOI (for paper)", "") or "")
            if "/" in paper_doi and " " not in paper_doi:
                dois.add(paper_doi)
        return dois
    except Exception as e:
        print(f"[warn] Could not fetch IRW dictionary from Google Sheet: {e}",
              file=sys.stderr)
        return set()


def _load_auto_exclusions() -> set:
    """Load DOIs to exclude: already in the IRW dictionary + in the processing queue."""
    existing = _load_existing_irw_dois()
    queued = _load_queued_from_sheet()
    total = existing | queued
    print(f"[exclude] {len(existing)} DOIs already in IRW, "
          f"{len(queued)} in processing queue → {len(total)} total excluded",
          flush=True)
    return total


def discover(queries, exclude: set, relevance_on: bool, sources=None,
             on_hit=None) -> list:
    """Discover candidates across all sources for each query.

    on_hit: optional callable(Hit) invoked immediately when a new candidate
    passes all filters — use this to write results incrementally rather than
    waiting for the full run to finish.
    """
    import time as _time
    active = sources if sources is not None else SOURCES
    seen, results = set(), []
    total = len(queries)
    t0 = _time.time()
    for i, q in enumerate(queries, 1):
        q_new = 0
        q_start = _time.time()
        print(f"[query {i}/{total}] {q}", flush=True)
        for src in active:
            src_new = 0
            for hit in src(q):
                key = hit.doi or f"{hit.source}:{hit.title.strip().lower()}"
                if not key or key in seen:
                    continue
                if hit.doi and hit.doi in exclude:
                    continue
                if not is_relevant(hit, relevance_on):
                    continue
                seen.add(key)
                results.append(hit)
                q_new += 1
                src_new += 1
                if on_hit:
                    on_hit(hit)
            if src_new:
                print(f"  [{src.__name__:20}] +{src_new}", flush=True)
        elapsed = _time.time() - t0
        print(f"  → {q_new} new this query | {len(results)} total | "
              f"{elapsed:.0f}s elapsed", flush=True)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*", default=["item response theory"])
    ap.add_argument("--all", action="store_true", help="disable relevance filter")
    ap.add_argument("--out", default="candidates.csv")
    ap.add_argument("--sources", metavar="NAME", nargs="+",
                    help=f"query only these sources (choices: {', '.join(SOURCE_MAP)})")
    args = ap.parse_args()

    queries = args.queries or ["item response theory"]

    if args.sources:
        unknown = set(args.sources) - set(SOURCE_MAP)
        if unknown:
            ap.error(f"Unknown sources: {', '.join(unknown)}. Choices: {', '.join(SOURCE_MAP)}")
        active_sources = [SOURCE_MAP[s] for s in args.sources]
        print(f"Querying sources: {', '.join(args.sources)}")
    else:
        active_sources = None

    queued_dois = _load_auto_exclusions()
    exclude = queued_dois

    if queued_dois:
        print(f"Excluding {len(queued_dois):,} DOIs already queued for processing  (Google Sheet)")
    print(f"[note] IRW duplicate check runs at the start of Step 2 (irw_process_queue.py).")
    print()

    fieldnames = ["source", "title", "doi", "published", "url"]
    outf = open(args.out, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()
    outf.flush()

    hits = []

    def on_hit(h):
        hits.append(h)
        writer.writerow(asdict(h))
        outf.flush()

    discover(queries, exclude, relevance_on=not args.all, sources=active_sources,
             on_hit=on_hit)
    outf.close()

    print(f"{len(hits)} candidates found -> {args.out}")
    for h in hits[:25]:
        print(f"  [{h.source:9}] {h.title[:70]}")


if __name__ == "__main__":
    main()
