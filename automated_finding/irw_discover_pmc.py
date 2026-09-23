"""
irw_discover_pmc.py
=====================
Generalizes the irw_discover_plos.py approach (search a single open-access
journal directly, pull attached Supporting Information files, no repository
involved) to any journal that's well-indexed in Europe PMC, instead of
hand-writing a new HTML scraper per publisher.

Why this works as one connector for many journals, where irw_discover_plos.py
needed a publisher-specific scraper: Europe PMC's `{PMCID}/supplementaryFiles`
endpoint returns an article's SI archive the same way regardless of
publisher (PLOS, BMC, PeerJ, Nature, SAGE, ...), as long as the article is
deposited in PMC. That sidesteps the "BMC needs a new per-site parser,
Frontiers is an unscrapable JS SPA" problem noted for the journal-by-journal
scraping approach (see SKILL.md's "Generalizing to other journals" section)
-- this connector never touches a publisher's own website at all.

JOURNALS below is NOT every journal in journal_scout's output -- it's the
"harvest now" / "sample manually first" tiers from
journal_scout/journal_yield_summary.md, MINUS the PLOS family (PLOS ONE,
PLOS Global Public Health, PLOS Medicine, PLOS Digital Health, PLOS Mental
Health all scored well but are already covered by irw_discover_plos.py's
own api.plos.org-based connector -- kept as-is per 2026-08-11 decision, not
migrated here, to avoid running two discovery paths over the same journals
and to not touch a pipeline that's already working). Journals journal_scout
flagged "skip" or "not reachable this way" are deliberately excluded --
don't add a journal here without a yield measurement backing it up (see
SKILL.md's "don't build a new-journal connector speculatively" rule, which
this script's existence is itself an application of, one level up).

Two-phase, same shape as irw_discover_plos.py:
  1. search_pmc(query, issn)  cheap: Europe PMC search API, resultType=lite
     (title + a `hasSuppl` flag, no full record), restricted to one journal
     ISSN, OA + full-text only. Candidates with hasSuppl != 'Y' are dropped
     immediately -- no chance of a usable file, so no point spending a
     second request on them.
  2. process_one(hit)  per candidate: one core-record lookup (for license +
     abstract-informed relevance is NOT re-checked here, title-only
     matches the rest of the codebase's convention -- see is_relevant()),
     then the supplementaryFiles archive itself. Reads the zip's manifest
     in memory, picks the first tabular-looking file, and runs it through
     the SAME triage_dataset()/load_table() gate every other connector
     uses.

  3. If (2) yields no tabular file, the article's Data Availability
     statement is read from its JATS full text and any deposit it names is
     handed to irw_batch_updated's resolvers, via the link handling
     shared with irw_discover_plos.py (`triage_external_link`, which lives
     in irw_batch_updated so neither connector imports the other).

This step used to be skipped, on the reasoning that the supplementaryFiles
endpoint is the point of this connector and that chasing DAS-linked repos
was the repo pipeline's job anyway. Both halves turned out to be wrong.
Nothing else reaches these deposits: the repo connectors search repository
indexes, and a deposit is only found there if its own metadata matches a
construct term -- an article's data file usually does not. And the cost
argument does not survive measurement: the full text averages 137 KB
against the ~367 KB supplementary zip already downloaded for every
candidate, and it is fetched only on the failure path. PLOS made exactly
this mistake and it cost 395 recoverable candidates (#2191, #2193); of a
random 20 PMC candidates retired as `no_usable_file`, 5 name a deposit the
resolvers can read.

Run:
    python irw_discover_pmc.py "self-efficacy scale" "reading assessment" --out pmc_triage.csv
    python irw_discover_pmc.py "PHQ-9" --limit 10 --out pmc_test.csv   # sanity check first
    python irw_discover_pmc.py "term" --journals peerj,heliyon --out pmc_triage.csv
"""

from __future__ import annotations

