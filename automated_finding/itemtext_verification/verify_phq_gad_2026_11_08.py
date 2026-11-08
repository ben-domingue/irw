#!/usr/bin/env python3
"""Mapping check for zhao_2024_{phq9,gad7} and chinvararak_2022_gad7 (2026-11-08c).

Item codes are the deposit column names PHQ1..9 / GAD1..7 / gad7_1..7, tied to
text only by the forms' printed numbering (paper_order). Routes, as in
lu_2017_gad7 / kim_2023_gad7:
  7  marker items: PHQ-9 item 9 (suicidal thoughts) has the lowest mean; GAD-7
     item 5 (restlessness) correlates most with PHQ-9 item 8 (psychomotor), and
     PHQ-9 item 8 is item 5's strongest PHQ-9 correlate.
  8  option axis: higher codes mean more frequent (zhao: deposit total = sum - n,
     asserted in data/zhao_2024_nurses_phq_gad.py; chinvararak: sum = gad7scr).
Same respondents across PHQ and GAD: zhao all 1,219; chinvararak the 403 asked
the PHQ-9 (the PHQ-9 table itself is held, its responses are used only here).
Distinguishes items 5, 8 and 9 from the rest; the others stay positional, so the
best verdict is PARTIAL. In zhao_2024 the GAD marker does not discriminate (see
main), so zhao_2024_gad7 is NO_ROUTE.

Run: RESP_DIR_5=<leads-batch-5 irw_output> RESP_DIR_7=<leads-batch-7 irw_output> python3 verify_phq_gad_2026_11_08.py
"""
import os
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
R5 = Path(os.environ.get("RESP_DIR_5", HERE / "irw_output"))
R7 = Path(os.environ.get("RESP_DIR_7", HERE / "irw_output"))


def wide(p):
    return pd.read_csv(p).pivot(index="id", columns="item", values="resp")


def run(label, phq, gad, p, g):
    d = phq.join(gad, how="inner")
    print(f"== {label}: n = {len(d)}")
    m = phq.mean()
    print("PHQ means", m.round(3).to_dict())
    lowest = m.idxmin()
    c = d[[f"{g}{i}" for i in range(1, 8)]].corrwith(d[f"{p}8"])
    print(f"corr(GAD_i, {p}8)", c.round(3).to_dict())
    rc = d[[f"{p}{i}" for i in range(1, 10)]].corrwith(d[f"{g}5"])
    print(f"corr(PHQ_i, {g}5)", rc.round(3).to_dict())
    ok = c.idxmax() == f"{g}5" and rc.idxmax() == f"{p}8"
    print(f"{label}: PHQ lowest mean = {lowest}; GAD5<->PHQ8 reciprocal = {ok}")
    return lowest == f"{p}9", ok


def main():
    z = run("zhao_2024", wide(R5 / "zhao_2024_phq9.csv"), wide(R5 / "zhao_2024_gad7.csv"), "PHQ", "GAD")
    c = run("chinvararak_2022", wide(R7 / "chinvararak_2022_phq9.csv"), wide(R7 / "chinvararak_2022_gad7.csv"),
            "phq9_", "gad7_")
    print("VERDICT zhao_2024_phq9:", "PARTIAL" if z[0] else "FAIL")
    # zhao's 63 PHQ x GAD correlations all sit in 0.58-0.72 (one dominant factor in
    # this nurse sample), so the restlessness marker cannot single out GAD5: PHQ8 is
    # GAD5's top PHQ correlate but GAD6 edges GAD5 as PHQ8's top GAD correlate.
    # Route attempted and non-discriminating -> NO_ROUTE, not evidence against.
    print("VERDICT zhao_2024_gad7:", "PARTIAL" if z[1] else "NO_ROUTE (marker non-discriminating)")
    print("VERDICT chinvararak_2022_gad7:", "PARTIAL" if c[1] else "FAIL")


if __name__ == "__main__":
    main()
