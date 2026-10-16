#!/usr/bin/env python3
"""Item text for kessler_2020_ebcck_18 (Mendeley 10.17632/tzv223xgsr.2). English administration.

Positional case: data/kessler_2020_ebcck.py docx_items(18) returns the 18 stems of EB-CCK_18item.docx in
document order; the claim is that the k-th paragraph is Item_k of the Study 2 workbooks (paper_order). The
claim is checked in verify_kessler_2020_ebcck_18.R (item polarity). The 30- and 22-item pools FAIL that check
and ship no item text. The 1-7 agreement anchors are not in the deposit, so option_text is blank except
for the endpoints named in the paper's method ("strongly disagree" / "strongly agree").
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("kessler_2020_ebcck")
TABLE = "kessler_2020_ebcck_18"
ANCHOR = {1: "strongly disagree", 7: "strongly agree"}


def main():
    stems = mod.docx_items(18)
    rows = []
    for k, stem in enumerate(stems, start=1):
        for r in range(1, 8):
            rows.append(row(TABLE, f"{TABLE}_1", f"Item_{k}", "Epistemic Beliefs about the Co-Construction of Knowledge (EB-CCK), 18 items, 1-7",
                            "eng", r, stem, option_text=ANCHOR.get(r, "")))
    write(TABLE, rows)


if __name__ == "__main__":
    main()
