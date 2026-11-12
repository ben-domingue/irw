#!/usr/bin/env python3
"""openESM -> IRW: plan a record, review the plan, emit a data script.

openESM (https://openesmdata.org) publishes each experience sampling dataset as
a harmonised `<dataset_id>_ts.tsv` on Zenodo, plus a metadata record in
https://github.com/openesm-project/openesm-metadata that describes every
column: its type (`rating_scale`, `binary`, ...), its wording and anchors
(`coding`), its construct. That is most of what a hand-written ingest script
works out by reading a codebook, so most of the script can be generated.

Not all of it. The first 13 records (#1698) turned up time stamps marked UTC
that are local time, a file whose row order is not time order, -1 meaning "not
applicable" inside a 1-7 scale, slider *start positions* typed as rating
scales, and codebook ranges the data contradict. None of that is decidable
from the metadata. So the tool works in two steps, with a person between them:

  plan   writes automated_finding/openesm/<dataset_id>.json (the spec) and
         <dataset_id>_report.md. The spec holds every decision -- which columns
         are items, how they split into tables, what `wave` and `date` are --
         pre-filled where the metadata settles it, "TODO" where it does not,
         and a `flags` list of the things a person must look at. Each flag
         needs a written `resolution`; those sentences become the coding notes
         in the script's docstring.
  emit   refuses while any TODO or unresolved flag remains, then writes a
         self-contained data/<script>.py (CLAUDE.md: data scripts do not
         import shared code) and <dataset_id>_dict.jsonl, one dictionary row
         per table for stage_dict_row.py.

Then run the generated script like any other in data/, and review its output
the same way.

Usage (from src/):
  python automated_finding/openesm_ingest.py status
  python automated_finding/openesm_ingest.py plan 0013          # or 0013_hoebeke
  python automated_finding/openesm_ingest.py emit automated_finding/openesm/0013_hoebeke.json
  python data/<script>.py
  python automated_finding/stage_dict_row.py --source-via openESM < <one line of the .jsonl>

`plan` refuses a record that is already in IRW (built from openESM, or held
from the original deposit) unless --force; --force exists to re-plan a built
record as a check on this tool, not to ingest it twice. A record with fewer
than 100 people is flagged rather than refused: datastandard.md's floor would
skip it, but whether that floor binds ESM data is open (#3421).

Network: the openESM metadata bundle (GitHub), the Zenodo API, and the OSF or
Zenodo API for the original deposit's licence. Downloads are cached in
~/.cache/irw/openesm.
"""

import argparse
import datetime as dt
import json
import os
import pprint
import re
import sys
import textwrap
import unicodedata
from collections import Counter, OrderedDict
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent            # src/automated_finding
SRC = HERE.parent                                 # src/
SPEC_DIR = HERE / "openesm"
DATA_DIR = SRC / "data"
CACHE = Path(os.environ.get("IRW_OPENESM_CACHE",
                            Path.home() / ".cache" / "irw" / "openesm"))
METADATA_URL = ("https://raw.githubusercontent.com/openesm-project/"
                "openesm-metadata/main/datasets.json")
HEADERS = {"User-Agent": "IRW-openESM-ingest/1.0"}

# Studies openESM catalogues that IRW took from the original deposit before
# the openESM ingest. They carry no openESM note, deliberately: `Source via`
# records the route we took (ruled 2026-10-21).
HELD_INDEPENDENTLY = {
    "0001": "mhscdc_fried_2020_* (osf.io/mvdpe)",
    "0008": "westhoff2023_{pbat,stopd} (osf.io/ejtzs)",
    "0019": "soderberg_2024_* (zenodo 13332148)",
}

# openESM label -> the spelling the dictionary uses. A label not here stops
# the plan: it needs reading (e.g. "CC0 1.0 - modified").
LICENCES = {
    "CC-BY 4.0": "CC BY 4.0", "CC BY 4.0": "CC BY 4.0",
    "CC BY-NC 4.0": "CC BY-NC 4.0", "CC BY-NC-SA 4.0": "CC BY-NC-SA 4.0",
    "CC BY-SA 4.0": "CC BY-SA 4.0", "CC0 1.0": "CC0 1.0", "GPL-3.0": "GPL-3.0",
}



def norm_licence(name):
    """'CC-By Attribution 4.0 International' (OSF), 'cc-by-4.0' (Zenodo),
    'CC BY 4.0' (Figshare) -> 'CC BY 4.0'. Unrecognised names come back as is."""
    n = re.sub(r"[-_\s]+", " ", (name or "").lower())
    n = n.replace("attribution", "by").replace("noncommercial", "nc") \
         .replace("non commercial", "nc").replace("sharealike", "sa") \
         .replace("share alike", "sa").replace("noderivatives", "nd")
    if re.search(r"\bcc ?0\b|public domain|zero", n):
        return "CC0 1.0"
    if n.startswith("cc"):
        parts = [p for p in ("by", "nc", "nd", "sa") if re.search(rf"\b{p}\b", n)]
        ver = re.search(r"(\d\.\d)", n)
        return "CC " + "-".join(p.upper() for p in parts) + (f" {ver.group(1)}" if ver else "")
    return name


ITEM_TYPES = {"rating_scale"}               # items by default
CANDIDATE_TYPES = {"binary", "numeric"}     # a person decides
TIME_TYPES = {"PosixCt"}
STRUCTURE = {"id", "day", "beep", "counter"}
NA_LABEL = re.compile(r"not applicable|\bn/?a\b|don.?t know|no answer|"
                      r"missing|prefer not|no contact", re.I)
ANCHOR = re.compile(r"(-?\d+(?:\.\d+)?)\s*=\s*(.*?)\s*"
                    r"(?=(?:\s-?\d+(?:\.\d+)?\s*=)|\n|$)")
TODO = "TODO"
MIN_IDS = 100                               # datastandard.md sample floor


# --------------------------------------------------------------------------
# sources

