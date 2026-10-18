#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/rkw2g38rjp
# DOI: 10.17632/rkw2g38rjp
#   Zara, Sandra (2024). "Data set for the supplementary data analyses for the
#   associations of child maltreatment and diabetes in a representative German
#   sample." Mendeley Data.
# Data: CTQ OPD Diabetes Data.xlsx (5,041 rows x 76 columns; a representative
#       German population sample).
# License: CC BY 4.0 (Mendeley public API, data_licence.short_name).
#
# Item text: not shipped. The source is an .xlsx, so no label levels exist,
#   and the headers are positional codes (OPD_01_SW_0_4, PHQ4_01) carrying a
#   subscale tag but no wording. The OPD-SQS wording is in Ehrenthal et al.
#   (2012, Z Psychosom Med Psychother) and the PHQ-4 wording in Kroenke et al.
#   (2009, Psychosomatics) -- both one citation away, neither in the deposit.
#
# Tables (item codes are the source column names):
#   zara_2024_opd_sqs  OPD_01..OPD_12, 0-4. The OPD Structure Questionnaire
#       short form; the three subscale tags in the column names are SW
#       (self-perception), BM (?), KG (?) -- carried as itemcov-free codes
#       because the deposit never expands them.
#   zara_2024_phq4     PHQ4_01..PHQ4_04, 0-3. PHQ-4 (two PHQ-2 depression
#       items + two GAD-2 anxiety items). The register lists the PHQ/GAD
#       screener family as `ship`.
#
# NOT shipped -- the 28 CTQ items (CTQ_03_EA, REP25_CTQ_01_PN, ...):
#   the Childhood Trauma Questionnaire (Bernstein & Fink) is distributed
#   commercially by Pearson. It has no row in
#   itemtext/instrument_rights_register.csv, so neither the sweep nor
#   irw_validate's rights check would have stopped it -- this is a hand
#   judgment, and it wants a register row either way (noted in BATCH_LOG).
#   The CTQ columns also carry -1 as a user-missing code, which is a second
#   reason not to ship them untouched.
#
# Dropped, with reasons printed by the script:
#   - SA_sum/PA_sum/EA_sum/PN_sum/EN_sum, *_severity, *_dummy, PHQ4_tot,
#     OPD_SQS, OPD_self, OPD_contact, OPD_relation: composites.
#   - PHQ2, GAD2, GAD2_dich, PHQ2_dich: subtotals of the PHQ-4 items.
#   - Diab_dummy, income: kept as covariates (see below).
#   - the 28 CTQ items: rights, above.
# id: the source ID (1..5041, unique).
# Covariates: cov_age, cov_age_groups, cov_sex, cov_partnership_status,
#   cov_years_of_education, cov_income, cov_diabetes.

import io
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
API = "https://data.mendeley.com/public-api/datasets/rkw2g38rjp"
FILENAME = "CTQ OPD Diabetes Data.xlsx"

OPD = [f"OPD_{i:02d}_{t}_0_4" for i, t in zip(
    range(1, 13), ["SW", "SW", "BM", "KG", "SW", "KG",
                   "BM", "SW", "BM", "KG", "KG", "BM"])]
PHQ4 = [f"PHQ4_{i:02d}" for i in range(1, 5)]

TABLES = {
    "zara_2024_opd_sqs": (OPD, {0, 1, 2, 3, 4}),
    "zara_2024_phq4": (PHQ4, {0, 1, 2, 3}),
}
COVS = {"age": "cov_age", "age_groups": "cov_age_groups", "sex": "cov_sex",
        "partnership_status": "cov_partnership_status",
        "years_of_education": "cov_years_of_education",
        "income": "cov_income", "Diab_dummy": "cov_diabetes"}
COMPOSITES = {"SA_sum", "PA_sum", "EA_sum", "PN_sum", "EN_sum",
              "EN_severity", "PN_severity", "EA_severity", "PA_severity",
              "SA_severity", "EN_dummy", "PN_dummy", "EA_dummy", "PA_dummy",
              "SA_dummy", "PHQ4_tot", "OPD_SQS", "OPD_self", "OPD_contact",
              "OPD_relation", "PHQ2", "GAD2", "GAD2_dich", "PHQ2_dich"}


def fetch():
    meta = requests.get(API, headers=UA, timeout=60).json()
    lic = (meta.get("data_licence") or {}).get("short_name")
    assert lic == "CC BY 4.0", lic
    url = next(f["content_details"]["download_url"] for f in meta["files"]
               if f["filename"] == FILENAME)
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = fetch()
    assert d.shape == (5041, 76), d.shape

    ctq = [c for c in d.columns if "CTQ" in c]
    assert len(ctq) == 28, len(ctq)
    items = {c for its, _ in TABLES.values() for c in its}
    assert items <= set(d.columns), items - set(d.columns)

    # Balance the books: every source column is an item, a covariate, a
    # printed composite, the id, or a rights-withheld CTQ item.
    known = items | set(COVS) | COMPOSITES | set(ctq) | {"ID"}
    assert set(d.columns) == known, set(d.columns) ^ known
    print(f"dropped {len(COMPOSITES)} composite/subtotal column(s)")
    print(f"dropped {len(ctq)} CTQ item(s): commercially licensed "
          f"(Bernstein & Fink / Pearson), not in the rights register")
    print(f"kept {len(COVS)} covariate(s), {len(items)} item(s)")

    assert d["ID"].is_unique and d["ID"].nunique() == 5041
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.rename(columns={"ID": "id"}).melt(
            id_vars=["id"] + cov_cols, value_vars=its,
            var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == len(its) > 1
        pv = {i: allowed for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
