#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0359401
# DOI: 10.1371/journal.pone.0359401
# Paper: Wasike B (2026). SHOCKING! College professor reveals hidden secrets of
#   news headlines. Can you guess? Examining the efficacy of clickbait
#   detection training and news literacy. PLOS ONE.
# Data: figshare 10.6084/m9.figshare.34077594, one CSV ("PlosONE Data –
#   10.1371:journal.pone.0359401.csv"), 857 rows x 277 columns. No codebook;
#   the article's Methods and its S1 File (instrument appendix) document the
#   measures. SPSS system-missing is written as the string "#NULL!".
# License: CC BY 4.0 (stated on the figshare record itself).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# row 22, refined flag worth_retrying on dup_id_item). There is no duplicate:
# ResponseID is unique over all 857 rows (asserted); the triage flag came from
# its column guess, not from the file.
#
# Design (paper): a Qualtrics-panel sample of US social media users (paper
# N = 858; the deposit has 857, attention-check failures already removed).
# Everyone rated ten headlines (pre-test), then completed the survey measures,
# then was randomised to a clickbait-detection tutorial (test, N = 429) or a
# placebo news-lead tutorial (control, N = 428), then rated ten DIFFERENT
# headlines (post-test).
#
# SIX output tables (one per measure):
#   wasike_2026_news_literacy      NL_1..NL_15, Ashley et al. modified news
#                                  literacy quiz, true/false or multiple choice.
#                                  resp = scored 0/1, resp_raw = option code.
#   wasike_2026_crt                CRT_1..CRT_5, multiple-choice cognitive
#                                  reflection items (4 options). resp = 0/1,
#                                  resp_raw = option code.
#   wasike_2026_tolerance_ambiguity TFA_1..TFA_12, Herman et al. tolerance for
#                                  ambiguity, 1 strongly disagree - 5 strongly
#                                  agree, as answered (the deposit's *_Rev
#                                  reverse-coded copies are dropped).
#   wasike_2026_signal_detection   Signal_1..Signal_10, "how much advertising
#                                  messaging" each of 6 news + 4 advertorial
#                                  headlines contains, 1 none - 5 a lot, as
#                                  answered (*_Rev copies dropped).
#   wasike_2026_clickbait_detection CB1_H1..H10 (pre) + CB2_H1..H10 (post):
#                                  clickbait vs non-clickbait judgment.
#                                  resp = correct 0/1, resp_raw = 1/2 as coded.
#                                  wave 1 = pre-test, 2 = post-test; treat.
#   wasike_2026_clickbait_engagement CB1_Hk_SME1..3 and CB2_Hk_SME1..3: how
#                                  likely to click / read / share, 1 not at all
#                                  likely - 5 very likely, 20 headlines x 3 =
#                                  60 items; wave and treat as above.
#
# Scoring key. The deposit carries its own scored columns (NL_k_Ans, CRT_k_Ans,
#   Hk_Pre, Hk_Post), and for every answered cell each option code maps to
#   exactly one score (asserted below), so the key is read off them. They are
#   NOT shipped as-is: they score "#NULL!" (no answer) as 0 for NL/CRT and,
#   for several headlines, as 1 (e.g. all 17 blank CB1_H1 cells score 1 in
#   H1_Pre). Here a blank answer is a missing response and is dropped, per the
#   data standard. The key that results: headlines H1-H5 are keyed 1 and H6-H10
#   keyed 2 in both phases, i.e. the deposit numbers the five clickbait
#   headlines first (S1 File: 5 clickbait + 5 non-clickbait per phase, listed
#   there in a different, mixed order, so code 1 = "clickbait").
#
# treat: 1 = Test_Group 1 (429, the group that answered the clickbait quiz
#   Training1_*; S1 Table gives test N = 429, control N = 428), 0 = Test_Group
#   2. Assignment happened AFTER the pre-test and the survey measures, so
#   treat is carried only on the two headline tables, where wave separates
#   pre- from post-randomisation responses.
#
# Covariates (codes as deposited, no labels in the deposit): cov_soc_med_use,
#   cov_gender (2 = 443, consistent with the paper's 51.7% female), cov_age,
#   cov_ethnicity (a multi-select string such as "1,3"), cov_region,
#   cov_political, cov_income.
# DROPPED, not items: StartDate/EndDate, ResponseID and transaction_id (panel
#   identifiers; id is the row index), Ethnicity2 (free-text self-described
#   ethnicity), the 26 page timers (Timing*, V154; which headline each timer
#   belongs to is not documented), Attention_1-3 (constant: failures were
#   removed), Tutoria_1/2 (empty), the two training-quiz pairs Training1_*/
#   Training2_* (manipulation check, two items each, different per group),
#   Drive_1/2 (drive for information, only two items), every scored/reverse
#   copy (*_Ans, *_Rev, Hk_Pre/Post) and every composite (totals, averages,
#   SME_*, CB_*_TOT*, Detect_Diff*, *_AVG, Drive_ALL).
#
# Imputation: none stated; every item cell is an integer in its scale or
#   "#NULL!" (asserted).
#
# Item text: HELD. Label levels checked: figshare CSV headers (NL_, CRT_,
#   TFA_, Signal_, H codes; no value labels), the article, and S1 File.
#   Instruments: news literacy = 15 knowledge items of Ashley, Craft, Maksl,
#   Tully & Vraga 2023 (ref 43), modified; wording not deposited (register
#   ASHLEY-NL2023, hold). CRT = Thomson & Oppenheimer's CRT-2 (4 items) + one
#   study-authored item, as multiple choice; not deposited (register CRT-2,
#   hold; the originators' PDF says CC BY 3.0 but Crossref lists CC BY-NC-ND
#   3.0 -- unresolved). TFA = Herman et al. 2010, 12 items; not deposited
#   (TFA-Herman, hold). Signal headlines: publishers' headlines (NBC Select,
#   HuffPost, Wirecutter), not deposited (WASIKE-SIGNAL-HEADLINES, hold).
#   Clickbait headlines: Bena, Rouard & Corneille 2023 + AP/NYT, printed in S1
#   but in an order that does not map to H1-H10, and third-party
#   (WASIKE-CLICKBAIT-HEADLINES, hold) -- unmappable regardless of rights.
#
# PII: with "#NULL!" read as missing, the string columns are StartDate,
#   EndDate, ResponseID, transaction_id, Ethnicity and Ethnicity2.
#   ResponseID (Qualtrics R_ code) and transaction_id (22-char panel token)
#   are platform IDs, replaced by the row index, Ethnicity2 holds 15 short ethnicity
#   self-descriptions and is dropped. No names, emails or locations.

