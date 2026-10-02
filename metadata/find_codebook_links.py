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
                 name_readme     README only. Kept apart because a README may or
                                 may not describe the variables; whether the
                                 site shows these is undecided (#2766)
                 dataverse_ddi   Dataverse's public DDI export for a tabular
                                 file (variable names + labels), which works
                                 even when the file itself is guestbook-gated

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
--offline without touching any API.

Not a pipeline stage: a full crawl is ~700 deposits, OSF has to be paced
(~2.5s per call, osf-api sweeps 429 when fanned out), and codebook files do
not change once deposited. Run by hand, niced:

    nice -n 19 python3 metadata/find_codebook_links.py [--hosts osf,zenodo] [--limit N]
    python3 metadata/find_codebook_links.py --offline     ##re-match the cache only
"""
from __future__ import annotations

import argparse
import csv
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
UA = "irw-codebook-links/1.0 (+https://itemresponsewarehouse.org; ben-domingue/irw#2766)"

##Python does not happy-eyeball, and figshare/OSF/doi.org publish dead AAAA
##records from here: every call stalls ~20s on IPv6 before falling back.
_gai = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _gai(*a, **k) if r[0] == socket.AF_INET]

CODEBOOK = re.compile(
    r"code[\s_-]?book|data[\s_-]?dictionar|dictionar(y|ies)\b|_dictionary|"
    r"^variables?[\s_.-]|variable[\s_-]?(list|label|description|key|guide)s?|data[\s_-]?key|\bddi\b|"
    r"libro[\s_-]?de[\s_-]?c[oó]digos|diccionario|livro[\s_-]?de[\s_-]?c[oó]digos|"
    r"dicion[aá]rio|codificaci[oó]n|code[\s_-]?sheet|coding[\s_-]?(scheme|manual|key)",
    re.I,
)
README = re.compile(r"read[\s_-]?me|l[eé]ame", re.I)
##A file named `codebook.R` is the code that writes one, not the codebook.
CODE_EXT = re.compile(r"\.(r|py|do|sps|sas|jl|m|ipynb)$", re.I)

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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hosts", default="", help="comma list to crawl (default: all crawlable)")
    ap.add_argument("--limit", type=int, default=0, help="crawl at most N new deposits")
    ap.add_argument("--offline", action="store_true", help="no network; re-match cached listings")
    ap.add_argument("--recheck", action="store_true", help="re-list deposits already in the cache")
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

    write_csv(LINKS_OUT, links, ["table", "url", "file_name", "host", "how_found",
                                 "n_same_kind_in_deposit", "deposit_url", "checked_at"])
    write_csv(CHECKED_OUT, checked, ["table", "data_url", "host", "deposit", "outcome", "checked_at"])
    print(f"{len(links)} links for {len({x['table'] for x in links})} tables -> {LINKS_OUT.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
