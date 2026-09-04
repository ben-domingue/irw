"""
irw_discover_plos.py
=====================
PILOT: adapts the discovery/triage pipeline to a single open-access journal
(PLOS ONE) instead of a data repository.

Why this is a different source, not a duplicate of the existing connectors:
PLOS ONE is 100% CC-BY, and many authors deposit their raw item-response
data as "Supporting Information" files attached directly to the article
(e.g. "S1 Data.xlsx") rather than in an external repository. Those files
never surface via the Dataverse/Zenodo/OSF/Dryad/Figshare connectors in
irw_discover_updated.py -- they're not in any of those systems. This script
finds them by reading the article page itself.

Two-phase, mirroring the discover -> batch split used elsewhere:
  1. search_plos(query)  cheap: PLOS Solr search API (api.plos.org),
     title/abstract/DOI only, restricted to PLOS ONE via eissn (robust to
     the "PLoS ONE" / "PLOS ONE" naming drift in their own metadata).
  2. process_one(hit)    per candidate: fetch the article page, read the
     Data Availability statement, and pull any Supporting Information
     file whose declared format looks tabular (CSV/XLSX/XLS/SAV/DTA/TSV).
     Download it and run it through the SAME triage_dataset() content/
     format gate irw_batch_updated.py uses -- no separate scoring logic.

Also records the Data Availability statement text and any external URL it
contains (e.g. a Dryad/OSF DOI) even when there's no local SI file to
triage, so a human can decide whether to chase that lead through the
regular repo-based pipeline instead.

Run:
    python irw_discover_plos.py "self-efficacy scale" "reading assessment" --out plos_triage.csv
    python irw_discover_plos.py "PHQ-9" --limit 10 --out plos_test.csv   # sanity check first
"""

from __future__ import annotations

import re
import csv
import time
import argparse
from dataclasses import dataclass, asdict
from collections import defaultdict
from urllib.parse import urlparse
from concurrent.futures import ProcessPoolExecutor, BrokenExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

import requests

from irw_discover_updated import (
    Hit, is_relevant, norm_doi, _load_auto_exclusions, in_runs_dir,
)
from irw_batch_updated import check_license, TABULAR_EXT, polite_get, FileTooLarge
from irw_triage_updated import load_table, triage_dataset, preflight_deps

UA = {"User-Agent": "irw-discovery-scout/1.0 (research; contact itemresponsewarehouse@stanford.edu)"}
PLOS_SEARCH_API = "https://api.plos.org/search"
PLOS_ARTICLE_URL = "https://journals.plos.org/{slug}/article?id={doi}"

# slug (as used in journals.plos.org URLs) -> (eissn, display name). eissn is
# the stable Solr filter (journal name strings drift, e.g. "PLoS ONE" vs
# "PLOS ONE"); slug confirmed against a live article URL for each journal
# (2026-07-27) rather than guessed. Deliberately not the full PLOS family --
# see TODO.md/BATCH_LOG.md for why Biology/Genetics/Pathogens/etc. are
# excluded (lab/genomic data, not item responses).
JOURNALS = {
    "plosone": ("1932-6203", "PLOS ONE"),
    "mentalhealth": ("2837-8156", "PLOS Mental Health"),
    "globalpublichealth": ("2767-3375", "PLOS Global Public Health"),
}
DEFAULT_JOURNAL = "plosone"


# ---------------------------------------------------------------------------
# Phase 1: discover — cheap Solr search, title/abstract/DOI only
# ---------------------------------------------------------------------------

