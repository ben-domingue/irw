#!/usr/bin/env python3
"""Item text for the three blanc_2024_* tables (Zenodo 10.5281/zenodo.14512684). Spanish administration.

Cheap case: data/blanc_2024_sexuality.py stems() reads each item's .sav variable label (the Spanish stem) and
value labels (the anchors); the item code is the deposit's own column name. Anchors are given only for the
labelled scale points; unlabeled points stay blank. No English translation is shipped.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("blanc_2024_sexuality")
INSTR = {"blanc_2024_sos": "Sexual Opinion Survey (erotofobia-erotofilia), 16 items, 1-7",
         "blanc_2024_sdi": "Sexual Desire Inventory-2 (deseo sexual), 13 items",
         "blanc_2024_sexual_assertiveness": "Hurlbert Index of Sexual Assertiveness (asertividad sexual), 25 items, 0-4"}


def main():
    import pandas as pd
    rows = {t: [] for t in INSTR}
    for table, code, stem, vl in mod.stems():
        resp = pd.read_csv(mod.OUT_DIR / f"{table}.csv")
        observed = sorted(resp.loc[resp["item"] == code, "resp"].unique())
        for r in sorted(set(observed) | set(vl)):
            rows[table].append(row(table, f"{table}_1", code, INSTR[table], "spa", int(r), stem.strip(),
                                   option_text=vl.get(r, "")))
    for t, rs in rows.items():
        write(t, rs)


if __name__ == "__main__":
    main()