import re
import csv
import io
import time
import zipfile
import argparse
from urllib.parse import urlencode
from concurrent.futures import ProcessPoolExecutor, BrokenExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

import requests

from irw_discover_updated import (
    Hit, is_relevant, norm_doi, _load_auto_exclusions, in_runs_dir,
)
from irw_batch_updated import (
    check_license, TABULAR_EXT, polite_get, FileTooLarge,
    extract_external_link, triage_external_link,
)
from irw_triage_updated import load_table, triage_dataset, preflight_deps

EUROPEPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
# includeInlineImage=false is load-bearing, not an optimisation. Without it
# Europe PMC packages every inline figure into the zip, and for a large
# fraction of articles that packaging step dies with a 500 -- which the
# 2026-09-02 weekly run recorded as `download_failed` for 37 of 60
# candidates, all CC-BY with hasSuppl=Y. Re-requesting those 37 with the
# flag set recovered 36. It also shrinks the download to the files we
# actually read (tabular supplements), so it is faster besides.
EUROPEPMC_SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
                   "{pmcid}/supplementaryFiles?includeInlineImage=false")
# Full text, for the Data Availability statement. The core record does NOT
# carry it: it has hasData/dataLinksTagsList but no statement text and no
# repository URL, and the /datalinks endpoint answers 500. Measured over 20
# articles (2026-09-16): mean 137 KB, max 243 KB -- smaller than the
# supplementary zip this connector already downloads for every candidate,
# and fetched only after that zip has failed to yield a tabular file.
EUROPEPMC_FULLTEXT = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
                      "{pmcid}/fullTextXML")
ARTICLE_URL = "https://europepmc.org/article/PMC/{pmcid}"

# slug -> (issn_l, display name). See module docstring for how this list
# was chosen -- it's journal_scout's measured output, not a guess.
JOURNALS = {
    # harvest now (non-PLOS; PLOS family stays on irw_discover_plos.py)
    "peerj": ("2167-8359", "PeerJ"),
    "screports": ("2045-2322", "Scientific Reports"),
    "jofintelligence": ("2079-3200", "Journal of Intelligence"),
    # sample manually first
    "mbr": ("0027-3171", "Multivariate Behavioral Research"),
    "behavsci": ("2076-328X", "Behavioral Sciences"),
    "apm": ("0146-6216", "Applied Psychological Measurement"),
    "bmcmrm": ("1471-2288", "BMC Medical Research Methodology"),
    "jopd": ("2050-9863", "Journal of Open Psychology Data"),
    "bmcpubhealth": ("1471-2458", "BMC Public Health"),
    "heliyon": ("2405-8440", "Heliyon"),
    "psychometrika": ("0033-3123", "Psychometrika"),
}
DEFAULT_JOURNALS = ",".join(JOURNALS)


# ---------------------------------------------------------------------------
# Phase 1: discover — cheap Europe PMC search, resultType=lite
# ---------------------------------------------------------------------------

# Count of search queries that exhausted their retries. A failed query is
# otherwise indistinguishable from a query that legitimately returned nothing,
# which is how the 2026-08-19 backlog sweep logged "100/100 terms visited"
# while roughly two thirds of them never actually ran. Read this at the end of
# a run and put it in the search_terms_log note.
SEARCH_FAILURES = 0


