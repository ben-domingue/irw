#!/usr/bin/env python3
"""Find each source deposit's own codebook file and write metadata/codebook_links.csv (#2766).

The Codebook section on a table page is the IRW's reconstruction (#2763,
column_docs.csv). What item codes and unlabelled values mean is in the
source's own codebook, and the page could only point at the whole deposit.
This lists the files in each deposit and keeps the ones whose NAME says they
are a codebook, so the page and MCP describe_columns can link the file itself.

ONE RULE: never guess a codebook. A file is linked only when its name matches
one of the patterns below, and `how_found` records which one. A deposit with a
codebook named `S1_File.pdf` gets no link; that is the honest answer.

  how_found      name_codebook   codebook / data dictionary / variable list /
                                 data key / DDI / the Spanish and Portuguese
                                 equivalents in the file name
                 name_readme     a README whose text does NOT name the table's
                                 columns (or could not be read): MCP only
                 readme_names_columns
                                 a README whose TEXT names at least
                                 README_MIN_NAMES of the table's own column or
                                 item names (`evidence` lists them). A sample of
                                 25 README-only hits (10-02) split ~half
                                 describing the variables, ~40% install steps,
                                 folder layouts and code notes; the name alone
                                 cannot tell them apart, the text can
                 dataverse_ddi   Dataverse's public DDI export for a tabular
                                 file (variable names + labels), which works
                                 even when the file itself is guestbook-gated
                 recorded_at_ingest
                                 the codebook file whoever built the table
                                 named, via stage_dict_row.py `codebook_url`
                                 (automated_finding/codebook_at_ingest.csv,
                                 #2770). The strongest evidence: a person read
                                 it to write the build script

Hosts with an API that lists a deposit's files: OSF, Dataverse (Harvard and
dataverse.nl), figshare (incl. the frontiersin/plos portals), Zenodo, Mendeley
Data. Only tables in the matching *metadata.csv are swept: the biblio files
keep rows for renamed and retired tables (#2767). doi.org links are routed by DOI prefix, and resolved by one HEAD request
only when the prefix is unknown. Everything else (PLOS supplementary files,
statistics offices, openICPSR, which returns 403 to scripts) is recorded in the
checked file with its reason and not crawled.

Outputs:
  metadata/codebook_links.csv          table, url, file_name, host, how_found,
                                       n_same_kind_in_deposit, deposit_url, checked_at
  metadata/codebook_links_checked.csv  one row per (table, deposit): what was tried, and
                                       the outcome (hit / no_match / out_of_scope:<why>
                                       / error:<what>). A re-run skips tables
                                       already checked unless --recheck.

Deposit file listings are cached in metadata/logs/codebook_listings.json
(git-ignored), so the name patterns can be changed and re-applied with
--offline without touching any API. README texts and each table's names (its
item names, read from Redivis, plus the cov_* and traced source columns in
column_docs.csv) are cached beside it the same way.

Two ways to run it. A FULL sweep (~700 deposits; OSF has to be paced at
~2.5s per call) is by hand, niced. `--new-only` is stage 15 of the weekly
pipeline (#2770): it keeps every committed row for tables already in
codebook_links_checked.csv and sweeps only tables that are not, so it needs no
local cache and takes minutes. Codebook files do not change once deposited.

    nice -n 19 python3 metadata/find_codebook_links.py [--hosts osf,zenodo] [--limit N]
    python3 metadata/find_codebook_links.py --offline     ##re-match the cache only
    python3 metadata/find_codebook_links.py --new-only    ##weekly: new tables only

The README check needs each table's item names from Redivis (the `redivis`
Python package and a token). Without them a README is left `name_readme` with
evidence "not checked", never passed on a guess.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
BIBLIOS = ["biblio.csv", "comps_biblio.csv", "nominal_biblio.csv", "simsyn_biblio.csv"]
LINKS_OUT = HERE / "codebook_links.csv"
CHECKED_OUT = HERE / "codebook_links_checked.csv"
CACHE = HERE / "logs" / "codebook_listings.json"
README_CACHE = HERE / "logs" / "codebook_readme_text.json"
NAMES_CACHE = HERE / "logs" / "codebook_table_names.json"
COLUMN_DOCS = HERE / "column_docs.csv"
INGEST_CODEBOOKS = HERE.parent / "automated_finding" / "codebook_at_ingest.csv"
LINK_FIELDS = ["table", "url", "file_name", "host", "how_found",
               "n_same_kind_in_deposit", "deposit_url", "evidence", "checked_at"]
CHECKED_FIELDS = ["table", "data_url", "host", "deposit", "outcome", "checked_at"]
TABLE_SCRIPTS = HERE / "table_scripts.csv"
README_MIN_NAMES = 3
README_MAX_WORD_ITEMS = 100
##Names too generic to show that a text is about THIS table's columns.
NAME_STOP = {"id", "item", "resp", "age", "sex", "gender", "group", "time", "date",
             "wave", "score", "total", "type", "name", "data", "year", "country",
             "condition", "trial", "rt", "school", "class", "grade", "study"}
UA = "irw-codebook-links/1.0 (+https://itemresponsewarehouse.org; ben-domingue/irw#2766)"

##Python does not happy-eyeball, and figshare/OSF/doi.org publish dead AAAA
##records from here: every call stalls ~20s on IPv6 before falling back.
_gai = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _gai(*a, **k) if r[0] == socket.AF_INET]

CODEBOOK = re.compile(
    r"code[\s_-]?book|data[\s_-]?dictionar|dictionar(y|ies)\b|_dictionary|"
    r"^variables?\.(xlsx?|csv|txt|pdf|docx?|md|rtf)$|variable[\s_-]?(list|label|description|key|guide)s?|data[\s_-]?key|\bddi\b|"
    r"libro[\s_-]?de[\s_-]?c[oó]digos|diccionario|livro[\s_-]?de[\s_-]?c[oó]digos|"
    r"dicion[aá]rio|codificaci[oó]n|code[\s_-]?sheet|coding[\s_-]?(scheme|manual|key)",
    re.I,
)
README = re.compile(r"read[\s_-]?me|l[eé]ame", re.I)
##A file named `codebook.R` is the code that writes one, not the codebook; an
##.Rdata/.rds file is data, whatever it is called.
CODE_EXT = re.compile(r"\.(r|py|do|sps|sas|jl|m|ipynb|rdata|rds)$", re.I)

HOST_PACE = {"osf": 2.5, "dataverse": 0.5, "figshare": 0.5, "figshare_collection": 0.5, "zenodo": 0.7, "mendeley": 0.7, "doi": 0.5}
_last_call: Dict[str, float] = {}


def match(name: str) -> Optional[str]:
    if CODE_EXT.search(name):
        return None
    if CODEBOOK.search(name):
        return "name_codebook"
    if README.search(name):
        return "name_readme"
    return None


##--- routing: data URL -> (host, deposit key) ------------------------------

def route(url: str) -> Tuple[str, str]:
    """Return (host, key) for a crawlable deposit, or ("skip", reason)."""
    u = (url or "").strip()
    if not u.lower().startswith("http"):
        return "skip", "no_url"
    p = urllib.parse.urlparse(u)
    net = p.netloc.lower().removeprefix("www.")
    path = p.path
    if net in ("doi.org", "dx.doi.org"):
        return route_doi(urllib.parse.unquote(path.lstrip("/")))
    if net == "osf.io":
        m = re.match(r"/([a-z0-9]{5})(?:/|$)", path, re.I)
        return ("osf", m.group(1).lower()) if m else ("skip", "osf_unparsed")
    if net in ("dataverse.harvard.edu", "dataverse.nl"):
        q = urllib.parse.parse_qs(p.query)
        pid = (q.get("persistentId") or [""])[0]
        return ("dataverse", f"{net}|{dataset_pid(pid)}") if pid else ("skip", "dataverse_no_pid")
    if net.endswith("figshare.com"):
        if path.startswith("/s/"):
            return "skip", "figshare_private_link"
        if path.startswith("/collections/"):
            ids = re.findall(r"/(\d{5,})(?=/|$)", path)
            return ("figshare_collection", ids[-1]) if ids else ("skip", "figshare_unparsed")
        ids = re.findall(r"/(\d{5,})(?=/|$)", path)
        return ("figshare", ids[-1]) if ids else ("skip", "figshare_unparsed")
    if net == "zenodo.org":
        m = re.search(r"/(?:records?)/(\d+)", path)
        return ("zenodo", m.group(1)) if m else ("skip", "zenodo_unparsed")
    if net == "data.mendeley.com":
        m = re.match(r"/datasets/([a-z0-9]{10})", path)
        return ("mendeley", m.group(1)) if m else ("skip", "mendeley_unparsed")
    if net == "openicpsr.org":
        return "skip", "openicpsr_blocks_scripts"
    if net == "journals.plos.org":
        return "skip", "plos_supplementary"
    return "skip", f"host:{net}"


def dataset_pid(pid: str) -> str:
    """A Dataverse FILE pid (doi:10.7910/DVN/ABCDEF/GHIJKL) -> its dataset's pid."""
    m = re.match(r"(doi:10\.\d+/[^/]+/[^/]+)/[^/]+$", pid, re.I)
    return m.group(1) if m else pid


