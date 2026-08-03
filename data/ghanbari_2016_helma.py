#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0149202
# SI file: journal.pone.0149202_S3_File.sav
# DOI: 10.1371/journal.pone.0149202
#
# Health Literacy Measure for Adolescents (HELMA): 7 subscales administered
# to 582 Iranian adolescents. The SI file's actual columns (access1-11,
# reading1-6, understand1-9, appraise1-5, use1-5, com1-8, num1-3) do not
# match the item counts in the companion "Scoring for the HELMA" SI file
# (S4 File, a .doc scoring manual) -- that manual describes a different,
# shorter validated subset (e.g. access 5 items, reading 5, understand 10,
# use 4) plus a "self-efficacy" subscale that isn't present in this raw
# data file at all. Rather than trust the manual's item grouping, the
# response encoding for each subscale was verified directly from the raw
# per-item value_counts() in the .sav file:
#   access, reading, understand, appraise, use, com: all cleanly 1-5
#     ordinal (a 5-point frequency-style Likert), consistent across every
#     item in each block.
#   num (numeracy): cleanly binary 0/1 (incorrect/correct), consistent
#     across all 3 items.
# No sentinel codes observed in any block; ~100 scattered NaNs out of
# 582*66 cells are genuine item-nonresponse (not imputed -- the article
# text contains no imputation language ("imput", "MICE", "LOCF", etc.)).
# License: CC BY 4.0 (confirmed on article page).

import os
import re
import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0149202.s003"

COV_RENAME = {
    "mantaghe": "cov_region",
    "age": "cov_age",
    "class": "cov_class",
    "field": "cov_field",
    "sex": "cov_sex",
    "momedu": "cov_mother_education",
    "mamjob": "cov_mother_job",
    "papedu": "cov_father_education",
    "papjob": "cov_father_job",
    "TVsch": "cov_tv_schoolday",
    "TVvac": "cov_tv_holiday",
    "Intsch": "cov_internet_schoolday",
    "Intvac": "cov_internet_holiday",
    "magazine": "cov_magazine_use",
    "radio": "cov_radio_use",
    "interestinhealth": "cov_interest_in_health",
    "healthstatus": "cov_health_status",
    "firstsource": "cov_first_health_info_source",
}

SUBSCALES = {
    "ghanbari_2016_helma_access": (r"^access\d+$", 1, 5),
    "ghanbari_2016_helma_reading": (r"^reading\d+$", 1, 5),
    "ghanbari_2016_helma_understand": (r"^understand\d+$", 1, 5),
    "ghanbari_2016_helma_appraise": (r"^appraise\d+$", 1, 5),
    "ghanbari_2016_helma_use": (r"^use\d+$", 1, 5),
    "ghanbari_2016_helma_comm": (r"^com\d+$", 1, 5),
    "ghanbari_2016_helma_numeracy": (r"^num\d+$", 0, 1),
}


def load_raw():
    import requests
    headers = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
    r = requests.get(SI_URL, headers=headers, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/ghanbari_2016_helma_s3.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, meta = pyreadstat.read_sav(tmp_path)
    os.remove(tmp_path)
    return df


def convert():
    df = load_raw()

    df = df.rename(columns={"code": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)

    for out_name, (pattern, vmin, vmax) in SUBSCALES.items():
        item_cols = [c for c in df.columns if re.match(pattern, c)]
        sub = df[["id"] + cov_cols + item_cols].copy()

        long = sub.melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= vmin) & (long["resp"] <= vmax)]

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        long.to_pickle(out_path.replace(".csv", ".pkl"))  # scratch, not shipped
        os.remove(out_path.replace(".csv", ".pkl"))

        try:
            import pyreadr
            pyreadr.write_rdata(out_path.replace(".csv", ".RData"), long, df_name="d")
        except Exception as e:
            print(f"WARNING: could not write RData for {out_name}: {e}")

        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
