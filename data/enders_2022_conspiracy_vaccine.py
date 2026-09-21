#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0276082
# DOI: 10.1371/journal.pone.0276082
# Data: OSF https://osf.io/6a7et/ , "Raw Data.csv"
# License: CC0 1.0 Universal -- verified on the OSF node itself via the
#          OSF API (public=true, license "CC0 1.0 Universal").
#
# Enders, Uscinski, Klofstad & Stoler (2022), "On the relationship
# between conspiracy theory beliefs, misinformation, and vaccine
# hesitancy." PLOS ONE. N=2,055 US adults.
#
# Built from "Raw Data.csv" (the deposit's own Qualtrics export), NOT
# from "Clean Data.dta". The README calls the latter "the 'clean' (i.e.,
# recoded) dataset", and Analyses.do lines 401-402 reverse-code PSS4_2
# and PSS4_3 into it:
#       replace pss4_2 = (pss4_2 * -1) + 4
# datastandard.md says not to recode reverse-scored items, so the raw
# export is the correct source. Everything else is identical between the
# two files.
#
# Fourteen instruments ride in this one survey, each on its own response
# scale, so per the one-file-per-scale rule this writes fourteen tables.
#
# Three columns are dropped as degenerate: COVCONS_8, MISC_9 and
# VICTIM_5 each take exactly one value across all 2,055 respondents,
# which is the signature of an embedded attention check ("select
# 'agree'"), not of a response.
#
# The PSS-4 block appears TWICE in the Qualtrics export (pandas
# de-duplicates the second copy to PSS4_1.1..PSS4_4.1). The two copies
# genuinely disagree -- 44% to 83% of rows differ per item, and the
# item-wise correlations are +0.64/-0.54/-0.58/+0.75, so this is not a
# duplicated upload but two real administrations. Nothing in the README,
# the .do file or the article says what the second one is, so only the
# first block ships and the second is left alone rather than invented
# into a `wave`. Carried in TODO.md.
#
# ZIP is present in the raw export and is deliberately not carried.
#
# Item text: not shipped. The Qualtrics export's question-text header row
# was stripped before deposit (row 1 is data, not wording), the .dta
# carries only uppercased column names as variable labels, and the
# deposit has no codebook. The wording for most of these batteries is in
# the article's own appendix; that is a later pass.
import os
import pandas as pd

RAW = os.environ.get("ENDERS_CSV", "Raw Data.csv")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

# table -> (source columns, permitted resp values)
SCALES = {
    "enders_2022_vaccine_hesitancy":   ([f"VAXHES_{i}" for i in range(1, 11)], [1, 2, 3, 4, 5]),
    "enders_2022_covid_vax_misinfo":   ([f"COVVAXINFO_{i}" for i in range(1, 6)], [1, 2, 3, 4, 5]),
    "enders_2022_covid_conspiracy":    ([f"COVCONS_{i}" for i in range(1, 8)], [1, 2, 3, 4, 5]),
    "enders_2022_conspiracy_thinking": ([f"CTSCALE_{i}" for i in range(1, 5)], [1, 2, 3, 4, 5]),
    "enders_2022_misinformation":      ([f"MISC_{i}" for i in range(1, 9)], [1, 2, 3, 4, 5]),
    # The Dark Triad's three subscales ship separately: Analyses.do enters
    # `manipulate`, `narcissism` and `psychopathy` as three distinct
    # predictors rather than one composite, which is the source-side
    # evidence that these are distinct constructs.
    "enders_2022_machiavellianism":    ([f"MACH_{i}" for i in range(1, 5)], [1, 2, 3, 4, 5]),
    "enders_2022_narcissism":          ([f"NARC_{i}" for i in range(1, 5)], [1, 2, 3, 4, 5]),
    "enders_2022_psychopathy":         ([f"PSYC_{i}" for i in range(1, 5)], [1, 2, 3, 4, 5]),
    "enders_2022_populism":            ([f"POP_{i}" for i in range(1, 5)], [1, 2, 3, 4, 5]),
    "enders_2022_victimhood":          ([f"VICTIM_{i}" for i in range(1, 5)], [1, 2, 3, 4, 5]),
    "enders_2022_science_literacy":    ([f"SCILIT_{i}" for i in range(1, 12)], [0, 1]),
    "enders_2022_pss4":                ([f"PSS4_{i}" for i in range(1, 5)], [0, 1, 2, 3, 4]),
    "enders_2022_eq8_empathy":         ([f"EQ8_{i}" for i in range(1, 9)], [0, 1, 2, 3]),
    "enders_2022_compassion":          ([f"COMPASSION_{i}" for i in range(1, 6)], [1, 2, 3, 4, 5, 6, 7]),
    "enders_2022_institutional_trust": (["TRUST_EXP", "TRUST_ECO", "TRUST_FED", "TRUST_SCI",
                                         "TRUST_DOC", "TRUST_LEG", "TRUST_PRF", "TRUST_FIN",
                                         "TRUST_PHO", "TRUST_PHA"], [1, 2, 3, 4, 5, 6, 7]),
    "enders_2022_conflict":            ([f"CONFLICT_{i}" for i in range(1, 13)], [0, 1]),
}

COVS = {
    "GENDER": "cov_gender",
    "YEARBORN": "cov_year_born",
    "INC": "cov_income_band",
    "EDU": "cov_education",
    "STATE": "cov_state",
    "POLID": "cov_party_id",
    "POLIDEO": "cov_ideology",
    "POLINT": "cov_political_interest",
    "COVILL": "cov_had_covid",
    "COVVAX": "cov_covid_vaccinated",
}

# Constant across all respondents -- embedded attention checks, not responses.
DEGENERATE = ["COVCONS_8", "MISC_9", "VICTIM_5"]


def main():
    df = pd.read_csv(RAW, low_memory=False)

    for c in DEGENERATE:
        assert df[c].nunique(dropna=True) <= 1, f"{c} is not degenerate -- re-check"
    print(f"dropped as degenerate (single-valued attention checks): {DEGENERATE}")

    dup_pss = [c for c in df.columns if c.startswith("PSS4_") and c.endswith(".1")]
    assert len(dup_pss) == 4, f"expected a second PSS-4 block, found {dup_pss}"
    print(f"second PSS-4 administration left unshipped: {dup_pss}")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())
    for c in cov_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    os.makedirs(OUTDIR, exist_ok=True)
    total = 0
    for table, (items, permitted) in SCALES.items():
        missing = [c for c in items if c not in df.columns]
        assert not missing, f"{table}: missing source columns {missing}"

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])

        bad = long.loc[~long["resp"].isin(permitted), "resp"].unique()
        assert len(bad) == 0, f"{table}: off-scale resp values: {bad}"
        assert (long["resp"] % 1 == 0).all(), f"{table}: fractional resp"
        assert long["item"].nunique() > 1, f"{table}: single-item scale"

        long = long[["id", "item", "resp"] + cov_cols]
        n = long["id"].nunique()
        assert n >= 100, f"{table}: below the 100-id floor: {n}"

        out = os.path.join(OUTDIR, f"{table}.csv")
        assert not os.path.exists(out) or table in SCALES, "output name collision"
        long.to_csv(out, index=False)
        total += len(long)
        print(f"{table:34s} {len(long):7,} responses | {n:,} ids | "
              f"{long['item'].nunique():2d} items")

    assert len(set(SCALES)) == len(SCALES), "duplicate output table name"
    print(f"\n{len(SCALES)} tables, {total:,} responses total")


if __name__ == "__main__":
    main()