def _europepmc_get(params: dict) -> dict | None:
    """GET against the Europe PMC search endpoint, through polite_get so
    every call (search and file download alike) shares one per-domain rate
    limit against www.ebi.ac.uk.

    Returns None only after all retries are exhausted, and bumps
    SEARCH_FAILURES when it does. HTTPError is retried alongside the
    connection errors: Europe PMC returns transient 404s and stub bodies
    under load, and treating those as "no results" silently empties a sweep.
    """
    global SEARCH_FAILURES
    url = EUROPEPMC_SEARCH + "?" + urlencode(params)
    for attempt in range(4):
        try:
            r = polite_get(url)
            return r.json()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError,
                ValueError) as e:   # ValueError covers a non-JSON stub body
            if attempt == 3:
                SEARCH_FAILURES += 1
                print(f"[pmc] QUERY FAILED after 4 attempts: {e}", flush=True)
                return None
            wait = 5 * (attempt + 1)
            print(f"[pmc] transient error, retrying in {wait}s: {e}", flush=True)
            time.sleep(wait)
        except Exception as e:
            SEARCH_FAILURES += 1
            print(f"[pmc] QUERY FAILED: {e}", flush=True)
            return None
    return None


def search_pmc(query: str, issn: str, max_rows: int = 300, page_size: int = 100):
    """Yields raw Europe PMC lite result dicts for a full-text query,
    restricted to one journal ISSN, OA + full-text only. Paginates via
    cursorMark until max_rows or results are exhausted."""
    cursor = "*"
    fetched = 0
    while fetched < max_rows:
        data = _europepmc_get({
            "query": f'{query} AND ISSN:"{issn}" AND HAS_FT:y AND OPEN_ACCESS:y',
            "resultType": "lite",
            "pageSize": page_size,
            "cursorMark": cursor,
            "format": "json",
        })
        if not data:
            return
        results = data.get("resultList", {}).get("result", [])
        if not results:
            return
        for r in results:
            yield r
        fetched += len(results)
        next_cursor = data.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            return
        cursor = next_cursor


def from_pmc(query: str, journal: str):
    """Discovery connector, same shape as irw_discover_updated.py's from_*
    functions and irw_discover_plos.py's from_plos(). Relevance filtering
    is title-only, matching the rest of the codebase's from_* connectors
    (not PLOS's title+abstract special case -- Europe PMC's lite result
    doesn't carry an abstract, and fetching one via resultType=core for
    every search hit just to filter would double Phase-1's request count
    for no proven benefit over the title-only convention used elsewhere)."""
    issn, _ = JOURNALS[journal]
    for d in search_pmc(query, issn):
        title = d.get("title", "")
        probe = Hit("pmc", title, "", d.get("doi", ""), d.get("firstPublicationDate", "")[:10])
        if not is_relevant(probe, enabled=True, query=query):
            continue
        if d.get("hasSuppl") != "Y":
            continue
        pmcid = d.get("pmcid")
        if not pmcid:
            continue
        yield Hit(f"pmc:{journal}", title, ARTICLE_URL.format(pmcid=pmcid),
                  norm_doi(d.get("doi", "")), d.get("firstPublicationDate", "")[:10])


# ---------------------------------------------------------------------------
# Phase 2: resolve — fetch license (core record) + supplementary-files
# archive, pick the first tabular file, triage it
# ---------------------------------------------------------------------------

_RE_PMCID = re.compile(r"(PMC\d+)")


# Returned when the core record could not be read at all, as distinct from a
# record that was read and carries no license. See fetch_core_license.
LICENSE_LOOKUP_FAILED = "__lookup_failed__"