def get_json(url, **kw):
    r = requests.get(url, headers=HEADERS, timeout=60, **kw)
    r.raise_for_status()
    return r.json()


def catalogue():
    """openESM's bundled metadata, cached for a day."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "datasets.json"
    fresh = (path.exists() and dt.datetime.now().timestamp()
             - path.stat().st_mtime < 86400)
    if not fresh:
        r = requests.get(METADATA_URL, headers=HEADERS, timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
    recs = json.loads(path.read_text())["datasets"]
    return {f"{r['dataset_id']}_{slug(r['first_author'])}": r for r in recs}


def find(cat, key):
    hits = [k for k in cat if k == key or k.split("_")[0] == key.zfill(4)]
    if len(hits) != 1:
        sys.exit(f"{key!r} matches {hits or 'no record'}; "
                 "give the 4-digit id or the full dataset_id")
    return hits[0], cat[hits[0]]


def zenodo_record(doi):
    """The latest version behind openESM's concept DOI."""
    concept = doi.rsplit(".", 1)[-1]
    return get_json(f"https://zenodo.org/api/records/{concept}")


def download(rec, filename):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{rec['id']}_{filename}"
    if not path.exists():
        url = (f"https://zenodo.org/api/records/{rec['id']}/files/"
               f"{filename}/content")
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def original_licence(link):
    """Best effort: the original deposit's licence from OSF or Zenodo."""
    link = link or ""
    try:
        m = re.search(r"osf\.io/([a-z0-9]{5})", link, re.I)
        if m:
            node = get_json(f"https://api.osf.io/v2/nodes/{m.group(1)}/")
            rel = node["data"]["relationships"].get("license")
            if not rel:
                return "none recorded on OSF", f"OSF API, node {m.group(1)}"
            lic = get_json(rel["links"]["related"]["href"])
            return lic["data"]["attributes"]["name"], f"OSF API, node {m.group(1)}"
        m = re.search(r"figshare\.com/articles/(?:[^/]+/)*?(\d{6,})", link)
        if m:
            art = get_json(f"https://api.figshare.com/v2/articles/{m.group(1)}")
            return (art.get("license", {}).get("name", "none"),
                    f"Figshare API, article {m.group(1)}")
        m = (re.search(r"zenodo\.org/records?/(\d+)", link)
             or re.search(r"10\.5281/zenodo\.(\d+)", link))
        if m:
            rec = get_json(f"https://zenodo.org/api/records/{m.group(1)}")
            return (rec["metadata"].get("license", {}).get("id", "none"),
                    f"Zenodo API, record {m.group(1)}")
    except (requests.RequestException, KeyError, ValueError) as e:
        return TODO, f"lookup failed ({type(e).__name__}); read {link}"
    return TODO, f"not OSF or Zenodo; read {link}"


# --------------------------------------------------------------------------
# what IRW already holds

def irw_state():
    """dataset id (4 digits) -> where IRW already has it."""
    state = {k: f"held from the original deposit: {v}"
             for k, v in HELD_INDEPENDENTLY.items()}
    for p in sorted(DATA_DIR.glob("*.py")):
        text = p.read_text(errors="ignore")
        if "openesm" not in text.lower():
            continue
        # "openESM 0012_dejonckheere", "Listed by openESM as 0071_scharbert".
        # Anchor on "openESM": a bare id can be a cross-reference (the Study 1
        # ryvkina script mentions 0057_ryvkina, which is Study 2).
        for m in re.finditer(r"openESM(?: as)? (00\d\d)_[a-z]", text):
            state.setdefault(m.group(1), f"built: data/{p.name}")
    for p in sorted(SPEC_DIR.glob("*.json")):
        state.setdefault(p.name[:4], f"planned: {p.relative_to(SRC)}")
    return state


def already_in_irw(rec, zrec):
    """Deposit ids of this record that already appear in IRW's metadata.
    openESM ids and IRW table names do not line up, so match on deposits."""
    text = ""
    for p in [SRC / "metadata" / "biblio.csv", HERE / "dictionary_auto.csv"]:
        if p.exists():
            text += p.read_text(encoding="utf-8", errors="ignore").lower()
    keys = []
    link = (rec.get("link_to_data") or "").lower()
    keys += [rf"osf\.io/{m}\b" for m in re.findall(r"osf\.io/([a-z0-9]{5})", link)]
    keys += [rf"zenodo[./a-z]*{m}\b" for m in re.findall(r"zenodo[./a-z]*?(\d{6,})", link)]
    keys += [re.escape(m) for m in re.findall(r"10\.\d{4,}/[^\s;?#]+", link)]
    keys += [rf"zenodo\.{zrec['id']}\b", rf"zenodo\.{rec['zenodo_doi'].rsplit('.', 1)[-1]}\b"]
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", (rec.get("paper_doi") or "").lower())
    if doi:
        keys.append(re.escape(doi))
    return [k.replace("\\", "") for k in keys if re.search(k, text)]


# --------------------------------------------------------------------------
# reading openESM's metadata

def slug(s, keep=40):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s[:keep].rstrip("_")


def parse_coding(coding):
    """'Stem\\n1 = lo\\n7 = hi\\n-1 = not applicable' ->
    (stem, {value: label}, [na codes])."""
    coding = (coding or "").replace("\r", "")
    anchors = OrderedDict()
    for m in ANCHOR.finditer(coding):
        v = float(m.group(1))
        anchors[int(v) if v.is_integer() else v] = m.group(2).strip()
    first = ANCHOR.search(coding)
    stem = coding[:first.start()] if first else coding
    stem = re.sub(r"\s+", " ", stem).strip()
    na = [v for v, lab in anchors.items() if NA_LABEL.search(lab)]
    for v in na:
        anchors.pop(v)
    return stem, anchors, na


