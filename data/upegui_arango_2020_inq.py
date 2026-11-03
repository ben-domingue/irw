#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0232030
# DOI: 10.1371/journal.pone.0232030
# Paper: Upegui-Arango, L. D., Forkmann, T., Nielsen, T., Hallensleben, N.,
#   Glaesmer, H., Spangenberg, L., Teismann, T., Juckel, G., & Boecker, M.
#   (2020). Psychometric evaluation of the Interpersonal Needs Questionnaire
#   (INQ) using item analysis according to the Rasch model. PLOS ONE 15(8):
#   e0232030.
# Data: journal.pone.0232030.s002 (S1 Data, .xlsx). Four sheets: "General
#   population" (2,508 German adults, representative survey) and "Clinical
#   sample" (185 inpatients: 97 with depression, 88 with a suicide history),
#   plus "Mixed1"/"Mixed2" -- each the clinical sample plus 185 people DRAWN
#   FROM the general-population sheet (Methods), i.e. re-used rows. Only the
#   first two sheets are shipped, so no respondent appears twice.
#   S1 Material (.pdf) lists the 15 German INQ items.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, upegui_arango_2020_inq: the German INQ-15 (Van Orden et
# al. 2012), 1 "not at all true for me" .. 7 "very true for me". Same
# instrument, same scale in both samples, so one file with cov_sample.
# Item ids are the deposit's column names: INQ1..INQ6 (perceived
# burdensomeness), INQ7_reversed .. INQ15_reversed and INQ9/11/12
# (thwarted belongingness). The "_reversed" columns are ALREADY reverse-
# scored in the deposit and are shipped as deposited; the suffix says so.
# The clinical sheet does not carry INQ9, INQ11 or INQ12 -- the three items
# the paper excluded from its TB analysis -- so those items have general-
# population responses only.
# In the general-population sheet no respondent used category 7 on INQ1-6
# (perceived burdensomeness is near-floor there: 14,079 of 14,980 cells are
# 1); 7 is observed on every other item and in the clinical sample.
#
# Covariates: cov_sample (general population / clinical), cov_gender
# (2 = female: 1,391 of 2,508 = 55.5%, the paper's figure for the general
# sample; the clinical sheet's 105 of 184 = 57% vs the paper's "52%" is
# noted, not resolved). The age-group code is NOT shipped: the paper says the
# four groups were cut separately per sample, so one code means different
# ages in the two sheets.
#
# Item text: NOT SHIPPED. The German stems are in S1 Material (a PDF table,
#   cheap to read), but the INQ (Van Orden, Cukrowicz, Witte & Joiner 2012)
#   is a named third-party instrument with no grant in the register; held,
#   register row written 2026-11-02.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("UPEGUI_RAW", "journal.pone.0232030.s002.xlsx")
NAME = "upegui_arango_2020_inq"


def convert():
    gen = pd.read_excel(RAW, sheet_name="General population")
    cli = pd.read_excel(RAW, sheet_name="Clinical sample")
    assert len(gen) == 2508 and len(cli) == 185
    for d in (gen, cli):
        txt = [c for c in d.columns if pd.api.types.is_string_dtype(d[c])]
        print(f"PII screen: {len(txt)} text columns of {len(d.columns)} examined: {txt}")
        assert len(d.columns) > 0 and txt == []
    assert int((gen["gender"] == 2).sum()) == 1391   # 55.5% female, as the paper reports

    gen_items = [c for c in gen.columns if c.startswith("INQ")]
    cli_items = [c for c in cli.columns if c.startswith("INQ")]
    assert len(gen_items) == 15 and set(cli_items) == set(gen_items) - {"INQ9", "INQ11", "INQ12"}
    gen = gen.assign(id=range(1, len(gen) + 1), cov_sample="general population")
    cli = cli.assign(id=range(len(gen) + 1, len(gen) + len(cli) + 1), cov_sample="clinical")
    assert set(gen.columns) - set(gen_items) == {"agegroup", "gender", "id", "cov_sample"}
    assert set(cli.columns) - set(cli_items) == {"agegroup", "gender", "id", "cov_sample"}

    parts = []
    for d, items in ((gen, gen_items), (cli, cli_items)):
        d = d.assign(cov_gender=d["gender"].map({1: "male", 2: "female"}))
        parts.append(d.melt(id_vars=["id", "cov_sample", "cov_gender"], value_vars=items,
                            var_name="item", value_name="resp"))
    long = pd.concat(parts).dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(1, 7).all()
    long = long[["id", "item", "resp", "cov_sample", "cov_gender"]]
    assert not long.duplicated(["id", "item"]).any() and long["item"].nunique() == 15
    checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in gen_items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    print("dropped columns: agegroup (cut per sample); sheets Mixed1/Mixed2 (re-used rows)")


if __name__ == "__main__":
    convert()