def fetch_core_license(pmcid: str, attempts: int = 3) -> str:
    """One core-record lookup for the `license` field. Separate from the
    Phase-1 lite search because resultType=core is a meaningfully heavier
    response (full abstract, author list, etc.) -- not worth paying for
    every search hit, only for candidates that already passed relevance +
    hasSuppl filtering.

    An EMPTY resultList is not "this article has no licence" -- it is a
    failed lookup. Europe PMC returns well-formed bodies with no results
    under load (the same stub-body behaviour `_europepmc_get` retries HTTP
    errors for), and this function used to read that as `""`, which
    `check_license` then normalised to `unknown`. That verdict is sticky:
    the DOI is written to the seen ledger with a licence note saying the
    terms could not be confirmed, and the standing rule is to skip an
    unverified candidate. The 2026-09-20 recycled-term sweep is what
    measured the cost -- 34 of its 34 `unknown` rows re-checked as `cc-by`
    minutes later, 19 of them on actionable candidates including the run's
    only `good` row. Nothing in the log marked it, because nothing had
    failed in a way the code could see.

    So: retry an empty result, and if it stays empty return
    LICENSE_LOOKUP_FAILED rather than `""`. A record that IS read and
    carries no license field still returns `""` -- that one is a real
    absence.
    """
    for attempt in range(attempts):
        data = _europepmc_get({
            "query": f"PMCID:{pmcid}",
            "resultType": "core",
            "pageSize": 1,
            "format": "json",
        })
        results = (data or {}).get("resultList", {}).get("result", [])
        if results:
            return results[0].get("license", "") or ""
        if attempt < attempts - 1:
            time.sleep(2 * (attempt + 1))
    return LICENSE_LOOKUP_FAILED


# JATS puts the Data Availability statement in a <sec sec-type=...>, a
# <notes notes-type=...> or a <custom-meta>, with the type spelled
# "data-availability", "data-availability-statement" or "availability"
# depending on the publisher. Matching on the markup mentioning availability
# of data or code found a statement in 19 of 20 sampled articles (the miss
# genuinely has none), so this stays a pattern rather than an XML parse.
_RE_DAS_BLOCK = re.compile(
    r"<(sec|notes|custom-meta)\b[^>]*?(?:sec-type|notes-type|id)\s*=\s*"
    r"[\"'][^\"']*(?:data|code)[^\"']*avail[^\"']*[\"'][^>]*>(.*?)</\1>",
    re.IGNORECASE | re.DOTALL)
# Fallback: a titled section whose heading says so.
_RE_DAS_TITLE = re.compile(
    r"<(sec|notes)\b[^>]*>\s*<title>[^<]*(?:data|code)[^<]*availab[^<]*</title>(.*?)</\1>",
    re.IGNORECASE | re.DOTALL)
_RE_XML_TAG = re.compile(r"<[^>]+>")


def fetch_fulltext_xml(pmcid: str) -> str:
    """The article's JATS full text. Only called once the supplementary
    archive has already failed to produce a tabular file."""
    return polite_get(EUROPEPMC_FULLTEXT.format(pmcid=pmcid)).text


def extract_data_availability(xml: str) -> str:
    """The Data Availability statement as plain text, or "" if absent."""
    m = _RE_DAS_BLOCK.search(xml or "") or _RE_DAS_TITLE.search(xml or "")
    if not m:
        return ""
    text = _RE_XML_TAG.sub(" ", m.group(2))
    return re.sub(r"\s+", " ", text).strip()


def _data_availability_handoff(pmcid: str, base: dict, si_reason: str) -> dict | None:
    """Triage the deposit the article's Data Availability statement names.

    Returns None when there is no statement, no link in it, or the full text
    cannot be fetched -- the caller then keeps its own no_usable_file verdict.

    This connector used to stop at "the supplementary archive holds nothing
    tabular" and retire the DOI, which is how PLOS lost 395 recoverable
    candidates before #2191. Of a random 20 PMC candidates retired that way,
    5 named a figshare/OSF deposit that the resolvers read.
    """
    try:
        xml = fetch_fulltext_xml(pmcid)
    except Exception:
        return None
    avail = extract_data_availability(xml)
    base["data_availability"] = avail[:300]
    link = extract_external_link(avail)
    base["external_link"] = link
    if not link:
        return None
    row = triage_external_link(link, base)
    # triage_external_link's no-resolver wording is written for PLOS's
    # Supporting Information; say what actually failed here.
    if row.get("flag") == "external_unresolved":
        row["reasons"] = f"{si_reason} | {row['reasons'].split('; ', 1)[-1]}"[:400]
    return row


