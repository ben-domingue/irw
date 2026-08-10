#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250927
# DOI: 10.1371/journal.pone.0250927
#
# Girma, Tsehay, Mamaru, Abera (2021). Depression and its determinants among
# adolescents in Jimma town, Southwest Ethiopia. PLOS ONE.
#
# S1 Dataset (XLS) contains raw item-level responses. Two clean instruments
# with genuine per-item raw data (rather than only composite scores):
#
#   PHQ-9 depression items (0-3 scale, "not at all" to "nearly every day"):
#     INTEREST, DEPRESSF, SLEEPCON, FATGUEFE, APPETITE, WORTHFEE, CONCENTR,
#     SLOWLYSE, DEATHWIS
#   Oslo-3 Social Support Scale raw items (item-specific ranges):
#     CLOSENUM (1-4), CONCERNP (1-5), HELPPRAT (1-5)
#   Confirmed via arithmetic: min possible sum 1+1+1=3, max 4+5+5=14, which
#   matches the paper's reported Oslo-3 composite range of 3-14 exactly -
#   i.e. these are the three raw items behind the "oslo3"/"OSL3" composite
#   columns (which are excluded here as aggregates).
#
# Excluded as not part of either raw scale / already-computed aggregates:
#   agebin3, grade9-12, orthodox/muslim/protestant/other (dummy covariates),
#   abuse, neglect, oslo3, OSL3, lowsupp, highsupp, scoredep (composites);
#   DYSTHICF, DIFICULT, SUICMOTH, SUICEVER (distinct single-purpose
#   screening items on different scales, not part of PHQ-9 or Oslo-3).
#
# IDAUTOMA has one duplicate value (545 unique of 546 rows) so the row index
# is used as `id` instead, per datastandard.md guidance.
#
# No imputation: paper states "Fifteen participants submitted either
# incomplete or inconsistent survey questionnaire, and it was not included
# in the analysis" (exclusion, not imputation).

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SRC_URL = "https://doi.org/10.1371/journal.pone.0250927.s001"

PHQ9_ITEMS = ["INTEREST", "DEPRESSF", "SLEEPCON", "FATGUEFE", "APPETITE",
              "WORTHFEE", "CONCENTR", "SLOWLYSE", "DEATHWIS"]
OSLO3_ITEMS = ["CLOSENUM", "CONCERNP", "HELPPRAT"]

COV_MAP = {
    "AGECHRON": "cov_age",
    "SEXRESPO": "cov_sex",
    "GRADELEV": "cov_grade_level",
    "RELIGION": "cov_religion",
    "SCHOOLTY": "cov_school_type",
    "RESIDECE": "cov_residence",
}


def load():
    import io
    import requests
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = load()
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]

    os.makedirs(OUT_DIR, exist_ok=True)

    def write(item_cols, vmin, vmax, fname):
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= vmin) & (long["resp"] <= vmax)]
        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    write(PHQ9_ITEMS, 0, 3, "girma_2021_phq9.csv")
    write(OSLO3_ITEMS, 1, 5, "girma_2021_oslo3.csv")


if __name__ == "__main__":
    convert()
