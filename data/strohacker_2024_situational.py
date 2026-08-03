#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307369
# S1 Data: https://doi.org/10.1371/journal.pone.0307369.s002
# DOI: 10.1371/journal.pone.0307369
#
# Strohacker, Sudeck, Ibrahim & Keegan (2024), "Exploring person-specific
# associations of situational motivation and readiness with leisure-time
# physical activity", PLOS ONE. Event-contingent EMA design: N=22
# participants, 519 pre-/post leisure-time-physical-activity (LTPA) session
# reports over 10 weeks.
#
# The S1 Data workbook's "LTPA Only_For Analysis" sheet is a flat table
# (one row per session report) once the embedded codebook/descriptor row
# (row 0, e.g. "1=strongly disagree...5=strongly agree") is skipped -- this
# turned out to be a simple header-offset issue, not the deep multi-step
# reconstruction the earlier triage note anticipated. It contains two
# distinct pre-activity multi-item report modules (identified by column
# prefix), each shipped here as its own scale/file per "one scale per file":
#   - BMZI_* (11 items): a situational-motive subset of the revised Bernese
#     motive and goal inventory in exercise and sport, 5-point Likert
#     (1 = strongly agree ... 5 = strongly disagree; direction not recoded).
#   - ARMS_* (10 items): a situational-readiness subset of the Acute
#     Readiness Monitoring Scale, 7-point scale (0 = does not apply at all
#     ... 6 = fully applies).
# Aggregate columns (Physical_Readiness, Physical_Fatigue, Cognitive_
# Readiness, Cognitive_Fatigue, ThreatChallenge_Readiness -- each an explicit
# sum of two of the above items per the descriptor row) and the two
# post-activity single items (PA_RPE, PA_FeelingScale) are excluded: the
# former are composites, the latter are single-item measures, not part of
# either multi-item module.
#
# Rows are grouped contiguously by StudyID in file order (verified), so a
# per-person sequential session counter is used as `wave` -- duplicate
# id+item pairs across sessions are expected and valid per the data
# standard's repeated-measures guidance.

import io
import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file?"
           "type=supplementary&id=10.1371/journal.pone.0307369.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "strohacker_2024_bmzi_motive": ("BMZI_", 1, 5),
    "strohacker_2024_arms_readiness": ("ARMS_", 0, 6),
}


def convert():
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    xl = pd.ExcelFile(io.BytesIO(r.content))
    raw = pd.read_excel(xl, sheet_name="LTPA Only_For Analysis", header=0)

    # Row 0 is an embedded codebook/descriptor row, not data -- skip it.
    data = raw.iloc[1:].reset_index(drop=True)
    data = data.dropna(subset=["StudyID"]).reset_index(drop=True)

    data["id"] = data["StudyID"].astype(int)
    # Per-person sequential session index (rows are grouped contiguously by
    # StudyID in source order).
    data["wave"] = data.groupby("id").cumcount() + 1

    for out_name, (prefix, lo, hi) in SCALES.items():
        item_cols = [c for c in data.columns if c.startswith(prefix)]
        df = data[["id", "wave"] + item_cols].copy()
        long = df.melt(id_vars=["id", "wave"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert long["resp"].between(lo, hi).all(), f"{out_name}: out-of-range value"

        out_cols = ["id", "item", "resp", "wave"]
        long = long[out_cols]

        csv_path = os.path.join(OUT_DIR, out_name + ".csv")
        long.to_csv(csv_path, index=False)
        try:
            import pyreadr
            pyreadr.write_rdata(os.path.join(OUT_DIR, out_name + ".RData"),
                                 long, df_name="d")
        except ImportError:
            long.to_pickle(os.path.join(OUT_DIR, out_name + ".rdata_fallback.pkl"))

        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