def process_one(hit: Hit) -> dict:
    journal = hit.source.split(":", 1)[1] if ":" in hit.source else ""
    m = _RE_PMCID.search(hit.url)
    pmcid = m.group(1) if m else ""
    base = {"source": "pmc", "journal": journal, "title": hit.title,
            "doi": hit.doi, "url": hit.url, "pmcid": pmcid}
    empty_meta = {"n_responses": "", "n_participants": "", "n_items": "",
                  "density": "", "data_file": ""}

    if not pmcid:
        return {**base, "flag": "error", "reasons": "could not parse PMCID from URL",
                "license": "", **empty_meta}

    license_raw = fetch_core_license(pmcid)
    if license_raw == LICENSE_LOOKUP_FAILED:
        # Inconclusive, so the DOI is NOT ledgered and a later run retries it.
        return {**base, "flag": "license_lookup_failed", "license": "",
                "reasons": "could not read the Europe PMC core record for this "
                           "PMCID after 3 attempts -- licence unread, not absent",
                **empty_meta}
    license_norm, blocked, unknown = check_license(license_raw)
    base["license"] = license_norm
    if blocked:
        return {**base, "flag": "license_restricted",
                "reasons": f"license '{license_norm}' does not permit redistribution",
                **empty_meta}

    try:
        r = polite_get(EUROPEPMC_SUPPL.format(pmcid=pmcid))
        content = r.content
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status == 404:
            reason = "no supplementary-files archive for this PMCID"
            return (_data_availability_handoff(pmcid, base, reason)
                    or {**base, "flag": "no_usable_file", "reasons": reason, **empty_meta})
        return {**base, "flag": "download_failed", "reasons": str(e)[:200], **empty_meta}
    except FileTooLarge as e:
        return {**base, "flag": "file_too_large", "reasons": str(e), **empty_meta}
    except Exception as e:
        return {**base, "flag": "download_failed", "reasons": str(e)[:200], **empty_meta}

    try:
        zf = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile:
        reason = "supplementary-files response was not a valid zip archive"
        return (_data_availability_handoff(pmcid, base, reason)
                or {**base, "flag": "no_usable_file", "reasons": reason, **empty_meta})

    names = zf.namelist()
    tabular = [n for n in names if any(n.lower().endswith(ext) for ext in TABULAR_EXT)]
    if not tabular:
        reason = (f"no tabular-format file among {len(names)} supplementary "
                  f"file(s): {'; '.join(names[:10])}")[:400]
        return (_data_availability_handoff(pmcid, base, reason)
                or {**base, "flag": "no_usable_file", "reasons": reason, **empty_meta})

    fname = tabular[0]
    try:
        df = load_table(zf.read(fname), filename=fname)
    except Exception as e:
        return {**base, "flag": "download_failed", "reasons": str(e)[:200],
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": fname}

    try:
        t = triage_dataset(df)
        meta = t.metadata or {}
        reasons = list(t.reasons)
        if unknown:
            reasons.append("license_unknown* — could not confirm an open license; verify before submission")
        return {**base, "flag": t.flag, "reasons": " | ".join(reasons)[:400],
                "n_responses": meta.get("n_responses", ""),
                "n_participants": meta.get("n_participants", ""),
                "n_items": meta.get("n_items", ""),
                "density": meta.get("density", ""),
                "data_file": fname,
                "n_other_files": len(tabular) - 1}
    except Exception as e:
        return {**base, "flag": "error", "reasons": str(e)[:200],
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": fname}


# ---------------------------------------------------------------------------
# Orchestration — copied from irw_discover_plos.py's process isolation
# harness rather than imported: it's tightly coupled to this module's own
# process_one, and each discovery script stays self-contained (matching the
# rest of the pipeline's "no shared dependencies between scripts" norm).
# ---------------------------------------------------------------------------

FIELDNAMES = ["source", "journal", "doi", "title", "url", "pmcid", "license",
              "flag", "reasons", "data_availability", "external_link",
              "data_file", "n_responses", "n_participants",
              "n_items", "density", "n_other_files"]

# License lookup + SI download + one file parse -- and, on the failure path,
# a full-text fetch, a DOI redirect and a repository listing besides.
_PROCESS_TIMEOUT = 180


def _new_pool() -> ProcessPoolExecutor:
    return ProcessPoolExecutor(max_workers=1)


def _kill_pool_workers(pool: ProcessPoolExecutor) -> None:
    """See irw_discover_plos.py's identical helper for why this exists:
    a native-library segfault (pyreadstat on a corrupt .sav) or a hang
    otherwise leaves an orphaned worker process running unattended."""
    procs = list((getattr(pool, "_processes", None) or {}).values())
    for p in procs:
        if p.is_alive():
            p.terminate()
    for p in procs:
        p.join(timeout=5)
        if p.is_alive():
            p.kill()
            p.join(timeout=5)


def process_one_isolated(hit: Hit, pool: ProcessPoolExecutor) -> tuple[dict, ProcessPoolExecutor]:
    journal = hit.source.split(":", 1)[1] if ":" in hit.source else ""
    base = {"source": "pmc", "journal": journal, "title": hit.title,
            "doi": hit.doi, "url": hit.url}
    try:
        fut = pool.submit(process_one, hit)
        row = fut.result(timeout=_PROCESS_TIMEOUT)
        return row, pool
    except BrokenExecutor:
        pool.shutdown(wait=False)
        return ({**base, "flag": "crashed",
                 "reasons": "worker process died (likely a native-library segfault, "
                            "e.g. a corrupt .sav/.xlsx file)"},
                _new_pool())
    except FutureTimeoutError:
        _kill_pool_workers(pool)
        pool.shutdown(wait=False, cancel_futures=True)
        return ({**base, "flag": "timeout",
                 "reasons": f"exceeded {_PROCESS_TIMEOUT}s"},
                _new_pool())
    except Exception as e:
        return ({**base, "flag": "error", "reasons": str(e)[:200]}, pool)


def _load_done_dois(path: str) -> set:
    import os
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["doi"] for row in csv.DictReader(f) if row.get("doi")}


# Permanent, cross-run record of every DOI this connector has ever triaged
# -- shared by manual (`python irw_discover_pmc.py ...`) and scheduled
# (irw_discover_pmc_monthly.py) invocations alike, so a term searched by
# hand and the same term in the scheduled high-yield list don't
# re-download and re-triage the same candidate. See irw_discover_plos.py's
# identical SEEN_DOIS_PATH for the full rationale (same design, mirrored).
SEEN_DOIS_PATH = "pmc_seen_dois.csv"

# Flags that mean "we never actually examined this candidate" -- an infra
# failure, not a verdict about the data. Recording these in the cross-run
# ledger would retire the DOI forever on the strength of a transient 500 or
# a crash, so they are left out and picked up by a later run.
INCONCLUSIVE_FLAGS = {"download_failed", "error", "license_lookup_failed"}


def load_seen_dois(path: str = SEEN_DOIS_PATH) -> set:
    import os
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["doi"] for row in csv.DictReader(f) if row.get("doi")}