import os
import socket
import sys
import tempfile

import pandas as pd
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/69675252"
RAW = os.environ.get("WASIKE_RAW", "")
N_ROWS = 857

COVS = {"Soc_Med_Use": "cov_soc_med_use", "Gender": "cov_gender",
        "Age": "cov_age", "Ethnicity": "cov_ethnicity", "Region": "cov_region",
        "Political": "cov_political", "Income": "cov_income"}

H = range(1, 11)
NL = [f"NL_{k}" for k in range(1, 16)]
CRT = [f"CRT_{k}" for k in range(1, 6)]
TFA = [f"TFA_{k}" for k in range(1, 13)]
SIG = [f"Signal_{k}" for k in range(1, 11)]
DET = [f"CB{p}_H{k}" for p in (1, 2) for k in H]
ENG = [f"CB{p}_H{k}_SME{q}" for p in (1, 2) for k in H for q in (1, 2, 3)]
# scored copy the deposit carries for each scored item
SCORED = {**{c: c + "_Ans" for c in NL + CRT},
          **{f"CB1_H{k}": f"H{k}_Pre" for k in H},
          **{f"CB2_H{k}": f"H{k}_Post" for k in H}}

DROP_EXACT = {"StartDate", "EndDate", "ResponseID", "transaction_id",
              "Ethnicity2", "Test_Group", "V154", "Attention_1", "Attention_2",
              "Attention_3", "Tutoria_1", "Tutoria_2", "Training1_1",
              "Training1_2", "Training2_1", "Training2_2", "Drive_1",
              "Drive_2", "Drive_ALL", "Drive_AVG"}
DROP_PREFIX = ("Timing", "CB_", "SME_", "Detect_Diff", "Training_")
DROP_SUFFIX = ("_Ans", "_Rev", "_TOT", "_AVG", "_Pre", "_Post")


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "wasike.csv")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def key_from_scored(df, raw, scored):
    """Option code -> score, read off the deposit's scored copy over answered
    cells only; asserts each option maps to exactly one score."""
    ans = df[raw].notna()
    pairs = df.loc[ans, [raw, scored]].drop_duplicates()
    assert pairs[raw].is_unique, (raw, pairs.values.tolist())
    key = dict(zip(pairs[raw].astype(int), pairs[scored].astype(int)))
    assert set(key.values()) == {0, 1} and sum(key.values()) == 1, (raw, key)
    return key