def route_doi(doi: str) -> Tuple[str, str]:
    d = doi.lower()
    if d.startswith("10.1371/"):
        return "skip", "plos_supplementary"
    if d.startswith("10.7910/"):
        return "dataverse", f"dataverse.harvard.edu|{dataset_pid('doi:' + doi)}"
    if d.startswith("10.34894/"):
        return "dataverse", f"dataverse.nl|{dataset_pid('doi:' + doi)}"
    if d.startswith("10.17605/osf.io/"):
        return "osf", d.rsplit("/", 1)[1][:5]
    m = re.match(r"10\.6084/m9\.figshare\.(\d+)", d)
    if m:
        return "figshare", m.group(1)
    m = re.match(r"10\.5281/zenodo\.(\d+)", d)
    if m:
        return "zenodo", m.group(1)
    m = re.match(r"10\.17632/([a-z0-9]{10})", d)
    if m:
        return "mendeley", m.group(1)
    return "doi", doi


##--- HTTP ------------------------------------------------------------------

def get(url: str, host: str, method: str = "GET", tries: int = 5):
    """Paced request with backoff on 429/5xx. Returns (status, body_or_final_url)."""
    for attempt in range(tries):
        wait = HOST_PACE.get(host, 1.0) - (time.time() - _last_call.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.time()
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, (r.geturl() if method == "HEAD" else json.loads(r.read().decode("utf-8")))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(min(120, 10 * 2 ** attempt))
                continue
            return e.code, None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt < tries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            return -1, str(e)
    return -1, None


##--- listers: key -> {"status": ..., "files": [{name, url, ddi?}]} ---------

def list_zenodo(key: str) -> dict:
    s, d = get(f"https://zenodo.org/api/records/{key}", "zenodo")
    if s != 200:
        return {"status": f"error:{s}"}
    files = d.get("files") or []
    return {"status": "ok", "landing": f"https://zenodo.org/records/{key}",
            "files": [{"name": f["key"], "url": f"https://zenodo.org/records/{key}/files/{urllib.parse.quote(f['key'])}"} for f in files]}


def list_figshare(key: str) -> dict:
    s, d = get(f"https://api.figshare.com/v2/articles/{key}", "figshare")
    if s != 200:
        return {"status": f"error:{s}"}
    landing = d.get("url_public_html") or f"https://figshare.com/articles/dataset/_/{key}"
    return {"status": "ok", "landing": landing,
            "files": [{"name": f["name"], "url": f"{landing}?file={f['id']}"} for f in d.get("files") or []]}


def list_figshare_collection(key: str) -> dict:
    s, d = get(f"https://api.figshare.com/v2/collections/{key}/articles?page_size=100", "figshare")
    if s != 200:
        return {"status": f"error:{s}"}
    out = []
    for a in d or []:
        r = list_figshare(str(a["id"]))
        if r["status"] != "ok":
            return {"status": f"{r['status']} (article {a['id']})"}
        out += r["files"]
    return {"status": "ok", "landing": f"https://figshare.com/collections/_/{key}", "files": out}


def list_mendeley(key: str) -> dict:
    s, d = get(f"https://data.mendeley.com/public-api/datasets/{key}", "mendeley")
    if s != 200:
        return {"status": f"error:{s}"}
    v = d.get("version")
    landing = f"https://data.mendeley.com/datasets/{key}/{v}" if v else f"https://data.mendeley.com/datasets/{key}"
    out = []
    for f in d.get("files") or []:
        dl = (f.get("content_details") or {}).get("download_url")
        out.append({"name": f.get("filename", ""), "url": dl or landing})
    return {"status": "ok", "landing": landing, "files": out}


def list_dataverse(key: str) -> dict:
    server, pid = key.split("|", 1)
    s, d = get(f"https://{server}/api/datasets/:persistentId/?persistentId={urllib.parse.quote(pid, safe=':/')}", "dataverse")
    if s != 200:
        return {"status": f"error:{s}"}
    v = (d.get("data") or {}).get("latestVersion") or {}
    out = []
    for f in v.get("files") or []:
        df = f.get("dataFile") or {}
        fid = df.get("id")
        out.append({"name": f.get("label") or df.get("filename", ""),
                    "url": f"https://{server}/file.xhtml?fileId={fid}",
                    ##only ingested (tabular) files have a DDI variable export
                    "ddi": f"https://{server}/api/access/datafile/{fid}/metadata/ddi" if df.get("originalFileFormat") or df.get("tabularTags") is not None else None})
    return {"status": "ok", "landing": f"https://{server}/dataset.xhtml?persistentId={pid}", "files": out}


def _osf_walk(url: str, depth: int, out: List[dict], path: str = "") -> Optional[int]:
    while url:
        s, d = get(url, "osf")
        if s != 200:
            return s
        for x in d.get("data") or []:
            a = x.get("attributes") or {}
            if a.get("kind") == "folder" and depth > 0:
                rel = ((x.get("relationships") or {}).get("files") or {}).get("links", {}).get("related", {}).get("href")
                if rel:
                    _osf_walk(rel, depth - 1, out, f"{path}{a.get('name')}/")
            elif a.get("kind") == "file":
                out.append({"name": a.get("name", ""), "path": path + a.get("name", ""),
                            "url": (x.get("links") or {}).get("html") or ""})
        url = (d.get("links") or {}).get("next")
    return None


def list_osf(key: str) -> dict:
    """osfstorage of the node and of its direct child components, folders to depth 3.

    A 404 on /nodes/ is not a missing deposit: the GUID may be a registration
    (osf-api-sweep-rate-limits). 401 is a view-only link, also not missing.
    """
    out: List[dict] = []
    base = None
    for kind in ("nodes", "registrations"):
        s = _osf_walk(f"https://api.osf.io/v2/{kind}/{key}/files/osfstorage/", 3, out)
        if s is None:
            base = kind
            break
        if s != 404:
            return {"status": f"error:{s}"}
    if base is None:
        ##maybe the GUID is a single file
        s, d = get(f"https://api.osf.io/v2/files/{key}/", "osf")
        if s == 200:
            a = d["data"]["attributes"]
            return {"status": "ok", "landing": f"https://osf.io/{key}/",
                    "files": [{"name": a.get("name", ""), "url": f"https://osf.io/{key}/"}]}
        return {"status": f"error:{s}"}
    s, d = get(f"https://api.osf.io/v2/{base}/{key}/children/", "osf")
    if s == 200:
        for c in d.get("data") or []:
            _osf_walk(f"https://api.osf.io/v2/{base}/{c['id']}/files/osfstorage/", 3, out, f"{c['id']}:")
    return {"status": "ok", "landing": f"https://osf.io/{key}/", "files": out}


def resolve_doi(doi: str) -> Tuple[str, str]:
    s, final = get(f"https://doi.org/{doi}", "doi", method="HEAD")
    if s != 200 or not isinstance(final, str):
        return "skip", f"doi_unresolved:{s}"
    h, k = route(final)
    return (h, k) if h != "doi" else ("skip", "doi_loop")


LISTERS = {"zenodo": list_zenodo, "figshare": list_figshare, "figshare_collection": list_figshare_collection, "mendeley": list_mendeley,
           "dataverse": list_dataverse, "osf": list_osf}


##--- main ------------------------------------------------------------------

##--- README content check -------------------------------------------------

def download_url(link: dict) -> Optional[str]:
    """Where a link's raw bytes are, per host (the stored url is a landing page)."""
    u, h = link["url"], link["host"]
    if h == "osf":
        m = re.match(r"https://osf\.io/([a-z0-9]+)/files/osfstorage/([0-9a-f]+)", u)
        return (f"https://files.osf.io/v1/resources/{m.group(1)}/providers/osfstorage/{m.group(2)}"
                if m else None)
    if h == "dataverse":
        m = re.match(r"https://([^/]+)/file\.xhtml\?fileId=(\d+)", u)
        return f"https://{m.group(1)}/api/access/datafile/{m.group(2)}" if m else None
    if h in ("figshare", "figshare_collection"):
        m = re.search(r"[?&]file=(\d+)", u)
        return f"https://ndownloader.figshare.com/files/{m.group(1)}" if m else None
    if h == "zenodo":
        return u + "?download=1"
    if h == "mendeley":
        return u
    return None


def extract_text(raw: bytes, name: str) -> str:
    """Plain text from a README's bytes. Lossy is fine: only names are matched."""
    import subprocess
    import tempfile
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    if ext == "pdf" or raw[:4] == b"%PDF":
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(raw); f.flush()
            try:
                return subprocess.run(["pdftotext", "-l", "30", f.name, "-"], capture_output=True,
                                      timeout=60).stdout.decode("utf-8", "replace")
            except (OSError, subprocess.SubprocessError):
                return ""
    if ext == "docx" or raw[:2] == b"PK":
        import zipfile
        try:
            x = zipfile.ZipFile(io.BytesIO(raw)).read("word/document.xml").decode("utf-8", "replace")
            return re.sub(r"<[^>]+>", " ", x.replace("</w:p>", "\n"))
        except Exception:
            return ""
    text = raw.decode("utf-8", "replace")
    if ext in ("rtf",) or text.startswith("{\\rtf"):
        text = re.sub(r"\\[a-z]+-?\d* ?|[{}]", " ", text)
    if ext in ("html", "htm"):
        text = re.sub(r"<[^>]+>", " ", text)
    ##.doc and anything else binary: keep the printable runs
    return re.sub(r"[^\x09\x0a\x0d\x20-\x7e\u00a0-\uffff]+", " ", text)


def readme_text(link: dict, cache: Dict[str, str], offline: bool) -> Optional[str]:
    if link["url"] in cache:
        return cache[link["url"]]
    if offline:
        return None
    dl = download_url(link)
    if not dl:
        return None
    host = link["host"]
    for attempt in range(3):
        wait = HOST_PACE.get(host, 1.0) - (time.time() - _last_call.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.time()
        try:
            req = urllib.request.Request(dl, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read(5_000_000)
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(15 * (attempt + 1))
                continue
            cache[link["url"]] = ""     ##e.g. a guestbook-gated Dataverse file
            return ""
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(10)
                continue
            return None
    cache[link["url"]] = extract_text(raw, link["file_name"])[:400_000]
    return cache[link["url"]]


def table_names(table: str, dataset: Optional[str], cache: Dict[str, List[str]],
                docs: Dict[str, List[dict]], offline: bool,
                scripts: Optional[List[str]] = None) -> Optional[List[str]]:
    """The table's names: item names (Redivis), cov_* suffixes, traced source
    columns, and the names quoted in its build scripts."""
    key = table.lower()
    if key not in cache:
        if offline or not dataset:
            return None
        try:
            import redivis
            q = redivis.query(f"SELECT DISTINCT item FROM datapages.{dataset}.{table} LIMIT 2000")
            items = [str(x) for x in q.to_pandas_dataframe(progress=False)["item"]]
        except Exception as e:
            print(f"  item names for {table}: {type(e).__name__}", file=sys.stderr)
            return None
        cache[key] = items
    items = cache[key]
    ##A table with many items is usually a stimulus set (words, pictures): its
    ##items are not variables, and a word list matches any English README.
    if len(items) > README_MAX_WORD_ITEMS:
        items = [i for i in items if re.search(r"[0-9_]|[a-z][A-Z]", i)]
    names = set(items) | script_literals(scripts or [])
    for r in docs.get(key, []):
        if r["column"].startswith("cov_"):
            names.add(r["column"][4:])
        if r.get("source_column"):
            names.add(r["source_column"])
    return sorted({n.strip() for n in names if n and len(n.strip()) >= 3 and n.strip().lower() not in NAME_STOP})


def script_literals(paths: List[str]) -> set:
    """Quoted names in a table's build scripts: the SOURCE columns it reads.

    A README usually documents the source file, whose columns the script then
    renames (`subid` -> id), so the IRW's own names would miss it. Only
    identifier-shaped literals count; file names are dropped.
    """
    out = set()
    for p in paths:
        try:
            src = (HERE.parent / p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in re.findall(r"""["']([A-Za-z][A-Za-z0-9_.]{2,40})["']""", src):
            ##identifier-shaped only (BC_10, SubID, ptci3): a plain word from a
            ##script -- "files", "university" -- shows nothing about a README
            if (re.search(r"[0-9_]|[a-z][A-Z]", m)
                    and not re.search(r"\.(csv|sav|dta|xlsx?|txt|rds|rdata|zip|r|py|json|data)$", m, re.I)):
                out.add(m)
    return out


def names_in_text(names: List[str], text: str) -> List[str]:
    low = text.lower()
    return [n for n in names if re.search(r"(?<![a-z0-9_])" + re.escape(n.lower()) + r"(?![a-z0-9_])", low)]


def read_csv(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[dict], fields: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def check_readmes(links: List[dict], offline: bool) -> None:
    """Promote README rows whose text names the table's columns (in place)."""
    texts = json.loads(README_CACHE.read_text()) if README_CACHE.exists() else {}
    names_cache = json.loads(NAMES_CACHE.read_text()) if NAMES_CACHE.exists() else {}
    scripts_of = {r["table"].lower(): [x for x in re.split(r"[;|]\s*", r.get("scripts") or "") if x]
                  for r in read_csv(TABLE_SCRIPTS)}
    docs: Dict[str, List[dict]] = {}
    for r in read_csv(COLUMN_DOCS):
        docs.setdefault(r["table"].lower(), []).append(r)
    dataset_of = {}
    for b in BIBLIOS:
        for r in read_csv(HERE / b.replace("biblio", "metadata")):
            if r.get("dataset"):
                dataset_of[r["table"].lower()] = r["dataset"]
    readmes = [x for x in links if x["how_found"] == "name_readme"]
    for i, x in enumerate(readmes):
        text = readme_text(x, texts, offline)
        names = table_names(x["table"], dataset_of.get(x["table"].lower()), names_cache, docs, offline,
                            scripts_of.get(x["table"].lower()))
        if text is None or names is None:
            x["evidence"] = "not checked"
        elif not text.strip():
            x["evidence"] = "unreadable"
        else:
            hit = names_in_text(names, text)
            x["evidence"] = f"names {len(hit)}/{len(names)}" + (": " + ", ".join(hit[:8]) if hit else "")
            if len(hit) >= README_MIN_NAMES:
                x["how_found"] = "readme_names_columns"
        if not offline and i % 25 == 24:
            README_CACHE.write_text(json.dumps(texts, ensure_ascii=False))
            NAMES_CACHE.write_text(json.dumps(names_cache, ensure_ascii=False))
    if not offline:
        README_CACHE.write_text(json.dumps(texts, ensure_ascii=False))
        NAMES_CACHE.write_text(json.dumps(names_cache, ensure_ascii=False))
    ##n_same_kind counts the README kinds again now that some were promoted
    by_dep: Dict[Tuple[str, str], int] = {}
    for x in links:
        if x["how_found"] in ("name_readme", "readme_names_columns"):
            by_dep[(x["table"], x["how_found"])] = by_dep.get((x["table"], x["how_found"]), 0) + 1
    for x in links:
        if x["how_found"] in ("name_readme", "readme_names_columns"):
            x["n_same_kind_in_deposit"] = by_dep[(x["table"], x["how_found"])]
        x.setdefault("evidence", "")


def ingest_links(live: set) -> List[dict]:
    """recorded_at_ingest rows from codebook_at_ingest.csv, for live tables.

    "none" (the builder looked and the source ships no codebook) yields no
    row: there is nothing to link, and the sweep still runs for that table.
    """
    out = []
    for r in read_csv(INGEST_CODEBOOKS):
        url = (r.get("codebook_url") or "").strip()
        table = (r.get("table") or "").strip()
        if table not in live or not url.lower().startswith("http"):
            continue
        p = urllib.parse.urlparse(url)
        out.append({"table": table, "url": url,
                    "file_name": urllib.parse.unquote(p.path.rstrip("/").rsplit("/", 1)[-1]) or url,
                    "host": p.netloc.lower().removeprefix("www."), "how_found": "recorded_at_ingest",
                    "n_same_kind_in_deposit": 1, "deposit_url": "", "evidence": "",
                    "checked_at": (r.get("recorded_at") or "").strip()})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hosts", default="", help="comma list to crawl (default: all crawlable)")
    ap.add_argument("--limit", type=int, default=0, help="crawl at most N new deposits")
    ap.add_argument("--offline", action="store_true", help="no network; re-match cached listings")
    ap.add_argument("--recheck", action="store_true", help="re-list deposits already in the cache")
    ap.add_argument("--new-only", action="store_true",
                    help="keep committed rows; sweep only tables not yet in the checked file")
    ap.add_argument("--no-readme-check", action="store_true",
                    help="skip reading README texts (README hits stay name_readme)")
    args = ap.parse_args()
    hosts = set(filter(None, args.hosts.split(",")))
    today = date.today().isoformat()

    cache: Dict[str, dict] = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    tables: List[Tuple[str, str]] = []
    for b in BIBLIOS:
        ##biblio keeps rows for renamed and retired tables (#2767); only tables
        ##in the matching *metadata.csv exist to be linked
        live = {r["table"] for r in read_csv(HERE / b.replace("biblio", "metadata"))}
        tables += [(r["table"], r.get("URL__for_data_") or "") for r in read_csv(HERE / b) if r["table"] in live]
    live_tables = {t for t, _ in tables}

    ##--new-only: what is already committed stands; only unseen tables are swept
    kept_links: List[dict] = []
    kept_checked: List[dict] = []
    if args.new_only:
        prev_checked = [r for r in read_csv(CHECKED_OUT) if r["table"] in live_tables]
        done = {r["table"] for r in prev_checked if r["outcome"] != "not_yet_checked"}
        kept_checked = [r for r in prev_checked if r["table"] in done]
        kept_links = [r for r in read_csv(LINKS_OUT)
                      if r["table"] in done and r["how_found"] != "recorded_at_ingest"]
        tables = [(t, u) for t, u in tables if t not in done]
        print(f"--new-only: {len(done)} tables already checked, {len(tables)} to sweep",
              file=sys.stderr)

    routed: Dict[str, List[Tuple[str, str, str]]] = {}
    for t, cell in tables:
        ##a few cells hold several deposits separated by ';'
        urls = [x.strip() for x in re.split(r"\s*;\s*", cell) if x.strip()] or [""]
        routed[t] = []
        for u in urls:
            h, k = route(u)
            if h == "doi":
                ck = f"doi|{k}"
                if ck not in cache and not args.offline and (not hosts or "doi" in hosts):
                    hh, kk = resolve_doi(k)
                    cache[ck] = {"status": "resolved", "host": hh, "key": kk, "checked_at": today}
                h, k = (cache[ck]["host"], cache[ck]["key"]) if ck in cache else ("skip", "doi_not_resolved_yet")
            routed[t].append((u, h, k))

    todo = sorted({(h, k) for rs in routed.values() for _, h, k in rs if h in LISTERS and (not hosts or h in hosts)})
    n = 0
    for h, k in todo:
        ck = f"{h}|{k}"
        if args.offline or (ck in cache and not args.recheck):
            continue
        if args.limit and n >= args.limit:
            break
        res = LISTERS[h](k)
        res["checked_at"] = today
        cache[ck] = res
        n += 1
        print(f"[{n}/{len(todo)}] {h} {k}: {res['status']} {len(res.get('files') or [])} files", file=sys.stderr, flush=True)
        if n % 20 == 0:
            CACHE.parent.mkdir(exist_ok=True)
            CACHE.write_text(json.dumps(cache, indent=0, ensure_ascii=False))
    if not args.offline:   ##an offline re-match must not race a crawl writing the cache
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=0, ensure_ascii=False))

    links, checked = [], []
    for t, _ in tables:
        for u, h, k in routed[t]:
            row = {"table": t, "data_url": u, "host": h, "deposit": k if h != "skip" else "", "checked_at": ""}
            checked.append(row)
            if h == "skip":
                row["outcome"] = f"out_of_scope:{k}"
                continue
            res = cache.get(f"{h}|{k}")
            if res is None:
                row["outcome"] = "not_yet_checked"
                continue
            row["checked_at"] = res.get("checked_at", "")
            if res["status"] != "ok":
                row["outcome"] = res["status"]
                continue
            hits = []
            for f in res.get("files") or []:
                how = match(f["name"])
                if how:
                    hits.append({"table": t, "url": f["url"], "file_name": f.get("path") or f["name"],
                                 "host": h, "how_found": how, "checked_at": row["checked_at"]})
                if f.get("ddi"):
                    hits.append({"table": t, "url": f["ddi"], "file_name": f["name"], "host": h,
                                 "how_found": "dataverse_ddi", "checked_at": row["checked_at"]})
            ##A deposit with many codebooks (one per scale, say) attaches all of
            ##them to every table it built. Matching a table to one of them means
            ##decoding abbreviations (FamBel = family_belonging), which is the
            ##guessing this script refuses; record the count and the deposit's
            ##landing page so a page can say "19 codebook files in the deposit".
            for kind in ("name_codebook", "name_readme"):
                same = [x for x in hits if x["how_found"] == kind]
                for x in same:
                    x["n_same_kind_in_deposit"] = len(same)
            for x in hits:
                x.setdefault("n_same_kind_in_deposit", "")
                x["deposit_url"] = res.get("landing", "")
            links += hits
            kinds = sorted({x["how_found"] for x in hits})
            row["outcome"] = "hit:" + "+".join(kinds) if kinds else "no_match"

    if not args.no_readme_check:
        check_readmes(links, args.offline)

    for x in links:
        x.setdefault("evidence", "")
    links = ingest_links(live_tables) + kept_links + links
    ##one row per (table, url): a deposit reached by two routes (a multi-URL
    ##cell, a child component) lists the same file twice. Keep the strongest.
    rank = {"recorded_at_ingest": 0, "name_codebook": 1, "readme_names_columns": 2,
            "name_readme": 3, "dataverse_ddi": 4}
    best: Dict[Tuple[str, str], dict] = {}
    for x in links:
        k = (x["table"], x["url"])
        if k not in best or rank.get(x["how_found"], 9) < rank.get(best[k]["how_found"], 9):
            best[k] = x
    links = list(best.values())
    checked = kept_checked + checked
    links.sort(key=lambda x: (x["table"].lower(), x["how_found"], x["url"]))
    checked.sort(key=lambda x: (x["table"].lower(), x["data_url"]))
    write_csv(LINKS_OUT, links, LINK_FIELDS)
    write_csv(CHECKED_OUT, checked, CHECKED_FIELDS)
    print(f"{len(links)} links for {len({x['table'] for x in links})} tables -> {LINKS_OUT.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
