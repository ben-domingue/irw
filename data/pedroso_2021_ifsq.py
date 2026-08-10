#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257991
# DOI: 10.1371/journal.pone.0257991
#
# Pedroso, Gubert (2021). Cross-cultural adaptation and validation of the
# Infant Feeding Style Questionnaire in Brazil. PLOS ONE.
#
# S1 Dataset (XLSX) contains raw item-level responses to the four subscales
# of the Infant Feeding Style Questionnaire - Brazil (IFSQ-Br), each on a
# 5-point Likert scale (belief items: disagree..agree; behavior items:
# never..always). Values are stored as strings with comma decimals (e.g.
# "1,00"). N=465 mother-infant pairs. Paper confirms no imputation ("We did
# not conduct data imputation, as no variable had more than 10% missing
# values") and no sentinel "I don't know/does not apply" codes appear in
# this raw file (values are cleanly 1-5 across every item).
#
# Subscales (one output file each, per datastandard.md "one file per
# scale"):
#   LF  Laissez-faire      (11 items: LF1-5, LF6recoded-9recoded, LF10-11)
#   PR  Pressuring         (17 items: PR1-8, PR11-19 - source numbering
#                            skips PR9/PR10)
#   RS  Restriction        (11 items: RS1-4, RS5recoded-6recoded, RS7-11)
#   RP  Responsiveness     (12 items: RP1-12)
#
# Excluded: mean_* columns (already-computed subscale composite means).

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SRC_URL = "https://doi.org/10.1371/journal.pone.0257991.s002"

SCALES = {
    "laissezfaire": [c for c in ["LF1", "LF2", "LF3", "LF4", "LF5",
                                  "LF6recoded", "LF7recoded", "LF8recoded",
                                  "LF9recoded", "LF10", "LF11"]],
    "pressuring": [f"PR{i}" for i in list(range(1, 9)) + list(range(11, 20))],
    "restriction": ["RS1", "RS2", "RS3", "RS4", "RS5recoded", "RS6recoded",
                     "RS7", "RS8", "RS9", "RS10", "RS11"],
    "responsiveness": [f"RP{i}" for i in range(1, 13)],
}


def convert():
    import io
    import requests
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, item_cols in SCALES.items():
        item_cols = [c for c in item_cols if c in df.columns]
        sub = df[["id"] + item_cols].copy()
        for c in item_cols:
            sub[c] = (sub[c].astype(str).str.replace(",", ".", regex=False))
            sub[c] = pd.to_numeric(sub[c], errors="coerce")

        long = sub.melt(id_vars=["id"], value_vars=item_cols,
                         var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]
        long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"pedroso_2021_ifsq_{name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