def coding_of(f):
    """The wording-and-anchors text of a feature. Older records put it all in
    `coding` ("Stem\\n1 = lo\\n7 = hi"); newer ones (0076_bayer on) leave
    `coding` out and split it into `details` (the stem) and `labels`
    ("1. Very Negative\\n2. ..."), which is rewritten here to the old form."""
    if (f.get("coding") or "").strip():
        return f["coding"]
    labels = re.sub(r"(?m)^\s*(-?\d+(?:\.\d+)?)\.\s+", r"\1 = ", f.get("labels") or "")
    return ((f.get("details") or "").strip() + "\n" + labels).strip()


def parse_coding_all(coding):
    """Every anchor, missing-value codes included."""
    return {(int(float(m.group(1))) if float(m.group(1)).is_integer()
             else float(m.group(1))): m.group(2).strip()
            for m in ANCHOR.finditer((coding or "").replace("\r", ""))}


def bibtex_to_reference(bib):
    """A first draft of the APA reference from openESM's BibTeX. Check it."""
    f = dict(re.findall(r"(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", bib or ""))
    if not f:
        return TODO
    clean = lambda s: re.sub(r"[{}]", "", s).strip()
    names = []
    for a in clean(f.get("author", "")).split(" and "):
        last, _, first = a.partition(",")
        ini = " ".join(p[0] + "." for p in re.split(r"[\s-]+", first.strip()) if p)
        names.append(f"{last.strip()}, {ini}".strip(", "))
    auth = (", ".join(names[:-1]) + ", & " + names[-1]) if len(names) > 1 else names[0]
    year = (f.get("year") or f.get("date", "")[:4])
    venue = clean(f.get("journaltitle") or f.get("journal") or "")
    vol = clean(f.get("volume", ""))
    num = clean(f.get("number", ""))
    pages = clean(f.get("pages", "")).replace("--", "-")
    tail = venue + (f", {vol}" if vol else "") + (f"({num})" if num else "") \
        + (f", {pages}" if pages else "")
    return f"{auth} ({year}). {clean(f.get('title', ''))}. {tail}."


# --------------------------------------------------------------------------
# plan

