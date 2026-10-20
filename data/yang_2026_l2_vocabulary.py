#!/usr/bin/env python3

# Source: https://doi.org/10.1371/journal.pone.0356062
# DOI: 10.1371/journal.pone.0356062
#   Yang, C., Yu, X., & Li, H. (2026). Relationship among motivation,
#   vocabulary learning strategies and the breadth of vocabulary knowledge:
#   A structural equation modeling study on second language learning.
#   PLOS One, 20(9). Published 2026-09-22.
# Data: Supporting Information file "pone.0356062.s001.xlsx"
#   (10.1371/journal.pone.0356062.s001), single sheet "原始" ("raw"),
#   275 Chinese university EFL learners x 228 columns.
# License: CC BY 4.0 (verified on the PLOS article page and in Crossref's
#   license record for the DOI, 2026-10-20).
#
# Item text: IN HAND but NOT shipped here, pending rights rulings. Both
#   levels checked -- this is an .xlsx, so there is no variable-label level;
#   the column headers themselves ARE the full item wording, for every item
#   in both tables ("I imagine myself using English in my future career.",
#   "50, BACTERIUM: They didn't find a single bacterium." plus its four
#   option strings). So extraction is solved and costs nothing to redo; the
#   blocker is rights, not text, and both instruments are third-party:
#     - the 140 vocabulary items are the Vocabulary Size Test (Nation &
#       Beglar, 2007) -- the target words, example sentences and all four
#       distractors per item are that instrument's own wording, reproduced
#       in the deposit. The published VST is where this needs a ruling.
#     - the 81 Likert items are adapted L2 Motivational Self System and
#       vocabulary-learning-strategy scales (the ideal-L2-self and
#       ought-to-L2-self blocks read as Taguchi/Dornyei-lineage wording).
#       They need identification from the stems and a register row each.
#   Neither instrument has a row in itemtext/instrument_rights_register.csv,
#   so nothing would have warned, and silence does not ship. Logged rather
#   than shipped so the batch is not stalled on two rulings.
#
# TWO tables -- two distinct instruments, two different response formats,
# administered to the same 275 respondents:
#   yang_2026_l2_motivation  -- 81 Likert items, 5-point frequency scale
#   yang_2026_vocabulary_size -- 140 four-option multiple-choice items,
#                                scored 0/1 against a derived-and-verified key
#
# id: the deposit's "No." column, 1..275, one row per respondent. A plain
#   row index assigned by the depositors, not PII, and shared across both
#   tables so a respondent links between them.
#
# resp (Likert): the file stores the chosen anchor as text. The five anchors
#   carry their own percentages, which fixes the order and the direction:
#   Never(0%)=1 < Seldom(20%)=2 < Sometimes(40%-50%)=3 < Often(60%-70%)=4
#   < Usually(80%)=5. Mapped to 1-5 rather than left as strings.
#
# resp (vocabulary): the file stores the chosen OPTION TEXT ("c. looked
#   at"), which is nominal and cannot ship as resp. It is scored 0/1 against
#   an answer key DERIVED from the responses and then VERIFIED exactly: the
#   deposit also ships its own "Total Score " column (22-135 over 140
#   items), and the derived key reproduces that column exactly -- 275 of 275
#   respondents, maximum absolute difference 0. That is a falsifiable check
#   on all 140 items at once, not a plausibility argument, which is the only
#   reason this table ships at all. The key is derived here rather than
#   hardcoded so the check runs on every execution; if the deposit's file
#   ever changes, this script fails rather than shipping a silent mis-scoring.
#   The script asserts the exact reproduction and refuses to write otherwise.
#
# Dropped: "Total Score " -- a composite of the 140 vocabulary items, not a
#   response. It is used here only as the verification target described above.
#
# Covariates: the deposit's five background questions, carried on both
#   tables. Three of them ("Which region...", "What field of study...",
#   "What is your grade?") contain values where the answer string is
#   repeated two or three times ("Rural areaRural area"), an export artifact
#   of the survey tool; the repetition is collapsed rather than read as a
#   distinct category. cov_gaokao_english is the self-reported national
#   college-entrance-exam English score, stored as text and coerced to a
#   number.
#
# PII: none. 226 string-dtype columns were examined (selected with
#   pd.api.types.is_string_dtype, never dtype == object, and the count is
#   asserted non-zero below so an empty selection cannot report clean).
#   There is no name, email, date of birth, postal code, phone number or
#   free-text box in the file; every string column is either an item's chosen
#   option or one of the five background answers. "No." is a row index.
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s5"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "plos" / "pone.0356062"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SI_URL = "https://doi.org/10.1371/journal.pone.0356062.s001"
FNAME = "pone.0356062.s001.xlsx"
SHEET = "原始"

ID_COL = "No."
TOTAL_COL = "Total Score "
COVS = {
    "What is your gender?": "cov_gender",
    "What is your grade?": "cov_grade",
    "Which region is your high school located in? ": "cov_high_school_region",
    "What was your Gaokao English score? ( ) Please fill in the box below. ":
        "cov_gaokao_english",
    "What field of study is your current major in? ( )": "cov_major",
}

LIKERT = {"Never（0%）": 1, "Seldom（20%）": 2, "Sometimes（40%-50%）": 3,
          "Often（60%-70%）": 4, "Usually（80%）": 5}
LIKERT_SCALE = set(LIKERT.values())
VST_SCALE = {0, 1}

