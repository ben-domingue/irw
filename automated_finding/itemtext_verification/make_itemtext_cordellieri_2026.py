#!/usr/bin/env python3
"""Item text for cordellieri_2026_scedd / _bsss8 / _rpodd (Zenodo 22375285). Italian stems from the
deposited SCEDD_codebook.xlsx ("Description / item wording", keyed by variable name). Anchors come from
the codebook's "Coding / response scale" column only where it names them; otherwise option_text is
blank: the BSSS-8 line names no anchors and the RPoDD line ("1 = not at all risky to 5 = extremely
risky", in English) describes a 5-point scale where the data carry 1-4, so neither block gets option
text. Italian administration; no English in the deposit -> _translated left empty.
"""
import re

from _itemtext_writer_c import load_script, row, write

mod = load_script("cordellieri_2026_scedd")
INSTR = {"scedd": "Scale of Cognitive and Emotional Distraction in Driving (SCEDD), 29-item initial pool",
         "bsss8": "Brief Sensation Seeking Scale (BSSS-8), Italian", "rpodd": "Risk perception of distracted driving, 9 items"}


def anchors(scale_text, n):
    """Pull '1 = x ... n = y' style anchors out of the coding text; blank when absent."""
    found = dict((int(k), v.strip(" .;")) for k, v in re.findall(r"(\d)\s*=\s*([^;,/\n]+)", scale_text or ""))
    return {r: found.get(r, "") for r in range(1, n + 1)}


def main():
    cb = mod.codebook()
    wording = dict(zip(cb["Variable"], cb["Description / item wording"]))
    coding = dict(zip(cb["Variable"], cb["Coding / response scale"]))
    import pandas as pd
    for k, instr in INSTR.items():
        table = f"cordellieri_2026_{k}"
        resp = pd.read_csv(mod.OUT_DIR / f"{table}.csv")
        items = sorted(resp["item"].unique())
        n = int(resp["resp"].max())
        rows = []
        for c in items:
            opt = anchors(str(coding.get(c, "")), n) if k == "scedd" else {r: "" for r in range(1, n + 1)}
            for r in range(1, n + 1):
                rows.append(row(table, f"{table}_1", c, instr, "Italian", r, " ".join(str(wording[c]).split()), option_text=opt[r]))
        print(f"  {table}: scale text = {str(coding.get(items[0]))[:90]!r}")
        write(table, rows)


if __name__ == "__main__":
    main()
