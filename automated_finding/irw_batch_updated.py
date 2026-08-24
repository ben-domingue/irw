"""
irw_batch.py
============
Runs the triage pipeline over a whole discovery file (e.g. irw_discovered.csv),
turning ~hundreds of candidate landing pages into one ranked triage summary.

Pipeline per candidate:
    landing-page URL  ->  RESOLVE to a real data file  ->  download
                      ->  triage_dataset()  ->  record flag + metadata

Why this is more than "loop 500 times":
  * RESOLVE   : discovery stored landing pages, not direct file links. Each
                repository exposes its files through a different API, so we
                resolve them per-source. This is the brittle part.
  * POLITE    : per-domain delay so we don't hammer (and get blocked by) a repo.
  * RESUMABLE : every result is checkpointed to disk. Re-running skips finished
                rows, so a Colab disconnect at row 450 doesn't waste the first 449.
  * HONEST FLAGS: at scale the biggest bucket is usually "couldn't get a usable
                file" — that gets its own flag instead of masquerading as
                'human_assistance'.

Flags produced:
    good              confident mapping + clean QC (still needs a human glance)
    human_assistance  got data, but mapping/QC needs a person
    no_usable_file    landing page had no resolvable tabular file
    file_too_large    tabular file exists but exceeds MAX_FILE_BYTES; flagged
                      for manual/future handling rather than downloaded
    download_failed   network/HTTP error fetching the file
    error             unexpected problem (message recorded)

USAGE — always start small, then scale:
    python irw_batch.py irw_discovered.csv --limit 5      # test on 5 first!
    python irw_batch.py irw_discovered.csv                # full run, resumable
    python irw_batch.py irw_discovered.csv --resume       # continue after a stop
"""

from __future__ import annotations

import os
import re
import csv
import json
import time
import argparse
from collections import defaultdict
from urllib.parse import urlparse

import requests
import pandas as pd

from irw_triage_updated import load_table, triage_dataset, irw_metadata
from irw_discover_updated import SourceBlocked, in_runs_dir, resolve_in_path


class FileListUnreachable(Exception):
    """Couldn't retrieve a dataset's file listing (network/HTTP/parse error).

    Deliberately distinct from "the listing was retrieved and had no tabular
    file" -- the first is retryable and must not become a sticky verdict, the
    second is a real finding about the dataset."""

UA = {"User-Agent": "irw-batch/1.0 (research; contact itemresponsewarehouse@stanford.edu)"}
TABULAR_EXT = (".csv", ".tsv", ".tab", ".xlsx", ".xls",
               ".sav", ".dta", ".sas7bdat", ".rdata", ".rda", ".rds")
PER_DOMAIN_DELAY = 1.5          # seconds between hits to the same domain
CHECKPOINT = "irw_batch_checkpoint.jsonl"

# Files over this size are flagged file_too_large instead of downloaded.
# pandas readers (esp. read_stata/read_excel) can expand well beyond a
# file's on-disk size in memory -- batches 19 and 20 each OOM-killed this
# script outright (no traceback, ~21GB RSS on a 30GB box) on Dataverse
# candidates whose .dta files ran 1.4-1.58GB. See TODO.md's "no file-size
# guard" pipeline-improvement note.
MAX_FILE_BYTES = 200 * 1024 * 1024  # 200MB


class FileTooLarge(Exception):
    def __init__(self, size: int, limit: int = MAX_FILE_BYTES):
        self.size = size
        self.limit = limit
        super().__init__(f"{size:,} bytes, over the {limit:,}-byte ceiling")


# ---------------------------------------------------------------------------
# License checking
# ---------------------------------------------------------------------------

_BLOCKED_LICENSES = {"cc-by-nc", "cc-by-nd", "cc-by-nc-nd", "cc-by-nc-sa",
                     "all-rights-reserved", "arr"}
_OPEN_LICENSES    = {"cc0", "cc-pddc", "cc-by", "cc-by-sa", "public-domain"}