def plan(args):
    cat = catalogue()
    did, rec = find(cat, args.dataset)
    num = did[:4]
    state = irw_state().get(num, "")
    if state and not state.startswith("planned") and not args.force:
        sys.exit(f"{did} is already in IRW ({state}). --force to re-plan anyway.")
    label = rec.get("license", "")
    if label not in LICENCES:
        sys.exit(f"{did}: openESM licence {label!r} is not one this tool knows. "
                 "Read it and rule on it first (datastandard.md, 'Before you start').")

    zrec = zenodo_record(rec["zenodo_doi"])
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from reserved import text_is_reserved
    if text_is_reserved(" ".join(str(x) for x in (
            rec.get("zenodo_doi", ""), rec.get("doi", ""), rec.get("url", ""),
            f"https://zenodo.org/records/{zrec.get('id', '')}",
            zrec.get("doi", ""), zrec.get("conceptdoi", ""),
            zrec.get("conceptrecid", "") and
            f"https://zenodo.org/records/{zrec.get('conceptrecid')}"))):
        sys.exit("This dataset is on the reserved list (automated_finding/"
                 "reserved.py) and can't be planned. Ask Ben.")
    files = [f["key"] for f in zrec["files"]]
    ts_file = next((f for f in files if f.endswith("_ts.tsv")), None)
    if not ts_file:
        sys.exit(f"{did}: no *_ts.tsv in Zenodo record {zrec['id']} ({files})")
    did = ts_file[:-len("_ts.tsv")]           # openESM's own id, e.g. 0019_soederberg
    dupes = already_in_irw(rec, zrec)
    if dupes and not args.force:
        sys.exit(f"{did}: its deposit already appears in IRW's metadata "
                 f"({', '.join(dupes)}). Check before going on; --force to plan anyway.")
    df = pd.read_csv(download(zrec, ts_file), sep="\t", low_memory=False).copy()
    feats = {f["name"]: f for f in rec["features"]}
    flags = []

    def flag(what):
        flags.append({"what": what, "resolution": ""})

    missing = [c for c in feats if c not in df.columns]
    extra = [c for c in df.columns if c not in feats]
    if missing or extra:
        flag(f"metadata and data disagree: described but absent {missing}; "
             f"present but undescribed {extra}")
    if "id" not in df.columns:
        sys.exit(f"{did}: no `id` column")
    n_ids = int(df["id"].nunique())
    if n_ids < MIN_IDS:
        # A flag, not a refusal: whether the floor binds intensive longitudinal
        # data, where each person contributes many observations, is open (#3421).
        flag(f"{n_ids} people, under the {MIN_IDS}-person floor (datastandard.md, "
             "'Before you start': skipped outright). Do not ingest unless Ben "
             "has ruled ESM records exempt (#3421); cite the ruling here.")

    # ---- order, wave, date -------------------------------------------------
    times = [c for c in df.columns if feats.get(c, {}).get("variable_type") in TIME_TYPES]
    prefer = ["answer", "start", "creat", "complet", "end", "issued", "sent", "schedul"]
    times.sort(key=lambda c: next((i for i, p in enumerate(prefer)
                                   if p in (c + " " + feats[c]["description"]).lower()), 99))
    order, date = None, None
    if times:
        col = times[0]
        ts = pd.to_datetime(df[col], utc=True, errors="coerce")
        bad = int(ts.isna().sum() - df[col].isna().sum())
        if bad:
            flag(f"{bad} values of {col} do not parse as time stamps")
        order = {"by": "timestamp", "column": col}
        date = {"column": col, "tz": TODO, "tz_evidence": TODO,
                "window": [TODO, TODO]}
        span = (f"{ts.min():%Y-%m-%d %H:%M} .. {ts.max():%Y-%m-%d %H:%M} as written"
                if ts.notna().any() else "no parsable values")
        hours = ts.dt.hour.value_counts().sort_index()
        flag(f"`wave` = each person's prompts numbered in {col} order "
             f"(openESM time columns, best first: {times}). `date` = {col} "
             f"as Unix seconds. Data run {span}. Set date.window from the "
             "paper's collection period.")
        flag("Time zone of " + col + ". Written with a `Z`, but in 0072_neubauer "
             "and 0056/0057_ryvkina the `Z` stamps are local time. Hour-of-day "
             "counts as written: " + ", ".join(f"{h}h:{n}" for h, n in hours.items())
             + ". " + tz_hint(df, feats, ts) + " Set date.tz to 'UTC' if the stamps "
             "are true UTC, or to the study's IANA zone (e.g. 'Europe/Berlin') "
             "if they are local time, and say how you know in date.tz_evidence.")
        dup = int(pd.DataFrame({"id": df["id"], "t": ts}).dropna()
                  .duplicated(["id", "t"]).sum())
        if dup:
            flag(f"{dup} prompts share a time stamp with another prompt of the "
                 "same person; they will be numbered in file order. Check why.")
        if "counter" in df.columns or {"day", "beep"} <= set(df.columns):
            key = ["counter"] if "counter" in df.columns else ["day", "beep"]
            o = df[["id"] + key].assign(_t=ts).dropna(subset=["_t"])
            disagree = int((o.groupby("id")["_t"].rank(method="first")
                            != o.sort_values(key).groupby("id").cumcount()
                            .reindex(o.index) + 1).sum())
            if disagree:
                flag(f"time order and {key} order disagree for {disagree} prompts. "
                     "Usually the time stamp is right (in 0018_bailon the file "
                     "listed App rows before Web rows); confirm.")
    elif "counter" in df.columns:
        order = {"by": "counter", "column": "counter"}
        flag("no time stamps: `wave` = openESM `counter` (the scheduled prompt "
             "number), so missed prompts leave gaps; no `date`.")
    elif {"day", "beep"} <= set(df.columns):
        b = pd.to_numeric(df["beep"], errors="coerce")
        d = pd.to_numeric(df["day"], errors="coerce")
        order = {"by": "day_beep", "day_min": int(d.min()), "beep_min": int(b.min()),
                 "beeps_per_day": int(b.max() - b.min() + 1)}
        flag("no time stamps or counter: `wave` = (day - day_min) * beeps_per_day "
             "+ (beep - beep_min) + 1. Check beeps_per_day against "
             f"the sampling scheme ({rec.get('sampling_scheme')!r}); no `date`.")
    else:
        order = {"by": TODO}
        flag("no time stamp, counter or day/beep: decide what `wave` is")

    # ---- items ---------------------------------------------------------------
    issues = {"range": [], "na": Counter(), "ac": [], "noanchor": []}
    beeps = (pd.to_numeric(df["beep"], errors="coerce")
             if "beep" in df.columns and df["beep"].nunique() <= 12 else None)

    def item_entry(c):
        f = feats[c]
        stem, anchors, na = parse_coding(coding_of(f))
        if f["variable_type"] == "binary" and not anchors:
            anchors = {0: "not selected / false", 1: "selected / true"}
        x = df[c]
        if x.dtype == bool or x.dtype == object:
            x = x.map({True: 1, False: 0, "TRUE": 1, "FALSE": 0}).where(x.notna())
        x = pd.to_numeric(x, errors="coerce")
        obs = x[~x.isin(na)].dropna()
        e = {"column": c, "item": slug(c, 60), "stem": stem or f["description"],
             "anchors": {str(k): v for k, v in anchors.items()},
             "scale": [min(anchors), max(anchors)] if anchors else [TODO, TODO],
             "na_codes": na,
             "integer": bool((obs % 1 == 0).all()),
             "observed": ([float(obs.min()), float(obs.max()), int(obs.size)]
                          if obs.size else [None, None, 0]),
             "asked_at_beeps": (sorted(int(b) for b in beeps[x.notna()].dropna().unique())
                                if beeps is not None else None),
             "construct": f.get("construct", ""), "source": f.get("source", "")}
        if obs.size and anchors and (obs.min() < min(anchors) or obs.max() > max(anchors)):
            issues["range"].append(f"{c} ({min(anchors)}..{max(anchors)} vs "
                                   f"{obs.min():g}..{obs.max():g})")
        ac = str(f.get("answer_categories", "")).strip()
        if anchors and ac.isdigit() and all(isinstance(k, int) for k in anchors):
            n = max(anchors) - min(anchors) + 1 + len(na)
            if int(ac) != n:
                issues["ac"].append(f"{c} ({ac} vs {n})")
        raw = parse_coding_all(coding_of(f))
        for v in na:
            issues["na"][(v, raw.get(v, ""))] += 1
        if not anchors:
            issues["noanchor"].append(c)
        return e

    # Walk the columns in file order. A run of items breaks where the response
    # scale, the source or the prompts an item is asked at changes, or where
    # anything that is not an item intervenes; a run then splits on column-name
    # prefix where that gives blocks of three or more (study_motivation_* vs
    # activity_motivation_*, mother_* vs father_*). It is a first guess.
    runs, run, prev, candidates, not_shipped = [], [], None, [], {}
    def close():
        nonlocal run
        if run:
            runs.append(run)
        run = []
    for c in df.columns:
        f = feats.get(c)
        vt = (f or {}).get("variable_type")
        if c in STRUCTURE or (order and c == order.get("column")) \
                or (date and c == date.get("column")):
            continue
        if f is None:
            not_shipped[c] = TODO
            close(); prev = None
            continue
        if vt in ITEM_TYPES:
            e = item_entry(c)
            if not e["anchors"]:
                candidates.append(e)
                close(); prev = None
                continue
            # the scale's values, not its labels: anchor wording often
            # varies item by item within one questionnaire
            key = (e["source"].split("\n")[0].strip(),
                   (e["scale"][0], e["scale"][1]), tuple(e["na_codes"]),
                   tuple(e["asked_at_beeps"] or ()))
            if key != prev:
                close()
            run.append(e)
            prev = key
        else:
            close(); prev = None
            if vt in CANDIDATE_TYPES and (f.get("construct") or "").strip():
                candidates.append(item_entry(c))
            else:
                not_shipped[c] = f"{vt}: {f.get('description', '')}".strip()
    close()

    def split_affix(run, pos):
        """Split a run where column names share a first (pos=0) or last
        (pos=-1) token across three or more neighbours."""
        blocks = []
        for e in run:
            p = e["column"].split("_")[pos]
            if blocks and blocks[-1][0] == p:
                blocks[-1][1].append(e)
            else:
                blocks.append((p, [e]))
        out, small = [], []
        for p, b in blocks:
            if 3 <= len(b) < len(run):
                if small:
                    out.append(small); small = []
                out.append(b)
            else:
                small += b
        if small:
            out.append(small)
        return out

    def split_prefix(run):
        return [b2 for b in split_affix(run, 0) for b2 in split_affix(b, -1)]

    def topic(items):
        cols = [e["column"].split("_") for e in items]
        pre = []
        for toks in zip(*cols):
            if len(set(toks)) > 1:
                break
            pre.append(toks[0])
        suf = []
        for toks in zip(*[c[::-1] for c in cols]):
            if len(set(toks)) > 1:
                break
            suf.insert(0, toks[0])
        if len(items) > 1 and (pre or suf):
            return slug("_".join(pre or suf), 20)
        src = items[0]["source"].split("(")[0]
        if slug(src):
            return slug(src, 20)
        tags = Counter(t.strip() for e in items for t in e["construct"].split(",") if t.strip())
        return slug(tags.most_common(1)[0][0], 20) if tags else "items"

    author, year = slug(rec["first_author"]), rec["year"]
    script = f"{author}_{year}_esm"
    tables = []
    for r in runs:
        for items in split_prefix(r):
            name = f"{author}_{year}_{topic(items)}"
            while any(t["name"] == name for t in tables):
                name += "_2"
            src = items[0]["source"].split("\n")[0].strip()
            tables.append({"name": name, "instrument": src or TODO,
                           "description": TODO, "items": items})
    if issues["range"]:
        flag("Data outside the codebook scale: " + "; ".join(issues["range"])
             + ". Keep the data as shipped and widen `scale` (dejonckheere's 0 vs "
             "1), or drop the values -- and say which.")
    if issues["ac"]:
        flag("answer_categories disagrees with the anchors: " + "; ".join(issues["ac"]))
    for (v, lab), n in issues["na"].items():
        flag(f"{v} ({lab!r}) is read as missing in {n} item(s). Confirm it is "
             "not a scale point.")
    singles = [t["name"] for t in tables if len(t["items"]) == 1]
    if singles:
        flag(f"{len(singles)} proposed table(s) hold a single item ({', '.join(singles)}). "
             "Decide for each whether it belongs with a neighbouring table of the "
             "same questionnaire, stands alone, or is not shipped.")
    for t in tables:
        if len(t["name"]) > 40:
            flag(f"table name {t['name']} is over 40 characters")
    if beeps is not None and len({tuple(e["asked_at_beeps"] or ()) for t in tables
                                  for e in t["items"]}) > 1:
        flag("Items differ in the beeps they are asked at (see asked_at_beeps; "
             "e.g. an end-of-day questionnaire at the last beep). Tables are "
             "already split on it; name such tables so it shows (e.g. _eod).")
    flag("Tables are a first guess from file order, response scale, source, "
         "prompts asked at, and column-name prefixes. Read the codebook and split "
         "or merge so each table is one instrument or subscale (datastandard.md, "
         "'One file per scale'); rename each `<author>_<year>_<construct>`, and "
         "set `script` to the record's name.")
    if candidates:
        flag("`candidates` holds columns that may or may not be items (binary "
             "checkboxes, counts, rating scales whose coding gives no anchors"
             + (f" -- {', '.join(issues['noanchor'])}" if issues["noanchor"] else "")
             + "). Move any that "
             "are responses into a table; the rest go to `not_shipped` with a reason. "
             + ", ".join(e["column"] for e in candidates))
    if rec.get("cross_sectional_available") == "yes":
        flag("openESM says cross-sectional (baseline) data exist. Covariates such "
             "as age and gender are not handled by this tool: add them by hand to "
             "the generated script if wanted (neubauer_2023_stecco does), or note "
             "why not.")
    flag("Read openESM's additional_comments: "
         f"{rec.get('additional_comments') or '(none)'!r}")

    olic, how = original_licence(rec.get("link_to_data"))
    olic = norm_licence(olic) if olic != TODO else olic
    carried = LICENCES[label]
    flag(f"Licence: openESM {label!r}; original deposit {olic!r} ({how}). IRW "
         "carries openESM's label when it is stricter (ruled 2026-10-04); if the "
         "two differ, the difference goes in the notes and in the report to openESM.")
    flag("`reference` is drafted from openESM's BibTeX. Check it against the "
         "paper's DOI: the year (online vs print), page range and author list "
         "are where it goes wrong.")
    codebook = next((f for f in files if "codebook" in f.lower()), None)
    spec = OrderedDict(
        dataset_id=did,
        openesm=OrderedDict(
            first_author=rec["first_author"], year=year,
            licence=label, zenodo_concept_doi=rec["zenodo_doi"],
            zenodo_record=zrec["id"], zenodo_version_doi=zrec.get("doi", ""),
            filename=ts_file,
            codebook_url=(f"https://zenodo.org/records/{zrec['id']}/files/{codebook}"
                          if codebook else rec.get("link_to_codebook") or "none"),
            link_to_data=rec.get("link_to_data"), paper_doi=rec.get("paper_doi"),
            sampling_scheme=rec.get("sampling_scheme"),
            participants=rec.get("participants"),
            n_participants=rec.get("n_participants"),
            n_days=rec.get("n_days"), n_beeps_per_day=rec.get("n_beeps_per_day")),
        original_licence=OrderedDict(value=olic, how=how),
        licence=carried,
        reference=bibtex_to_reference(rec.get("reference_a")),
        script=script,
        input=OrderedDict(n_rows=len(df), n_ids=int(df["id"].nunique())),
        order=order, date=date,
        tables=tables, candidates=candidates, not_shipped=not_shipped,
        itemtext=OrderedDict(
            ship=False, language=TODO, translation_source=TODO,
            why=("openESM's `coding` wording is English; for a non-English study "
                 "it may be openESM's translation, not the authors'. Take wording "
                 "from the original codebook and set translation_source from "
                 "itemtext/provenance_vocab.csv, or leave ship=false and say why "
                 "in notes.")),
        notes=[],
        flags=flags)
    SPEC_DIR.mkdir(exist_ok=True)
    out = SPEC_DIR / f"{did}.json"
    if out.exists() and not args.force:
        sys.exit(f"{out} exists -- it may hold someone's decisions. --force to overwrite.")
    out.write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
    rep = SPEC_DIR / f"{did}_report.md"
    rep.write_text(report(spec, rec, df))
    print(f"wrote {out.relative_to(SRC)} and {rep.relative_to(SRC)}: "
          f"{len(tables)} table(s), {sum(len(t['items']) for t in tables)} items, "
          f"{len(candidates)} candidate(s), {len(flags)} flag(s) to resolve")