def append_seen_dois(dois, path: str = SEEN_DOIS_PATH) -> None:
    import os
    from datetime import datetime, timezone
    if not dois:
        return
    file_exists = os.path.exists(path)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["doi", "date"], lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerows({"doi": d, "date": today} for d in dois)


def main():
    preflight_deps()
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*", default=["item response theory"])
    ap.add_argument("--out", default="pmc_triage.csv")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap total candidates processed (for a quick sanity check)")
    ap.add_argument("--resume", action="store_true",
                    help="skip DOIs already present in --out and append to it, "
                         "rather than overwriting")
    ap.add_argument("--journals", default=DEFAULT_JOURNALS,
                    help="comma-separated journal slugs to search, from: "
                         f"{', '.join(JOURNALS)} (default: all)")
    ap.add_argument("--ignore-seen-dois", action="store_true",
                    help=f"don't consult/update {SEEN_DOIS_PATH} (the cross-run dedup "
                         "store shared with irw_discover_pmc_monthly.py) -- use to "
                         "deliberately re-triage a DOI, e.g. after a script fix")
    args = ap.parse_args()

    journals = [j.strip() for j in args.journals.split(",") if j.strip()]
    bad = [j for j in journals if j not in JOURNALS]
    if bad:
        raise SystemExit(f"Unknown journal slug(s): {bad}. Choose from: {list(JOURNALS)}")

    exclude = _load_auto_exclusions()
    print(f"Excluding {len(exclude):,} DOIs already in the IRW dictionary")

    global_seen = set() if args.ignore_seen_dois else load_seen_dois()
    if global_seen:
        print(f"Excluding {len(global_seen):,} DOIs already triaged in a prior run "
              f"(manual or scheduled -- see {SEEN_DOIS_PATH})")

    args.out = in_runs_dir(args.out)
    already_done = _load_done_dois(args.out) if args.resume else set()
    if already_done:
        print(f"Resuming: {len(already_done)} DOIs already in {args.out}, skipping them")
    print()

    outf = open(args.out, "a" if args.resume and already_done else "w",
                newline="", encoding="utf-8")
    writer = csv.DictWriter(outf, fieldnames=FIELDNAMES, extrasaction="ignore", lineterminator="\n")
    if not (args.resume and already_done):
        writer.writeheader()

    seen = set(already_done)
    newly_seen = []
    n_done = 0
    pool = _new_pool()
    try:
        for journal in journals:
            for q in args.queries:
                print(f"[{journal}] [query] {q}", flush=True)
                for hit in from_pmc(q, journal):
                    if hit.doi in seen or hit.doi in exclude or hit.doi in global_seen:
                        continue
                    seen.add(hit.doi)
                    row, pool = process_one_isolated(hit, pool)
                    if row["flag"] not in INCONCLUSIVE_FLAGS:
                        newly_seen.append(hit.doi)
                    writer.writerow(row)
                    outf.flush()
                    n_done += 1
                    print(f"  [{row['flag']:18}] {hit.title[:70]}", flush=True)
                    if args.limit and n_done >= args.limit:
                        break
                if args.limit and n_done >= args.limit:
                    break
            if args.limit and n_done >= args.limit:
                break
    finally:
        pool.shutdown(wait=False)
        outf.close()
        if not args.ignore_seen_dois:
            append_seen_dois(newly_seen)

    print(f"\n{n_done} candidates processed -> {args.out}")

    # Step 2b, in-process -- same call the scheduled connectors make. This
    # script triages off irw_triage_updated and never reaches
    # irw_batch_updated's --retriage flag, so a run fired BY HAND produced a
    # triage CSV with no refined_flag at all: the not_item_response rows
    # can't be dropped, the human_review rows can't be archived, and the
    # whole human_assistance bucket becomes nobody's job. #2076 fixed the
    # irw_batch_updated path and the monthly wrappers; the manual entry
    # points were missed, and the 2026-09-22 PMC batch-2 sweep is what
    # caught it -- 16 human_assistance rows, Step 2b run by hand afterwards.
    from irw_retriage_ha import chain_step2b
    chain_step2b(args.out, run=True)
    if SEARCH_FAILURES:
        print(f"WARNING: {SEARCH_FAILURES} search queries failed after all "
              f"retries -- their journal/term combinations were NOT actually "
              f"searched, even though any DOIs found by the ones that did run "
              f"have been written to {SEEN_DOIS_PATH}. Record this count in "
              f"the search_terms_log note and re-run the affected terms with "
              f"--ignore-seen-dois.", flush=True)


if __name__ == "__main__":
    main()
