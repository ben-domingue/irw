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

Known simplification vs. irw_discover_plos.py: this script does not scrape
the full-text body for a Data Availability statement or an external-repo
DOI mention (PLOS's `external_link` column) -- Europe PMC's supplementary-
files endpoint is the whole point of this connector; chasing DAS-linked
external repos is the regular repo-based pipeline's job already, and would
require fetching+parsing full-text XML per candidate, a meaningfully
heavier request than what this script does today. Worth adding later if it
turns out to matter.

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
from irw_batch_updated import check_license, TABULAR_EXT, polite_get, FileTooLarge
from irw_triage_updated import load_table, triage_dataset

EUROPEPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EUROPEPMC_SUPPL = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles"
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

def _europepmc_get(params: dict) -> dict | None:
    """GET against the Europe PMC search endpoint, through polite_get so
    every call (search and file download alike) shares one per-domain rate
    limit against www.ebi.ac.uk."""
    url = EUROPEPMC_SEARCH + "?" + urlencode(params)
    for attempt in range(3):
        try:
            r = polite_get(url)
            return r.json()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if attempt == 2:
                print(f"[pmc] {e}", flush=True)
                return None
            wait = 5 * (attempt + 1)
            print(f"[pmc] transient error, retrying in {wait}s: {e}", flush=True)
            time.sleep(wait)
        except Exception as e:
            print(f"[pmc] {e}", flush=True)
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
        if not is_relevant(probe, enabled=True):
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


def fetch_core_license(pmcid: str) -> str:
    """One core-record lookup for the `license` field. Separate from the
    Phase-1 lite search because resultType=core is a meaningfully heavier
    response (full abstract, author list, etc.) -- not worth paying for
    every search hit, only for candidates that already passed relevance +
    hasSuppl filtering."""
    data = _europepmc_get({
        "query": f"PMCID:{pmcid}",
        "resultType": "core",
        "pageSize": 1,
        "format": "json",
    })
    results = (data or {}).get("resultList", {}).get("result", [])
    return results[0].get("license", "") if results else ""


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
            return {**base, "flag": "no_usable_file",
                    "reasons": "no supplementary-files archive for this PMCID",
                    **empty_meta}
        return {**base, "flag": "download_failed", "reasons": str(e)[:200], **empty_meta}
    except FileTooLarge as e:
        return {**base, "flag": "file_too_large", "reasons": str(e), **empty_meta}
    except Exception as e:
        return {**base, "flag": "download_failed", "reasons": str(e)[:200], **empty_meta}

    try:
        zf = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile:
        return {**base, "flag": "no_usable_file",
                "reasons": "supplementary-files response was not a valid zip archive",
                **empty_meta}

    names = zf.namelist()
    tabular = [n for n in names if any(n.lower().endswith(ext) for ext in TABULAR_EXT)]
    if not tabular:
        return {**base, "flag": "no_usable_file",
                "reasons": f"no tabular-format file among {len(names)} supplementary "
                           f"file(s): {'; '.join(names[:10])}"[:400],
                **empty_meta}

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
              "flag", "reasons", "data_file", "n_responses", "n_participants",
              "n_items", "density", "n_other_files"]

_PROCESS_TIMEOUT = 90  # seconds; license lookup + SI download + one file parse


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
        writer = csv.DictWriter(f, fieldnames=["doi", "date"])
        if not file_exists:
            writer.writeheader()
        writer.writerows({"doi": d, "date": today} for d in dois)


def main():
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
    writer = csv.DictWriter(outf, fieldnames=FIELDNAMES, extrasaction="ignore")
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
                    newly_seen.append(hit.doi)
                    row, pool = process_one_isolated(hit, pool)
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


if __name__ == "__main__":
    main()