def tz_hint(df, feats, ts):
    """If the record also has a raw Unix time column, the lag between it and
    the Z stamps says whether the Z means UTC (0062_neubauer's check)."""
    for c in df.columns:
        f = feats.get(c, {})
        if "unix" in (f.get("description", "") + " " + c).lower() \
                and pd.api.types.is_numeric_dtype(df[c]):
            u = pd.to_datetime(df[c], unit="s", utc=True, errors="coerce")
            lag = (ts - u).dropna().dt.total_seconds() / 3600
            if lag.size:
                return (f"Lag of {ts.name} after the Unix column {c}: median "
                        f"{lag.median():.2f}h (IQR {lag.quantile(.25):.2f}.."
                        f"{lag.quantile(.75):.2f}h). Near 0 says UTC; a whole number "
                        "of hours says local time.")
    return "No Unix time column to check against: compare with the paper."


def report(spec, rec, df):
    t = spec["tables"]
    lines = [f"# openESM {spec['dataset_id']}: plan", "",
             f"{rec['first_author']} ({rec['year']}). {rec.get('participants', '')}. "
             f"{rec.get('sampling_scheme', '')}.",
             f"Data: {spec['openesm']['filename']}, {len(df):,} rows, "
             f"{spec['input']['n_ids']} people. Licence: {spec['licence']} "
             f"(original: {spec['original_licence']['value']}).", "",
             "## Proposed tables", ""]
    for tb in t:
        lines.append(f"**{tb['name']}** ({len(tb['items'])} items, scale "
                     f"{tb['items'][0]['scale'][0]}..{tb['items'][0]['scale'][1]}"
                     + (f", missing codes {tb['items'][0]['na_codes']}"
                        if tb['items'][0]['na_codes'] else "") + ")")
        for e in tb["items"]:
            lines.append(f"- `{e['item']}`: {e['stem'][:90]} "
                         f"(observed {e['observed'][0]}..{e['observed'][1]}, "
                         f"n={e['observed'][2]:,})")
        lines.append("")
    if spec["candidates"]:
        lines += ["## Candidates (decide)", ""]
        lines += [f"- `{e['column']}`: {e['stem'][:90]}" for e in spec["candidates"]]
        lines.append("")
    lines += ["## Not shipped", ""]
    lines += [f"- `{c}`: {why}" for c, why in spec["not_shipped"].items()]
    lines += ["", "## Flags (each needs a `resolution` in the spec)", ""]
    lines += [f"{i}. {f['what']}" for i, f in enumerate(spec["flags"], 1)]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# emit

