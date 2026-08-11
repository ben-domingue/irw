#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0267580
# DOI: 10.1371/journal.pone.0267580
#
# Witus & Larson (2022) "A randomized controlled trial of a video
# intervention shows evidence of increasing COVID-19 vaccination
# intention." PLOS ONE. CC BY 4.0.
#
# S1 Dataset (XLSX, "Witus Larson PNAS Data File", N=1632 MTurk
# respondents) has no explicit person-ID column -- row index is used as
# id per datastandard.md. Most columns are single miscellaneous survey
# items (different response ranges/scales) or precomputed dummy/
# demographic covariates, not a coherent multi-item instrument. The one
# genuine multi-item Likert battery present in the shared file is Q28_1-3
# ("The narrator was trustworthy / comforting / knowledgeable", 1-4 scale,
# "Not at all" to "Very"), answered only by the ~808/809 respondents
# randomized to one of the two video-narrator conditions (Male-Narrator
# vs Female-Narrator; text/control-arm respondents were not shown these
# items -- confirmed against the S1 Appendix's full survey flow/question
# text). `cov_narrator_gender` records which video arm a respondent saw.
# The paper's other multi-item batteries described in Methods/Appendix
# (Q10/Q12/Q14/Q16/Q18 -- vaccine understanding/safety/concern/trust/
# accuracy beliefs) are NOT present as columns in the shared S1 Dataset,
# only the single behavioral-intention outcome (Q8) and demographics are.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0267580.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_LABELS = {
    "Q28_1": "narrator_trustworthy",
    "Q28_2": "narrator_comforting",
    "Q28_3": "narrator_knowledgeable",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content),
                          sheet_name="Witus Larson PNAS Data File")


def convert():
    print("Fetching S1 Dataset (XLSX)...")
    df = fetch_raw()

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    item_cols = list(ITEM_LABELS.keys())
    # Keep only respondents who actually saw one of the two video arms
    # (the narrator-perception items were not administered to the
    # text/control arms).
    df = df.dropna(subset=item_cols, how="all").copy()

    df["cov_narrator_gender"] = pd.NA
    df.loc[df["MNV"] == 1, "cov_narrator_gender"] = "male"
    df.loc[df["FNV"] == 1, "cov_narrator_gender"] = "female"

    long = df.melt(id_vars=["id", "cov_narrator_gender"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].map(ITEM_LABELS)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 4)].reset_index(drop=True)

    long = long[["id", "item", "resp", "cov_narrator_gender"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "witus_2022_narrator_perception.csv")
    long.to_csv(out_path, index=False)

    print(f"witus_2022_narrator_perception: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
