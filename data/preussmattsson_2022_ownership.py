#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0277080
# S1 Data: https://doi.org/10.1371/journal.pone.0277080.s002
# DOI: 10.1371/journal.pone.0277080
#
# Preuss Mattsson, Coppi, Chancel & Ehrsson (2022), "Combination of
# visuo-tactile and visuo-vestibular correlations in illusory body ownership
# and self-motion sensations", PLOS ONE.
#
# The S1 Data workbook has 3 sheets. "Questionnaire Experiment" (the main
# study) only has N=30 participants -- below the IRW floor of 50. However
# "SCR Experiment-Questionnaire" administered the *same* 6-statement illusory
# ownership questionnaire (Table 2 in the paper: S1-S6, 7-point Likert scale
# -3 "fully disagree" to +3 "fully agree") across the same 2x2 factorial
# design (visuo-vestibular sync/async x visuo-tactile sync/async -> 4
# conditions: SVVSVT, AVVSVT, SVVAVT, AVVAVT) to a *different*, larger sample
# of N=50 participants (the cohort who also underwent skin-conductance
# recording; procedure differed only in trial count/order per the paper's
# Methods, so this sheet is NOT merged with the N=30 sheet -- kept as its own
# table). This sheet alone clears the N>=50 floor, so it is the one shipped.
#
# S7 in each condition block is a *different* construct (self-motion
# perception, rated on a 10-point visual analog scale, per Table 2's caption)
# rather than part of the ownership questionnaire -- excluded from this file
# per "one scale per file". No out-of-range values were found in S1-S6 for
# this sheet (checked programmatically: all values fall within -3..+3), and
# no imputation-related language appears in the paper text.

import io
import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file?"
           "type=supplementary&id=10.1371/journal.pone.0277080.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

CONDITIONS = ["SVVSVT", "AVVSVT", "SVVAVT", "AVVAVT"]


def convert():
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    xl = pd.ExcelFile(io.BytesIO(r.content))
    raw = pd.read_excel(xl, sheet_name="SCR Experiment-Questionnaire", header=None)

    data = raw.iloc[2:].reset_index(drop=True)
    id_col = data[0].astype(str)

    records = []
    for ci, cond in enumerate(CONDITIONS):
        base = 1 + ci * 7  # each condition block is 7 cols wide (S1-S7); S7 excluded
        for s in range(6):
            col = base + s
            vals = pd.to_numeric(data[col], errors="coerce")
            item_name = f"S{s+1}_{cond}"
            records.append(pd.DataFrame({"id": id_col, "item": item_name, "resp": vals}))

    long = pd.concat(records, ignore_index=True)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    assert id_col.nunique() == len(data), "id not unique"
    # sanity: all Likert values within documented -3..+3 range
    assert long["resp"].between(-3, 3).all(), "out-of-range value found in S1-S6"

    out_cols = ["id", "item", "resp"]
    long = long[out_cols]

    out_name = "preussmattsson_2022_ownership"
    csv_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(csv_path, index=False)
    try:
        import pyreadr
        pyreadr.write_rdata(os.path.join(OUT_DIR, out_name + ".RData"),
                             long, df_name="d")
    except ImportError:
        long.to_pickle(os.path.join(OUT_DIR, out_name + ".rdata_fallback.pkl"))

    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