def todos(x, path="spec"):
    if isinstance(x, dict):
        for k, v in x.items():
            if k not in ("why",):
                yield from todos(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from todos(v, f"{path}[{i}]")
    elif isinstance(x, str) and TODO in x:
        yield path


def check_spec(spec):
    skip = ("flags", "candidates") + (() if spec["itemtext"]["ship"] else ("itemtext",))
    errs = list(todos({k: v for k, v in spec.items() if k not in skip}))
    errs += [f"flag {i}: no resolution -- {f['what'][:70]}"
             for i, f in enumerate(spec["flags"], 1)
             if not (f.get("resolution") or "").strip()]
    if spec["candidates"]:
        errs.append("candidates is not empty: move each into a table or not_shipped")
    names = [t["name"] for t in spec["tables"]]
    for n in names:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_]{1,39}", n):
            errs.append(f"table name {n!r}: lowercase a-z0-9_, at most 40 characters")
    if len(set(names)) != len(names):
        errs.append("table names repeat")
    cols = [e["column"] for t in spec["tables"] for e in t["items"]]
    if len(set(cols)) != len(cols):
        errs.append("a column is in more than one table")
    for t in spec["tables"]:
        if not t["items"]:
            errs.append(f"{t['name']}: no items")
        for e in t["items"]:
            lo, hi = e["scale"]
            if not (isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and lo < hi):
                errs.append(f"{t['name']}.{e['column']}: scale {e['scale']}")
    d = spec.get("date")
    if d:
        try:
            a, b = (pd.Timestamp(w) for w in d["window"])
            if not a < b:
                errs.append("date.window: start is not before end")
        except (ValueError, TypeError):
            errs.append(f"date.window {d['window']}: not two dates")
    if spec["itemtext"]["ship"] and not spec["itemtext"]["language"]:
        errs.append("itemtext.language")
    return errs


