#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/I7FSYP
# DOI: 10.1017/ipo.2021.17
#   Vegetti F, Littvay L (2021). Belief in conspiracy theories and attitudes toward
#   political violence. Italian Political Science Review 1-15. Data: Harvard Dataverse
#   doi:10.7910/DVN/I7FSYP.
# Data: FV_LL_consp_IPSR.csv: 694 US respondents (a pilot flagged by `pilot`); -999 is
#       the missing code throughout. Item blocks (codes only, no labels or codebook):
#       cons1-15 conspiracy beliefs (1-5), endvio1-4 endorsement of political violence (1-5),
#       radact1-6 radical action intentions (1-7), agg1-29 aggression (1-7; the 29-item
#       Buss-Perry length), rwa1-19 right-wing authoritarianism (1-7), sdo1-16 social
#       dominance orientation (1-7), intself1-8 (1-7, the deposit's code), trust1-10 (0-10).
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The csv has codes only; the wording would have to come from
#   the article's appendix (positional) and several blocks are licensed instruments.
#
# Tables (item = the deposit's column name): vegetti_2021_conspiracy (15),
#   vegetti_2021_violence (4), vegetti_2021_radical_action (6), vegetti_2021_aggression (29),
#   vegetti_2021_rwa (19), vegetti_2021_sdo (16), vegetti_2021_intself (8), vegetti_2021_trust (10).
# Covariates: cov_pilot (0/1), cov_gender (1/2 as coded), cov_birth_year, cov_ideology
#   (ideo 1-7), cov_income (1-8), cov_degree (1-8).
# id: row index of the csv.

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

RAW_DIR = RAW_ROOT / "10_7910_dvn_i7fsyp"
BLOCKS = {"vegetti_2021_conspiracy": ("cons", 15, range(1, 6)), "vegetti_2021_violence": ("endvio", 4, range(1, 6)),
          "vegetti_2021_radical_action": ("radact", 6, range(1, 8)), "vegetti_2021_aggression": ("agg", 29, range(1, 8)),
          "vegetti_2021_rwa": ("rwa", 19, range(1, 8)), "vegetti_2021_sdo": ("sdo", 16, range(1, 8)),
          "vegetti_2021_intself": ("intself", 8, range(1, 8)), "vegetti_2021_trust": ("trust", 10, range(0, 11))}
COVS = {"pilot": "cov_pilot", "gender": "cov_gender", "year": "cov_birth_year", "ideo": "cov_ideology",
        "income": "cov_income", "degree": "cov_degree"}


def main() -> None:
    d = pd.read_csv(dv_fetch("10.7910/DVN/I7FSYP", "FV_LL_consp_IPSR.csv", RAW_DIR))
    assert len(d) == 694
    d = d.mask(d == -999)
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}
    for name, (pre, n, valid) in BLOCKS.items():
        items = [f"{pre}{k}" for k in range(1, n + 1)]
        assert set(items) <= set(d.columns), name
        out[name] = (long(d, items, covs, valid=valid), pv_for(items, valid))
    emit(out)


if __name__ == "__main__":
    main()
