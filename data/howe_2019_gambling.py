#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0209277
# DOI: 10.1371/journal.pone.0209277
# Paper: Howe, P. D. L., Vargas-Saenz, A., Hulbert, C. A., & Boldero, J. M.
#   (2019). Predictors of gambling and problem gambling in Victoria,
#   Australia. PLOS ONE 14(1): e0209277.
# Data: journal.pone.0209277.s004 (S4 Appendix, "Anonymized data", .sav),
#   3,361 adults from an Australian online panel (The Online Research Unit),
#   state of Victoria, 2016. S3 Appendix (.docx) is the questionnaire.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# EIGHTEEN output tables, every one a block the questionnaire administers as
# its own section with its own response scale. The .sav carries full variable
# labels (the stems) and value labels (the anchors) for every item, so each
# block below is identified from the wording, not from the column name:
#
#   howe_2019_cpgi               S2_1..S2_12, 12 problem-gambling items,
#                                  Never/Sometimes/Most of the time/Almost
#                                  always, recoded 0-3 as the paper scores it.
#                                  S2_1..S2_9 are the nine-item PGSI exactly
#                                  (Ferris & Wynne 2001); S2_10-12 (lied to
#                                  family, spent more than wanted, wanted to
#                                  stop) are the three further problem items
#                                  of the longer CPGI. One section, one scale,
#                                  one construct: shipped together, and the
#                                  description says which nine are the PGSI.
#   howe_2019_approval_{self,family,peers,others}
#                                  S3You/S3Fam/S3Peers/S3Others_1..12: the
#                                  extent YOU (your family / your peers /
#                                  people in general) approve of each of 12
#                                  gambling activities, 1 strongly disapprove
#                                  .. 5 strongly approve.
#   howe_2019_participation_{self,family,peers,others}
#                                  S4You/S4Fam/S4Peers/S4Others_1..12: how
#                                  often YOU (family / peers / people in
#                                  general) did each activity in the last 12
#                                  months, 1 = more than 6 times, 2 = less
#                                  than 6 times, 3 = never.
#   howe_2019_luck_perseverance    S5.1_1..4 (1-5 agreement)
#   howe_2019_overestimate_winning S5.2_1..4 (1-5 agreement)
#   howe_2019_depression           S6_1, S6_5, S6_11, S6_12
#   howe_2019_positive_urgency     S6_2, S6_4, S6_6, S6_8
#   howe_2019_low_esteem           S6_3, S6_7, S6_9, S6_10
#                                  Section 6 interleaves three four-item
#                                  scales on one frequency scale (1 rarely or
#                                  none of the time .. 5 always or most of the
#                                  time). The paper names the three
#                                  constructs and says each has four items;
#                                  the assignment above is from the stems
#                                  ("I feel depressed" / "When I am very
#                                  happy, I can't seem to stop myself ..." /
#                                  "I feel completely worthless").
#   howe_2019_ads_seen, howe_2019_promotions_received,
#   howe_2019_discussed_online, howe_2019_discussed_offline
#                                  S7.1..S7.4_1..12, the 12 activities again,
#                                  1 = more than 6 times, 2 = less than 6
#                                  times, 3 = never.
#
# THE 3-POINT FREQUENCY BLOCKS RUN FROM MOST TO LEAST FREQUENT (1 = more than
# 6 times, 3 = never). They ship as deposited -- the direction is consistent
# within every item, which is all the standard asks -- and every description
# says so.
#
# "DON'T KNOW" (5) ON THE CPGI BLOCK IS DROPPED, NOT A SCALE POINT. The paper:
# "When scoring, all the 'don't know' were skipped, so each question was
# scored on a range of 0-3." Recoded 1-4 -> 0-3 to match.
#
# Dropped: S2_13 and S5.1_5 (the two attention-check items; the deposit's own
# pass/fail flags for them ship as covariates instead), the section-header
# columns (S1, S2, S3You, ... all constant 1), Consent (constant), Status
# (constant 'Good Complete'), Loctn_TEXT and Lang_TEXT (free-text country and
# language of 'Other' respondents -- not PII, but free text), S7.5_1-S7.7_8
# (simulated gambling, a skip-gated block asked of 978 then 192), and S8 (a
# free-text comments box; read in full -- 911 distinct answers, no names,
# emails or addresses).
#
# PII screen: the questionnaire asked for a residential postcode on its first
# page; the deposited file does NOT carry it. Every text column was read
# (printed by screen_for_pii below).
#
# `id` is the row index (the deposit has no respondent id). One file, one
# numbering, so the 18 tables join on id.
#
# Covariates: gender (the deposit's own Male/Female labels; nobody chose
# 'Other'), age in years (18-88), metro vs regional Victoria, born in
# Australia, English main language at home, marital status, and the two
# attention-check outcomes (1 = failed), kept because 502 respondents failed
# the first and a user will want to filter on it.
#
# Item text: SHIPPED for the 12 study-authored activity batteries (approval x4,
# participation x4, ads/promotions/discussed x4) and for the depression block;
# NOT SHIPPED for the CPGI, luck/perseverance, overestimating-winning,
# positive-urgency and low-esteem blocks. Both label levels were read: the
# .sav carries the stem in every variable label and the anchors in every
# value label, so the words are in hand for all 18 tables; what differs is
# rights. The 12 activity batteries are the authors' own survey wording for
# 12 named gambling products. The depression items are a four-item CES-D
# short form (register: CES-D, ship_with_note). The CPGI/PGSI is Ferris &
# Wynne's instrument (register row added, hold); the two erroneous-cognition
# blocks are Raylu & Oei's GRCS wording ("If I concentrate hard enough I
# would be able to influence whether I win", register row added, hold); the
# positive-urgency items are UPPS-P (register: block); the low-esteem items
# match no published scale I could place by verbatim search (register row
# added, hold -- the paper cites them to its ref 57).