def _norm_license(raw: str) -> str:
    s = raw.lower().strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[-_]?\d+\.\d+$", "", s)   # strip version (e.g. cc-by-4.0 -> cc-by)
    s = re.sub(r"https?://.*creativecommons\.org/licenses/([^/]+).*", r"cc-\1", s)
    s = re.sub(r"https?://.*creativecommons\.org/publicdomain/zero.*", "cc0", s)
    return s

def check_license(raw: str) -> tuple[str, bool, bool]:
    """Returns (normalized, is_blocked, is_unknown)."""
    if not raw:
        return ("unknown", False, True)
    n = _norm_license(raw)
    return (n, n in _BLOCKED_LICENSES, n not in _OPEN_LICENSES and n not in _BLOCKED_LICENSES)


# ---------------------------------------------------------------------------
# RESOLVE: landing page -> direct data-file URL(s) + license
#   Each helper returns ([(file_url, filename)], license_str).
# ---------------------------------------------------------------------------

def _zenodo_files(url: str) -> tuple:
    m = re.search(r"(?:record|records)/(\d+)", url)
    if not m:
        return [], "", []
    r = requests.get(f"https://zenodo.org/api/records/{m.group(1)}",
                     headers=UA, timeout=30)
    r.raise_for_status()
    data = r.json()
    license_raw = (data.get("metadata", {}).get("license", {}) or {}).get("id", "")
    out, oversized = [], []
    for f in data.get("files", []):
        key = f.get("key", "")
        link = f.get("links", {}).get("self", "")
        if key.lower().endswith(TABULAR_EXT) and link:
            if (f.get("size") or 0) > MAX_FILE_BYTES:
                oversized.append((key, f.get("size")))
                continue
            out.append((link, key))
    return out, license_raw, oversized


