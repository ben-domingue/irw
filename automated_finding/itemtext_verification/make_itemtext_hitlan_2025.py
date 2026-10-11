#!/usr/bin/env python3
"""Item text for hitlan_2025_ders16 / _dirty_dozen / _celebrity_attitude (Dataverse 10.7910/DVN/E9WMPW).

Cheap case: the .sav variable labels are "<Qualtrics instruction> - <stem>" and the value labels are
the anchors; data/hitlan_2025_dark_triad_celebrity.py labels(block) splits them, so the item code is
the deposit's own column name. English administration (US undergraduates).
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("hitlan_2025_dark_triad_celebrity")
INSTR = {"hitlan_2025_ders16": "Difficulties in Emotion Regulation Scale, 16-item (DERS-16)",
         "hitlan_2025_dirty_dozen": "Dirty Dozen Dark Triad",
         "hitlan_2025_celebrity_attitude": "Celebrity attitude items"}


def main():
    for table, (block, n, valid, _) in mod.BLOCKS.items():
        rows = []
        for code, instr, stem, vl in mod.labels(block):
            assert set(vl) == set(valid), code
            for r in sorted(vl):
                rows.append(row(table, f"{table}_1", code, INSTR[table], "English", int(r), stem,
                                option_text=vl[r], instructions=instr))
        write(table, rows)


if __name__ == "__main__":
    main()
