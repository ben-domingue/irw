#!/usr/bin/env python3
"""HELD item text for bando_2026_spaq (10.1371/journal.pone.0358990; OSF
8cgdb, SPAQ-J_Questionnaire.pdf, osf.io/download/zgkrb).

Written to HOLD_DIR (Dropbox), NOT to itemtext_output: the SPAQ is a named
third-party instrument (Bothelius, Jernelov, Fredrikson, McCracken & Kaldo
2015, Sleep 38:1815) and no grant from its originators was located. The
translators' PDF says "This material is distributed under the Creative
Commons Attribution 4.0 International License (CC BY 4.0)", but a
translation is a derivative and the originator's page governs (2026-09-08
ruling); see the SPAQ hold row in itemtext/instrument_rights_register.csv.
Built so that a later clearance is an upload, not a redo.

Mapping: SPAQ1..SPAQ8 = the PDF's items numbered 1..8 (the codebook's own
numbering; the PDF's scoring note, items 1-4 Activity Engagement and 5-8
Willingness, matches the paper). Japanese only, no translation. Options 0-6
as printed (vertical column headers read top to bottom).

Run: RESP_DIR=<dir> RAW=<SPAQ-J pdf> HOLD_DIR=<dir> python3 make_itemtext_bando_2026_spaq.py
"""
import csv
import os
import re
import subprocess
from pathlib import Path

import pandas as pd

RESP_DIR = Path(os.environ["RESP_DIR"])
HOLD_DIR = Path(os.environ.get("HOLD_DIR", "/home/ben/Dropbox/projects/irw/data/itemtext"))
RAW = os.environ["RAW"]
T = "bando_2026_spaq"
INST = "Japanese version of the Sleep Problem Acceptance Questionnaire (SPAQ-J; Bando et al. 2026; original SPAQ, Bothelius et al. 2015)"
INSTR = "以下のそれぞれの記述にどの程度同意するか、選択肢を 1 つ選んでください。次の評価尺度を使って回答してください。"
ITEMS = [
    "状況は変わったものの、私は睡眠問題を抱えながらも普通の生活を送っている。",
    "睡眠問題を抱えながらも、充実した日々を送っている。",
    "睡眠問題を抱えてはいるが、私の生活は順調だ。",
    "睡眠問題を抱えているが、私は自分の人生で決めた道を今進んでいる。",
    "睡眠問題をコントロールすることが最優先だ。",
    "睡眠問題を解決することに集中する必要がある。",
    "自分の睡眠問題と戦い続けることが重要だ。",
    "自分の人生において重要な一歩を踏み出すには、その前に自分の睡眠問題に対する考えや気持ちを変えなければならない。",
]
OPTS = ["全くそう思わない", "ほぼそう思わない", "わずかにそう思う", "部分的にそう思う", "まあまあそう思う", "ほぼそう思う", "完全にそう思う"]


def main():
    # -layout puts each item's wrapped lines on consecutive lines with the
    # option digits 0-6 between them; drop digits and whitespace on both sides.
    # (The vertical option headers are not checked mechanically.)
    txt = subprocess.run(["pdftotext", "-layout", RAW, "-"], capture_output=True, text=True).stdout
    flat = re.sub(r"[\s0-9]+", "", txt)
    for s in ITEMS:
        assert re.sub(r"[\s0-9]+", "", s) in flat, s
    # the instruction block is interleaved with the vertical headers in -layout;
    # the reading-order extraction keeps it whole.
    plain = subprocess.run(["pdftotext", RAW, "-"], capture_output=True, text=True).stdout
    assert re.sub(r"\s+", "", INSTR) in re.sub(r"\s+", "", plain), INSTR
    resp = pd.read_csv(RESP_DIR / f"{T}.csv")
    rows = [{"table": T, "section_id": f"{T}_1", "item": f"SPAQ{i}", "instrument": INST, "language": "Japanese",
             "instructions": INSTR, "section_prompt": "", "item_text": s, "correct_response": "",
             "option_text": OPTS[v], "resp": v}
            for i, s in enumerate(ITEMS, start=1) for v in range(7)]
    assert {r["item"] for r in rows} == set(resp["item"])
    assert {r["resp"] for r in rows} == set(resp["resp"])
    HOLD_DIR.mkdir(parents=True, exist_ok=True)
    with open(HOLD_DIR / f"{T}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"HELD {T}__items.csv -> {HOLD_DIR}: {len(rows)} rows")


if __name__ == "__main__":
    main()