def _figshare_files(url: str) -> tuple:
    m = re.search(r"articles/(?:[^/]+/)?(?:[^/]+/)?(\d+)", url)
    if not m:
        return [], "", []
    r = requests.get(f"https://api.figshare.com/v2/articles/{m.group(1)}",
                     headers=UA, timeout=30)
    r.raise_for_status()
    data = r.json()
    license_raw = (data.get("license") or {}).get("name", "")
    out, oversized = [], []
    for f in data.get("files", []):
        name = f.get("name", "")
        dl = f.get("download_url", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            if (f.get("size") or 0) > MAX_FILE_BYTES:
                oversized.append((name, f.get("size")))
                continue
            out.append((dl, name))
    return out, license_raw, oversized


def _dryad_files(doi: str) -> tuple:
    if not doi:
        return [], "", []
    enc = requests.utils.quote(f"doi:{doi}", safe="")
    base = "https://datadryad.org/api/v2"
    r = requests.get(f"{base}/datasets/{enc}/versions", headers=UA, timeout=30)
    r.raise_for_status()
    versions = r.json().get("_embedded", {}).get("stash:versions", [])
    if not versions:
        return [], "", []
    latest_ver = versions[-1]
    license_raw = latest_ver.get("license", "")
    files_link = latest_ver.get("_links", {}).get("stash:files", {}).get("href", "")
    if not files_link:
        return [], license_raw, []
    r2 = requests.get(f"https://datadryad.org{files_link}", headers=UA, timeout=30)
    r2.raise_for_status()
    out, oversized = [], []
    for f in r2.json().get("_embedded", {}).get("stash:files", []):
        name = f.get("path", "")
        dl = f.get("_links", {}).get("stash:download", {}).get("href", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            if (f.get("size") or 0) > MAX_FILE_BYTES:
                oversized.append((name, f.get("size")))
                continue
            out.append((f"https://datadryad.org{dl}", name))
    return out, license_raw, oversized


def _dataverse_files(url: str, doi: str) -> tuple:
    pid = f"doi:{doi}" if doi else None
    if not pid:
        return [], "", []
    r = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId/",
                     params={"persistentId": pid}, headers=UA, timeout=30)
    if r.headers.get("x-amzn-waf-action") == "challenge":
        raise SourceBlocked(
            f"dataverse.harvard.edu is behind an AWS WAF JS bot-challenge "
            f"(HTTP {r.status_code}, empty body) -- site-wide, not "
            "query-specific. The same block hits /api/access/datafile, so no "
            "Dataverse candidate can be triaged until it lifts.")
    r.raise_for_status()
    latest = r.json().get("data", {}).get("latestVersion", {})
    license_raw = (latest.get("license") or {}).get("name", "") or latest.get("termsOfUse", "")
    out, oversized = [], []
    for f in latest.get("files", []):
        df = f.get("dataFile", {})
        name = df.get("filename", "")
        fid = df.get("id")
        if name.lower().endswith(TABULAR_EXT) and fid:
            if (df.get("filesize") or 0) > MAX_FILE_BYTES:
                oversized.append((name, df.get("filesize")))
                continue
            out.append((f"https://dataverse.harvard.edu/api/access/datafile/{fid}",
                        name))
    return out, license_raw, oversized


def _osf_files(url: str) -> tuple:
    node_id = [s for s in url.rstrip("/").split("/") if s][-1]
    r = requests.get(
        f"https://api.osf.io/v2/nodes/{node_id}/",
        headers=UA, timeout=30)
    r.raise_for_status()
    license_raw = (r.json().get("data", {}).get("relationships", {})
                   .get("license", {}).get("data", {}) or {}).get("id", "")
    r2 = requests.get(
        f"https://api.osf.io/v2/nodes/{node_id}/files/osfstorage/",
        headers=UA, timeout=30)
    r2.raise_for_status()
    out, oversized = [], []
    for f in r2.json().get("data", []):
        attrs = f.get("attributes", {})
        name = attrs.get("name", "")
        dl = f.get("links", {}).get("download", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            if (attrs.get("size") or 0) > MAX_FILE_BYTES:
                oversized.append((name, attrs.get("size")))
                continue
            out.append((dl, name))
    return out, license_raw, oversized


def _mendeley_files(url: str) -> tuple:
    """Mendeley Data (data.mendeley.com).

    Reached almost entirely via DataCite, whose records point at the
    landing page. That page is JS-rendered, so a scraper sees no files at
    all -- which is how the 2026-08-24 weekly run retired 29 Mendeley
    deposits as no_usable_file when every one I spot-checked had a .csv,
    .xlsx or .sav sitting right there. The public API needs no key and
    returns files and licence in one call."""
    m = re.search(r"/datasets/([A-Za-z0-9]+)", url)
    if not m:
        return [], "", []
    r = requests.get(
        f"https://data.mendeley.com/public-api/datasets/{m.group(1)}",
        headers=UA, timeout=30)
    r.raise_for_status()
    data = r.json()
    lic = data.get("data_licence") or {}
    license_raw = lic.get("short_name") or lic.get("url") or ""
    out, oversized = [], []
    for f in data.get("files", []):
        name = f.get("filename", "")
        cd = f.get("content_details") or {}
        dl = cd.get("download_url", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            size = f.get("size") or cd.get("size") or 0
            if size > MAX_FILE_BYTES:
                oversized.append((name, size))
                continue
            out.append((dl, name))
    return out, license_raw, oversized


# Hosts we can resolve regardless of which index surfaced the candidate.
# Deliberately narrow: _dataverse_files() hardcodes the Harvard API base,
# so other Dataverse installations (entrepot.recherche.data.gouv.fr,
# data.ru.nl, ...) must NOT be routed here.
_HOST_RESOLVERS = [
    ("data.mendeley.com", lambda url, doi: _mendeley_files(url)),
    ("zenodo.org",        lambda url, doi: _zenodo_files(url)),
    ("figshare.com",      lambda url, doi: _figshare_files(url)),
    ("osf.io",            lambda url, doi: _osf_files(url)),
    ("datadryad.org",     lambda url, doi: _dryad_files(doi)),
    ("dataverse.harvard.edu", _dataverse_files),
]


def _host_resolver(url: str):
    host = (urlparse(url).netloc or "").lower()
    for suffix, fn in _HOST_RESOLVERS:
        if host == suffix or host.endswith("." + suffix):
            return fn
    return None


def resolve_data_files(row: dict) -> tuple:
    """Dispatch to the right repository resolver. Returns
    ([(file_url, name)], license_str, [(name, size_bytes)]) -- the third
    element lists tabular files that were skipped for exceeding
    MAX_FILE_BYTES, so callers can flag them distinctly from
    'no_usable_file'."""
    src = (row.get("source") or "").lower()
    url = row.get("url") or ""
    doi = row.get("doi") or ""
    try:
        # Host first, source second. `source` records which index surfaced
        # the candidate, not where the data lives, so dispatching on it
        # alone silently retired every datacite row -- 87 of the 91
        # candidates in the 2026-08-24 weekly run -- as no_usable_file
        # without any resolver ever being called. Most of those rows point
        # at hosts already handled below.
        by_host = _host_resolver(url)
        if by_host is not None:
            return by_host(url, doi)
        if src == "zenodo":
            return _zenodo_files(url)
        if src == "figshare":
            return _figshare_files(url)
        if src == "dryad":
            return _dryad_files(doi)
        if src == "dataverse":
            return _dataverse_files(url, doi)
        if src == "osf":
            return _osf_files(url)
    except SourceBlocked:
        raise
    except Exception as e:
        # Distinguish "we could not reach the listing" from "we read the
        # listing and it holds nothing tabular". Both used to return an empty
        # file list, which process_one reported as no_usable_file -- a sticky
        # verdict recorded against a dataset nobody ever actually looked at.
        # Harvard's WAF made this concrete: every blocked Dataverse candidate
        # was being retired as "no resolvable tabular file on landing page".
        raise FileListUnreachable(f"{type(e).__name__}: {str(e)[:150]}") from e
    return [], "", []


# ---------------------------------------------------------------------------
# Politeness: per-domain rate limiting
# ---------------------------------------------------------------------------

_last_hit = defaultdict(float)

def polite_get(url: str, max_bytes: int = MAX_FILE_BYTES) -> requests.Response:
    """GET with per-domain rate limiting and a streaming size ceiling.
    Raises FileTooLarge (before the full body is buffered) if the response
    is bigger than max_bytes -- a backstop for downloads where a repo API
    doesn't expose file size upfront (e.g. PLOS supplementary files),
    complementing the pre-download size checks in the repo resolvers
    above.

    Retries a transient connection error (seen repeatedly in practice --
    brief local dropouts causing DNS-resolution failures or
    connection-refused) a couple of times with backoff before giving up,
    so a several-second blip doesn't get recorded as a permanent
    download_failed."""
    dom = urlparse(url).netloc
    for attempt in range(3):
        wait = PER_DOMAIN_DELAY - (time.time() - _last_hit[dom])
        if wait > 0:
            time.sleep(wait)
        try:
            resp = requests.get(url, headers=UA, timeout=120, stream=True)
            _last_hit[dom] = time.time()
            resp.raise_for_status()
            break
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            _last_hit[dom] = time.time()
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))
    cl = resp.headers.get("Content-Length")
    if cl and int(cl) > max_bytes:
        resp.close()
        raise FileTooLarge(int(cl), max_bytes)
    chunks, total = [], 0
    for chunk in resp.iter_content(chunk_size=1 << 20):
        total += len(chunk)
        if total > max_bytes:
            resp.close()
            raise FileTooLarge(total, max_bytes)
        chunks.append(chunk)
    resp._content = b"".join(chunks)
    resp._content_consumed = True
    return resp


# ---------------------------------------------------------------------------
# Process one candidate
# ---------------------------------------------------------------------------

def process_one(row: dict) -> dict:
    base = {"source": row.get("source", ""), "title": row.get("title", ""),
            "url": row.get("url", ""), "doi": row.get("doi", "")}

    try:
        files, license_raw, oversized = resolve_data_files(row)
    except (SourceBlocked, FileListUnreachable) as e:
        # Retryable, so it must land on a TRANSIENT_FLAGS flag -- never on a
        # sticky verdict that would retire the candidate for good.
        return {**base, "flag": "download_failed",
                "reasons": f"could not retrieve file listing -- {e}"[:200],
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}
    license_norm, blocked, unknown = check_license(license_raw)
    base["license"] = license_norm

    if blocked:
        return {**base, "flag": "license_restricted",
                "reasons": f"license '{license_norm}' does not permit redistribution",
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}

    if not files:
        if oversized:
            names = "; ".join(f"{n} ({s:,} bytes)" for n, s in oversized)
            return {**base, "flag": "file_too_large",
                    "reasons": f"tabular file(s) exceed the {MAX_FILE_BYTES:,}-byte "
                               f"ceiling, not downloaded: {names}",
                    "n_responses": "", "n_participants": "", "n_items": "",
                    "density": "", "data_file": oversized[0][0]}
        return {**base, "flag": "no_usable_file",
                "reasons": "no resolvable tabular file on landing page "
                           f"(checked {', '.join(TABULAR_EXT)})",
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}

    # Use the first tabular file. (Multi-file datasets -> human territory.)
    file_url, fname = files[0]
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
        if unknown:
            reasons.append(f"license_unknown* — license '{license_norm}' not recognised as open; verify before submission")
        return {**base, "flag": t.flag,
                "reasons": " | ".join(reasons)[:400],
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
# Checkpointing for resumability
# ---------------------------------------------------------------------------

def _key(row: dict) -> str:
    return row.get("doi") or row.get("url") or row.get("title", "")

# Permanent, cross-run record of every candidate key (doi/url/title, same
# as _key()) this script has ever triaged -- distinct from CHECKPOINT,
# which is scoped to a single (possibly interrupted) run and, without
# --resume, gets wiped on every fresh invocation. Shared by every manual
# `python irw_batch_updated.py ...` call and by the scheduled monthly/
# weekly repos routine alike, so a candidate one already triaged doesn't
# get re-downloaded by the other. Mirrors irw_discover_plos.py's/
# irw_discover_pmc.py's SEEN_DOIS_PATH design.
SEEN_KEYS_PATH = "repo_triage_seen_keys.csv"


def load_seen_keys(path: str = SEEN_KEYS_PATH) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["key"] for row in csv.DictReader(f) if row.get("key")}


def append_seen_keys(keys, path: str = SEEN_KEYS_PATH) -> None:
    import datetime as _dt
    if not keys:
        return
    file_exists = os.path.exists(path)
    today = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "date"])
        if not file_exists:
            writer.writeheader()
        writer.writerows({"key": k, "date": today} for k in keys)