import os
import re
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(REPO_ROOT, "automated_finding", "itemtext_output")
RAW = os.environ.get("HOWE_RAW", "S4_Appendix.sav")

N_ROWS = 3361
ITEMTEXT_COLS = ["table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response",
                 "option_text", "resp"]

ACTIVITY = list(range(1, 13))
FREQ3 = {1: "More than 6 times", 2: "Less than 6 times", 3: "Never"}

# table -> (source prefix, item numbers, lo, hi, section-header column,
#           instrument label or None when item text is held, recode)
BLOCKS = {
    "howe_2019_cpgi": ("S2_", ACTIVITY, 0, 3, "S2", None, "cpgi"),
    "howe_2019_approval_self": ("S3You_", ACTIVITY, 1, 5, "S3You", "Approval of 12 gambling activities (own approval)", None),
    "howe_2019_approval_family": ("S3Fam_", ACTIVITY, 1, 5, "S3Fam", "Approval of 12 gambling activities (perceived family approval)", None),
    "howe_2019_approval_peers": ("S3Peers_", ACTIVITY, 1, 5, "S3Peers", "Approval of 12 gambling activities (perceived peer approval)", None),
    "howe_2019_approval_others": ("S3Others_", ACTIVITY, 1, 5, "S3Others", "Approval of 12 gambling activities (perceived approval of people in general)", None),
    "howe_2019_participation_self": ("S4You_", ACTIVITY, 1, 3, "S4You", "Participation in 12 gambling activities, last 12 months (own)", None),
    "howe_2019_participation_family": ("S4Fam_", ACTIVITY, 1, 3, "S4Fam", "Participation in 12 gambling activities, last 12 months (perceived, family)", None),
    "howe_2019_participation_peers": ("S4Peers_", ACTIVITY, 1, 3, "S4Peers", "Participation in 12 gambling activities, last 12 months (perceived, peers)", None),
    "howe_2019_participation_others": ("S4Others_", ACTIVITY, 1, 3, "S4Others", "Participation in 12 gambling activities, last 12 months (perceived, people in general)", None),
    "howe_2019_luck_perseverance": ("S5.1_", [1, 2, 3, 4], 1, 5, "S5.1", None, None),
    "howe_2019_overestimate_winning": ("S5.2_", [1, 2, 3, 4], 1, 5, "S5.2", None, None),
    "howe_2019_depression": ("S6_", [1, 5, 11, 12], 1, 5, "S6", "Depression (four-item CES-D short form, as administered)", None),
    "howe_2019_positive_urgency": ("S6_", [2, 4, 6, 8], 1, 5, "S6", None, None),
    "howe_2019_low_esteem": ("S6_", [3, 7, 9, 10], 1, 5, "S6", None, None),
    "howe_2019_ads_seen": ("S7.1_", ACTIVITY, 1, 3, "S7.1", "Gambling advertisements seen, last year, 12 activities", None),
    "howe_2019_promotions_received": ("S7.2_", ACTIVITY, 1, 3, "S7.2", "Gambling promotions received, last year, 12 activities", None),
    "howe_2019_discussed_online": ("S7.3_", ACTIVITY, 1, 3, "S7.3", "Gambling activities discussed online, last year, 12 activities", None),
    "howe_2019_discussed_offline": ("S7.4_", ACTIVITY, 1, 3, "S7.4", "Gambling activities discussed offline, last year, 12 activities", None),
}

# Section 6 interleaves three scales; the stems settle which item is which.
S6_CHECK = {1: "lonely", 5: "depressed", 11: "sad", 12: "blues",
            2: "great mood", 4: "very happy", 6: "overjoyed", 8: "lose control",
            3: "miserable", 7: "incompetent", 9: "worthless", 10: "values"}


def screen_for_pii(df, meta):
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert txt, "the screen selected nothing"
    for c in txt:
        vals = df[c].astype(str).str.strip()
        vals = vals[vals != ""]
        hits = vals[vals.str.contains(r"@|\b\d{4}\b", regex=True)]
        print(f"  {c}: {vals.nunique()} distinct non-empty; "
              f"{len(hits)} with an @ or a 4-digit run")
        assert not vals.str.contains("@").any(), (c, "email-like value")
    # the postcode asked on page 1 is not in the deposit
    assert not any("post" in c.lower() for c in df.columns)
    assert not any("post" in (meta.column_names_to_labels.get(c) or "").lower()
                   for c in df.columns if c != "Loctn")


