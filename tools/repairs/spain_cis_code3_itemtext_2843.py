"""Add the code-3 option row to the item text of the 15 spain_* tables rebuilt in irw#2843.

    python3 spain_cis_code3_itemtext_2843.py LIVE_ITEMS_DIR CIS_RAW_DIR OUT_DIR

The rebuilt tables keep code 3, the scale's volunteered middle answer (NO LEER),
which the build had dropped as missing; their live item text listed only the
options 1, 2, 4, 5. For each <table>__items.csv in LIVE_ITEMS_DIR this adds, per
item, one row copied from the item's resp-1 row with resp = 3, option_text = the
CIS value label for code 3 (verbatim, from CIS_RAW_DIR/MD<study>/<study>.sav),
and option_text_translated = its English rendering below. Nothing else changes.
"""
import glob
import os
import sys

import pandas as pd
import pyreadstat

STUDY = {"spain_2024_values": 3473, "spain_2024_ideology": 3480, "spain_2026_love": 3508,
         "spain_2025_tourism": 3521, "spain_2026_prostitution": 3525}
ENGLISH = {
    "(NO LEER) Ni de acuerdo ni en desacuerdo": "(not read out) Neither agree nor disagree",
    "(NO LEER) Ni bastante ni poco": "(not read out) Neither a lot nor a little",
    "(NO LEER) Ni fácil ni difícil": "(not read out) Neither easy nor difficult",
    "(NO LEER) Regular": "(not read out) So-so",
}


def main(live_dir, raw_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    labels = {}
    for f in sorted(glob.glob(os.path.join(live_dir, "*__items.csv"))):
        table = os.path.basename(f)[: -len("__items.csv")]
        study = next(v for k, v in STUDY.items() if table.startswith(k + "_"))
        if study not in labels:
            _, meta = pyreadstat.read_sav(os.path.join(raw_dir, f"MD{study}", f"{study}.sav"),
                                          metadataonly=True)
            labels[study] = {k.lower(): v for k, v in meta.variable_value_labels.items()}
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        assert "3" not in set(d.resp), table
        add = []
        for item, g in d.groupby("item", sort=False):
            lab = labels[study][item][3.0]
            row = g[g.resp == "1"].iloc[0].copy()
            row["resp"], row["option_text"] = "3", lab
            if "option_text_translated" in row:
                row["option_text_translated"] = ENGLISH[lab]
            add.append(row)
        out = pd.concat([d, pd.DataFrame(add)], ignore_index=True)
        out.to_csv(os.path.join(out_dir, os.path.basename(f)), index=False)
        print(f"{table}__items: {len(d)} -> {len(out)} rows")


if __name__ == "__main__":
    main(*sys.argv[1:4])
