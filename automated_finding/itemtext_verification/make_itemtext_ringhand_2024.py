#!/usr/bin/env python3
"""Item text for ringhand_2024_ccam_tpb (Zenodo 10.5281/zenodo.14394129). Administered in eight
languages (English, German, Italian, Dutch, Greek, Spanish, Polish, French); the deposit carries the
English wording only, which ships in the base fields.

Cheap case: data/ringhand_2024_ccam.py stems() reads the .sav variable label (English stem, prefixed by
the construct tag, e.g. "AT_TPB: ...") and the value labels; the item code is the deposit's own column
name. The four AT semantic-differential items are labelled at the endpoints only ("very bad [1]" /
"very good [5]"); the bracketed number is stripped and the midpoints left blank.
"""
import re

from _itemtext_writer_c import load_script, row, write

mod = load_script("ringhand_2024_ccam")
TABLE = "ringhand_2024_ccam_tpb"
LANG = "English; German; Italian; Dutch; Greek; Spanish; Polish; French"


def main():
    rows = []
    for code, label, vl in mod.stems():
        stem = re.sub(r"^[A-Za-z_\- ]+?(TPB|Trust)( CCAM| Public Transport)?:\s*", "", label).strip()
        for r in sorted(vl):
            opt = re.sub(r"\s*\[\d\]$", "", vl[r])
            if re.fullmatch(r"\[\d\]", vl[r]):
                opt = ""
            rows.append(row(TABLE, f"{TABLE}_1", code, "Theory of Planned Behaviour and trust items on CCAM use (SINFONICA survey)",
                            LANG, int(r), stem, option_text=opt))
    write(TABLE, rows)


if __name__ == "__main__":
    main()
