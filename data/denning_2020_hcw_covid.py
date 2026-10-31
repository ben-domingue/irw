#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0238666
# DOI: 10.1371/journal.pone.0238666
# Paper: Denning, M., Goh, E. T., Tan, B., Kanneganti, A., Almonte, M., Scott,
#   A., Martin, G., Clarke, J., Sounderajah, V., Markar, S., Przybylowicz, J.,
#   Chan, Y. H., Sia, C.-H., Chua, Y. X., Sim, K., Lim, L., Tan, L., Tan, M.,
#   Sharma, V., Ooi, S., Winter Beatty, J., Flott, K., Mason, S., Chidambaram,
#   S., Yalamanchili, S., Zbikowska, G., Fedorowski, J., Dykowska, G., Wells,
#   M., Purkayastha, S., & Kinross, J. (2021). Determinants of burnout and
#   other aspects of psychological well-being in healthcare workers during the
#   Covid-19 pandemic: A multinational cross-sectional study. PLOS ONE 16(4):
#   e0238666.
# Data: journal.pone.0238666.s002 (S2 File, "Anonymised dataset", .csv).
#   3,537 healthcare workers in Singapore (2,503), the UK (765), Poland (232)
#   and elsewhere (37), surveyed 27 March - 16 June 2020.
# License: CC BY 4.0 (the article; the data is its own Supporting Information
#   file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# THREE output tables, one per instrument. The CSV carries every item TWICE:
# once as the respondent's chosen option in words (the column header is the
# full statement) and once as the authors' numeric recode. The words are the
# raw response and are what this script reads; the recodes are used only as
# a check.
#   denning_2020_saq    36 Safety Attitudes Questionnaire statements, 1-5
#                       (Disagree strongly .. Agree strongly). The deposit's
#                       SAQ.N columns are the authors' DICHOTOMISATION
#                       (agree/strongly agree = 1), which the paper uses for
#                       its "percent agreement" scoring; the five-point answer
#                       is what ships. "Not applicable" becomes missing.
#                       The paper says 35 statements; the file holds 36, and
#                       the 36th ("Medical errors are handled appropriately
#                       in this clinical area", position 8, answered by
#                       1,034) is the one without a dichotomised SAQ.N twin.
#                       Codes are SAQ.1..SAQ.36 by header position; the
#                       dichotomy is reproduced from the words on all 35
#                       twins (agree = 1, or disagree = 1 for the three
#                       negatively worded statements 2, 11, 36), asserted.
#   denning_2020_olbi   16 Oldenburg Burnout Inventory items, 1-4 (Strongly
#                       disagree .. Strongly agree), the AGREEMENT direction
#                       on every item. The deposit's OLBI.Q recode is the
#                       SCORED direction: it reverses the eight positively
#                       worded items so that higher = more burnout. Per the
#                       standard, reverse-keyed items are not recoded; the
#                       recode equals v or 5 - v on every cell (asserted),
#                       and the reversed set is printed.
#   denning_2020_hads   14 HADS items, 0-3, from the deposit's HADS.Q recode
#                       (the item-specific anchors differ per item; the recode
#                       is the instrument's own 0-3 scoring, checked against
#                       the words on item 1).
# Option strings arrive in inconsistent case ('Agree strongly' / 'Agree
# Strongly') and with curly vs straight apostrophes; normalised before
# mapping.
#
# `id` is the row index (no respondent id in the file).
#
# Covariates: gender, role (nurse/doctor/AHP/non-clinical; the deposit's
# role.1 code), country, redeployed (yes/no), treated a COVID-19 patient in
# the past week (the deposit's `treat` code 0 no / 1 yes / 2 don't know /
# 3 not applicable -- renamed cov_treated_covid_patient, since `treat` is the
# standard's trial-arm column and this is not one), days worked in the last
# 7, and education (the deposit's edu code). Free-text redeployment
# specialty, ethnicity, seniority and shift-length strings are dropped.
#
# Item text: SHIPPED for the SAQ (register: SAQ short form, ship) from the
# column headers, which are the statements as administered, with the
# five-point anchors. NOT SHIPPED for the HADS (register: block) and the
# OLBI (Demerouti's instrument; register row added, hold). The OLBI and HADS
# wording is in the column headers too, so both are rights holds, not gaps.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(REPO_ROOT, "automated_finding", "itemtext_output")
RAW = os.environ.get("DENNING_RAW", "S2_File.csv")
N_ROWS = 3537
ITEMTEXT_COLS = ["table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response",
                 "option_text", "resp"]

