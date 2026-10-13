#!/usr/bin/env python3
# Source: https://doi.org/10.1371/journal.pone.0230623.s005 (PLOS ONE Supporting Information S5)
# DOI: 10.1371/journal.pone.0230623
#   Jarbin H, Ivarsson T, Andersson M, Bergman H, Skarphedinsson G (2020). Screening
#   efficiency of the Mood and Feelings Questionnaire (MFQ) and Short Mood and Feelings
#   Questionnaire (SMFQ) in Swedish help seeking outpatients. PLOS ONE 15(3): e0230623.
# Data: pone.0230623.s005.sav: 267 child and adolescent psychiatric outpatients (6-17 y)
#       in Sweden; the 34-item MFQ (0 not true, 1 sometimes true, 2 true) as a parent report
#       (MFQ_k_M mother, n=211; MFQ_k_P father, n=95) and as the child's self-report
#       (MFQ_k_B child 6-12, n=78; MFQ_k_T teenager 13-17, n=127), plus LEAD diagnoses.
# License: CC BY 4.0 (PLOS ONE article and its Supporting Information).
#
# Item text: not shipped. Variable labels are positional ("MFQ_12_Mamma"); value labels
#   give the three anchors only. The MFQ wording is Angold's (Duke), not in the deposit.
#
# Tables (item = MFQ_1 .. MFQ_34, the deposit's item number):
#   jarbin_2020_mfq_self    the child's own report (child and teenager forms stacked;
#                           cov_age_group = child / teenager), 204 ids; one 10-year-old
#                           has both forms with different answers and keeps the child form
#   jarbin_2020_mfq_parent  parent report with `rater` = mother / father, 232 children
#                           (74 rated by both parents)
# resp 0-2. Covariates: cov_gender (0 boy, 1 girl), cov_age (years at MFQ, one decimal),
#   cov_dx_depression, cov_dx_anxiety, cov_dx_adhd, cov_dx_autism (LEAD diagnosis 0/1).
# id: row index of the .sav (the file has no participant id).

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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "10_1371_journal_pone_0230623"
URL = "https://doi.org/10.1371/journal.pone.0230623.s005"
COVS = ["cov_gender", "cov_age", "cov_dx_depression", "cov_dx_anxiety", "cov_dx_adhd", "cov_dx_autism"]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(download(URL, RAW_DIR / "pone.0230623.s005.sav")))
    assert len(d) == 267
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"gender": "cov_gender", "LDepressiontotal": "cov_dx_depression",
                          "LAnxietytotal_exkl_specfobi": "cov_dx_anxiety", "LADHDtotal": "cov_dx_adhd",
                          "LAutismspektrumtotal": "cov_dx_autism"})
    d["cov_age"] = d["AgeMFQ"].round(1)
    for c in COVS:
        if c != "cov_age":
            d[c] = d[c].astype("Int64")
    items = [f"MFQ_{k}" for k in range(1, 35)]
    parts = []
    b_cols = [f"MFQ_{k}_B" for k in range(1, 35)]
    t_cols = [f"MFQ_{k}_T" for k in range(1, 35)]
    both = d[b_cols].notna().any(axis=1) & d[t_cols].notna().any(axis=1)
    print(f"  {both.sum()} child(ren) with both self-report forms; the teenager form is dropped for them "
          f"(age {d.loc[both, 'AgeMFQ'].round(1).tolist()})")
    d.loc[both, t_cols] = pd.NA
    for suf, who in (("B", "child"), ("T", "teenager")):
        cols = {f"MFQ_{k}_{suf}": f"MFQ_{k}" for k in range(1, 35)}
        w = d[d[list(cols)].notna().any(axis=1)].copy()
        w["cov_age_group"] = who
        parts.append(long(w, list(cols), COVS + ["cov_age_group"], valid=range(0, 3), rename=cols))
    self_t = pd.concat(parts, ignore_index=True)
    assert not self_t.duplicated(["id", "item"]).any()  # no child is in both forms
    parts = []
    for suf, who in (("M", "mother"), ("P", "father")):
        cols = {f"MFQ_{k}_{suf}": f"MFQ_{k}" for k in range(1, 35)}
        w = d[d[list(cols)].notna().any(axis=1)].copy()
        w["rater"] = who
        parts.append(long(w, list(cols), COVS, valid=range(0, 3), extra=("rater",), rename=cols))
    parent_t = pd.concat(parts, ignore_index=True)[["id", "item", "resp", "rater"] + COVS]
    emit({"jarbin_2020_mfq_self": (self_t, pv_for(items, range(0, 3))),
          "jarbin_2020_mfq_parent": (parent_t, pv_for(items, range(0, 3)))})


if __name__ == "__main__":
    main()
