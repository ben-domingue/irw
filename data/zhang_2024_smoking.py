#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11229221
# DOI: 10.1186/s12889-024-19295-y
# "Breaking down barriers: rationalisations and motivation to stop among
# Chinese male smokers under cigarette dependence" (Zhang, Chen, Meng, Zhao,
# Liu & Tian, 2024), BMC Public Health.
# Data: 12889_2024_19295_MOESM2_ESM.sav (Supplementary Material 2), fetched via
#       the Europe PMC supplementaryFiles endpoint for PMC11229221. The other
#       supplement (MOESM1_ESM.docx, Table S1) is the item list; the rest of
#       the zip is figure images.
# License: CC BY 4.0 (article licence in the Europe PMC full-text record, with
#          BMC's CC0 waiver for data made available in the article). The data
#          are article-attached SI, so the article licence governs.
#
# Item text: shipped for both tables (SPSS variable labels carry each English
#   stem and value labels carry every response option; Table S1 in MOESM1
#   gives identical wording). The questionnaire was administered in Chinese
#   (street-intercept survey in Guiyang); no Chinese wording is in the article
#   or its supplements, so the English ships as a translated substitute with
#   language = Chinese.
#
# Multi-scale split, per the paper's Measures section:
#   - Chinese Male Smoking Rationalisation Scale (Huang et al., 2020): 26 items
#     in six subscales SFB/RGB/SAB/SSB/SEB/QHB, all 1-5 agreement -> one table
#     (one instrument; subscales stay together, named in item codes).
#   - Fagerstrom Test for Cigarette Dependence (FTCD/FTND): ND1-ND6, scored
#     0-3 (ND1, ND4) or 0-1 (the other four) as the value labels document ->
#     its own table. Mixed widths are the instrument's design, not a split.
#   - MTSS is a SINGLE item (Kotz et al., 2013) -> covariate, never a table.
# FTND and HSI are the file's own sum scores -> dropped as composites.
#
# The deposit is the paper's analytic sample (616 of 790; straight-liners
# already removed by the authors). No fractional values anywhere.

import sys
import tempfile
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11229221/supplementaryFiles"
SAV = "12889_2024_19295_MOESM2_ESM.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV = {
    "MTSS": "cov_mtss",              # 1-7, Motivation To Stop Scale (single item)
    "Age": "cov_age_group",          # 2 18-24 ... 7 65+
    "Education": "cov_education",    # 1-5
    "Resident": "cov_residence",     # 1 city, 2 township
    "Occupation": "cov_occupation",  # 1-6
    "Fage": "cov_age_first_smoked",  # 1 below 11 ... 8 above 65 (banded)
}
SUBSCALES = {"SFB": 5, "RGB": 3, "SAB": 6, "SSB": 4, "SEB": 5, "QHB": 3}
SRS = [f"{p}{i}" for p, n in SUBSCALES.items() for i in range(1, n + 1)]
FTCD = [f"ND{i}" for i in range(1, 7)]
FTCD_PERMITTED = {"ND1": {0, 1, 2, 3}, "ND2": {0, 1}, "ND3": {0, 1},
                  "ND4": {0, 1, 2, 3}, "ND5": {0, 1}, "ND6": {0, 1}}
SKIP = {
    "NO": "used as id (questionnaire number)",
    "CurrentSmoker": "constant 1 (inclusion screen)",
    "Gender": "constant 1 = male (inclusion criterion)",
    "FTND": "sum score of ND1-ND6 (composite)",
    "HSI": "Heaviness of Smoking Index, sum of ND1+ND4 (composite)",
}


def load() -> pd.DataFrame:
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            break
        time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")
    with zipfile.ZipFile(BytesIO(r.content)) as z, \
            tempfile.NamedTemporaryFile(suffix=".sav") as fh:
        fh.write(z.read(next(n for n in z.namelist() if n.endswith(SAV))))
        fh.flush()
        df, _ = pyreadstat.read_sav(fh.name)
    return df


def finish(df, items, table, permitted, constructs):
    d = df[["NO"] + list(COV) + items].rename(columns={"NO": "id", **COV})
    covs = list(COV.values())
    long = d.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all(), f"{table}: fractional resp (imputation?)"
    for c in ["id", "resp"] + covs:
        long[c] = long[c].astype(int)
    long = long[["id", "item", "resp"] + sorted(covs)]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    for it, grp in long.groupby("item"):
        assert set(grp["resp"]).issubset(permitted[it]), f"{table}/{it}: resp off-scale"
    assert not long.duplicated(["id", "item"]).any(), f"{table}: duplicate id/item"
    assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
    assert long["item"].nunique() == len(items) > 1, f"{table}: item count"
    report = irw_validate.validate_frame(
        long, label=table, profile="upload",
        context={"permitted_values": permitted, "item_constructs": constructs})
    print(report)
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert() -> None:
    df = load()
    assert df["NO"].is_unique
    used = set(COV) | set(SRS) | set(FTCD) | set(SKIP)
    unaccounted = [c for c in df.columns if c not in used]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")

    tables = ["zhang_2024_smoking_rationalisation", "zhang_2024_ftcd"]
    assert len(tables) == len(set(tables)), "duplicate output filenames"
    finish(df, SRS, tables[0],
           {i: {1, 2, 3, 4, 5} for i in SRS},
           {i: "smoking rationalisation" for i in SRS})
    finish(df, FTCD, tables[1], FTCD_PERMITTED,
           {i: "cigarette dependence" for i in FTCD})


if __name__ == "__main__":
    convert()
