#!/usr/bin/env python3
"""Item text for the four girma_2024_* tables (Mendeley 10.17632/jgsv7pcrs8). The .sav variable labels
are the English stems; the file carries no value labels on any item, so option_text is blank for every
scale point (never padded); option rows are limited to the table's observed resp set. English instrument; administered language not stated (left blank).
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("girma_2024_wellbeing")
INSTR = {"girma_2024_hope": "Adult Hope Scale (Snyder), 8 items, 1-8",
         "girma_2024_moral_identity": "Moral Identity Measure (Aquino & Reed 2002), 10 items, 1-7",
         "girma_2024_mlq": "Meaning in Life Questionnaire (Steger et al.), 10 items, 1-7",
         "girma_2024_wemwbs": "Warwick-Edinburgh Mental Well-being Scale, 14 items, 1-5"}


def main():
    import pandas as pd
    from _itemtext_writer_c import RESP_DIR
    rows = {t: [] for t in INSTR}
    for table, code, stem, valid in mod.stems():
        stem = stem.replace("(R)", "").strip()
        # option_text is blank for every point, so a never-endorsed point (MII: nobody chose 2) adds
        # nothing; keep the table's observed resp set so the set gate reads exactly (syafrijon precedent)
        observed = set(pd.read_csv(RESP_DIR / f"{table}.csv")["resp"])
        for r in valid:
            if r in observed:
                rows[table].append(row(table, f"{table}_1", code, INSTR[table], "", r, stem))
    for t, rs in rows.items():
        write(t, rs)


if __name__ == "__main__":
    main()