TEMPLATE = '''#!/usr/bin/env python3
"""{title}

Generated by automated_finding/openesm_ingest.py from
automated_finding/openesm/{did}.json -- edit that spec and re-emit rather than
editing this file, unless you mean to leave the generator behind.

Source: https://zenodo.org/records/{zrec} (openESM {did})
DOI: {zdoi}
{header}

Tables written
--------------
{tables}

Coding notes
------------
{notes}

Columns not shipped
-------------------
{not_shipped}
"""

import csv
import os
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
CACHE = Path.home() / ".cache" / "irw" / "openesm"
HEADERS = {{"User-Agent": "IRW-openESM-ingest/1.0"}}

REC = {zrec!r}
FILENAME = {filename!r}
N_ROWS, N_IDS = {n_rows!r}, {n_ids!r}
ORDER = {order}
DATE = {date}
ITEMTEXT = {itemtext_spec}
TABLES = {tables_spec}


def load():
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{{REC}}_{{FILENAME}}"
    if not path.exists():
        r = requests.get(f"https://zenodo.org/api/records/{{REC}}/files/"
                         f"{{FILENAME}}/content", headers=HEADERS, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    return pd.read_csv(path, sep="\\t", low_memory=False).copy()


def numeric(x):
    """TRUE/FALSE checkboxes -> 1/0; everything else to a number."""
    if x.dtype == bool or x.dtype == object:
        x = x.map({{True: 1, False: 0, "TRUE": 1, "FALSE": 0}}).where(x.notna())
    return pd.to_numeric(x, errors="raise")


def unix_seconds(col):
    """openESM writes ISO stamps with a Z. DATE['tz'] says what they are:
    'UTC', or the zone whose local wall-clock time they actually hold.
    Integer division by one second, so the pandas 3 datetime unit change
    cannot shrink the result (#3100)."""
    t = pd.to_datetime(col, utc=True)
    if DATE and DATE["tz"] != "UTC":
        t = (t.dt.tz_localize(None)
             .dt.tz_localize(DATE["tz"], ambiguous=False,
                             nonexistent="shift_forward")
             .dt.tz_convert("UTC"))
    return t, (t - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)


def answered(df):
    cols = [e["column"] for t in TABLES for e in t["items"]]
    return df[cols].notna().any(axis=1)


def add_wave_date(df):
    by = ORDER["by"]
    if by == "timestamp":
        t, secs = unix_seconds(df[ORDER["column"]])
        lost = t.isna() & answered(df)
        assert not lost.any(), f"{{lost.sum()}} answered prompts have no time stamp"
        df = df.assign(_t=t, date=secs).loc[t.notna()]
        df = df.reset_index().sort_values(["id", "_t", "index"], kind="stable")
        df["wave"] = df.groupby("id").cumcount() + 1
        df = df.drop(columns=["_t", "index"])
    elif by == "counter":
        df = df.assign(wave=numeric(df["counter"]).astype(int))
    elif by == "day_beep":
        day, beep = numeric(df["day"]), numeric(df["beep"])
        assert beep.between(ORDER["beep_min"],
                            ORDER["beep_min"] + ORDER["beeps_per_day"] - 1).all()
        df = df.assign(wave=((day - ORDER["day_min"]) * ORDER["beeps_per_day"]
                             + beep - ORDER["beep_min"] + 1).astype(int))
    else:
        raise ValueError(by)
    assert not df.duplicated(["id", "wave"]).any(), "id x wave repeats"
    if DATE:
        lo, hi = (pd.Timestamp(w, tz="UTC").timestamp() for w in DATE["window"])
        d = df.loc[answered(df), "date"]
        assert d.between(lo, hi).all(), (
            f"date outside the collection window {{DATE['window']}}: "
            f"{{pd.to_datetime(d.min(), unit='s')}} .. {{pd.to_datetime(d.max(), unit='s')}}")
    return df


def write_items(table):
    rows = []
    for e in table["items"]:
        lo, hi = e["scale"]
        values = range(int(lo), int(hi) + 1) if e["integer"] else sorted(
            float(v) for v in e["anchors"])
        for v in values:
            rows.append([table["name"], f"{{table['name']}}_1", e["item"],
                         table["instrument"], ITEMTEXT["language"], "", "", "", "",
                         e["stem"], "", "", e["anchors"].get(str(v), ""), "", v])
    path = os.path.join(ITEMDIR, f"{{table['name']}}__items.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\\n")
        w.writerow(["table", "section_id", "item", "instrument", "language",
                    "instructions", "instructions_translated",
                    "section_prompt", "section_prompt_translated",
                    "item_text", "item_text_translated", "correct_response",
                    "option_text", "option_text_translated", "resp"])
        w.writerows(rows)
    return path, len(rows)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df = load()
    assert len(df) == N_ROWS and df["id"].nunique() == N_IDS, df.shape
    df = add_wave_date(df)
    keep = ["id", "wave"] + (["date"] if DATE else [])
    for table in TABLES:
        cols = {{e["column"]: e for e in table["items"]}}
        part = df[keep].copy()
        for c, e in cols.items():
            x = numeric(df[c])
            part[e["item"]] = x.where(~x.isin(e["na_codes"]))
        long = part.melt(id_vars=keep, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        for c, e in cols.items():
            r = long.loc[long["item"] == e["item"], "resp"]
            lo, hi = e["scale"]
            assert r.between(lo, hi).all(), (table["name"], e["item"], r.min(), r.max())
        if all(e["integer"] for e in cols.values()):
            assert (long["resp"] % 1 == 0).all()
            long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + keep[1:]]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item", "wave"]).any()
        if DATE:
            assert (long.groupby("id")["date"].diff().dropna() >= 0).all()
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, (table["name"], [(c.name, c.detail) for c in bad])
        path = os.path.join(OUTDIR, f"{{table['name']}}.csv")
        long.to_csv(path, index=False)
        print(f"{{path}}: {{long['id'].nunique()}} people x {{long['item'].nunique()}} "
              f"items = {{len(long):,}} responses, max wave {{long['wave'].max()}}")
        if ITEMTEXT["ship"]:
            ipath, k = write_items(table)
            print(f"{{ipath}}: {{k}} item text rows")


if __name__ == "__main__":
    main()
'''