def search_plos(query: str, eissn: str, max_rows: int = 300, page_size: int = 100):
    """Yields raw PLOS search docs (dict) for a full-text query, restricted
    to the journal identified by eissn. Paginates until max_rows or results
    are exhausted."""
    start = 0
    while start < max_rows:
        # A few-second local network dropout (seen repeatedly in practice --
        # DNS resolution failures, connection-refused) otherwise kills the
        # whole remaining query list. Retry a transient connection error a
        # couple of times with backoff before giving up on this page.
        for attempt in range(3):
            try:
                r = requests.get(
                    PLOS_SEARCH_API,
                    params={
                        "q": f'everything:"{query}"',
                        "fq": f'eissn:"{eissn}" AND doc_type:full',
                        "fl": "id,title_display,abstract,publication_date",
                        "rows": page_size,
                        "start": start,
                        "wt": "json",
                    },
                    headers=UA, timeout=30)
                r.raise_for_status()
                docs = r.json().get("response", {}).get("docs", [])
                break
            except (requests.exceptions.ConnectionError,
                     requests.exceptions.Timeout) as e:
                if attempt == 2:
                    print(f"[plos] {e}", flush=True)
                    return
                wait = 5 * (attempt + 1)
                print(f"[plos] transient error, retrying in {wait}s: {e}", flush=True)
                time.sleep(wait)
            except Exception as e:
                print(f"[plos] {e}", flush=True)
                return
        if not docs:
            return
        for d in docs:
            yield d
        start += page_size
        time.sleep(0.5)


def from_plos(query: str, journal: str = DEFAULT_JOURNAL):
    """Discovery connector, same shape as irw_discover_updated.py's from_*
    functions. Relevance filtering uses title + abstract (abstracts carry
    construct terms that a title alone often doesn't). `journal` is a slug
    key into JOURNALS; encoded into the Hit's `source` field (as
    "plos:<slug>") so process_one (run in a separate worker process) can
    recover which journal a candidate came from without a second
    pool.submit() argument."""
    eissn, _ = JOURNALS[journal]
    for d in search_plos(query, eissn):
        doi = d.get("id", "")
        title = d.get("title_display", "")
        abstract = " ".join(d.get("abstract", []) or [])
        # Filter on combined text, but keep the Hit's title clean.
        probe = Hit("plos", f"{title} {abstract}", "", doi,
                     d.get("publication_date", "")[:10])
        if not is_relevant(probe, enabled=True, query=query):
            continue
        yield Hit(f"plos:{journal}", title,
                  PLOS_ARTICLE_URL.format(slug=journal, doi=doi), norm_doi(doi),
                  d.get("publication_date", "")[:10])


# ---------------------------------------------------------------------------
# Phase 2: resolve — fetch article page, pull Data Availability + Supporting
# Information files
# ---------------------------------------------------------------------------

# PLOS's "(FORMAT)" caption under each SI item -> real file extension, so
# load_table() (which dispatches on filename suffix) can read it.
_FORMAT_EXT = {
    "CSV": ".csv", "TSV": ".tsv", "XLSX": ".xlsx", "XLS": ".xls",
    "SAV": ".sav", "DTA": ".dta", "SAS7BDAT": ".sas7bdat",
    "RDATA": ".rdata", "RDS": ".rds", "TXT": ".csv",  # TXT SI is usually CSV-ish; try as csv
}

_RE_DATA_AVAIL = re.compile(
    r"Data Availability:\s*</strong>\s*(.*?)</p>", re.IGNORECASE | re.DOTALL)
_RE_SI_BLOCK = re.compile(
    r'<div class="supplementary-material">.*?'
    r'href="(article/file\?type=supplementary&amp;id=[^"]+)".*?'
    r'>(S\d+\s+\w+)\.\s*</a>(.*?)'
    r'<p class="postSiDOI">\(([A-Za-z0-9]+)\)</p>',
    re.DOTALL)
_RE_TAG = re.compile(r"<[^>]+>")
_RE_URL = re.compile(r'https?://[^\s"\'<>]+')
_RE_BARE_DOI = re.compile(r'\b10\.\d{4,9}/[^\s,;)"\'<>]+')

# External repos already covered by irw_discover_updated.py's own connectors
# -- flagged for visibility, not re-downloaded here.
_KNOWN_REPO_HOSTS = ("datadryad.org", "zenodo.org", "osf.io", "figshare.com",
                     "dataverse.harvard.edu")


def _strip_tags(s: str) -> str:
    return _RE_TAG.sub(" ", s).strip()


def fetch_plos_article(url: str) -> str:
    r = polite_get(url)
    return r.text