SAQ_MAP = {"disagree strongly": 1, "disagree slightly": 2, "neutral": 3,
           "agree slightly": 4, "agree strongly": 5, "not applicable": None}
SAQ_OPTS = {1: "Disagree strongly", 2: "Disagree slightly", 3: "Neutral",
            4: "Agree slightly", 5: "Agree strongly"}
OLBI_MAP = {"strongly disagree": 1, "disagree": 2, "agree": 3, "strongly agree": 4}


def norm(s):
    return s.astype(str).str.strip().str.lower().str.replace("’", "'", regex=False).where(s.notna())


def convert():
    df = pd.read_csv(RAW)
    df = df[[c for c in df.columns if not c.startswith("Unnamed")]]
    assert len(df) == N_ROWS, len(df)
    cols = list(df.columns)
    # the word columns: the SAQ statements run from 'Nurse input ...' to the
    # statement before 'I always find new and interesting aspects of my work.'
    # (OLBI item 1); the OLBI through 'When I work, I usually feel energized.';
    # the HADS through 'I can enjoy a good book or radio or TV program'
    i_saq = cols.index("Nurse input is well received in this clinical area.")
    i_olbi = cols.index("I always find new and interesting aspects of my work.")
    i_hads = cols.index("I feel tense or 'wound up'")
    i_end = cols.index("I can enjoy a good book or radio or TV program") + 1
    saq_txt, olbi_txt, hads_txt = cols[i_saq:i_olbi], cols[i_olbi:i_hads], cols[i_hads:i_end]
    assert len(saq_txt) == 36 and len(olbi_txt) == 16 and len(hads_txt) == 14, (len(saq_txt), len(olbi_txt), len(hads_txt))

    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text")
    free = [c for c in txt if c not in saq_txt + olbi_txt + hads_txt]
    print(f"  free-text/categorical columns read: {free}")
    for c in free:
        assert not df[c].astype(str).str.contains("@").any(), c
    df["id"] = range(1, N_ROWS + 1)

    # --- SAQ: words -> 1-5. Statement k in the header order is SAQ.k: the
    # deposit's dichotomy reproduces exactly from the words on all 32
    # positively worded statements that have a twin (agree/strongly agree =
    # 1) and on the three negatively worded ones (2, 11, 36: disagree = 1),
    # and statement 8 is the one with no SAQ.8 twin. All asserted.
    saq_num = [c for c in cols if re.fullmatch(r"SAQ\.\d+", c)]
    assert len(saq_num) == 35 and "SAQ.8" not in saq_num
    NEG = {2, 11, 36}
    saq = pd.DataFrame({"id": df["id"]})
    text_of = {}
    for k, stmt in enumerate(saq_txt, start=1):
        w = norm(df[stmt])
        assert set(w.dropna()) <= set(SAQ_MAP), (stmt, set(w.dropna()))
        v = w.map(SAQ_MAP)
        code = f"SAQ.{k}"
        if k != 8:
            dich = ((v <= 2) if k in NEG else (v >= 4)).astype(float).where(v.notna())
            ok = dich.notna() & df[code].notna()
            agree = (dich[ok] == df.loc[ok, code]).mean()
            assert ok.sum() > 1000 and agree > 0.995, (code, stmt, agree)
        saq[code] = v
        text_of[code] = stmt
    saq_cols = [f"SAQ.{k}" for k in range(1, 37)]
    print("SAQ: 36 statements tied to SAQ.1..36 by position, dichotomy reproduced on the 35 with a twin")

    # --- OLBI: words -> 1-4, must equal the deposit's recode
    olbi = pd.DataFrame({"id": df["id"]})
    flipped = []
    for k, stmt in enumerate(olbi_txt, start=1):
        v = norm(df[stmt]).map(OLBI_MAP)
        assert v.notna().all(), (k, stmt)
        same, rev = (v == df[f"OLBI.Q{k}"]).all(), ((5 - v) == df[f"OLBI.Q{k}"]).all()
        assert same or rev, (k, stmt)
        if rev:
            flipped.append(k)
        olbi[f"OLBI.Q{k}"] = v
    print(f"OLBI: raw agreement direction ships; the deposit's recode reverses items {flipped}")
    assert len(flipped) == 8, flipped
    olbi_cols = [f"OLBI.Q{k}" for k in range(1, 17)]

    # --- HADS: the deposit's 0-3 recode; words checked on item 1
    hads_cols = [f"HADS.Q{k}" for k in range(1, 15)]
    hads = df[["id"] + hads_cols].copy()
    w1 = norm(df[hads_txt[0]]).map({"not at all": 0, "from time to time, occasionally": 1,
                                    "a lot of the time": 2, "most of the time": 3})
    ok = w1.notna() & hads["HADS.Q1"].notna()
    assert (w1[ok] == hads.loc[ok, "HADS.Q1"]).all()

    cov = pd.DataFrame({
        "id": df["id"],
        "cov_gender": df["gender"].where(df["gender"].isin(["Female", "Male", "Non-binary"])),
        "cov_role": df["role.1"].map({0: "doctor", 1: "nurse", 2: "AHP", 3: "non_clinical"}),
        "cov_country": df["Country"],
        "cov_redeployed": df["redeployed"].astype(int),
        "cov_treated_covid_patient": df["treat"].map({0: "no", 1: "yes", 2: "dont_know", 3: "not_applicable"}),
        "cov_days_worked_last_week": df["days"].astype("Int64"),
        "cov_education": df["edu"].astype("Int64"),
    })
    assert (df["role.1"].map({0: "Doctor", 1: "Nurse", 2: "AHP", 3: "Non-clinical"}) == df["role"]).mean() > 0.99
    assert cov["cov_country"].value_counts().to_dict() == {"Singapore": 2503, "UK": 765, "Poland": 232, "Other": 37}
    cov_cols = [c for c in cov.columns if c != "id"]

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    total = 0
    for name, wide, icols, lo, hi in [("denning_2020_saq", saq, saq_cols, 1, 5),
                                      ("denning_2020_olbi", olbi, olbi_cols, 1, 4),
                                      ("denning_2020_hads", hads, hads_cols, 0, 3)]:
        long = wide.melt(id_vars=["id"], value_vars=icols, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(range(lo, hi + 1)), (name, sorted(long["resp"].unique()))
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["item"].nunique() == len(icols) and not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in icols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} resp={lo}-{hi}")
        if name == "denning_2020_saq":
            rows = [{"table": name, "section_id": f"{name}_1", "item": c,
                     "instrument": "Safety Attitudes Questionnaire (SAQ), 36 statements as administered",
                     "instructions": "NA", "section_prompt": "NA", "item_text": text_of[c].strip(),
                     "correct_response": "NA", "option_text": SAQ_OPTS[k], "resp": k}
                    for c in icols for k in range(1, 6)]
            it = pd.DataFrame(rows, columns=ITEMTEXT_COLS)
            assert set(it["item"]) == set(long["item"]) and set(it["resp"]) == set(long["resp"])
            it.to_csv(os.path.join(ITEMTEXT_DIR, name + "__items.csv"), index=False)
            print(f"  item text: {len(it)} rows")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
