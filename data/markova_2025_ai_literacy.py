#!/usr/bin/env python3

# Source: https://zenodo.org/records/16745477
# DOI: 10.5281/zenodo.16745477 (dataset; the record names no published paper)
#   Markova, Ekaterina; Yordanova, Gabriela (2025). AI Literacy and Attitudes in Bulgaria
#   2025: Validation of the General Attitudes toward Artificial Intelligence Scale (GAAIS)
#   and the Meta AI Literacy Scale (MAILS) [Dataset]. Zenodo.
# Data: "ai_literacy_bg2025.csv" (semicolon-separated, comma decimal mark): 1,006
#       respondents to an omnibus CAPI survey of the Bulgarian general population.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for both tables (English, from the deposit's own variable_codebook.xls
#   "Variable Lables" sheet, which gives the stem for every item, and its "Value Lables"
#   sheet for the anchors). The survey was administered in Bulgarian; the codebook
#   publishes only the English source wording of the two instruments, so that is what
#   ships, recorded as study_materials.
#
# Two tables, because the two instruments use different response widths:
#   markova_2025_gaais  20 items, 1-5 -- General Attitudes toward AI Scale. Positively
#                       (P*) and negatively (N*) worded items, raw direction.
#   markova_2025_mails  34 items, 0-10 -- Meta AI Literacy Scale.
# Not shipped:
#   every *_rec item column -- the depositor's reverse-scored copy of an N* item already
#     shipped in its raw direction (D4_rec is not one of these: it is the recoded
#     education covariate, and ships as cov_education);
#   Atn_1b_99 -- an instructed-response attention check ("select Strongly agree"), not an
#     item of either instrument;
#   the GAAIS_*/MAILS_* subscale means and EMP_Binary/employment_code/I3_other_code;
#   the I3_* multi-select "what do you use AI for" indicators and the D7_* employment
#     multi-select indicators, which are select-all checkbox flags coded as
#     0-or-the-option-number rather than responses on a scale.
# Item code: the deposit names MAILS item 24 with the bare column header "MAILS", which is
#   unusable as an item code next to MAILSI2f_23 and MAILSI2f_25. It is renamed
#   MAILSI2f_24, the name its neighbours imply, and the item text table spells it the same
#   way. Every other item keeps the deposit's own header, including the deposit's
#   inconsistent MAILS/MAILSI/IMAILS prefixes.
# Covariates: cov_age (D1), cov_age_group (D2), cov_sex (D3), cov_education (D4_rec),
#   cov_settlement (D5), cov_region (D6), cov_sector (D8), cov_income (D9),
#   cov_ethnic_group (D10), cov_family_status (D11), cov_employment_status.
#   Free-text "other" columns (D7_other_BG/_cat, D10_other_BG/_ENG, I3_other_BG/_cat) are
#   dropped: they are open-ended answers, not coded covariates.
# id: row index of the csv. The deposit's own "id" is not unique (1,003 distinct over
#   1,006 rows).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_16745477"
GAAIS = ["P1a_1", "P1a_2", "N1a_3", "P1a_4", "P1a_5", "N1a_6", "P1a_7",
         "N1b_8", "N1b_9", "N1b_10", "P1b_11", "P1b_12", "P1b_13",
         "P1c_14", "N1c_15", "P1c_16", "P1c_17", "P1c_18", "N1c_19", "N1c_20"]
MAILS_RENAME = {"MAILS": "MAILSI2f_24"}
COVS = {"D1": "cov_age", "D2": "cov_age_group", "D3": "cov_sex",
        "D4_rec": "cov_education", "D5": "cov_settlement", "D6": "cov_region",
        "D8": "cov_sector", "D9": "cov_income", "D10": "cov_ethnic_group",
        "D11": "cov_family_status", "employment_status": "cov_employment_status"}


def main() -> None:
    d = pd.read_csv(zenodo_fetch(16745477, "ai_literacy_bg2025.csv", RAW_DIR),
                    sep=";", decimal=",", encoding="utf-8-sig", dtype=str)
    assert len(d) == 1006, len(d)
    src = list(d.columns)
    mails_src = [c for c in src
                 if c.startswith(("MAILS", "IMAILS")) and "_" in c
                 and c.rsplit("_", 1)[1].isdigit()] + ["MAILS"]
    mails = [MAILS_RENAME.get(c, c) for c in mails_src]
    assert len(mails) == 34 and len(set(mails)) == 34, mails
    books(src, {
        "shipped": GAAIS + mails_src,
        "covariate": list(COVS),
        "non-unique deposit id, superseded by the row index": ["id"],
        "depositor's reverse-scored copy of an item already shipped raw":
            [c for c in src if c.endswith("_rec") and c not in COVS],
        "instructed-response attention check": ["Atn_1b_99"],
        "subscale mean or derived code":
            [c for c in src if c.startswith(("GAAIS_", "MAILS_"))]
            + ["EMP_Binary", "employment_code", "I3_other_code"],
        "select-all checkbox indicator":
            [c for c in src if c.startswith("I3_") and c.rsplit("_", 1)[1].isdigit()]
            + [c for c in src if c.startswith("D7_") and c.rsplit("_", 1)[1].isdigit()],
        "open-ended free text":
            ["D7_other_BG", "D7_other_cat", "D10_other_BG", "D10_other_ENG",
             "I3_other_BG", "I3_other_cat"],
    })
    for c in GAAIS + mails_src + list(COVS):
        d[c] = pd.to_numeric(d[c].str.strip().replace({"": None, '""': None}),
                             errors="coerce")
    # D9 98/99 and D10 666666 are refusal codes, not categories.
    d.loc[d["D9"].isin([98, 99]), "D9"] = None
    d.loc[d["D10"] == 666666, "D10"] = None
    d = d.rename(columns={**COVS, **MAILS_RENAME})
    covs = list(COVS.values())
    d["id"] = range(1, len(d) + 1)
    emit({
        "markova_2025_gaais": (long(d, GAAIS, covs, valid=range(1, 6)),
                               pv_for(GAAIS, range(1, 6))),
        "markova_2025_mails": (long(d, mails, covs, valid=range(0, 11)),
                               pv_for(mails, range(0, 11))),
    })


if __name__ == "__main__":
    main()
