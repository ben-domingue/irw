#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0122866
# DOI: 10.1371/journal.pone.0122866
# Paper: Maraz A, Kiraly O, Urban R, Griffiths MD, Demetrovics Z (2015). Why
#   do you dance? Development of the Dance Motivation Inventory (DMI). PLOS ONE
#   10(3): e0122866.
# Data: figshare 10.6084/m9.figshare.1287336 ("Dance motivation"), file
#   DanceMot_data_PlosOne_141212.sav, 447 Hungarian recreational Latin /
#   ballroom dancers, online survey.
# License: CC BY 4.0, verified on the DEPOSIT (api.figshare.com/v2/articles/
#   1287336: license "CC BY 4.0"); the article is also CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# ONE output table, maraz_2015_dmi: Motiv_1..Motiv_51, the full 51-item pool
# from which the paper derived the 24-item, 8-factor DMI (fitness, mood
# enhancement, intimacy, socialising, trance, mastery, self-confidence,
# escapism). The response scale RUNS BACKWARDS from the usual: 1 "nagyon
# jellemzo ram" (very characteristic of me) .. 5 "nem jellemzo ram" (not
# characteristic of me), the .sav's own value labels; kept as deposited.
# Covariates: gender (1 male / 2 female, value labels), age, highest education
#   (value labels, translated: primary school, vocational school,
#   upper-secondary leaving exam, college or university degree, and code 5,
#   unlabelled, kept as "5").
# Dropped: the eight factor scores F1..F8, Experience and Intensity (derived
#   composites), Studies, Works, SES, Kapcsolati_status (relationship status)
#   and the four Aktiv_* dance-experience columns.
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Both label levels are complete in the .sav (the
#   Hungarian stems as variable labels, the five anchors as value labels) and
#   the instrument is the authors' own (study-authored under the deposit's
#   CC BY). Not shipped because the administration was Hungarian and the
#   standard wants English in the *_translated columns: the paper's S1
#   Appendix (journal.pone.0122866.s001) gives English for the 24 retained DMI
#   items only, so 27 of 51 would need an IRW-generated translation.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("MARAZ_RAW", "DanceMot_data_PlosOne_141212.sav")
NAME = "maraz_2015_dmi"
EDU = {1.0: "primary school", 2.0: "vocational school", 3.0: "upper-secondary leaving exam",
       4.0: "college or university degree", 5.0: "5"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (447, 72)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    vl = meta.variable_value_labels
    assert vl["Gender"] == {1.0: "Férfi", 2.0: "Nő"}
    assert vl["Motiv_1"][1.0] == "nagyon jellemző rám" and vl["Motiv_1"][5.0] == "nem jellemző rám"
    items = [f"Motiv_{i}" for i in range(1, 52)]
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["Gender"].map({1.0: "male", 2.0: "female"})
    df["cov_age"] = df["Age"]
    df["cov_education"] = df["Education"].map(EDU)
    cov_cols = ["cov_gender", "cov_age", "cov_education"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    assert long["resp"].notna().all() and (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    dropped = ["F1_Fitness", "F2_MoodEnhancement", "F3_Intimacy", "F4_Socialising", "F5_Trance", "F6_Mastery",
               "F7_SelfConfidence", "F8_Escapism", "Experience", "Intensity", "Studies", "Works", "SES",
               "Kapcsolati_status", "Aktiv_Salsa", "Aktiv_Bachata", "Aktiv_Kizo_Zouk", "Aktiv_Latin_Std"]
    assert set(meta.column_names) == set(items) | {"Gender", "Age", "Education"} | set(dropped)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