def write(name, long, permitted, extra=()):
    assert len(name) <= 40, name
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(int)
    if "resp_raw" in long:
        long["resp_raw"] = long["resp_raw"].astype(int)
    assert long["id"].nunique() >= 100
    assert not long.duplicated(["id", "item"]).any(), name
    cols = (["id", "item", "resp"] + [c for c in ("resp_raw",) if c in long]
            + list(extra) + list(COVS.values()))
    long = long[cols].sort_values(["id", "item"], kind="stable")
    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
    path = os.path.join(OUT_DIR, name + ".csv")
    assert name not in write.seen, name
    write.seen.add(name)
    long.to_csv(path, index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-"
          f"{long['resp'].max()}")


write.seen = set()


def melt(df, items, extra=()):
    sub = df[["id"] + list(COVS.values()) + list(extra) + items]
    return sub.melt(id_vars=["id"] + list(COVS.values()) + list(extra),
                    value_vars=items, var_name="item", value_name="resp")


def convert():
    df = pd.read_csv(fetch(), na_values=["#NULL!"], keep_default_na=True,
                     dtype={"Ethnicity": str}, low_memory=False)
    assert df.shape == (N_ROWS, 277), df.shape
    assert df["ResponseID"].is_unique
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s): {strings}")
    assert len(df.columns) > 0
    assert set(strings) <= {"StartDate", "EndDate", "ResponseID", "Ethnicity",
                            "Ethnicity2", "transaction_id"}, strings
    assert df["Test_Group"].value_counts().to_dict() == {1.0: 429, 2.0: 428}
    # group 1 answered Training1_* (clickbait quiz), group 2 Training2_*
    assert (df["Training1_1"].notna() == (df["Test_Group"] == 1)).all()

    df = df.copy()  # defragment before adding columns
    df.insert(0, "id", range(1, N_ROWS + 1))
    df = df.rename(columns=COVS)
    df["treat"] = (df["Test_Group"] == 1).astype(int)

    # value domains
    for c in TFA + SIG + ENG:
        assert df[c].dropna().isin(range(1, 6)).all(), c
    for c in DET:
        assert df[c].dropna().isin([1, 2]).all(), c

    os.makedirs(OUT_DIR, exist_ok=True)
    keys = {c: key_from_scored(df, c, s) for c, s in SCORED.items()}
    for k in H:
        want = {1: 1, 2: 0} if k <= 5 else {1: 0, 2: 1}
        assert keys[f"CB1_H{k}"] == want and keys[f"CB2_H{k}"] == want, k

    def scored(items, extra=()):
        long = melt(df, items, extra)
        long["resp_raw"] = long["resp"]
        long["resp"] = [keys[i].get(int(r)) if pd.notna(r) else None
                        for i, r in zip(long["item"], long["resp_raw"])]
        assert long.loc[long["resp_raw"].notna(), "resp"].notna().all()
        return long

    write("wasike_2026_news_literacy", scored(NL), [0, 1])
    write("wasike_2026_crt", scored(CRT), [0, 1])
    write("wasike_2026_tolerance_ambiguity", melt(df, TFA), [1, 2, 3, 4, 5])
    write("wasike_2026_signal_detection", melt(df, SIG), [1, 2, 3, 4, 5])
    det = scored(DET, ("treat",))
    det["wave"] = det["item"].str[2].astype(int)
    write("wasike_2026_clickbait_detection", det, [0, 1], ("wave", "treat"))
    eng = melt(df, ENG, ("treat",))
    eng["wave"] = eng["item"].str[2].astype(int)
    write("wasike_2026_clickbait_engagement", eng, [1, 2, 3, 4, 5],
          ("wave", "treat"))

    # books: every source column is an item, a covariate, or dropped by rule
    used = set(NL + CRT + TFA + SIG + DET + ENG) | set(COVS)
    src = set(pd.read_csv(fetch(), nrows=0).columns)
    rest = {c for c in src - used if c not in DROP_EXACT
            and not c.startswith(DROP_PREFIX) and not c.endswith(DROP_SUFFIX)}
    assert rest == set(), rest
    print(f"6 tables; {len(src - used)} source columns dropped by rule, all "
          f"{len(src)} accounted for")


if __name__ == "__main__":
    convert()
