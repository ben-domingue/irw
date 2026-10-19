#!/usr/bin/env python3

# Source: https://zenodo.org/records/7394999
# DOI: 10.5281/zenodo.7394999 (dataset)
#   Karas, Dariusz (2022). Identification of the development of consumer ethnocentrism
#   during a pandemic [Dataset]. Zenodo.
# Data: two SPSS files, each the 17-item CETSCALE on a 1-7 agreement scale after
#       respondents read one of three press articles about consumer patriotism:
#         "Etnocentryzm_Baza_PL.sav"    1,083 Polish respondents, Polish wording.
#         "Ethnocentrism_Data_ENG.sav"    724 UK respondents, British wording.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for both tables (as administered -- Polish for the PL table, English
#   for the EN table -- from the SPSS variable labels, with the 1-7 anchors from the value
#   labels, which are present for all 17 items in both files). Checked both label levels.
#
# Two tables, not one. The instrument is the same CETSCALE in both samples, but the two
# administrations are not identical: the items are adapted to each country ("British people
# should always buy British-made products" vs the Polish wording naming Poland), and the
# deposit's own numbering puts different items at the same position -- PL P2.1 is "buying
# foreign-made products is wrong" where EN P2.1 is "British people should always buy
# British-made products". So the item codes do not mean the same thing across the files and
# collapsing them would join unrelated items.
#   karas_2022_cetscale_pl  1,083 x 17
#   karas_2022_cetscale_en    724 x 17
# cov_age: two respondents typed an impossible age into the free-text age box (-16 in
#   both files, 123 in the PL file); those two cells are blanked, nothing else is touched.
# treat: the press-article condition (the deposit's Prodzaj / Ptype, 1-3), kept as `treat`
#   because it is a randomised manipulation, with P1 (the manipulation-check question about
#   what the article was about) shipped as cov_article_recall rather than as an item.
# Covariates: cov_financial_change (P3), cov_gender (P4), cov_age (P5), cov_education (P6),
#   cov_nationality (P7), cov_article_recall (P1).
# id: row index within each file.
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

def books(all_cols, used: dict) -> None:
    """Every source column is either shipped or skipped for a printed reason."""
    seen = {}
    for reason, cols in used.items():
        for c in cols:
            assert c not in seen, (c, reason, seen[c])
            seen[c] = reason
    missing = [c for c in all_cols if c not in seen]
    assert not missing, f"unaccounted source columns: {missing}"
    extra = [c for c in seen if c not in all_cols]
    assert not extra, f"named columns not in the source: {extra}"
    for reason, cols in used.items():
        if reason != "shipped" and cols:
            print(f"    [skipped: {reason}] {len(cols)}: {', '.join(map(str, cols))[:300]}")


RAW_DIR = RAW_ROOT / "10_5281_zenodo_7394999"
ITEMS = [f"P2.{i}" for i in range(1, 18)]
COVS = {"P1": "cov_article_recall", "P3": "cov_financial_change",
        "P4": "cov_gender", "P5": "cov_age", "P6": "cov_education",
        "P7": "cov_nationality"}


def load(fname: str, treat_col: str, n: int) -> pd.DataFrame:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(7394999, fname, RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == n, (fname, len(d))
    books(list(d.columns), {"shipped": ITEMS, "covariate": list(COVS),
                            "randomised press-article condition": [treat_col]})
    d = d.rename(columns={treat_col: "treat", **COVS})
    d["treat"] = pd.to_numeric(d["treat"]).astype(int)
    d["cov_age"] = pd.to_numeric(d["cov_age"], errors="coerce")
    # P5 is a free-text age box; two respondents typed an impossible age (-16 in both
    # files, 123 in the PL file). Blanked rather than shipped or guessed at.
    bad = ~d["cov_age"].between(10, 100)
    print(f"    [cov_age] blanked {int((bad & d['cov_age'].notna()).sum())} "
          f"impossible age(s): {sorted(d.loc[bad, 'cov_age'].dropna().unique())}")
    d.loc[bad, "cov_age"] = None
    d["id"] = range(1, len(d) + 1)
    return d


def main() -> None:
    covs = list(COVS.values())
    v = range(1, 8)
    pl = load("Etnocentryzm_Baza_PL.sav", "Prodzaj", 1083)
    en = load("Ethnocentrism_Data_ENG.sav", "Ptype", 724)
    emit({
        "karas_2022_cetscale_pl": (long(pl, ITEMS, covs, valid=v, extra=("treat",)),
                                   pv_for(ITEMS, v)),
        "karas_2022_cetscale_en": (long(en, ITEMS, covs, valid=v, extra=("treat",)),
                                   pv_for(ITEMS, v)),
    })


if __name__ == "__main__":
    main()
