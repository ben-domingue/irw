#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/5FZO3F
# DOI: 10.7910/DVN/5FZO3F (dataset; the article "Effectiveness of therapeutic massage for
#   the reduction of pre-exam anxiety in nursing students" was not found in Crossref)
#   Sanz Martos, Sebastian (2024). Replication data for "Effectiveness of therapeutic
#   massage for the reduction of pre-exam anxiety in nursing students". Harvard Dataverse.
# Data: "Dataset relaxing tecniche.xlsx" (format=original), sheet
#       "Base de datos masaje_JASP": 129 nursing students x 94 columns -- Participant
#       number, the 40 STAI items before the massage ("Item 1".."Item 40", 0-3), the
#       State/Trait/Total/VAS pre scores, the same 40 items after ("Item 1.1".."Item
#       40.1"), the post scores, Gender, Age and relaxation-practice questions.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Headers are "Item <n>" only; STAI is a `block` row in
#   itemtext/instrument_rights_register.csv.
#
# Tables (0-3 as stored, the STAI's 1-4 shifted down; reverse-keyed items are stored
#   already reversed: the pre State and Trait totals equal the plain item sums, asserted,
#   and every state item correlates positively with the rest):
#   sanz_martos_2024_stai_state   Item 1-Item 20, before the massage
#   sanz_martos_2024_stai_trait   Item 21-Item 40, before the massage
# NOT shipped: the post-massage item columns. They are near-copies of the pre columns
#   (trait items identical in 99.5% of cells, state items in 96.5%), while the deposit's
#   own post totals disagree with them (Trait_Post equals their sum for 2 of 129
#   students), so they are not the post-test responses. The pre/post contrast is only in
#   the totals.
# Skipped: State/Trait/Total/VAS pre and post scores; Type and frequency (free text about
#   relaxation practice).
# Covariates: cov_gender (Female / Male), cov_age, cov_relax_practice (Yes / No: practises
#   any relaxation technique).
# id: Participant number (unique, 1-129).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


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


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_5fzo3f"
FNAME = "Dataset relaxing tecniche.xlsx"
P = "sanz_martos_2024_"
COVS = {"Gender": "cov_gender", "Age": "cov_age",
        "Practice any relaxing tecniche": "cov_relax_practice"}


def main() -> None:
    d = pd.read_excel(dv_fetch("10.7910/DVN/5FZO3F", FNAME, RAW_DIR))
    assert d.shape == (129, 94) and d["Participant number"].is_unique
    pre = [f"Item {i}" for i in range(1, 41)]
    post = [f"Item {i}.1" for i in range(1, 41)]
    scores = ["State_Pre", "Trait_Pre", "Total_Pre", "VAS_Pre", "State_Post", "Trait_Post",
              "Total_Post", "VAS_Post"]
    assert set(pre) | set(post) | set(scores) | set(COVS) | {"Participant number", "Type",
                                                              "frequency"} == set(d.columns)
    assert (d[pre[:20]].sum(axis=1) == d["State_Pre"]).all()
    assert (d[pre[20:]].sum(axis=1) == d["Trait_Pre"]).all()
    same = (d[post].to_numpy() == d[pre].to_numpy()).mean()
    agree = (d[post[20:]].sum(axis=1) == d["Trait_Post"]).mean()
    assert same > 0.95 and agree < 0.05, (same, agree)
    print(f"  [skip] post-test item columns: {same:.1%} of cells equal the pre columns; "
          f"Trait_Post matches their sum for {agree:.1%} of students")
    d["id"] = d["Participant number"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {}
    for suf, its in (("stai_state", pre[:20]), ("stai_trait", pre[20:])):
        t = long(d, its, covs, valid=range(0, 4))
        w = d[its]
        for i in its:
            assert w[i].corr(w.drop(columns=i).sum(axis=1)) > 0, i
        out[P + suf] = (t, {i: set(range(4)) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
