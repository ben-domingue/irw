#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0262944
# DOI: 10.1371/journal.pone.0262944
# Paper: Schoneberg, C., Bottcher, J., Janowetz, B., Rostalski, A.,
#   Kreienbrock, L., & Campe, A. (2022). An intercomparison study of ELISAs
#   for the detection of porcine reproductive and respiratory syndrome virus
#   -- evaluating six conditionally dependent tests. PLOS ONE 17(1): e0262944.
# Data: journal.pone.0262944.s008 (S8 Table, "Raw data of the study", .xlsx),
#   sheet 'Daten', 812 rows x 13 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# Blood sera from 812 pigs on 24 farms across 13 districts of southeast
# Germany.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table, 6 items, 4,866 responses. THE ITEMS ARE DIAGNOSTIC TESTS
# AND THE RESPONDENTS ARE PIGS, which is in scope and is worth spelling out
# because it looks unlike everything else in this batch.
#
# WHY THIS IS AN ITEM RESPONSE TABLE AND NOT A LAB SPREADSHEET. `datastandard`
# defines `id` as "the focal unit being measured -- typically a person, but
# sometimes another entity", and the 2026-08-10 ruling in this pipeline's
# SKILL.md says non-human subjects are not by themselves a reason to skip. A
# serum sample run through six commercial ELISA kits gives a 812 x 6 binary
# matrix in which each kit has its own sensitivity and specificity -- its own
# difficulty and discrimination -- against a latent infection status. The
# paper's own analysis is a LATENT CLASS MODEL of six conditionally dependent
# binary indicators with no gold standard, which is the same object an IRT
# model is. So: id = the serum sample, item = the ELISA kit, resp = 0/1.
#
# THE SIX ITEMS ARE NAMED PRODUCTS, in the article's own order, so the opaque
# Test1..Test6 headers are renamed to the kits they are:
#   Test1 PRRS X3 (Idexx)                 Test4 Ingezim PRRS 2.0 (Ingenasa)
#   Test2 pigtyp PRRSV Ab (Indical)       Test5 Ingezim PRRS universal (Ingenasa)
#   Test3 ID Screen PRRS indirect (IDVet) Test6 PrioCHECK (ThermoFisher)
# The item codes keep the deposit's Test1..Test6 so the join to the file is
# literal; the kit names go in the table description, where a reader looking
# for "which item is the IDVet kit" will find them.
#
# 0/1 IS NOT CONFIRMED AS NEGATIVE/POSITIVE BY THE ARTICLE's readable text,
# which says only that the tests return positive/negative and that the model's
# response values are 0 and 1. The deposit holds exactly {0, 1} on all six
# columns. So the direction is the obvious one and is NOT asserted as fact in
# the description -- the same treatment as the unstated Likert directions
# elsewhere in this batch.
#
# SIX MISSING CELLS, dropped. The article says eight animals with incomplete
# results were removed, leaving 804 for analysis; this raw file keeps all 812
# and leaves six Test6 cells empty. So the deposit is the PRE-exclusion file
# and the table carries 812 ids rather than the paper's 804. Recorded, not
# reconciled -- dropping animals to match an analysis set would discard real
# observations.
#
# COVARIATES, all three German and all three kept as the deposit's own labels:
#   Bestand    -> cov_farm, 24 farms, which is the clustering the paper's
#                 conditional-dependence model is about
#   Status     -> cov_status, the herd's vaccination/infection category
#                 ('frei', 'ungeimpft', 'inf/ungeimpft', 'EU P', 'EU RF',
#                 'US', 'US x EU U'). 32 rows have none; those ship blank.
#   Tiergruppe -> cov_animal_group ('AF' weaned piglets, 'JS' gilts, and
#                 '1./2.', '3./4.', '5./6.' for sows by parity group), which
#                 matches the paper's stated sampling design of ten weaned
#                 piglets, six gilts and 18 sows per farm.
#
# `id` is the deposit's `Proben-ID`, unique over all 812 rows. `Probennr.` is
# a second unique sample identifier and `lfd Nr` a row counter; both dropped.
# `IFN-Nr.` (34 values) is dropped as an unexplained laboratory reference.
#
# PII: not applicable in the usual sense -- the subjects are pigs. Screened
# anyway: the string columns are sample codes, a vaccination-status
# vocabulary and an age-group vocabulary. No person is named anywhere, and
# no farm is identified beyond a number.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SCHONEBERG_RAW", "journal.pone.0262944_S8_Table.xlsx")