def load_done(path: str) -> dict:
    done = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    done[rec["_key"]] = rec
                except Exception:
                    pass
    return done

def append_checkpoint(path: str, key: str, result: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"_key": key, **result}) + "\n")


# ---------------------------------------------------------------------------
# Batch driver
# ---------------------------------------------------------------------------

FLAG_ORDER = ["good", "human_assistance", "not_item_response", "below_min_n",
              "no_usable_file", "file_too_large", "license_restricted",
              "download_failed", "error"]

# Flags that mean "we couldn't reach the data", not "we evaluated the data".
# These must NEVER enter the seen-keys ledger: a source outage would otherwise
# permanently retire every candidate it touched, including after the outage
# clears. Concretely, Harvard's 2026-08-17 WAF block makes _dataverse_files()
# fail on an empty body -> download_failed; without this guard the next run
# would filter those DOIs out forever and the block would quietly cost us the
# candidates rather than just delaying them. Everything else is a real verdict
# about the dataset and stays sticky. See BATCH_LOG.md 2026-08-17.
TRANSIENT_FLAGS = {"download_failed", "error"}

def run_batch(candidates_csv: str, out_csv: str, limit: int | None,
              resume: bool, checkpoint: str = CHECKPOINT,
              ignore_seen_keys: bool = False) -> pd.DataFrame:
    rows = list(csv.DictReader(open(candidates_csv, encoding="utf-8")))

    global_seen = set() if ignore_seen_keys else load_seen_keys()
    if global_seen:
        print(f"Excluding {len(global_seen):,} candidates already triaged in a prior "
              f"run (manual or scheduled -- see {SEEN_KEYS_PATH})")
        rows = [r for r in rows if _key(r) not in global_seen]

    if limit:
        rows = rows[:limit]

    done = load_done(checkpoint) if resume else {}
    if resume and done:
        print(f"Resuming — {len(done)} already done, will be skipped.")
    elif not resume and os.path.exists(checkpoint):
        os.remove(checkpoint)   # fresh run

    results = list(done.values())
    newly_seen = []
    n_retryable = 0
    blocked_srcs: dict[str, str] = {}   # source -> why, once it hard-blocks
    for i, row in enumerate(rows, 1):
        k = _key(row)
        if k in done:
            continue
        src = (row.get("source") or "").lower()
        if src in blocked_srcs:
            # Already known unreachable this run -- don't spend a doomed
            # request per row. Still recorded (retryably) so the candidate
            # shows up in the output and comes back on the next run.
            res = {**{"source": row.get("source", ""), "title": row.get("title", ""),
                      "url": row.get("url", ""), "doi": row.get("doi", ""),
                      "license": ""},
                   "flag": "download_failed",
                   "reasons": f"skipped -- {src} blocked earlier this run: "
                              f"{blocked_srcs[src]}"[:200],
                   "n_responses": "", "n_participants": "", "n_items": "",
                   "density": "", "data_file": ""}
            append_checkpoint(checkpoint, k, res)
            results.append(res)
            n_retryable += 1
            continue
        print(f"[{i}/{len(rows)}] {row.get('source',''):9} "
              f"{(row.get('title','') or '')[:55]}", flush=True)
        res = process_one(row)
        if res.get("flag") == "download_failed" and "WAF" in res.get("reasons", ""):
            blocked_srcs[src] = "AWS WAF bot-challenge"
            print(f"        !! {src} appears blocked -- skipping its remaining "
                  f"rows this run (they stay retryable)", flush=True)
        append_checkpoint(checkpoint, k, res)
        results.append(res)
        if res.get("flag") not in TRANSIENT_FLAGS:
            newly_seen.append(k)
        else:
            n_retryable += 1
        print(f"        -> {res['flag']}", flush=True)

    if n_retryable:
        print(f"\n{n_retryable} candidate(s) left OUT of {SEEN_KEYS_PATH} "
              f"({'/'.join(sorted(TRANSIENT_FLAGS))}) so a later run retries "
              f"them once the source is reachable again", flush=True)

    if not ignore_seen_keys:
        append_seen_keys(newly_seen)

    df = pd.DataFrame(results)
    if not df.empty:
        df["_o"] = df["flag"].apply(lambda f: FLAG_ORDER.index(f)
                                    if f in FLAG_ORDER else 99)
        df = df.sort_values(["_o", "density"], ascending=[True, False]).drop(columns="_o")
        df.to_csv(out_csv, index=False)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates_csv")
    ap.add_argument("--out", default="irw_triage.csv")
    ap.add_argument("--limit", type=int, default=None,
                    help="process only the first N (use this to test first!)")
    ap.add_argument("--resume", action="store_true",
                    help="skip rows already in the checkpoint")
    ap.add_argument("--ignore-seen-keys", action="store_true",
                    help=f"don't consult/update {SEEN_KEYS_PATH} (the cross-run dedup "
                         "store shared with the scheduled repos routine) -- use to "
                         "deliberately re-triage a candidate, e.g. after a script fix")
    args = ap.parse_args()

    args.candidates_csv = resolve_in_path(args.candidates_csv)
    args.out = in_runs_dir(args.out)
    df = run_batch(args.candidates_csv, args.out, args.limit, args.resume,
                    ignore_seen_keys=args.ignore_seen_keys)
    print("\n" + "=" * 50)
    if df.empty:
        print("No results.")
        return
    counts = df["flag"].value_counts()
    print("TRIAGE SUMMARY")
    for flag in FLAG_ORDER:
        if flag in counts:
            print(f"  {flag:18} {counts[flag]}")
    print(f"\nFull summary -> {args.out}")
    print("Work the 'good' rows first; they're sorted to the top.")
    print("Add candidates you want to process to the queue sheet,")
    print("then run irw_process_queue.py.")


if __name__ == "__main__":
    main()