def extract_data_availability(html: str) -> str:
    m = _RE_DATA_AVAIL.search(html)
    return _strip_tags(m.group(1)) if m else ""


def extract_license(html: str) -> str:
    m = re.search(r"creativecommons\.org/licenses/([a-z-]+)", html, re.IGNORECASE)
    if m:
        return f"cc-{m.group(1).lower()}"
    if "creativecommons.org/publicdomain/zero" in html.lower():
        return "cc0"
    return ""


def extract_si_files(html: str, doi: str, journal: str = DEFAULT_JOURNAL) -> list[tuple[str, str]]:
    """Returns [(file_url, filename)] for SI items with a tabular-looking
    declared format. filename is synthesized (SI blocks don't expose a real
    one) so load_table() can dispatch on its extension."""
    out = []
    for m in _RE_SI_BLOCK.finditer(html):
        rel_url, si_id, caption, fmt = m.groups()
        fmt = fmt.upper()
        ext = _FORMAT_EXT.get(fmt)
        if not ext:
            continue   # DOCX/PDF/PPTX/TIFF/ZIP etc. -- not directly tabular
        file_url = f"https://journals.plos.org/{journal}/{rel_url.replace('&amp;', '&')}"
        si_label = si_id.replace(" ", "_")
        caption_text = _strip_tags(caption)[:60]
        out.append((file_url, f"{doi.split('/')[-1]}_{si_label}{ext}", caption_text))
    return out