def convert():
    df, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    labels = meta.column_names_to_labels
    vlabels = meta.variable_value_labels
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df, meta)
    assert (df["Status"] == "Good Complete").all()
    assert (df["Consent"] == 1).all()

    df["id"] = range(1, N_ROWS + 1)
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_gender": df["Gender"],
        "cov_age": df["Age"].astype(int),
        "cov_location": df["Location"],
        "cov_born_australia": (df["Loctn"] == 1).astype(int),
        "cov_english_at_home": (df["Lang"] == 1).astype(int),
        "cov_marital_status": df["MStat"].astype(int),
        "cov_failed_check_s2": (df["CheckS2"] != "").astype(int),
        "cov_failed_check_s5": (df["CheckS5"] != "").astype(int),
    })
    assert set(cov["cov_gender"]) == {"Male", "Female"}
    assert cov["cov_age"].between(18, 88).all()
    assert set(cov["cov_location"]) == {"Metro", "Regional"}
    assert cov["cov_failed_check_s2"].sum() == 502
    assert cov["cov_failed_check_s5"].sum() == 121
    cov_cols = [c for c in cov.columns if c != "id"]

    for n, kw in S6_CHECK.items():
        assert kw in labels[f"S6_{n}"].lower(), (n, labels[f"S6_{n}"])

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    used = set()
    total = 0
    names = set()
    for name, (pre, nums, lo, hi, header, instrument, recode) in BLOCKS.items():
        assert name not in names and len(name) <= 40, name
        names.add(name)
        cols = [f"{pre}{n}" for n in nums]
        for c in cols:
            assert c in df.columns, c
            assert c not in used, c
            used.add(c)
        assert (df[header] == 1).all(), header
        wide = df[["id"] + cols].copy()
        if recode == "cpgi":
            for c in cols:
                assert vlabels[c][5.0] == "Don't know", c
                assert vlabels[c][1.0] == "Never" and vlabels[c][4.0] == "Almost always"
            dk = int((wide[cols] == 5).sum().sum())
            wide[cols] = wide[cols].where(wide[cols] != 5) - 1
            print(f"{name}: {dk} 'Don't know' cells dropped")
        else:
            assert int(wide[cols].isna().sum().sum()) == 0, (name, "null cells")
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item",
                         value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), (name, sorted(long["resp"].unique()))
        assert set(long["resp"]) == set(range(lo, hi + 1)), (name, sorted(long["resp"].unique()))
        long = long.merge(cov, on="id", how="left")
        long = long[["id", "item", "resp"] + cov_cols]
        assert long["id"].nunique() == N_ROWS or recode == "cpgi"
        assert long["item"].nunique() == len(cols)
        assert not long.duplicated(["id", "item"]).any()

        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={lo}-{hi}")

        if instrument:
            prompt = re.sub(r"^Section\s*\d+\s*-\s*[^:]+:\s*", "", labels[header]).strip()
            rows = []
            for c in cols:
                stem = re.sub(r"\s+", " ", labels[c]).strip()
                stem = re.sub(r"^-\s*", "", stem)   # 'S3You_12' label starts '-Gambling on the Internet?'
                opts = vlabels[c]
                assert sorted(int(k) for k in opts) == list(range(lo, hi + 1)), (c, opts)
                for k in range(lo, hi + 1):
                    rows.append({"table": name, "section_id": f"{name}_1", "item": c,
                                 "instrument": instrument, "instructions": prompt,
                                 "section_prompt": "NA", "item_text": stem,
                                 "correct_response": "NA", "option_text": opts[float(k)],
                                 "resp": k})
            it = pd.DataFrame(rows, columns=ITEMTEXT_COLS)
            assert it["item_text"].str.len().gt(6).all()
            assert set(it["item"]) == set(long["item"]) and set(it["resp"]) == set(long["resp"])
            it.to_csv(os.path.join(ITEMTEXT_DIR, name + "__items.csv"), index=False)
            print(f"  item text: {len(it)} rows, instructions='{prompt[:60]}'")

    # balance the books: every column is shipped, a covariate, or dropped for a printed reason
    dropped = [c for c in df.columns if c not in used and c != "id"]
    print(f"{len(used)} item columns shipped; {len(dropped)} columns not items: {dropped}")
    expected_drop = {"Status", "Location", "AgeCat", "Gender", "CheckS2", "S2_13", "CheckS5",
                     "S5.1_5", "Consent", "S1", "Gndr", "Age", "Loctn", "Loctn_TEXT", "Lang",
                     "Lang_TEXT", "MStat", "S8", "S7.5", "S7.5_1", "S7.6_1", "S7.7_8_TEXT"}
    expected_drop |= {b[4] for b in BLOCKS.values()} | {f"S7.7_{i}" for i in range(1, 9)}
    assert set(dropped) == expected_drop, set(dropped) ^ expected_drop
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