N_RESP, N_LIKERT, N_VST = 275, 81, 140
VST_HEADER = re.compile(r"^\s*(\d+)\s*、\s*([A-Za-z'\-]+)\s*:")


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(SI_URL, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def collapse_repeat(value):
    """Undo the survey tool's "Rural areaRural area" export artifact."""
    if not isinstance(value, str):
        return value
    s = value.strip()
    for k in (4, 3, 2):
        if len(s) % k == 0:
            unit = s[: len(s) // k]
            if unit * k == s:
                return unit
    return s


def vst_code(header: str) -> str:
    m = VST_HEADER.match(str(header))
    assert m, f"unparseable vocabulary header: {header!r}"
    n, word = int(m.group(1)), m.group(2).lower()
    return f"v{n:03d}_{word}"


def derive_vst_key(df, vst_cols):
    """Answer key, derived from the responses and checked against the
    deposit's own Total Score column. Returns the key; the caller asserts."""
    total = df[TOTAL_COL].to_numpy()
    opts = {c: list(df[c].dropna().unique()) for c in vst_cols}
    ind = {c: {o: (df[c] == o).to_numpy().astype(int) for o in opts[c]}
           for c in vst_cols}
    # Start from the option most correlated with the total score, then
    # coordinate-descend on the absolute residual until it is zero.
    key = {c: max(opts[c], key=lambda o: np.corrcoef(ind[c][o], total)[0, 1])
           for c in vst_cols}
    res = sum(ind[c][key[c]] for c in vst_cols) - total
    for _ in range(50):
        if not np.any(res):
            break
        moved = False
        for c in vst_cols:
            best, best_v = key[c], np.abs(res).sum()
            for o in opts[c]:
                if o == key[c]:
                    continue
                v = np.abs(res - ind[c][key[c]] + ind[c][o]).sum()
                if v < best_v:
                    best, best_v = o, v
            if best != key[c]:
                res = res - ind[c][key[c]] + ind[c][best]
                key[c] = best
                moved = True
        if not moved:
            break
    return key


def finish(t, table, cov_cols, permitted):
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert t["id"].nunique() == N_RESP, t["id"].nunique()
    checks = run_qc(t, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=table, profile="upload",
                                         context={"permitted_values": permitted})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"{table}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} "
          f"resp={t['resp'].min()}-{t['resp'].max()}")
    return t


def main():
    df = pd.read_excel(fetch(), sheet_name=SHEET)
    assert len(df) == N_RESP, len(df)
    assert df[ID_COL].nunique() == N_RESP, "No. is not unique per respondent"

    # PII screen -- print the denominator so an empty selection is visible.
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] string-dtype columns examined: {len(text_cols)}")
    assert len(text_cols) > 0, "PII screen selected no columns"

    likert_cols, vst_cols = [], []
    for c in df.columns:
        if c in (ID_COL, TOTAL_COL) or c in COVS:
            continue
        vals = set(df[c].dropna().astype(str).unique())
        if vals and vals <= set(LIKERT):
            likert_cols.append(c)
        else:
            vst_cols.append(c)
    assert len(likert_cols) == N_LIKERT, len(likert_cols)
    assert len(vst_cols) == N_VST, len(vst_cols)

    df = df.rename(columns={ID_COL: "id", **COVS})
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        df[cov] = df[cov].map(collapse_repeat)
    df["cov_gaokao_english"] = pd.to_numeric(df["cov_gaokao_english"],
                                             errors="coerce")
    for cov in ("cov_high_school_region", "cov_major", "cov_grade"):
        assert df[cov].nunique() <= 4, (cov, sorted(df[cov].dropna().unique()))

    # --- Table 1: the 81-item Likert battery.
    m = (df[["id", *cov_cols, *likert_cols]]
         .melt(id_vars=["id", *cov_cols], value_vars=likert_cols,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    order = {c: i for i, c in enumerate(likert_cols)}
    m["item"] = m["item"].map(lambda c: f"m{order[c] + 1:03d}")
    m["resp"] = m["resp"].map(LIKERT)
    assert m["resp"].notna().all(), "unmapped Likert anchor"
    m["resp"] = m["resp"].astype(int)
    assert set(m["resp"]) <= LIKERT_SCALE, sorted(set(m["resp"]))
    finish(m, "yang_2026_l2_motivation", cov_cols, LIKERT_SCALE)

    # --- Table 2: the 140-item Vocabulary Size Test, scored 0/1.
    key = derive_vst_key(df, vst_cols)
    scored = sum((df[c] == key[c]).astype(int) for c in vst_cols)
    exact = int((scored == df[TOTAL_COL]).sum())
    print(f"[key] derived answer key reproduces the deposit's Total Score "
          f"for {exact}/{N_RESP} respondents "
          f"(max abs diff {int((scored - df[TOTAL_COL]).abs().max())})")
    assert exact == N_RESP, (
        "the derived answer key does NOT reproduce the deposit's own Total "
        "Score column exactly; refusing to ship a scored table on an "
        f"unverified key ({exact}/{N_RESP} matched)")

    v = df[["id", *cov_cols, *vst_cols]].copy()
    for c in vst_cols:
        v[c] = (v[c] == key[c]).astype(int)
    v = (v.melt(id_vars=["id", *cov_cols], value_vars=vst_cols,
                var_name="item", value_name="resp")
          .dropna(subset=["resp"]))
    v["item"] = v["item"].map(vst_code)
    assert v["item"].nunique() == N_VST, v["item"].nunique()
    v["resp"] = v["resp"].astype(int)
    assert set(v["resp"]) <= VST_SCALE, sorted(set(v["resp"]))
    finish(v, "yang_2026_vocabulary_size", cov_cols, VST_SCALE)


if __name__ == "__main__":
    main()
