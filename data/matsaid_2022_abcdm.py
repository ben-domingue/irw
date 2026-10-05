#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9310389
# DOI: 10.1186/s12889-022-13811-8
#   "The Malay version of the attitudes and beliefs about cardiovascular disease
#   (ABCD-M) risk questionnaire: a translation, reliability and validation study"
#   (Mat Said, Tengku Ismail, Abdul Hamid, Sahathevan, Abdul Aziz & Musa, 2022),
#   BMC Public Health 22:1412.
# Data: the article's supplementary files from the Europe PMC supplementaryFiles
#       zip: 12889_2022_13811_MOESM1_ESM.xlsx, sheet "Raw data" (179 respondents x
#       42 columns: ID, nine demographics, K1-K8, PR9-PR16, PB17-PB20, IC21-IC26,
#       and six domain totals). Its "Raw data information" sheet documents the
#       column blocks. (The triage read only the workbook's first sheet, "Figures
#       legend and tables title", and failed.) MOESM2_ESM.pdf is the bilingual
#       questionnaire and scoring guide.
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Item text: not shipped. Levels checked: the xlsx has no variable or value
#   labels (headers only: K1..IC26; the "Raw data information" sheet names the
#   blocks, not the items). The wording, Malay as administered plus English, is
#   in MOESM2_ESM.pdf, items numbered 1-26, and the codes carry the same number
#   (K1-K8 = items 1-8, PR9-PR16 = 9-16, PB17-PB20 = 17-20, IC21-IC26 = 21-26).
#   Not shipped because the one available check of that mapping, the paper's
#   Table 2 factor loadings, does not reproduce from the deposit for items 15/16
#   and 21-26 (see the data note): items 9-14 and 17-20 agree to ~0.03, but the
#   paper's weakest perceived-risk item is 15 (0.263) where the deposit's is
#   PR16 (0.135; PR15 0.514), and the paper's intention loadings (0.72-0.97 for
#   all six) are not recoverable from a deposit in which IC25/IC26 correlate
#   0.88 with each other and ~0.1 with IC21-IC24.
#
# Scoring (MOESM2 scoring guide and paper Methods "Instrument"):
#   Knowledge (items 1-8): answered True / False / Don't know; the deposit holds
#     the scored item, 1 = correct, 0 = incorrect or don't know (key: 1-7 True,
#     8 False). The raw T/F/DK answer is not in the deposit.
#   Items 9-26: "1, strongly disagree; 2, disagree; 3, agree; 4, strongly agree;
#     and 0, non-applicable". 0 is a non-response and is dropped (it is not a
#     step below "strongly disagree"); the paper's domain totals count it as 0.
#     Items 15, 23 and 26 are reverse-coded in the scoring guide (4 = strongly
#     disagree); the deposit stores the scored value - each domain total equals
#     the sum of the stored item values, and PR15 correlates positively with the
#     other risk items - so for those three items a higher resp is more
#     disagreement with the printed statement.
#
# Tables (one per domain, as in the scoring guide and the deposit's column blocks;
# the paper's CFA uses the three Likert domains as three factors):
#   matsaid_2022_abcdm_knowledge          K1-K8      0-1
#   matsaid_2022_abcdm_perceived_risk     PR9-PR16   1-4
#   matsaid_2022_abcdm_perceived_benefits PB17-PB20  1-4
#   matsaid_2022_abcdm_intention          IC21-IC26  1-4
#
# Sample: 179 Malay adults (18-66) attending government health clinics in four
# districts of Kelantan, Malaysia, Jan-Mar 2020; self-administered Malay form.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "matsaid_2022_abcdm"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9310389/supplementaryFiles"
FILE = "12889_2022_13811_MOESM1_ESM.xlsx"


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(zipfile.ZipFile(io.BytesIO(r.content)).read(FILE))
    return p


TABLES = {
    "matsaid_2022_abcdm_knowledge": [f"K{i}" for i in range(1, 9)],
    "matsaid_2022_abcdm_perceived_risk": [f"PR{i}" for i in range(9, 17)],
    "matsaid_2022_abcdm_perceived_benefits": [f"PB{i}" for i in range(17, 21)],
    "matsaid_2022_abcdm_intention": [f"IC{i}" for i in range(21, 27)],
}
TOTALS = {  # derived domain scores: checked, then not shipped
    "KNOWLEDGE": "matsaid_2022_abcdm_knowledge",
    "PERCEIVED_RISK": "matsaid_2022_abcdm_perceived_risk",
    "PERCEIVED_BENEFIT": "matsaid_2022_abcdm_perceived_benefits",
    "INTENTION": "matsaid_2022_abcdm_intention",
}
COVS = {
    "AGE": "cov_age",
    "GENDER": "cov_gender",
    "DISTRICT": "cov_district",
    "CLINIC": "cov_clinic",
    "STATUS": "cov_marital_status",
    "EDUCATION": "cov_education",
    "OCCUPATION": "cov_occupation",
    "INCOME": "cov_income",
}
# INCOME holds the lower bound of the paper's Table 1 bands (RM per month)
INCOME_BANDS = {1000: "<RM1000", 1001: "RM1001-3000", 3001: "RM3001-5000", 5001: ">RM5000"}


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Raw data")
    d.columns = [c.strip() for c in d.columns]
    assert d.shape == (179, 42), d.shape
    items = [c for v in TABLES.values() for c in v]
    assert len(items) == len(set(items)) == 26

    skipped = {
        "ETHNICITY": "constant (all 179 MALAY)",
        "AWARENESS": "derived total (sum of the 26 scored items)",
        "PERCENTAGE": "derived (AWARENESS / 80 x 100)",
    }
    skipped.update({t: "derived domain total" for t in TOTALS})
    # balance the books: every source column is the id, an item, a covariate, or skipped
    accounted = {"ID"} | set(items) | set(COVS) | set(skipped)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in skipped.items():
        print(f"  [skip] {c}: {why}")

    assert (d["ETHNICITY"] == "MALAY").all()
    assert d["ID"].is_unique and d["ID"].tolist() == list(range(1, 180))
    assert d[items].notna().all().all()
    for tot, name in TOTALS.items():
        assert (d[TABLES[name]].sum(axis=1) == d[tot]).all(), tot
    assert (d[items].sum(axis=1) == d["AWARENESS"]).all()
    assert d[TABLES["matsaid_2022_abcdm_knowledge"]].isin([0, 1]).all().all()
    likert = [c for c in items if not c.startswith("K")]
    assert d[likert].isin(range(0, 5)).all().all()

    d = d.rename(columns={"ID": "id", **COVS})
    for c in ["cov_gender", "cov_district", "cov_clinic", "cov_marital_status",
              "cov_education", "cov_occupation"]:
        d[c] = d[c].str.strip().str.lower()
    assert set(d["cov_income"].dropna()) == set(INCOME_BANDS)
    d["cov_income"] = d["cov_income"].map(INCOME_BANDS)
    covs = list(COVS.values())

    assert len(TABLES) == len(set(TABLES))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        n0 = len(t)
        if name != "matsaid_2022_abcdm_knowledge":
            na = t["resp"] == 0
            print(f"  {name}: dropped {na.sum()} non-applicable (0) responses of {n0}")
            t = t[~na]
            pv = {i: {1, 2, 3, 4} for i in its}
        else:
            pv = {i: {0, 1} for i in its}
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
