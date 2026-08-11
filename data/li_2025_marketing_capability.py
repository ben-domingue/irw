#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0326329
# DOI: 10.1371/journal.pone.0326329
#
# "Breaking the deadlock: A study on the pathway and effects of reshaping
# the sustainable marketing capability of Chinese time-honored brands"
# (PLOS ONE, 2025). S1 File (SPSS .sav) contains raw item-level responses
# (7-point Likert) from 352 individuals (managers/employees) at 47
# heritage enterprises, across eight distinct measurement constructs. Each
# construct is written as its own IRW file per the "one file per scale"
# rule.
#
# QC note: the PE (Policy Environment) items contain a subset of values
# that are non-integer and, in a few cases, exceed the stated 1-7 scale
# maximum (e.g. PE2 has values 7.35, PE3 has 7.497) -- these look like a
# multiplicative transformation applied to a subset of respondents rather
# than genuine raw ratings on the discrete 7-point scale. Per datastandard.md
# guidance on verifying continuous-looking columns and filtering corrupted
# values, only integer responses within the documented 1-7 range are kept;
# the corrupted non-integer/out-of-range values are dropped rather than
# "corrected" by inferring the multiplier.

import os
import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "automated_finding", "raw_downloads",
                    "li_2025_pone0326329_s1data.sav")

SCALES = {
    "li_2025_marketing_exploration": ["Eplor11", "Eplor12", "Eplor13", "Eplor14", "Eplor15"],
    "li_2025_marketing_exploitation": ["Eploit21", "Eploit22", "Eploit23", "Eploit24", "Eploit25"],
    "li_2025_marketing_culture": ["MCultu11", "MCultu12", "MCultu13", "MCultu14", "MCultu15"],
    "li_2025_marketing_learning": ["MLear26", "MLear27", "MLear28", "MLear29", "MLear210"],
    "li_2025_marketing_operation": ["MOper311", "MOper312", "MOper313", "MOper314", "MOper315"],
    "li_2025_corporate_performance": [f"Perfo4{i}" for i in range(16, 26)],
    "li_2025_market_environment": ["ME1", "ME2", "ME3", "ME4", "ME5"],
    "li_2025_policy_environment": ["PE1", "PE2", "PE3", "PE4", "PE5"],
}

COV_RENAME = {
    "Type": "cov_firm_type",
    "Size": "cov_firm_size",
    "Gender": "cov_gender",
    "Position": "cov_position",
    "Located": "cov_location",
    "Industry": "cov_industry",
}


def convert():
    df, meta = pyreadstat.read_sav(SRC)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)  # no person-ID column in source
    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # keep only integer responses within the documented 1-7 scale
        is_integer = (long["resp"] == long["resp"].round())
        in_range = (long["resp"] >= 1) & (long["resp"] <= 7)
        long = long[is_integer & in_range].reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]
        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
