#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/h5ydkf3mjt/1
# DOI: 10.17632/h5ydkf3mjt.1 (data)
#   He J (2026). Hand Hygiene Promotion in Primary Schools Using a KAP-Emotional Design Framework:
#   A Cluster-Randomized Controlled Feasibility Study [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley Data)
# Data: "Hand-washing timing questionnaire score.xlsx" -- a cartoon-based questionnaire on WHEN to
#   wash hands, 12 situations scored 0/1, at T0 (baseline) and T1 (after the one-week "Fun Hand
#   Hygiene Workshop"); 253 primary-school children, ids T101.. (intervention, 125) and C.. (control,
#   128). Stored score columns, not raw answers: several situations are distractors (e.g. "after
#   singing", "before watching television") where the correct answer is presumably "no", so 1 =
#   correct. Each wave's "Total score (0-12)" equals the item sum in all but 6 complete rows (5 at T0,
#   1 at T1; each off by 1, the hand-entered total), so the items are taken as authoritative.
#
# Table: he_2026_handwashing_timing -- item = the situation as printed in the header, snake_cased
#   with a trailing "_time" dropped ("before toilet time" -> before_toilet, "after play time" ->
#   after_play; a bare "time" reads as a covariate) and the header's "toliet" corrected to toilet;
#   wave = 0 (T0) / 1 (T1); treat = 1 for T ids, 0 for C ids.
#   Blank cells (13 children at T0, 18 at T1) are not rows. Totals not shipped.
# Not built: "Handwashing skill score.xlsx" (50 children, below the 100 floor).
# id: the questionnaire number (T101, C342), kept -- it carries no information beyond the arm.
# Item text: not shipped -- the situations are in the headers but the instrument is a cartoon
#   questionnaire (pictures) whose prompt wording and keyed answers are not in the deposit.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/h5ydkf3mjt/files/"
       "9228ee1c-865c-47be-b9a6-ca1498b0cc26/file_downloaded")


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), header=None)
    head = list(raw.iloc[1])
    assert raw.iloc[0, 1] == "T0" and raw.iloc[0, 14] == "T1"
    assert head[13].startswith("Total") and head[26].startswith("Total")
    d = raw.iloc[2:].reset_index(drop=True)
    assert d[0].is_unique and len(d) == 253
    rows = []
    for w, cols in ((0, range(1, 13)), (1, range(14, 26))):
        x = d[list(cols)].apply(pd.to_numeric)
        tot = pd.to_numeric(d[cols[-1] + 1])
        ok = x.notna().all(axis=1)
        bad = ok & (x.sum(axis=1) != tot)
        print(f"wave {w}: {bad.sum()} stored totals differ from the item sum")
        assert bad.sum() <= 6
        for c in cols:
            item = re.sub(r"[^a-z0-9]+", "_", head[c].strip().lower()).strip("_")
            item = re.sub(r"_time$", "", item).replace("toliet", "toilet")
            rows.append(pd.DataFrame({"id": d[0], "item": item, "resp": x[c], "wave": w}))
    t = pd.concat(rows).dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].isin([0, 1]).all()
    t["treat"] = t["id"].str[0].map({"T": 1, "C": 0})
    assert t["treat"].notna().all() and t["item"].nunique() == 12
    assert not t.duplicated(["id", "item", "wave"]).any()
    t = t[["id", "item", "resp", "wave", "treat"]].sort_values(["id", "wave", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / "he_2026_handwashing_timing.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
