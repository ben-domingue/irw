#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190771
# DOI: 10.1371/journal.pone.0190771
# Data: OSF https://osf.io/rav8k/ (DOI 10.17605/OSF.IO/RAV8K),
#       "KOERNER_SCS_for OSF data sharing (2018 01 15).SAV"
# License: CC BY 4.0 -- verified on the OSF node itself via the OSF API
#          (public=true, license "CC-By Attribution 4.0 International"),
#          not merely inherited from the PLOS article.
#
# Coroiu, Kwakkenbos, Moran, Thombs, Albani, Bourkas et al. (2018),
# "Structural validation of the Self-Compassion Scale with a German
# general population sample." PLOS ONE. N=2,448.
#
# The deposit carries three instruments at item level, each on its own
# response scale, so per datastandard.md's one-file-per-scale rule this
# writes three tables:
#   coroiu_2018_scs   -- Self-Compassion Scale, 26 items, 1-5
#   coroiu_2018_cses  -- Core Self-Evaluations Scale, 12 items, 1-5
#   coroiu_2018_phq9  -- PHQ-9, 9 items, 0-3
# The GAD-2 (q301, q302) is only two items, which is not a scale, so it
# is carried as two covariates rather than as a fourth table.
#
# Administered in German (the file is an English-labelled export of a
# German survey -- CSES's own value labels still read "5=stimme
# vollkommen zu"). SPSS user-missing codes -1 "no response" and -2
# "Filter" are declared in the file and pyreadstat maps them to NaN;
# this is asserted below rather than assumed.
#
# Item text: NOT shipped in this pass, for two separate reasons.
#   - The variable labels are English glosses of a German administration,
#     and several are elided ("PHQ9 1. Little interest or pleasure... =
#     PHQ2 item 1"), so they are not the administered wording and not
#     verbatim even in English. Both label levels were checked and both
#     are populated (55/55 variable labels, 53 value-label variables).
#   - Rights are undetermined for two of the three instruments: the PHQ
#     family is verdict=ship in instrument_rights_register.csv, but
#     Neff's Self-Compassion Scale and Judge et al.'s Core Self-
#     Evaluations Scale have no register entry. Escalated rather than
#     decided.
import os
import pandas as pd
import pyreadstat

RAW = os.environ.get("CORNIU_SAV", "KOERNER_SCS_for OSF data sharing (2018 01 15).SAV")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

SCALES = {
    "coroiu_2018_scs":  ([f"SCS{n}" for n in range(1, 27)], [1, 2, 3, 4, 5]),
    "coroiu_2018_cses": ([f"CSES{n}" for n in range(1, 13)], [1, 2, 3, 4, 5]),
    "coroiu_2018_phq9": ([f"PHQ9_{n}" for n in range(1, 10)], [0, 1, 2, 3]),
}

COVS = {
    "s2_sex": "cov_sex",
    "s4_age": "cov_age",
    "s5_relation": "cov_marital_status",
    "s6_employmt": "cov_employment",
    "s8_educat": "cov_education",
    "q301": "cov_gad2_nervous",
    "q302": "cov_gad2_worry",
}


def main():
    df, meta = pyreadstat.read_sav(RAW)

    all_items = [c for cols, _ in SCALES.values() for c in cols]
    accounted = set(all_items) | set(COVS) | {"ID"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"columns: {len(all_items)} items across {len(SCALES)} scales, "
          f"{len(COVS)} covariates (incl. the 2-item GAD-2), 1 id")

    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df), "ID is not unique per row"

    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())

    os.makedirs(OUTDIR, exist_ok=True)
    for table, (items, permitted) in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = pd.to_numeric(long["resp"])

        # The -1/-2 user-missing codes must not have survived as data.
        assert (long["resp"] >= 0).all(), "sentinel codes survived into resp"
        bad = long.loc[~long["resp"].isin(permitted), "resp"].unique()
        assert len(bad) == 0, f"{table}: off-scale resp values: {bad}"
        assert (long["resp"] % 1 == 0).all(), f"{table}: fractional resp"

        long = long[["id", "item", "resp"] + cov_cols]
        n = long["id"].nunique()
        assert n >= 100, f"{table}: below the 100-id floor: {n}"

        out = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(out, index=False)
        print(f"{table}: {len(long):,} responses | {n:,} ids | "
              f"{long['item'].nunique()} items -> {out}")


if __name__ == "__main__":
    main()
