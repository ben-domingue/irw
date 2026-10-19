#!/usr/bin/env python3

# Source: https://zenodo.org/records/6875363
# DOI: 10.5281/zenodo.6875363 (dataset)
#   White, Trenton M. (2022). COVID-19 Vaccine Hesitancy in the Pandemic's Third Year
#   [Dataset]. Zenodo.
#   Paper: Lazarus, J. V., Wyka, K., White, T. M., Picchio, C. A., Gostin, L. O.,
#   Larson, H. J., Rabin, K., Ratzan, S. C., Kamarulzaman, A., & El-Mohandes, A. (2023).
#   A survey of COVID-19 vaccine acceptance across 23 countries in 2022. Nature Medicine,
#   29, 366-375. 10.1038/s41591-022-02185-4
# Data: "COVID-19_VacHesdata_2022.csv.csv": 23,000 respondents, 1,000 per country in each
#       of 23 countries, surveyed 28 June - 8 July 2022 by stratified online panel.
#       Questions q0001-q0025, of which twelve form two fully answered 5-point blocks.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped, and this is a checked absence rather than an unchecked one. The
#   deposit's second file, COVID19_VacHescode_2022.SAS, is analysis code: it carries no
#   variable labels and no question wording. The 2022 questionnaire is in the Nature
#   Medicine supplementary information, which is behind the journal's paywall (the paper
#   has no PMC record and is not open access). The 2021 wave of the same survey series IS
#   open (Nat Commun, PMC9247969, CC BY) and publishes its full questionnaire, in which
#   questions 1-6 are the six-item COVID-VAC agreement block (COVID-19 is a dangerous
#   health threat / can be prevented by vaccination / risks of disease exceed risks of the
#   vaccine / the vaccines available to me are safe / I trust my government to deliver /
#   I trust the science) -- but that instrument has 31 questions where the 2022 file has
#   25, so the numbering demonstrably changed between waves and the 2021 stems must not be
#   assumed onto these columns.
#
# Two tables, items keyed by the deposit's own question numbers, no construct asserted:
#   white_2022_covid_vac_items_1_6    q0001-q0006, 1-5, answered by all 23,000.
#   white_2022_covid_vac_items_15_20  q0015-q0020, 1-5, answered by all 23,000. The
#     authors' own SAS file tabulates exactly these six together (the Figure 5 block),
#     which is the evidence that they are one block rather than six unrelated questions.
# Not shipped as items: q0007-q0014 and q0021-q0025. Each is a single branching or
#   factual question of its own (vaccination status, children, mandates, attention), with
#   widths of 3, 4 or 7 and -- for q0008, q0009, q0011, q0022, q0023 -- blanks where the
#   skip pattern applied. They are survey questions, not a scale, and nothing in the
#   deposit says which belong together.
# Covariates: cov_country, cov_age, cov_age_group, cov_gender, cov_education, cov_income,
#   cov_survey_weight (the deposit's Weights, the stratification weight), cov_date
#   (collection date, as deposited). The 23 country-specific education and region columns
#   are not shipped: each is populated only for its own country, so they are 46 mostly
#   blank columns whose codes are not comparable across countries, and the harmonised
#   Education column is shipped instead.
# id: row index of the csv; the deposit carries no respondent identifier.
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_6875363"
FNAME = "COVID-19_VacHesdata_2022.csv.csv"
BLOCK_A = [f"q{i:04d}" for i in range(1, 7)]
BLOCK_B = [f"q{i:04d}" for i in range(15, 21)]
COVS = {"Country": "cov_country", "Age": "cov_age", "Age_group": "cov_age_group",
        "Gender": "cov_gender", "Education": "cov_education", "Income": "cov_income",
        "Weights": "cov_survey_weight", "Collection_Date": "cov_date"}


def main() -> None:
    d = pd.read_csv(zenodo_fetch(6875363, FNAME, RAW_DIR), low_memory=False)
    assert len(d) == 23000, len(d)
    src = list(d.columns)
    other_q = [f"q{i:04d}" for i in list(range(7, 15)) + list(range(21, 26))]
    country_cols = [c for c in src if c.endswith(
        ("_edu", "_education", "_region", "_regions"))]
    assert len(country_cols) == 46, len(country_cols)
    books(src, {
        "shipped": BLOCK_A + BLOCK_B,
        "covariate": list(COVS),
        "single branching or factual survey question, not part of a scale": other_q,
        "country-specific education/region code, superseded by the harmonised Education":
            country_cols,
    })
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    d["cov_date"] = d["cov_date"].astype(str).str.strip()
    d["id"] = range(1, len(d) + 1)
    v = range(1, 6)
    emit({
        "white_2022_covid_vac_items_1_6":
            (long(d, BLOCK_A, covs, valid=v), pv_for(BLOCK_A, v)),
        "white_2022_covid_vac_items_15_20":
            (long(d, BLOCK_B, covs, valid=v), pv_for(BLOCK_B, v)),
    })


if __name__ == "__main__":
    main()