def process_one(hit: Hit) -> dict:
    journal = hit.source.split(":", 1)[1] if ":" in hit.source else DEFAULT_JOURNAL
    base = {"source": "plos", "journal": journal, "title": hit.title,
            "doi": hit.doi, "url": hit.url}
    try:
        html = fetch_plos_article(hit.url)
    except Exception as e:
        return {**base, "flag": "download_failed", "reasons": f"article page: {e}"[:200],
                "data_availability": "", "external_link": "", "license": "",
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}

    avail = extract_data_availability(html)
    ext_link = ""
    for m in _RE_URL.finditer(avail):
        host = urlparse(m.group(0)).netloc
        if any(h in host for h in _KNOWN_REPO_HOSTS) or "doi.org" in host:
            ext_link = m.group(0)
            break
    if not ext_link:
        # Data Availability statements often give a bare DOI ("doi:
        # 10.5061/dryad.xxxx") with no URL scheme at all.
        m = _RE_BARE_DOI.search(avail)
        if m:
            ext_link = f"https://doi.org/{m.group(0)}"

    license_raw = extract_license(html)
    license_norm, blocked, unknown = check_license(license_raw)
    base["license"] = license_norm
    base["data_availability"] = avail[:300]
    base["external_link"] = ext_link

    if blocked:
        return {**base, "flag": "license_restricted",
                "reasons": f"license '{license_norm}' does not permit redistribution",
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}

    files = extract_si_files(html, hit.doi, journal)
    if not files:
        reasons = "no tabular-format Supporting Information file on article page"
        if ext_link:
            reasons += f"; Data Availability points elsewhere: {ext_link}"
        return {**base, "flag": "no_usable_file", "reasons": reasons,
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}

    file_url, fname, caption = files[0]
    try:
        content = polite_get(file_url).content
        df = load_table(content, filename=fname)
    except FileTooLarge as e:
        return {**base, "flag": "file_too_large", "reasons": str(e),
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": fname}
    except Exception as e:
        return {**base, "flag": "download_failed", "reasons": str(e)[:200],
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": fname}

    try:
        t = triage_dataset(df)
        meta = t.metadata or {}
        reasons = list(t.reasons)
        reasons.append(f"SI caption: {caption}")
        if unknown:
            reasons.append(f"license_unknown* — could not confirm CC-BY on page; verify before submission")
        return {**base, "flag": t.flag, "reasons": " | ".join(reasons)[:400],
                "n_responses": meta.get("n_responses", ""),
                "n_participants": meta.get("n_participants", ""),
                "n_items": meta.get("n_items", ""),
                "density": meta.get("density", ""),
                "data_file": fname,
                "n_other_files": len(files) - 1}
    except Exception as e:
        return {**base, "flag": "error", "reasons": str(e)[:200],
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": fname}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

FIELDNAMES = ["source", "journal", "doi", "title", "url", "license", "flag",
              "reasons", "data_availability", "external_link", "data_file",
              "n_responses", "n_participants", "n_items", "density",
              "n_other_files"]

# Permanent, cross-run record of every DOI this connector has ever
# triaged -- shared by manual (`python irw_discover_plos.py ...`) and
# scheduled (irw_discover_plos_monthly.py) invocations alike, so a term
# searched by hand and the same term in the scheduled high-yield list don't
# re-download and re-triage the same candidate. Distinct from `--resume`,
# which only dedups within a single --out file. Not the same signal as
# "already in the IRW dictionary" (_load_auto_exclusions) -- a candidate
# can be seen here (attempted) long before it's shipped (or ever, if it was
# rejected) there.
SEEN_DOIS_PATH = "plos_seen_dois.csv"

# Flags that mean "we never actually examined this candidate" -- an infra
# failure, not a verdict about the data. Recording these in the cross-run
# ledger would retire the DOI forever on the strength of a transient 500 or
# a crash, so they are left out and picked up by a later run.
INCONCLUSIVE_FLAGS = {"download_failed", "error"}


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

# Native readstat/openpyxl code (pyreadstat's .sav parser especially) can
# segfault outright on a corrupt file -- that's a C-level crash, not a
# catchable Python exception, so a bare try/except around process_one()
# doesn't protect a long unattended run. Isolate each candidate in its own
# worker process instead: a crashed worker gets recorded as a 'crashed' row
# and the pool is respawned, rather than taking the whole batch down.
_PROCESS_TIMEOUT = 90  # seconds; article fetch + one file download+parse


def _new_pool() -> ProcessPoolExecutor:
    return ProcessPoolExecutor(max_workers=1)


def _kill_pool_workers(pool: ProcessPoolExecutor) -> None:
    """Forcibly terminates any live worker OS processes in `pool`.

    `ProcessPoolExecutor.shutdown(wait=False, cancel_futures=True)` only
    drops futures that haven't started yet -- it does NOT stop a worker
    that's already mid-task, since the stdlib gives no public API for that.
    On a timeout the worker is still out there, still holding whatever
    memory it had (confirmed 2026-08-03: an abandoned timed-out worker
    parsing an .xlsx ran unattended for 30+ minutes and grew to ~22GB RSS,
    nearly OOMing the host, before being killed by hand). `_processes` is
    an internal attribute (stable across CPython 3.3-3.13 in practice, used
    here defensively) mapping pid -> the underlying multiprocessing.Process;
    grab it before shutdown() tears the pool down and terminate it directly.
    """
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
    """Runs process_one(hit) in a subprocess. Returns (row, pool) -- pool is
    replaced with a fresh one if the worker crashed or hung."""
    journal = hit.source.split(":", 1)[1] if ":" in hit.source else DEFAULT_JOURNAL
    base = {"source": "plos", "journal": journal, "title": hit.title,
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


def main():
    preflight_deps()
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", nargs="*", default=["item response theory"])
    ap.add_argument("--out", default="plos_triage.csv")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap total candidates processed (for a quick sanity check)")
    ap.add_argument("--resume", action="store_true",
                    help="skip DOIs already present in --out and append to it, "
                         "rather than overwriting")
    ap.add_argument("--journals", default=DEFAULT_JOURNAL,
                    help="comma-separated journal slugs to search, from: "
                         f"{', '.join(JOURNALS)} (default: {DEFAULT_JOURNAL})")
    ap.add_argument("--ignore-seen-dois", action="store_true",
                    help=f"don't consult/update {SEEN_DOIS_PATH} (the cross-run dedup "
                         "store shared with irw_discover_plos_monthly.py) -- use to "
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
                for hit in from_plos(q, journal):
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


if __name__ == "__main__":
    main()
