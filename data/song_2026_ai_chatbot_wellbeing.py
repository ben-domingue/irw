#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/34829139
# DOI: 10.6084/m9.figshare.34829139.v1 (data; no paper DOI on the record)
#   Song, J. (2026). "De-identified Survey Data on AI Chatbot Use and College
#   Students' Subjective Well-being." figshare.
# Data: AI_chatbot_student_wellbeing_deidentified.xlsx (519 Chinese college
#   students x 75 columns; platform metadata already removed by the
#   depositor). Column headers are the Chinese question text, each prefixed
#   with its questionnaire number ("5、我在闲暇时会主动使用AI聊天机器人").
# License: CC BY 4.0 (figshare record).
# Codebook: none (headers carry the wording; no value labels).
#
# Item text: not shipped -- the stems are the headers, but no rights-register
#   rows exist (MSPSS, UCLA-8, GWB); left for an itemtext pass.
#
# Item codes: "q<questionnaire number>", read from each header's own number
#   prefix (asserted), so the code-to-wording tie is not positional.
# Tables (items kept as deposited, no reverse-scoring):
#   song_2026_chatbot_use    q5-q13, AI chatbot use, 1-5
#   song_2026_mspss          q14-q25, Multidimensional Scale of Perceived
#                            Social Support (family/friends/others), 1-7
#   song_2026_loneliness     q28-q35, 8-item loneliness scale (ULS-8 style,
#                            two items reworded to include AI), 1-4
#   song_2026_self_efficacy  q36-q45, General Self-Efficacy Scale adapted to
#                            student life, 1-4
#   song_2026_gwb            q46-q54, General Well-Being Schedule items, 1-6
# Not shipped: chatbot brand and support-source checklists (binary
#   multi-select), and the demographics: gender, single status and year are
#   numeric codes with no labels in the deposit, so they are not carried.
# id = row index.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/70785831"
SPEC = {
    "song_2026_chatbot_use": (range(5, 14), range(1, 6)),
    "song_2026_mspss": (range(14, 26), range(1, 8)),
    "song_2026_loneliness": (range(28, 36), range(1, 5)),
    "song_2026_self_efficacy": (range(36, 46), range(1, 5)),
    "song_2026_gwb": (range(46, 55), range(1, 7)),
}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (519, 75), d.shape
    num = {}
    for c in d.columns:
        m = re.match(r"^(\d+)、", str(c))
        if m and not str(c).startswith(m.group(0) + "("):
            n = int(m.group(1))
            if n not in num:
                num[n] = c
    d["id"] = range(1, len(d) + 1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (qs, vals) in SPEC.items():
        allowed = set(vals)
        cols = {num[q]: f"q{q}" for q in qs}
        x = d[["id"] + list(cols)].rename(columns=cols)
        long = x.melt(id_vars=["id"], var_name="item",
                      value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - allowed, table
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed
                                                for c in cols.values()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
