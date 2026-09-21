#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0315687
# DOI: 10.1371/journal.pone.0315687
# Data: journal.pone.0315687_S1_Appendix.xlsx (S1 Appendix)
# License: CC BY 4.0 (verified on the article page and in Crossref metadata)
#
# Roy et al. (2024), "Prevalence and predictors of functional
# gastrointestinal disorder among the undergraduate students of
# Bangladesh." PLOS ONE. N=1,019.
#
# The deposit carries five candidate item blocks. Only two survive
# inspection, and the other three are excluded for stated reasons rather
# than quietly dropped:
#
#   SHIPPED
#   phq1..phq9   -> roy_2024_phq9    PHQ-9, 0-3, clean on every item.
#   sas1..sas10  -> roy_2024_sas_sv  10 items on 1-6, clean on every
#                                    item (the SAS-SV's format).
#
#   NOT SHIPPED
#   isi1..isi7   The Insomnia Severity Index block is 100% missing --
#                every cell of all seven columns is empty.
#   pss1..pss4   Unresolvable. The file also has pss1_new..pss4_new, and
#                the analysed score `pss_sc` equals sum(pss*_new) for
#                99.9% of rows but sum(pss1..4) for only 5.6%. pss*_new
#                is NOT derivable from pss1..4: across all sixteen
#                column pairings, neither identity nor reversal
#                (4 - x) matches above 26%, which is chance for a
#                5-point scale. One of the two blocks is mislabelled and
#                the deposit gives no way to say which, so neither
#                ships. An author query would settle it.
#   aw1..aw10    Not one scale. aw1/aw8/aw9/aw10 take 0-4 while
#                aw2..aw7 take {0,2,3,5,6} -- gaps at 1 and 4, which is
#                a multi-select coding rather than an ordinal scale.
#                aw1 additionally holds a single value of 43 (row 901,
#                against a 0-4 range everywhere else in that column):
#                a data-entry error, isolated to one cell of one item.
#
# Item text: not shipped. The sheet has bare column codes, there is no
# codebook in the deposit, and both shipped instruments are third-party.
import os
import pandas as pd
from irw_validate.compat import run_qc

RAW = os.environ.get("ROY_XLSX", "journal.pone.0315687_S1_Appendix.xlsx")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

SCALES = {
    "roy_2024_phq9":   ([f"phq{n}" for n in range(1, 10)], [0, 1, 2, 3]),
    "roy_2024_sas_sv": ([f"sas{n}" for n in range(1, 11)], [1, 2, 3, 4, 5, 6]),
}

COVS = {
    "age": "cov_age",
    "gender": "cov_gender",
    "marital": "cov_marital_status",
    "income": "cov_income",
    "religion": "cov_religion",
    "living_with": "cov_living_with",
    "smoking": "cov_smoking",
    "activity": "cov_physical_activity",
    "bmi": "cov_bmi",
    "fgid": "cov_fgid",
}

EXCLUDED = {
    "isi": [f"isi{n}" for n in range(1, 8)],
    "pss": [f"pss{n}" for n in range(1, 5)] + [f"pss{n}_new" for n in range(1, 5)],
    "aw": [f"aw{n}" for n in range(1, 11)],
}


def main():
    df = pd.read_excel(RAW)
    num = lambda c: pd.to_numeric(df[c], errors="coerce")

    # Re-assert each exclusion rather than trusting the comment above.
    assert num("isi1").notna().sum() == 0 and \
        all(num(c).notna().sum() == 0 for c in EXCLUDED["isi"]), "ISI block is not empty"
    pss_sc = num("pss_sc")
    raw_sum = sum(num(f"pss{i}") for i in range(1, 5))
    new_sum = sum(num(f"pss{i}_new") for i in range(1, 5))
    assert (new_sum == pss_sc).mean() > 0.9 and (raw_sum == pss_sc).mean() < 0.2, \
        "the pss_sc provenance is not what the header comment says"
    assert set(num("aw2").dropna().unique()) <= {0, 2, 3, 5, 6}, "aw2 coding changed"
    print("excluded blocks re-verified: isi (all missing), pss (unresolvable), aw (not one scale)")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())
    for c in cov_cols:
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

        bad = [c for c in run_qc(long, permitted_values=permitted,
                                 item_constructs={i: table for i in long["item"].unique()})
               if c.status == "fail"]
        assert not bad, f"{table}: run_qc failures: {[(c.name, c.detail) for c in bad]}"

        out = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(out, index=False)
        print(f"{table:20s} {len(long):6,} responses | {n:,} ids | "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
