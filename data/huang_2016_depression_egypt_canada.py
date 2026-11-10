#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5147018
# DOI: 10.7717/peerj.2783
#   "The effects of the gender-culture interaction on self-reports of depressive
#   symptoms: cross-cultural study among Egyptians and Canadians" (Huang, Beshai,
#   Yu & Kronfol, 2016), PeerJ 4:e2783.
# Data: the article's supplementary file peerj-04-2783-s001.sav from the Europe
#   PMC supplementaryFiles zip: 292 rows x 98 columns. SPSS variable labels give
#   each column's coding (e.g. "1 = Yes, 0 = No").
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Sample: rows with questionnaire data are the 152 people who completed the
#   intake questionnaire package (the other 140 rows hold only the structured
#   interview screen and are not shipped). Of the 152, `Eligibility` = 1 for 131,
#   which reproduces the paper's sample exactly (Egypt 29 depressed + 29
#   non-depressed; Canada 35 + 38); 21 were screened not eligible. All 152 ship,
#   with cov_eligible. `Participant_Number` is reused between the depressed and
#   healthy arms (13 numbers each name two different people, differing in age,
#   sex and 24-41 answers), so `id` is the row index.
#
# Tables:
#   huang_2016_bdi2             Pre_BDI_01..21        0-3  BDI-II (paper Method)
#   huang_2016_pdsq_depression  Pre_PDSQD_01..21      0/1  PDSQ Major Depressive Disorder subscale
#   (Psychiatric Diagnostic Screening Questionnaire, Zimmerman & Mattia 2001.)
#   The PDSQ Psychosis (22-27), Alcohol (28-33) and Drug (34-39) items are NOT
#   shipped: psychosis and substance dependence were exclusion criteria, so they
#   are 99-100% "No" (item 26 constant) and carry no information.
#   BDI: 5 cells hold fractional values (1.5, 1.52, 0.92, 0.59) - mean-imputed;
#   they are dropped. BDI_T (= the stored item sum, including those cells) and
#   the two Dozois-Dobson subscale scores are derived and not shipped.
#
# Not shipped: Screen_1..18 (the structured interview screen, yes/no with
#   99999-style sentinels and unlabelled 0s), ManiaScreen_01/02, the derived
#   totals, Pre_Dem_MotherBirth/FatherBirth.
#
# Covariates (source codes; labels in the SPSS value labels): Dep_Status
#   (0 depressed, 1 healthy), Nationality (3 Canadian, 4 Egyptian), gender
#   (1 M, 2 F), age, birthplace, marital status, income band, education,
#   religion, first and primary language, Eligibility (1 eligible, 2 not).
#
# Item text: not shipped. Levels checked: SPSS variable labels hold only the
#   response coding ("1 = Yes, 0 = No") for the PDSQ items and nothing for the
#   BDI items; value labels are the yes/no anchors. BDI-II (Pearson) and PDSQ
#   (WPS) wording is copyrighted and not in the deposit.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "huang_2016"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5147018/supplementaryFiles"
FILE = "peerj-04-2783-s001.sav"


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        p.write_bytes(z.read([n for n in z.namelist() if n.endswith(FILE)][0]))
    return p


TABLES = {
    "huang_2016_bdi2": ([f"Pre_BDI_{i:02d}" for i in range(1, 22)], {0, 1, 2, 3}),
    "huang_2016_pdsq_depression": ([f"Pre_PDSQD_{i:02d}" for i in range(1, 22)], {0, 1}),
}
COVS = {
    "Dep_Status": "cov_dep_status",
    "Nationality": "cov_nationality",
    "Pre_Dem_Gender": "cov_gender",
    "Pre_Dem_Age": "cov_age",
    "Pre_Dem_SelfBirth": "cov_birthplace",
    "Pre_Dem_Marital": "cov_marital",
    "Pre_Dem_Income": "cov_income",
    "Pre_Dem_Education": "cov_education",
    "Pre_Dem_Religion": "cov_religion",
    "Pre_Dem_FirstLang": "cov_first_language",
    "Pre_Dem_PrimaryLang": "cov_primary_language",
    "Eligibility": "cov_eligible",
}


def main() -> None:
    d, _ = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (292, 98), d.shape
    items = [c for its, _ in TABLES.values() for c in its]
    screen_items = [c for c in d.columns if c.startswith(("Pre_PDSQPSYC", "Pre_PDSQALC", "Pre_PDSQDRG"))]
    assert len(screen_items) == 18
    skipped = ({"Participant_Number": "reused across arms; id = row index",
                "Pre_Dem_MotherBirth": "not carried", "Pre_Dem_FatherBirth": "not carried",
                "ManiaScreen_01": "screen", "ManiaScreen_02": "screen",
                "DozoisDobsonCogAff": "derived subscale", "DozoisDobsonSomaticVeg": "derived subscale",
                "BDI_T": "derived total"}
               | {f"Screen_{i}": "interview screen" for i in range(1, 19)}
               | {c: "PDSQ exclusion-screen subscale, ~all No" for c in screen_items})
    accounted = set(items) | set(COVS) | set(skipped)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted

    has = d[items + screen_items].notna().any(axis=1)
    assert has.sum() == 152 and d.loc[has, items].isna().sum().sum() == 1  # 1 blank PDSQ cell
    d = d[has].reset_index(drop=True)
    assert (d["Eligibility"] == 1).sum() == 131
    el = d[d["Eligibility"] == 1]
    assert pd.crosstab(el["Nationality"], el["Dep_Status"]).values.tolist() == [[35, 38], [29, 29]]
    bdi = TABLES["huang_2016_bdi2"][0]
    assert (d[bdi].sum(axis=1) - d["BDI_T"]).abs().max() < 1e-9
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, pv_set) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        frac = t["resp"] % 1 != 0
        if frac.any():
            print(f"  {name}: dropped {frac.sum()} fractional (imputed) cells")
            assert name == "huang_2016_bdi2" and frac.sum() == 5
            t = t[~frac]
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() == 152
        pv = {i: pv_set for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