def bullet(text, width=76, indent="  "):
    words, lines, cur = text.split(), [], "*"
    for w in words:
        if len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = indent + w
        else:
            cur += " " + w
    lines.append(cur)
    return "\n".join(lines)


def emit(args):
    path = Path(args.spec)
    spec = json.loads(path.read_text())
    errs = check_spec(spec)
    if errs:
        sys.exit("not ready to emit:\n  " + "\n  ".join(errs))
    o, did = spec["openesm"], spec["dataset_id"]
    out = DATA_DIR / f"{spec['script']}.py"
    if out.exists() and not args.force:
        sys.exit(f"{out.relative_to(SRC)} exists; --force to overwrite")
    olic = spec["original_licence"]["value"]
    licence_note = ("" if norm_licence(olic) == spec["licence"] else
                    f" (the openESM copy's label, carried; the original "
                    f"deposit is {olic})")
    slim = [{"name": t["name"], "instrument": t["instrument"],
             "items": [{k: e[k] for k in ("column", "item", "stem", "anchors",
                                           "scale", "na_codes", "integer")}
                       for e in t["items"]]} for t in spec["tables"]]
    it = spec["itemtext"]
    header = "\n".join(textwrap.fill(line, 79, subsequent_indent="    ") for line in [
        f"Original deposit: {o['link_to_data']} ({olic})",
        f"Paper: {spec['reference']} "
        f"doi:{re.sub(r'^https?://(dx[.])?doi[.]org/', '', o['paper_doi'] or '')}",
        f"Data: {o['filename']}",
        f"License: {spec['licence']}{licence_note}",
        "Item text: " + (f"shipped, {it['language']}, translation_source="
                         f"{it['translation_source']}" if it["ship"] else
                         "not shipped (see coding notes)"),
        "",
        f"{spec['input']['n_ids']} people ({o['participants']}); "
        f"{o['sampling_scheme']}."])
    src = TEMPLATE.format(header=header,
        title=f"{o['first_author']} ({o['year']}), via the openESM harmonised copy.",
        did=did, zrec=o["zenodo_record"], zdoi=o["zenodo_version_doi"],
        filename=o["filename"],
        tables="\n".join(f"{t['name']:<40} {len(t['items'])} items, "
                         f"{t['items'][0]['scale'][0]}..{t['items'][0]['scale'][1]}"
                         for t in spec["tables"]),
        notes="\n".join(bullet(n) for n in
                        spec["notes"] + [f["resolution"] for f in spec["flags"]]),
        not_shipped="\n".join(f"{c:<22} {why}" for c, why in spec["not_shipped"].items())
        or "(none)",
        n_rows=spec["input"]["n_rows"], n_ids=spec["input"]["n_ids"],
        order=pprint.pformat(spec["order"], width=70),
        date=pprint.pformat(spec["date"], width=70),
        itemtext_spec=pprint.pformat({"ship": it["ship"], "language": it["language"]}),
        tables_spec=pprint.pformat(slim, width=78, sort_dicts=False),
    )
    out.write_text(src)
    dict_rows = []
    for t in spec["tables"]:
        notes = (f"Processed from the openESM harmonised copy ({did}, "
                 f"{o['zenodo_version_doi']})"
                 + (f", which openESM licenses {spec['licence']}; the original "
                    f"deposit ({o['link_to_data']}) is {olic}. The terms of the "
                    "copy used are carried."
                    if licence_note else
                    f"; original deposit {o['link_to_data']}, also {olic}.")
                 + f" See data/{spec['script']}.py.")
        dict_rows.append(OrderedDict(
            table=t["name"], description=t["description"],
            url=f"https://zenodo.org/records/{o['zenodo_record']}",
            reference=spec["reference"],
            doi=re.sub(r"^https?://(dx\.)?doi\.org/", "", o["paper_doi"] or ""),
            doi_data=o["zenodo_version_doi"], original_license=spec["licence"],
            public_reshare="Public", derived_license=spec["licence"],
            notes=notes, codebook_url=o["codebook_url"]))
    jl = SPEC_DIR / f"{did}_dict.jsonl"
    jl.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in dict_rows))
    print(f"wrote {out.relative_to(SRC)} and {jl.relative_to(SRC)}\nnext:\n"
          f"  python {out.relative_to(SRC)}\n"
          f"  # then, once the output is reviewed, per line of the .jsonl:\n"
          f"  sed -n 1p {jl.relative_to(SRC)} | python automated_finding/"
          f"stage_dict_row.py --source-via openESM")


# --------------------------------------------------------------------------
# status

def status(args):
    cat, state = catalogue(), irw_state()
    rows = [(did, r["year"], r.get("license", ""), state.get(did[:4], "open"))
            for did, r in cat.items()]
    for did, year, lic, st in rows:
        print(f"{did:<22} {year}  {lic:<20} {st}")
    c = Counter(s.split(":")[0] for *_, s in rows)
    print(f"\n{len(rows)} records: " + ", ".join(f"{n} {k}" for k, n in c.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="every openESM record and whether IRW has it")
    p = sub.add_parser("plan", help="write a spec and report for one record")
    p.add_argument("dataset")
    p.add_argument("--force", action="store_true")
    e = sub.add_parser("emit", help="spec -> data/<script>.py + dictionary rows")
    e.add_argument("spec")
    e.add_argument("--force", action="store_true")
    args = ap.parse_args()
    {"status": status, "plan": plan, "emit": emit}[args.cmd](args)


if __name__ == "__main__":
    main()
