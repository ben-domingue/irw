#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/cb4y7z9g2s
# DOI: 10.17632/cb4y7z9g2s (Mendeley Data, 2026; Habiba, Most.; Mondol, Md. Nafij; Yeasmin Lina,
#   Farhana; Tripura, Khokaneswar). "Tourists' Attitudes toward Artificial Intelligence Powered
#   Recommendation Systems in Tourism Planning"; no linked article.
# Data: "... Dataset(original).xlsx" sheet "Form responses 1", a Google Forms export of 367 Bangladeshi
#       tourists. Eight 4-item blocks on 1 strongly disagree .. 5 strongly agree: PU perceived
#       usefulness, PC privacy concern, SI social influence, TAA tourist awareness & attitude, TA trust
#       in AI, TCF tourist & contextual factors, PV perceived value, BIUA behavioural intention. Each
#       item's column header is "<Construct> [<CODE>: <stem>]"; the code is taken from that header.
#       "Hypothesis and Survey Instruments.docx" is the questionnaire (same codes and stems).
#       The "(Responses) - Copy" workbook is the same data with demographics as text.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: shipped (column headers carry code and stem; anchors from the header's scale line
#   "1 = Strongly Disagree | ... | 5 = Strongly Agree"). Built by
#   automated_finding/itemtext_verification/make_itemtext_habiba_2026.py from stems(). English
#   instrument deposited; administered language not stated (left blank).
#
# Table: habiba_2026_ai_tourism (32 items, 1-5), one table for the eight TAM/UTAUT blocks.
# Covariates: cov_gender (1 male, 2 female, 3 prefer not to say), cov_age_group (1 <18 .. 5 33+),
#   cov_education (1 secondary or below .. 5 PhD), cov_residence (1 urban, 2 semi-urban, 3 rural),
#   cov_travel_freq (1 one .. 5 more than 10 per year), cov_tech_access (1 smartphone only, 2 laptop
#   only, 3 both, 4 limited), cov_prior_ai_use (1 once, 2 rarely, 3 occasionally, 4 regularly).
# id: row index of the export (no respondent identifier; the Timestamp column is not shipped).
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def zenodo_fetch(record: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://zenodo.org/api/records/{record}", headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == fname][0]
        download(url, p)
    return p


def figshare_fetch(article: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.figshare.com/v2/articles/{article}", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == fname][0]
        download(url, p)
    return p


def mendeley_fetch(dataset: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://data.mendeley.com/public-api/datasets/{dataset}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"] if f["filename"] == fname][0]
        download(url, p)
    return p


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values or None). QC, validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=(),
         rename: dict | None = None) -> pd.DataFrame:
    """Melt `items` to long, drop missing, check integer codes inside `valid`, order columns.
    `rename` maps a source column to the `item` code it ships under (default: the column name)."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", *extra, "item"]).reset_index(drop=True)


def pv_for(items, valid) -> dict:
    return {i: set(valid) for i in items}


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p
import re

RAW_DIR = RAW_ROOT / "mdl_cb4y7z9g2s"
FNAME = "Tourists' Attitudes toward AI-Powered Recommendation Systems in Tourism Planning Dataset(original).xlsx"
HDR = re.compile(r"^(?P<construct>.+?)\s*\[(?P<code>[A-Z]+\d+):\s*(?P<stem>.+)\]\s*$", re.S)
ANCH = {1: "Strongly Disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly Agree"}


def load():
    d = pd.read_excel(mendeley_fetch("cb4y7z9g2s", FNAME, RAW_DIR), sheet_name="Form responses 1")
    d = d.drop(columns=[c for c in d.columns if str(c).startswith("Column")])
    assert len(d) == 367
    return d


def parse(d):
    """{code: (construct, stem, column)} from the item headers."""
    out = {}
    for c in d.columns:
        m = HDR.match(str(c))
        if m:
            construct = re.sub(r"\s*\n.*", "", m["construct"], flags=re.S).strip()
            out[m["code"]] = (construct, " ".join(m["stem"].split()), c)
    assert len(out) == 32, len(out)
    return out


def stems():
    d = load()
    for code, (construct, stem, _) in parse(d).items():
        yield code, construct, stem, ANCH


def main() -> None:
    d = load()
    items = parse(d)
    d = d.rename(columns={col: code for code, (_, _, col) in items.items()})
    d["id"] = range(1, len(d) + 1)
    demo = [c for c in d.columns if str(c).startswith("1=") or str(c).startswith("1 =")]
    assert len(demo) == 7, demo
    names = ["cov_gender", "cov_age_group", "cov_education", "cov_residence", "cov_travel_freq",
             "cov_tech_access", "cov_prior_ai_use"]
    for c, n in zip(demo, names):
        d[n] = d[c].astype("Int64")
    codes = list(items)
    emit({"habiba_2026_ai_tourism": (long(d, codes, names, valid=range(1, 6)), pv_for(codes, range(1, 6)))})


if __name__ == "__main__":
    main()
