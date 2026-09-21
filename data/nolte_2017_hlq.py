#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0172340
# DOI: 10.1371/journal.pone.0172340
# Data: journal.pone.0172340_S1_File.sav (S1 File)
# License: CC BY 4.0 (verified on the article page and in Crossref metadata)
#
# Nolte, Osborne, Dwinger, Elsworth, Conrad, Rose, Harter & Dirmaier
# (2017), "German translation, cultural adaptation, and validation of the
# Health Literacy Questionnaire (HLQ)." PLOS ONE. N=1,058 German adults
# with chronic conditions.
#
# The HLQ is nine distinct scales, not one instrument with a total score
# -- its authors are explicit that it has no overall score -- so this
# writes nine tables. The nine also split across two response formats,
# which datastandard.md forbids mixing in one file regardless:
#   scales 1-5 (23 items) on 1-4, "trifft ueberhaupt nicht zu".."trifft
#   voellig zu"; scales 6-9 (21 items) on 1-5, "kann ich nicht".."sehr
#   einfach".
#
# The scale membership below is NOT inferred from column order. It is the
# published HLQ structure (4/4/5/5/5 then 5/6/5/5 = 44 items), and each
# group is independently confirmed by the German variable labels: the
# first group is all about having a doctor or therapist one can rely on,
# the second about having sufficient information, and so on. The column
# order in the .sav happens to agree, which is a check rather than the
# source.
#
# T3_Group is the sampling group ("Control group" / "Group declined
# participation"), not a treatment assignment, so it rides as cov_ rather
# than as `treat`.
#
# Item text: NOT shipped here, and it is the cheap kind -- the .sav's
# variable labels carry all 44 items in the GERMAN wording respondents
# actually read, and the value labels carry both anchor sets in German
# too. The blocker is rights, not recovery: the HLQ is licensed by Deakin
# University and has no entry in instrument_rights_register.csv.
# Escalated rather than decided; if it clears, this is a one-pass job
# with the administered-language columns already satisfied.
import os
import pandas as pd
import pyreadstat

RAW = os.environ.get("HLQ_SAV", "journal.pone.0172340_S1_File.sav")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

P1 = [1, 2, 3, 4]        # trifft ueberhaupt nicht zu .. trifft voellig zu
P2 = [1, 2, 3, 4, 5]     # kann ich nicht .. sehr einfach

SCALES = {
    "nolte_2017_hlq_provider_support": (["T3_1_11", "T3_1_14", "T3_1_26", "T3_1_32"], P1),
    "nolte_2017_hlq_information":      (["T3_1_04", "T3_1_17", "T3_1_23", "T3_1_34"], P1),
    "nolte_2017_hlq_managing_health":  (["T3_1_08", "T3_1_16", "T3_1_21", "T3_1_27", "T3_1_31"], P1),
    "nolte_2017_hlq_social_support":   (["T3_1_03", "T3_1_06", "T3_1_19", "T3_1_24", "T3_1_29"], P1),
    "nolte_2017_hlq_appraisal":        (["T3_1_02", "T3_1_10", "T3_1_20", "T3_1_25", "T3_1_30"], P1),
    "nolte_2017_hlq_engage_providers": (["T3_2_02", "T3_2_04", "T3_2_07", "T3_2_15", "T3_2_20"], P2),
    "nolte_2017_hlq_navigating":       (["T3_2_01", "T3_2_08", "T3_2_11", "T3_2_13", "T3_2_16", "T3_2_19"], P2),
    "nolte_2017_hlq_find_information": (["T3_2_03", "T3_2_06", "T3_2_10", "T3_2_14", "T3_2_18"], P2),
    "nolte_2017_hlq_understand_info":  (["T3_2_05", "T3_2_09", "T3_2_12", "T3_2_17", "T3_2_21"], P2),
}

COVS = {
    "T3_Group": "cov_study_group",
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Relationship": "cov_lives_with_partner",
    "Edu": "cov_years_schooling",
    "Employment": "cov_employment",
    "Net_income": "cov_net_income_band",
}
REDUNDANT = ["Agegroup"]  # banded recode of Age, which is kept in full


def main():
    df, meta = pyreadstat.read_sav(RAW)

    all_items = [c for cols, _ in SCALES.values() for c in cols]
    assert len(all_items) == 44, f"expected 44 HLQ items, listed {len(all_items)}"
    assert len(set(all_items)) == 44, "an item is listed in two scales"

    accounted = set(all_items) | set(COVS) | set(REDUNDANT)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"columns: 44 items across {len(SCALES)} HLQ scales, "
          f"{len(COVS)} covariates, {len(REDUNDANT)} recode dropped")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())

    os.makedirs(OUTDIR, exist_ok=True)
    assert len(set(SCALES)) == len(SCALES), "duplicate output table name"
    for t in SCALES:
        assert len(t) <= 40, f"table name over the 40-char cap: {t} ({len(t)})"

    total = 0
    for table, (items, permitted) in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = pd.to_numeric(long["resp"])

        bad = long.loc[~long["resp"].isin(permitted), "resp"].unique()
        assert len(bad) == 0, f"{table}: off-scale resp values: {bad}"
        assert (long["resp"] % 1 == 0).all(), f"{table}: fractional resp"

        long = long[["id", "item", "resp"] + cov_cols]
        n = long["id"].nunique()
        assert n >= 100, f"{table}: below the 100-id floor: {n}"

        out = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(out, index=False)
        total += len(long)
        print(f"{table:34s} {len(long):6,} responses | {n:,} ids | "
              f"{long['item'].nunique()} items")

    print(f"\n{len(SCALES)} tables, {total:,} responses total")


if __name__ == "__main__":
    main()
