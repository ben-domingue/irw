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
                 typed_codebook  a document the repository itself types as a
                                 codebook (LDbase lists "Codebook: <title>")
                 package_doc     a CRAN package's help page for the dataset
                                 the table's build script loads (load("x.rda"),
                                 data(x), pkg::x): the package documentation IS
                                 the codebook. Only that dataset, never the
                                 whole manual
                 doc_names_columns
                                 a journal supplementary document (PLOS, Europe
                                 PMC; text documents only, never the data) whose
                                 TEXT names >= README_MIN_NAMES of the table's
                                 names (#2792). name_codebook there means the
                                 authors' caption or a workbook SHEET name says
                                 codebook / variables / legend
                 questionnaire   a supplementary file the authors caption as
                                 the questionnaire / instrument; kept only when
                                 nothing above documents the table (#2792)
                 recorded_at_ingest
                                 the codebook file whoever built the table
                                 named, via stage_dict_row.py `codebook_url`
                                 (automated_finding/codebook_at_ingest.csv,
                                 #2770). The strongest evidence: a person read
                                 it to write the build script

Hosts with an API that lists a deposit's files: OSF, Dataverse (Harvard and
dataverse.nl), figshare (incl. the frontiersin/plos portals), Zenodo, Mendeley
Data, GitHub, GitLab; LDbase (its server-rendered pages list typed documents);
CRAN (the reference manual's topic index); openpsychometrics.org (the zip the
table's reference or script names, listed inside -- #2787); PLOS and
Europe PMC articles (the JATS supplementary-material list; workbooks and
text documents are downloaded, size-capped, and opened -- #2792). Only tables in the matching *metadata.csv are swept: the biblio files
keep rows for renamed and retired tables (#2767). doi.org links are routed by DOI prefix, and resolved by one HEAD request
only when the prefix is unknown. Everything else (statistics offices, openICPSR, which returns 403 to scripts) is recorded in the
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
import os
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

HOST_PACE = {"osf": 2.5, "dataverse": 0.5, "figshare": 0.5, "figshare_collection": 0.5, "zenodo": 0.7,
             "mendeley": 0.7, "doi": 0.5, "github": 1.0, "gitlab": 1.0, "ldbase": 1.5, "cran": 0.5,
             "opsych": 1.0, "plos": 1.0, "epmc": 1.5}
_last_call: Dict[str, float] = {}


def match(name: str) -> Optional[str]:
    if CODE_EXT.search(name) or re.search(r"templat|plantilla|modelo_de", name, re.I):
        return None     ##a blank codebook TEMPLATE documents nothing (#2787)
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
    if net == "github.com":
        m = re.match(r"/([^/]+)/([^/]+?)(?:\.git)?(?:/(?:tree|blob)/([^/]+)(/.*)?)?/?$", path)
        if not m:
            return "skip", "github_unparsed"
        owner, repo, ref, sub = m.groups()
        if (owner.lower(), repo.lower()) == ("ben-domingue", "irw"):
            return "skip", "irw_own_script"     ##our own simulation/build scripts
        if sub and "/blob/" in path:
            sub = sub.rsplit("/", 1)[0]         ##a file link: its folder
        return "github", f"{owner}/{repo}@{ref or ''}:{(sub or '').strip('/')}"
    if net == "gitlab.com":
        m = re.match(r"/(.+?)(?:/-/.*)?/?$", path)
        return ("gitlab", m.group(1)) if m else ("skip", "gitlab_unparsed")
    if net == "ldbase.org":
        m = re.match(r"/(datasets|projects|documents)/([0-9a-f-]{36})", path)
        return ("ldbase", f"{m.group(1)}/{m.group(2)}") if m else ("skip", "ldbase_unparsed")
    if net == "cran.r-project.org":
        m = re.search(r"/packages?/([A-Za-z0-9.]+)", path) or re.search(r"package=([A-Za-z0-9.]+)", p.query)
        return ("cran", m.group(1)) if m else ("skip", "cran_unparsed")
    if net == "openpsychometrics.org":
        return "opsych", ""                     ##the zip is per table; resolved in main()
    if net == "openicpsr.org":
        return "skip", "openicpsr_blocks_scripts"
    if net == "journals.plos.org":
        m = re.search(r"(10\.1371/journal\.[a-z]{4}\.\d{7})", urllib.parse.unquote(p.query + path), re.I)
        return ("plos", m.group(1).lower()) if m else ("skip", "plos_unparsed")
    if net == "europepmc.org":
        m = re.search(r"/(PMC\d+)", path, re.I)
        return ("epmc", m.group(1).upper()) if m else ("skip", "epmc_not_pmc")
    return "skip", f"host:{net}"


def dataset_pid(pid: str) -> str:
    """A Dataverse FILE pid (doi:10.7910/DVN/ABCDEF/GHIJKL) -> its dataset's pid."""
    m = re.match(r"(doi:10\.\d+/[^/]+/[^/]+)/[^/]+$", pid, re.I)
    return m.group(1) if m else pid


def route_doi(doi: str) -> Tuple[str, str]:
    d = doi.lower()
    if d.startswith("10.1371/"):
        m = re.match(r"(10\.1371/journal\.[a-z]{4}\.\d{7})", d)
        return ("plos", m.group(1)) if m else ("skip", "plos_unparsed")
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


def get_raw(url: str, host: str, tries: int = 3, accept: str = "*/*"):
    """Like get(), for HTML and binary bodies: (status, bytes or None)."""
    for attempt in range(tries):
        wait = HOST_PACE.get(host, 1.0) - (time.time() - _last_call.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.time()
        headers = {"User-Agent": UA, "Accept": accept}
        if host == "github" and os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as r:
                return r.status, r.read(60_000_000)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(15 * (attempt + 1))
                continue
            return e.code, None
        except (urllib.error.URLError, TimeoutError):
            if attempt < tries - 1:
                time.sleep(10)
                continue
            return -1, None
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


def list_github(key: str) -> dict:
    """key = owner/repo@ref:subpath; the repository tree, under subpath."""
    repo, rest = key.split("@", 1)
    ref, sub = rest.split(":", 1)
    if not ref:
        s, b = get_raw(f"https://api.github.com/repos/{repo}", "github", accept="application/vnd.github+json")
        if s != 200:
            return {"status": f"error:{s}"}
        ref = json.loads(b)["default_branch"]
    s, b = get_raw(f"https://api.github.com/repos/{repo}/git/trees/{urllib.parse.quote(ref)}?recursive=1",
                   "github", accept="application/vnd.github+json")
    if s != 200:
        return {"status": f"error:{s}"}
    out = []
    for e in json.loads(b).get("tree") or []:
        pth = e.get("path", "")
        if e.get("type") != "blob" or (sub and not pth.startswith(sub + "/")):
            continue
        q = urllib.parse.quote(pth)
        out.append({"name": pth.rsplit("/", 1)[-1], "path": pth,
                    "url": f"https://github.com/{repo}/blob/{ref}/{q}",
                    "raw": f"https://raw.githubusercontent.com/{repo}/{ref}/{q}"})
    return {"status": "ok", "landing": f"https://github.com/{repo}", "files": out}


def list_gitlab(key: str) -> dict:
    pid = urllib.parse.quote(key, safe="")
    s, b = get_raw(f"https://gitlab.com/api/v4/projects/{pid}", "gitlab", accept="application/json")
    if s != 200:
        return {"status": f"error:{s}"}
    ref = json.loads(b).get("default_branch") or "main"
    out, page = [], 1
    while page:
        s, b = get_raw(f"https://gitlab.com/api/v4/projects/{pid}/repository/tree?recursive=true"
                       f"&per_page=100&page={page}", "gitlab", accept="application/json")
        if s != 200:
            return {"status": f"error:{s}"}
        rows = json.loads(b)
        for e in rows:
            if e.get("type") == "blob":
                q = urllib.parse.quote(e["path"])
                out.append({"name": e["name"], "path": e["path"],
                            "url": f"https://gitlab.com/{key}/-/blob/{ref}/{q}",
                            "raw": f"https://gitlab.com/{key}/-/raw/{ref}/{q}"})
        page = page + 1 if len(rows) == 100 else 0
    return {"status": "ok", "landing": f"https://gitlab.com/{key}", "files": out}


def list_ldbase(key: str) -> dict:
    """LDbase has no open API, but its pages list documents by type.

    A document titled "Codebook: X" is typed as a codebook BY THE REPOSITORY,
    which is stronger evidence than a file name. A /documents/ link is itself a
    document: its title is matched like a file name.
    """
    url = f"https://ldbase.org/{key}"
    s, b = get_raw(url, "ldbase", accept="text/html")
    if s != 200:
        return {"status": f"error:{s}"}
    h = b.decode("utf-8", "replace")
    out, seen = [], set()
    if key.startswith("documents/"):
        t = re.search(r"<title>\s*(?:Metadata for Document:\s*)?(.*?)\s*(?:\|.*)?</title>", h, re.S)
        out.append({"name": html_unescape(t.group(1)) if t else key, "url": url})
    for a, txt in re.findall(r'<a[^>]+href="(/documents/[0-9a-f-]{36})"[^>]*>(.*?)</a>', h, re.S):
        txt = html_unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", txt))).strip()
        if a in seen:
            continue
        seen.add(a)
        typed = txt.lower().startswith("codebook:")
        out.append({"name": txt.split(":", 1)[1].strip() if typed else txt,
                    "url": "https://ldbase.org" + a, "typed": typed})
    return {"status": "ok", "landing": url, "files": out}


def html_unescape(x: str) -> str:
    import html
    return html.unescape(x)


def list_cran(pkg: str) -> dict:
    """The package's help topics, from the official reference-manual index."""
    url = f"https://search.r-project.org/CRAN/refmans/{pkg}/html/00Index.html"
    s, b = get_raw(url, "cran", accept="text/html")
    if s != 200:
        return {"status": f"error:{s}"}
    topics = sorted(set(re.findall(r'href="([^"/#]+)\.html"', b.decode("utf-8", "replace"))))
    return {"status": "ok", "landing": f"https://cran.r-project.org/package={pkg}",
            "files": [{"name": t, "url": f"https://search.r-project.org/CRAN/refmans/{pkg}/html/{t}.html",
                       "topic": True} for t in topics if t != "00Index"]}


def list_opsych(zipname: str) -> dict:
    """The files inside one openpsychometrics.org zip (all < 10 MB, 10-02)."""
    import zipfile
    url = f"https://openpsychometrics.org/_rawdata/{zipname}"
    s, b = get_raw(url, "opsych")
    if s != 200 or not b:
        return {"status": f"error:{s}"}
    try:
        names = [n for n in zipfile.ZipFile(io.BytesIO(b)).namelist() if not n.endswith("/")]
    except zipfile.BadZipFile:
        return {"status": "error:bad_zip"}
    return {"status": "ok", "landing": url,
            "files": [{"name": n.rsplit("/", 1)[-1], "inner": n, "url": url} for n in names]}


##--- journal supplementary files (PLOS, Europe PMC; #2792) -----------------
##PLOS authors almost never upload a file called a codebook (0 of 40 sampled
##articles, 10-02); the files are S1_File.xlsx. So an article's supplementary
##files are judged by what is IN them or what the authors' caption says:
##  name_codebook      the caption says codebook / data dictionary / ..., or a
##                     workbook has a SHEET with such a name
##  doc_names_columns  a text document (never .csv/.xlsx: those may be the
##                     data, whose header names every column) names >=
##                     README_MIN_NAMES of the table's own names
##  questionnaire      the caption says questionnaire / instrument; shown only
##                     when none of the above was found for the table

PLOS_JOURNALS = {"pone": "plosone", "pmed": "plosmedicine", "pbio": "plosbiology",
                 "pcbi": "ploscompbiol", "pgen": "plosgenetics", "ppat": "plospathogens",
                 "pntd": "plosntds", "pgph": "globalpublichealth", "pdig": "digitalhealth",
                 "pclm": "climate", "pmen": "mentalhealth", "pwat": "water",
                 "pstr": "sustainabilitytransformation", "pcsy": "complexsystems"}
CAPTION_CODEBOOK = re.compile(
    r"code[\s_-]?book|data[\s_-]?dictionar|variable[\s_-]?(list|label|description|definition|key|guide)s?|"
    r"(description|definition|list)s? of (the |all )?variables|data[\s_-]?key|"
    r"legend (of|for) (the )?(variables|data|codes|columns)|libro de c[oó]digos|diccionario de (datos|variables)",
    re.I)
CAPTION_SKIP = re.compile(r"^attachment$|checklist|reviewer|response to|strobe|prisma|consort|"
                          r"tripod|stard|arrive|minimal (underlying )?data set? (statement|policy)", re.I)
CAPTION_QUESTIONNAIRE = re.compile(r"questionnaires?|\binstruments?\b|survey (items|form|tool|instrument)|"
                                   r"\bscale items|item (wording|list)|survey questions|cuestionario|question[aá]rio", re.I)
CAPTION_IS_DATA = re.compile(r"\bdata(set|base)?\b|\bresponses\b|\braw\b", re.I)
##Results tables name the items too (loadings per item, correlations): naming
##the columns is not documenting them. Pilot 10-02: "correlations between
##PHQ-9 items and with other questionnaires", "Data processing output".
CAPTION_RESULTS = re.compile(r"correlat|coefficient|loading|descriptive|statistic|regression|\bresults?\b|"
                             r"output|\bfit\b|invariance|distribution|\bmeans?\b|anova|reliabilit|"
                             r"\balpha\b|frequenc|percentage|\bscores\b|analys[ie]s|matrix|\bfactors?\b", re.I)
##A qualitative coding scheme for interviews is called a codebook too, and
##documents no column (pilot: "Interview codebook").
CAPTION_EXPLICIT = re.compile(r"code[\s_-]?book|dictionar|variable[\s_-]?(description|definition)s?", re.I)
CAPTION_QUALITATIVE = re.compile(r"interview|qualitative|thematic|open[- ]ended|focus group|translation", re.I)
SHEET_CODEBOOK = re.compile(r"^\s*(variables?|legend|descriptions?|data description|variable description|"
                            r"key|codes|coding)\s*$", re.I)
WORKBOOK_EXT = {"xlsx", "xlsm", "xls"}
TEXT_DOC_EXT = {"docx", "doc", "pdf", "txt", "rtf", "odt"}
SUPP_CAP = 60_000_000           ##bytes; a larger file is listed but not opened
_TEXTS: Optional[Dict[str, str]] = None


def texts() -> Dict[str, str]:
    """README / document texts by link url (README_CACHE), loaded once."""
    global _TEXTS
    if _TEXTS is None:
        _TEXTS = json.loads(README_CACHE.read_text()) if README_CACHE.exists() else {}
    return _TEXTS


def sheet_names(raw: bytes, ext: str) -> Optional[List[str]]:
    try:
        if ext == "xls" and raw[:2] != b"PK":
            import xlrd
            return xlrd.open_workbook(file_contents=raw, on_demand=True).sheet_names()
        import openpyxl
        return openpyxl.load_workbook(io.BytesIO(raw), read_only=True).sheetnames
    except Exception:
        return None


def caption_kind(label: str, caption: str) -> Optional[str]:
    """What the authors' own label + caption says the file is."""
    lc = f"{label} {caption}"
    if CAPTION_CODEBOOK.search(lc) and not CAPTION_QUALITATIVE.search(lc):
        ##"Dataset ... with English variable labels" is the data file
        if not (CAPTION_IS_DATA.search(lc) and not CAPTION_EXPLICIT.search(lc)):
            return "name_codebook"
    if CAPTION_IS_DATA.search(lc) or CAPTION_RESULTS.search(lc):
        return "data_or_results"
    ##"Dutch guidelines for questionnaire research", "List of controls and
    ##instruments used" (full run, 10-02)
    if CAPTION_QUESTIONNAIRE.search(lc) and not re.search(r"guideline|\bcontrols\b", lc, re.I):
        return "questionnaire"
    return None


def open_supp(f: dict, raw: Optional[bytes]) -> None:
    """Fill a supplementary file's sheets (workbooks) or text (documents), in place."""
    ext = f["name"].lower().rsplit(".", 1)[-1] if "." in f["name"] else ""
    if raw is None:
        f["opened"] = "too_large_or_failed"
        return
    f["opened"] = "ok"
    if ext in WORKBOOK_EXT:
        f["sheets"] = sheet_names(raw, ext)
    elif ext in TEXT_DOC_EXT:
        texts()[f["url"]] = extract_text(raw, f["name"])[:400_000]


def wants_bytes(f: dict) -> bool:
    ext = f["name"].lower().rsplit(".", 1)[-1] if "." in f["name"] else ""
    return ext in WORKBOOK_EXT or ext in TEXT_DOC_EXT


def get_capped(url: str, host: str, cap: int = SUPP_CAP, timeout: int = 180) -> Tuple[int, Optional[bytes]]:
    """get_raw with a size cap: (status, bytes), bytes None if over the cap."""
    for attempt in range(3):
        wait = HOST_PACE.get(host, 1.0) - (time.time() - _last_call.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
                b = r.read(cap + 1)
                return r.status, (b if len(b) <= cap else None)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(30 * (attempt + 1))
                continue
            return e.code, None
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < 2:
                time.sleep(15)
                continue
            return -1, None
    return -1, None


def _jats_text(x: str) -> str:
    return html_unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x))).strip()


def jats_supplements(xml: str) -> List[dict]:
    """label, caption, href, mimetype of each <supplementary-material>, deduplicated by href."""
    out, seen = [], set()
    for m in re.finditer(r"<supplementary-material\b(.*?)</supplementary-material>", xml, re.S):
        body = m.group(1)
        href = re.search(r'xlink:href="([^"]+)"', body)
        if not href or href.group(1) in seen:
            continue
        seen.add(href.group(1))
        lab = re.search(r"<label>(.*?)</label>", body, re.S)
        cap = re.search(r"<caption>(.*?)</caption>", body, re.S)
        mime = re.search(r'mimetype="([^"]*)"(?:\s+mime-subtype="([^"]*)")?', body)
        out.append({"href": href.group(1), "label": _jats_text(lab.group(1)) if lab else "",
                    "caption": _jats_text(cap.group(1)) if cap else "",
                    "mime": "/".join(x for x in (mime.groups() if mime else ()) if x)})
    return out


def _ext_of(sup: dict) -> str:
    m = re.search(r"\(([A-Z0-9]{2,5})\)\s*$", sup["caption"])
    if m:
        return m.group(1).lower()
    mt = sup["mime"].lower()
    for k, v in (("spreadsheetml", "xlsx"), ("ms-excel", "xls"), ("wordprocessingml", "docx"),
                 ("msword", "doc"), ("pdf", "pdf"), ("text/plain", "txt"), ("rtf", "rtf"),
                 ("zip", "zip"), ("csv", "csv")):
        if k in mt:
            return v
    return ""


def list_plos(doi: str) -> dict:
    """A PLOS article's supplementary files, from its JATS XML; workbooks and
    text documents are downloaded (size-capped) and opened."""
    code = doi.split(".")[-2]
    journal = PLOS_JOURNALS.get(code)
    if not journal:
        return {"status": f"error:unknown_journal_{code}"}
    base = f"https://journals.plos.org/{journal}/article"
    s, b = get_raw(f"{base}/file?id={doi}&type=manuscript", "plos", accept="application/xml")
    if s != 200 or not b:
        return {"status": f"error:{s}"}
    out = []
    for sup in jats_supplements(b.decode("utf-8", "replace")):
        sid = sup["href"].rsplit(".", 1)[-1]             ##s001
        if CAPTION_SKIP.search(sup["label"]) or CAPTION_SKIP.search(sup["caption"]):
            continue
        ext = _ext_of(sup)
        f = {"name": sup["label"].replace(" ", "_") + (f".{ext}" if ext else ""), "supp_id": sid,
             "url": f"{base}/file?type=supplementary&id={doi}.{sid}",
             "label": sup["label"], "caption": sup["caption"]}
        if wants_bytes(f):
            s2, raw = get_capped(f["url"], "plos")
            open_supp(f, raw if s2 == 200 else None)
        out.append(f)
    return {"status": "ok", "landing": f"{base}?id={doi}", "files": out}


def list_epmc(pmcid: str) -> dict:
    """A PMC article's supplementary files: the captions from Europe PMC's
    full-text XML, the bytes from its one-zip-per-article endpoint. The public
    link is the file on pmc.ncbi.nlm.nih.gov."""
    rest = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}"
    s, b = get_raw(f"{rest}/fullTextXML", "epmc", tries=5, accept="application/xml")
    if s != 200 or not b:
        return {"status": f"error:{s}"}
    sups = [x for x in jats_supplements(b.decode("utf-8", "replace"))
            if not (CAPTION_SKIP.search(x["label"]) or CAPTION_SKIP.search(x["caption"]))]
    out = []
    for sup in sups:
        name = sup["href"].rsplit("/", 1)[-1]
        out.append({"name": name, "label": sup["label"], "caption": sup["caption"],
                    "url": f"https://pmc.ncbi.nlm.nih.gov/articles/instance/{pmcid[3:]}/bin/{urllib.parse.quote(name)}"})
    if any(wants_bytes(f) for f in out):
        import zipfile
        s2, raw = get_capped(f"{rest}/supplementaryFiles", "epmc", cap=4 * SUPP_CAP,
                              timeout=600)   ##it builds the zip first: 230 s seen 10-02
        zf = None
        if s2 == 200 and raw:
            try:
                zf = zipfile.ZipFile(io.BytesIO(raw))
            except zipfile.BadZipFile:
                zf = None
        inner = {n.rsplit("/", 1)[-1]: n for n in (zf.namelist() if zf else [])}
        for f in out:
            if wants_bytes(f):
                n = inner.get(f["name"])
                open_supp(f, zf.read(n) if n and zf.getinfo(n).file_size <= SUPP_CAP else None)
    return {"status": "ok", "landing": f"https://europepmc.org/article/PMC/{pmcid}", "files": out}


def caption_owners(caption: str, siblings: set) -> set:
    """The article's tables a caption names by acronym ("CBI-K" -> jeon_2019_cbi).

    Empty when it names none of them: then the file is the article's and goes
    to every table. When it names some, it belongs to those only (pilot 10-02:
    the CBI-K questionnaire was attached to the article's CES-D table).
    """
    toks = set()
    for a in re.findall(r"\b[A-Z][A-Za-z0-9]*[A-Z][A-Za-z0-9-]*\b", caption):
        toks |= {x.lower() for x in [a.replace("-", "")] + a.split("-") if len(x) >= 3}
    return {s for s in siblings if any(tok in part for part in s.lower().split("_") if len(part) >= 3
                                       for tok in toks)}


def supp_hits(t: str, h: str, res: dict, own_ids: set, checked_at: str,
              siblings: Optional[set] = None) -> List[dict]:
    """Candidate rows for one table from one article's supplementary files.

    Text documents become `doc_candidate` rows, judged against the table's
    names by check_readmes (kept as doc_names_columns or dropped). The table's
    own data file is never a candidate for the content check.
    """
    hits = []
    for f in res.get("files") or []:
        row = {"table": t, "url": f["url"], "host": h, "checked_at": checked_at,
               "file_name": f["name"]}
        kind = caption_kind(f.get("label", ""), f.get("caption", ""))
        owners = caption_owners(f.get("caption", ""), siblings or set())
        if owners and t not in owners:
            continue
        if kind == "name_codebook":
            hits.append({**row, "how_found": "name_codebook", "evidence": f"caption: {f['caption'][:200]}"})
            continue
        sheets = [x for x in (f.get("sheets") or []) if CODEBOOK.search(x) or SHEET_CODEBOOK.match(x)]
        for sh in sheets:
            hits.append({**row, "url": f["url"], "file_name": f"{sh} (sheet in {f['name']})",
                         "how_found": "name_codebook", "evidence": "sheet name"})
        if sheets:
            continue
        ext = f["name"].lower().rsplit(".", 1)[-1] if "." in f["name"] else ""
        if (ext in TEXT_DOC_EXT and kind != "data_or_results" and f.get("supp_id", f["url"]) not in own_ids
                and f["url"] in texts()):
            hits.append({**row, "how_found": "doc_candidate", "evidence": ""})
        if kind == "questionnaire":
            hits.append({**row, "how_found": "questionnaire", "evidence": f"caption: {f['caption'][:200]}"})
    return hits


LISTERS = {"zenodo": list_zenodo, "figshare": list_figshare, "figshare_collection": list_figshare_collection, "mendeley": list_mendeley,
           "github": list_github, "gitlab": list_gitlab, "ldbase": list_ldbase, "cran": list_cran,
           "opsych": list_opsych, "plos": list_plos, "epmc": list_epmc,
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
    if h in ("github", "gitlab"):
        return link.get("raw") or None
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
    """The names the text contains, whole-word, case-blind, each counted once
    (`Education` and `education` from two sources are one name)."""
    low, seen, out = text.lower(), set(), []
    for n in names:
        k = n.lower()
        if k not in seen and re.search(r"(?<![a-z0-9_])" + re.escape(k) + r"(?![a-z0-9_])", low):
            seen.add(k)
            out.append(n)
    return out


def read_csv(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[dict], fields: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def check_readmes(links: List[dict], offline: bool) -> None:
    """Promote README rows whose text names the table's columns (in place)."""
    texts_ = texts()
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
    readmes = [x for x in links if x["how_found"] in ("name_readme", "doc_candidate")]
    for i, x in enumerate(readmes):
        text = readme_text(x, texts_, offline)
        names = table_names(x["table"], dataset_of.get(x["table"].lower()), names_cache, docs, offline,
                            scripts_of.get(x["table"].lower()))
        if text is None or names is None:
            x["evidence"] = "not checked"
        elif not text.strip():
            x["evidence"] = "unreadable"
        else:
            hit = names_in_text(names, text)
            x["evidence"] = f"names {len(hit)}/{len(names)}" + (": " + ", ".join(hit[:8]) if hit else "")
            ##a journal document must name something besides covariates: a
            ##questionnaire matching only demographics (Education, Tenure)
            ##shows nothing about this table's items (pilot 10-02)
            covs = {n.lower() for r in docs.get(x["table"].lower(), []) if r["column"].startswith("cov_")
                    for n in (r["column"][4:], r.get("source_column") or "")}
            items_hit = [n for n in hit if n.lower() not in covs] \
                if x["how_found"] == "doc_candidate" else ["n/a"]
            ##plain words (economic, health, afraid) turn up in any text on the
            ##topic: with fewer than README_MIN_NAMES specific names (a code,
            ##a phrase), a document must name at least half the table's names
            if x["how_found"] == "doc_candidate":
                specific = [n for n in hit if re.search(r"[0-9_ ]|[a-z][A-Z]", n)]
                if len(specific) < README_MIN_NAMES and len(hit) < max(README_MIN_NAMES, len(names) / 2):
                    items_hit = []
            if len(hit) >= README_MIN_NAMES and items_hit:
                x["how_found"] = ("doc_names_columns" if x["how_found"] == "doc_candidate"
                                  else "readme_names_columns")
        if not offline and i % 25 == 24:
            README_CACHE.write_text(json.dumps(texts_, ensure_ascii=False))
            NAMES_CACHE.write_text(json.dumps(names_cache, ensure_ascii=False))
    if not offline:
        README_CACHE.write_text(json.dumps(texts_, ensure_ascii=False))
        NAMES_CACHE.write_text(json.dumps(names_cache, ensure_ascii=False))
    ##a journal document that does not name the table's columns is not linked;
    ##a questionnaire is shown only when nothing documents the columns (#2792)
    links[:] = [x for x in links if x["how_found"] != "doc_candidate"]
    documented = {x["table"] for x in links if x["host"] in ("plos", "epmc")
                  and x["how_found"] in ("name_codebook", "doc_names_columns")}
    links[:] = [x for x in links if not (x["how_found"] == "questionnaire" and x["table"] in documented)]
    for kind in ("doc_names_columns", "questionnaire"):
        for t in {x["table"] for x in links if x["how_found"] == kind}:
            same = [x for x in links if x["table"] == t and x["how_found"] == kind]
            for x in same:
                x["n_same_kind_in_deposit"] = len(same)
    ##n_same_kind counts the README kinds again now that some were promoted
    by_dep: Dict[Tuple[str, str], int] = {}
    for x in links:
        if x["how_found"] in ("name_readme", "readme_names_columns"):
            by_dep[(x["table"], x["how_found"])] = by_dep.get((x["table"], x["how_found"]), 0) + 1
    for x in links:
        if x["how_found"] in ("name_readme", "readme_names_columns"):
            x["n_same_kind_in_deposit"] = by_dep[(x["table"], x["how_found"])]
        x.setdefault("evidence", "")


def table_context() -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """table -> its build scripts (stage 13), and table -> its biblio citation text."""
    scripts = {r["table"]: [x for x in re.split(r"[;|]\s*", r.get("scripts") or "") if x]
               for r in read_csv(TABLE_SCRIPTS)}
    cite: Dict[str, str] = {}
    for b in BIBLIOS:
        for r in read_csv(HERE / b):
            cite.setdefault(r["table"], (r.get("Reference_x") or "") + " " + (r.get("BibTex") or ""))
    return scripts, cite


def script_text(paths: List[str]) -> str:
    out = []
    for p in paths:
        try:
            out.append((HERE.parent / p).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass
    return "\n".join(out)


def opsych_zip(table: str, scripts: Dict[str, List[str]], cite: Dict[str, str]) -> Optional[str]:
    """The openpsychometrics.org zip a table's citation or build script names.

    Exactly one, or None: several candidates (or none) is not something to pick
    between.
    """
    zips = set(re.findall(r"openpsychometrics\.org/_rawdata/([A-Za-z0-9_.-]+\.zip)",
                          cite.get(table, "") + " " + script_text(scripts.get(table, []))))
    return zips.pop() if len(zips) == 1 else None


def cran_datasets(table: str, pkg: str, scripts: Dict[str, List[str]]) -> set:
    """Names the table's build script loads or uses as data from the package.

    Battery scripts build one table per section and end it with
    save(df, file="<table>.Rdata") or write.csv(df, file="<table>.csv"), so the
    section ending in THIS table's file is the one read; a script with no such
    write is read whole. Candidates are only kept if they are help topics of
    the package (checked by the caller), so `NAME$...` and `x <- NAME` are safe
    to collect: a base function never appears in a package's topic index.
    """
    src = script_text(scripts.get(table, []))
    if not src:
        return set()
    writes = list(re.finditer(r"""(?:save|write\.csv|write\.table|fwrite|write_csv)\([^)]*?file\s*=\s*["']([^"']+)["']""", src))
    seg = src
    for i, m in enumerate(writes):
        stem = re.sub(r"\.(rdata|rda|csv|rds)$", "", m.group(1).rsplit("/", 1)[-1], flags=re.I)
        if stem.lower() == table.lower():
            seg = src[(writes[i - 1].end() if i else 0):m.start()]
            break
    names = set(re.findall(r"""load\(\s*["'](?:[^"']*/)?([A-Za-z0-9_.]+)\.(?:rda|rdata)["']""", seg, re.I))
    names |= set(re.findall(r"""\bdata\(\s*["']?([A-Za-z][A-Za-z0-9_.]*)""", seg))
    names |= set(re.findall(re.escape(pkg) + r"::([A-Za-z][A-Za-z0-9_.]*)", seg))
    names |= set(re.findall(r"\b([A-Za-z][A-Za-z0-9_.]*)\$", seg))
    names |= set(re.findall(r"<-\s*([A-Za-z][A-Za-z0-9_.]*)\s*(?:$|\n|\[)", seg))
    return {n for n in names if n not in ("list", "package")}


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
    ap.add_argument("--rematch", default="",
                    help="with --new-only: comma list of hosts whose tables are matched again "
                         "(from the listing cache, so rule changes apply)")
    ap.add_argument("--sample", type=int, default=0,
                    help="seed: crawl deposits in a seeded random order (pilots, with --limit)")
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
    scripts_of, cite_of = table_context()

    ##--new-only: what is already committed stands; only unseen tables are swept
    kept_links: List[dict] = []
    kept_checked: List[dict] = []
    if args.new_only:
        prev_checked = [r for r in read_csv(CHECKED_OUT) if r["table"] in live_tables]
        ##a table whose host was out of scope and is now listable (#2787) is
        ##swept again; everything else already checked stands
        newly = {r["table"] for r in prev_checked
                 if r["outcome"].startswith("out_of_scope") and route(r["data_url"])[0] != "skip"}
        rematch = set(filter(None, args.rematch.split(",")))
        newly |= {r["table"] for r in prev_checked if r["host"] in rematch}
        done = {r["table"] for r in prev_checked if r["outcome"] != "not_yet_checked"} - newly
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
            if h == "opsych":
                z = opsych_zip(t, scripts_of, cite_of)
                h, k = ("opsych", z) if z else ("skip", "opsych_no_zip_named")
            if h == "doi":
                ck = f"doi|{k}"
                if ck not in cache and not args.offline and (not hosts or "doi" in hosts):
                    hh, kk = resolve_doi(k)
                    cache[ck] = {"status": "resolved", "host": hh, "key": kk, "checked_at": today}
                h, k = (cache[ck]["host"], cache[ck]["key"]) if ck in cache else ("skip", "doi_not_resolved_yet")
            routed[t].append((u, h, k))

    todo = sorted({(h, k) for rs in routed.values() for _, h, k in rs if h in LISTERS and (not hosts or h in hosts)})
    if args.sample:
        import random
        random.Random(args.sample).shuffle(todo)
    ##An offline FULL run rebuilds both CSVs from the local listing cache alone.
    ##A cache that is missing deposits (a fresh worktree, a deleted cache) would
    ##silently drop every table it lacks -- it did, on 10-02, down to 299 of
    ##1,028 tables before anything was committed. Refuse; --new-only is safe.
    if args.offline and not args.new_only:
        missing = [d for d in todo if f"{d[0]}|{d[1]}" not in cache]
        if len(missing) > 0.05 * max(len(todo), 1):
            sys.exit(f"--offline without --new-only would rebuild from a cache missing "
                     f"{len(missing)} of {len(todo)} deposits and drop their rows. "
                     f"Use --new-only --offline, or run online to fill the cache.")
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
            README_CACHE.write_text(json.dumps(texts(), ensure_ascii=False))
    if not args.offline:   ##an offline re-match must not race a crawl writing the cache
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=0, ensure_ascii=False))
        README_CACHE.write_text(json.dumps(texts(), ensure_ascii=False))

    siblings: Dict[Tuple[str, str], set] = {}
    for t, rs in routed.items():
        for _, h, k in rs:
            siblings.setdefault((h, k), set()).add(t)
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
            if h in ("plos", "epmc"):
                own = {sid for uu, hh, _ in routed[t] if hh == "plos" for sid in re.findall(r"\.(s\d{3})\b", uu)}
                hits = supp_hits(t, h, res, own, row["checked_at"], siblings.get((h, k), set()))
                for kind in ("name_codebook",):
                    same = [x for x in hits if x["how_found"] == kind]
                    for x in same:
                        x["n_same_kind_in_deposit"] = len(same)
                for x in hits:
                    x.setdefault("n_same_kind_in_deposit", "")
                    x["deposit_url"] = res.get("landing", "")
                links += hits
                kinds = sorted({x["how_found"] for x in hits})
                row["outcome"] = "hit:" + "+".join(kinds) if kinds else "no_match"
                continue
            hits = []
            wanted = cran_datasets(t, k, scripts_of) if h == "cran" else set()
            for f in res.get("files") or []:
                if f.get("topic"):
                    ##a CRAN help topic counts only for the dataset this table loads
                    if f["name"] in wanted:
                        hits.append({"table": t, "url": f["url"], "file_name": f"{k}::{f['name']}",
                                     "host": h, "how_found": "package_doc", "checked_at": row["checked_at"]})
                    continue
                how = "typed_codebook" if f.get("typed") else match(f["name"])
                if how:
                    name = (f"{f['name']} (inside {k})" if h == "opsych" else f.get("path") or f["name"])
                    hits.append({"table": t, "url": f["url"], "file_name": name, "raw": f.get("raw", ""),
                                 "host": h, "how_found": how, "checked_at": row["checked_at"],
                                 "evidence": (f"in zip: {f['inner']}" if h == "opsych" else "")})
                if f.get("ddi"):
                    hits.append({"table": t, "url": f["ddi"], "file_name": f["name"], "host": h,
                                 "how_found": "dataverse_ddi", "checked_at": row["checked_at"]})
            ##A deposit with many codebooks (one per scale, say) attaches all of
            ##them to every table it built. Matching a table to one of them means
            ##decoding abbreviations (FamBel = family_belonging), which is the
            ##guessing this script refuses; record the count and the deposit's
            ##landing page so a page can say "19 codebook files in the deposit".
            for kind in ("name_codebook", "name_readme", "typed_codebook", "package_doc"):
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
    else:
        links = [x for x in links if x["how_found"] != "doc_candidate"]

    for x in links:
        x.setdefault("evidence", "")
    links = ingest_links(live_tables) + kept_links + links
    ##one row per (table, url): a deposit reached by two routes (a multi-URL
    ##cell, a child component) lists the same file twice. Keep the strongest.
    rank = {"recorded_at_ingest": 0, "typed_codebook": 1, "package_doc": 1, "name_codebook": 1,
            "readme_names_columns": 2, "doc_names_columns": 2,
            "name_readme": 3, "questionnaire": 3, "doc_candidate": 8, "dataverse_ddi": 4}
    best: Dict[Tuple[str, str], dict] = {}
    for x in links:
        k = (x["table"], x["url"])
        if k not in best or rank.get(x["how_found"], 9) < rank.get(best[k]["how_found"], 9):
            best[k] = x
    links = list(best.values())
    ##journal outcomes from the FINAL links: a doc_candidate judged against
    ##the table's names is kept or dropped only after the content check
    final_kinds: Dict[Tuple[str, str], set] = {}
    for x in links:
        if x["host"] in ("plos", "epmc"):
            final_kinds.setdefault((x["table"], x["host"]), set()).add(x["how_found"])
    for row in checked:
        if row["host"] in ("plos", "epmc") and (row["outcome"].startswith("hit:") or row["outcome"] == "no_match"):
            kinds = sorted(final_kinds.get((row["table"], row["host"]), ()))
            row["outcome"] = "hit:" + "+".join(kinds) if kinds else "no_match"
    checked = kept_checked + checked
    links.sort(key=lambda x: (x["table"].lower(), x["how_found"], x["url"]))
    checked.sort(key=lambda x: (x["table"].lower(), x["data_url"]))
    write_csv(LINKS_OUT, links, LINK_FIELDS)
    write_csv(CHECKED_OUT, checked, CHECKED_FIELDS)
    print(f"{len(links)} links for {len({x['table'] for x in links})} tables -> {LINKS_OUT.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
