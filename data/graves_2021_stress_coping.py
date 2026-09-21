#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255634
# DOI: 10.1371/journal.pone.0255634
# Data: journal.pone.0255634_S1_Dataset.csv (S1 Dataset)
# License: CC BY 4.0 (verified on the article page and in Crossref metadata)
#
# Graves, Hall, Dias-Karch, Haischer & Apter (2021), "Gender differences
# in perceived stress and coping among college students." PLOS ONE.
# N=1,055 observations.
#
# Two instruments at item level, one file each:
#   graves_2021_pss10       -- Perceived Stress Scale, 10 items, 0-4
#   graves_2021_brief_cope  -- Brief-COPE, 28 items, 1-4
# The fourteen Brief-COPE subscale scores, Adaptive_Cope,
# Maladaptive_Cope, PSS_Total, PSS_Cat and Stress_Cat are all composites
# of those items and are dropped.
#
# `prepost` is carried as a covariate, NOT as `wave`. The file has no
# person identifier and 607 + 448 = 1,055 rows, i.e. one row per
# observation with no way to link a "pre" row to its "post" row. A wave
# column would assert a within-person design the data cannot support.
#
# V48, V49 and V50 are entirely blank in the deposit and are dropped.
# Several columns are stored as text with a space for missing, so every
# numeric column is coerced rather than trusted.
#
# Item text: not shipped. The CSV has bare column codes, there is no
# codebook in the deposit, and both instruments are third-party
# (Cohen's PSS-10; Carver's Brief-COPE) rather than study materials.
import os
import pandas as pd

RAW = os.environ.get("GRAVES_CSV", "journal.pone.0255634_S1_Dataset.csv")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

SCALES = {
    "graves_2021_pss10":      ([f"PSS{n}" for n in range(1, 11)], [0, 1, 2, 3, 4]),
    "graves_2021_brief_cope": ([f"BC{n}" for n in range(1, 29)], [1, 2, 3, 4]),
}

COVS = {
    "Term": "cov_term",
    "type": "cov_course_type",
    "sec": "cov_section",
    "prepost": "cov_prepost",
    "age": "cov_age",
    "gender": "cov_gender",
    "level": "cov_class_level",
    "PSShlth": "cov_self_rated_health",
    "Yoga": "cov_yoga",
    "Pilates": "cov_pilates",
    "HFL": "cov_health_fitness_lifestyle",
}

COMPOSITES = ["PSS_Total", "PSS_Cat", "Stress_Cat", "Adaptive_Cope", "Maladaptive_Cope",
              "Self_Distraction", "Active_Coping", "Denial", "Substance_Use",
              "Emotional_Support", "Instru_Support", "Behavioral_Disengage", "Venting",
              "Pos_Reframe", "Planning", "Humor", "Acceptance", "Religion", "Self_Blame"]
EMPTY = ["V48", "V49", "V50"]
OTHER = ["filter_$"]  # SPSS filter flag, not data


def main():
    df = pd.read_csv(RAW, low_memory=False)

    for c in EMPTY:
        assert df[c].apply(lambda v: str(v).strip() == "").all(), f"{c} is not empty"
    print(f"dropped as entirely blank: {EMPTY}")

    all_items = [c for cols, _ in SCALES.values() for c in cols]
    accounted = set(all_items) | set(COVS) | set(COMPOSITES) | set(EMPTY) | set(OTHER)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"columns: {len(all_items)} items across {len(SCALES)} scales, "
          f"{len(COVS)} covariates, {len(COMPOSITES)} composites dropped")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())
    for c in cov_cols:
        if c != "cov_term":  # the only genuinely categorical covariate ("Fall"/"Spri")
            df[c] = pd.to_numeric(df[c], errors="coerce")

    os.makedirs(OUTDIR, exist_ok=True)
    for table, (items, permitted) in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])

        bad = long.loc[~long["resp"].isin(permitted), "resp"].unique()
        assert len(bad) == 0, f"{table}: off-scale resp values: {bad}"
        assert (long["resp"] % 1 == 0).all(), f"{table}: fractional resp"

        long = long[["id", "item", "resp"] + cov_cols]
        n = long["id"].nunique()
        assert n >= 100, f"{table}: below the 100-id floor: {n}"

        out = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(out, index=False)
        print(f"{table:26s} {len(long):6,} responses | {n:,} ids | "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