TABLE = "schoneberg_2022_prrsv_elisa"
N_ROWS = 812
ITEMS = [f"Test{i}" for i in range(1, 7)]
KITS = {"Test1": "PRRS X3 (Idexx)", "Test2": "pigtyp PRRSV Ab (Indical)",
        "Test3": "ID Screen PRRS indirect (IDVet)",
        "Test4": "Ingezim PRRS 2.0 (Ingenasa)",
        "Test5": "Ingezim PRRS universal (Ingenasa)",
        "Test6": "PrioCHECK (ThermoFisher)"}
COVS = {"Bestand": "cov_farm", "Status": "cov_status",
        "Tiergruppe": "cov_animal_group"}
DROP = {"lfd Nr": "a row counter",
        "Probennr.": "a second unique sample identifier; Proben-ID is used",
        "IFN-Nr.": "an unexplained laboratory reference number"}
N_MISSING = 6


def convert():
    df = pd.read_excel(RAW, sheet_name="Daten")
    assert len(df) == N_ROWS, len(df)

    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: the subjects are pigs. {len(strings)} string "
          f"column(s): {strings}")
    assert set(strings) <= {"Proben-ID", "Probennr.", "Status", "Tiergruppe"}, \
        strings
    for c in ("Status", "Tiergruppe"):
        assert df[c].nunique() <= 10, (c, df[c].nunique(),
                                       "no longer a closed vocabulary")
    print("  the string columns are sample codes and two closed vocabularies "
          "(vaccination status, animal age group). No person is named and no "
          "farm is identified beyond a number")

    accounted = {"Proben-ID"} | set(COVS) | set(DROP) | set(ITEMS)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print("dropped: " + "; ".join(f"{k} ({v})" for k, v in DROP.items()))

    vals = df[ITEMS].stack().dropna()
    assert set(vals.unique()) == {0, 1}, sorted(vals.unique())
    missing = int(df[ITEMS].isna().sum().sum())
    assert missing == N_MISSING, (
        f"{missing} missing cells, not the {N_MISSING} this script expects; "
        f"the article removes 8 animals with incomplete results, so recheck "
        f"which file this is")
    print(f"{missing} missing cells (all in Test6), dropped. The article "
          f"analyses 804 animals after removing 8 with incomplete results; "
          f"this raw file keeps all {N_ROWS}, so the table carries "
          f"{N_ROWS} ids")

    assert df["Proben-ID"].nunique() == len(df), "Proben-ID is not unique"
    df = df.rename(columns={"Proben-ID": "id", **COVS})
    cov_cols = sorted(COVS.values())
    print(f"cov_farm: {df['cov_farm'].nunique()} farms; cov_status: "
          f"{df['cov_status'].nunique()} categories with "
          f"{int(df['cov_status'].isna().sum())} blank; cov_animal_group: "
          f"{sorted(df['cov_animal_group'].unique())}")

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    assert long["id"].nunique() == N_ROWS
    assert long["item"].nunique() == len(ITEMS)
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == len(ITEMS) * N_ROWS - N_MISSING, len(long)
    assert len(TABLE) <= 40, TABLE
    long = long[["id", "item", "resp"] + cov_cols]

    checks = run_qc(long, permitted_values={i: [0, 1] for i in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp=0-1")
    for i in ITEMS:
        pos = long.loc[long["item"] == i, "resp"].mean()
        print(f"    {i}: {pos:.1%} positive  [{KITS[i]}]")


if __name__ == "__main__":
    convert()
