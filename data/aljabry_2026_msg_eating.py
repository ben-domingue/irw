#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0360433
# DOI: 10.1371/journal.pone.0360433
# Paper: Al Jabry LK, Shawwa A, Sarhan Y, Issa R, Abweh O, Qashqeesh H, et al.
#   (2026). Association between habitual MSG consumption and compulsive eating
#   behaviors in university students: A cross-sectional study. PLOS ONE 21(11).
# Data: S2 File (CSV, "Anonymized study dataset"), 558 rows x 47 columns,
#   attached to the article. S1 File is the bilingual questionnaire (PDF),
#   which is where the response-option order below was read from.
# License: CC BY 4.0 (the article's licence covers its SI files).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format).
#
# Palestinian (West Bank) university students, Google Forms survey. Responses
# are stored as option LABELS (English, with the Arabic half lost to '?' in the
# CSV's encoding); each is mapped to a number here, with the order taken from
# the questionnaire PDF (S1 File). FOUR output tables:
#
#   aljabry_2026_msg_ffq -- food frequency questionnaire for 17 MSG-rich foods
#       (the paper says 20; the deposit has 17). 0 = Never, 1 = 1-3 times per
#       month, 2 = 1-2 times per week, 3 = 3-4 times per week, 4 = 5 or more
#       times per week. Item codes are slugs of the food named in each header.
#   aljabry_2026_yfas -- the paper's "Yale Food Addiction Scale 2.0" section:
#       11 symptom items on a 5-point frequency scale (0 = Never, 1 = Once a
#       month or less, 2 = 2-4 times a month, 3 = 2-3 times a week, 4 = 4+
#       times a week) plus the two clinical-significance items (distress,
#       impairment), 0 = No / 1 = Yes. This is an abbreviated adaptation, not
#       the 35-item YFAS 2.0 with its 8-point scale. One table: the two binary
#       items are part of the same section of the same instrument, and a
#       format difference alone is not a reason to split.
#       yfas_01..yfas_11 follow the header order; yfas_distress, yfas_impairment.
#   aljabry_2026_bes -- 7 statement-choice items from the Binge Eating Scale
#       section (the published BES has 16). Each item's options are scored 0 =
#       least severe upward, in the order the questionnaire lists them -- which
#       is least-to-most severe for every item except bes_02, whose options are
#       listed most-severe first. resp_raw carries the English option chosen,
#       because the numeric score is IRW's ordering, not the source's.
#   aljabry_2026_pss4 -- Perceived Stress Scale, 4 items, 0 = Never .. 4 = Very
#       Often (the standard PSS coding). Items 2 and 3 are the positively worded
#       ones; shipped unreversed.
#
# Rows: the deposit has 558 rows and 5 of them are exact duplicates of another
#   row across all 47 columns. The paper's own audit removed "five exact
#   duplicate records" (560 -> 555); its figures do not reconcile with this
#   file's 558, but the duplicates are dropped here on the same rule, leaving
#   553 respondents. No missing cells anywhere in the file.
# Covariates: cov_age (as deposited, a string: "18".."25" and "25+"),
#   cov_gender (Female/Male), cov_year (study year 1-6), cov_height_cm,
#   cov_weight_kg, cov_ed_diagnosis (self-reported prior eating-disorder
#   diagnosis, Yes/No -- an exclusion criterion in the paper, but 84 rows answer
#   Yes and the file is shipped as deposited).
# `id`: none in the deposit; row index after the duplicate drop.
#
# Imputation: none described ("statistical analyses were restricted to
#   questionnaires that had been completed in full"); all values are option
#   labels, so nothing can be fractional.
#
# Item text: SHIPPED for aljabry_2026_msg_ffq only; the other three HELD.
#   Label levels checked: the S2 CSV has no variable/value labels (a plain CSV);
#   its column HEADERS carry the bilingual stems (English kept, Arabic lost to
#   '?') and its cell values are the option labels; S1 File (the bilingual
#   Google Forms questionnaire) carries every stem and option in English and
#   Arabic. Instruments, named from the stems (read against the article's
#   Methods and refs 11-13):
#   - FFQ: study-authored food list + frequency stem; the article cites no FFQ
#     source. Register ALJABRY-FFQ (ship, article CC BY 4.0). Built by
#     automated_finding/itemtext_verification/make_itemtext_aljabry_2026.py
#     (English half of each header; language "English; Arabic").
#   - YFAS: 13 items whose stems are YFAS 2.0 statements, lightly reworded
#     (Gearhardt, Corbin & Brownell 2016; e.g. "I ate certain foods so often or
#     in such large amounts..."; read from memory of the YFAS 2.0, not
#     against a fetched copy).
#     Register YFAS-2 (hold, new 2026-11-09): no redistribution grant located.
#   - BES: 7 of the 16 Gormally et al. (1982) Binge Eating Scale statement
#     groups. Register BES (hold, new 2026-11-09).
#   - PSS-4: Cohen's PSS-4 stems ("unable to control the important things");
#     register PSS (block).
#
# PII: screened over all 47 columns (42 string columns, every one a closed
#   option list; 2 numeric: height, weight). No names, emails, dates, IDs,
#   free text or geography. The questionnaire's free-text final question and
#   the "college" question are not in the deposit.

import os
import re
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
URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0360433.s002")
RAW = os.environ.get("ALJABRY_RAW", "")

FFQ = [("Instant Noodles", "ffq_instant_noodles"),
       ("Potato Chips", "ffq_potato_chips"),
       ("Flavored Crackers", "ffq_flavored_crackers"),
       ("Fast Food Burgers", "ffq_fast_food_burgers"),
       ("Fried Chicken", "ffq_fried_chicken"),
       ("Soy Sauce", "ffq_soy_sauce"),
       ("Salad Dressings", "ffq_salad_dressings"),
       ("Bouillon Cubes", "ffq_bouillon_cubes"),
       ("Seasoning Packets", "ffq_seasoning_packets"),
       ("Pretzels", "ffq_pretzels"),
       ("Chinese Takeout", "ffq_chinese_takeout"),
       ("Condiments", "ffq_condiments"),
       ("Pre-Packaged Deli Meats", "ffq_deli_meats"),
       ("Cheese-Flavored Popcorn", "ffq_cheese_popcorn"),
       ("Pizza", "ffq_pizza"),
       ("Nacho Cheese Sauce", "ffq_nacho_cheese_sauce"),
       ("Tomato Paste", "ffq_tomato_paste")]
FFQ_MAP = {"Never": 0, "1-3 times per month": 1, "1-2 times per week": 2,
           "3-4 times per week": 3, "5 or more times per week": 4}

YFAS_STEMS = ["I ate certain foods so often", "I had such strong urges",
              "I avoided professional, social", "I had withdrawal symptoms",
              "I needed to eat more and more", "I kept eating certain foods",
              "I found that I needed to eat more", "I tried to cut down",
              "I continued to eat the same", "I had such a strong desire",
              "I found that when I started"]
YFAS_MAP = {"Never": 0, "Once a month or less": 1, "2-4 times a month": 2,
            "2-3 times a week": 3, "4+ times a week": 4}
YN_MAP = {"No": 0, "Yes": 1}

# BES options in questionnaire order (S1 File, items 12-18), scored least
# severe = 0. Matched on the English prefix of each option label.
BES = [
    ["I don't feel any guilt", "Sometimes I feel guilty",
     "I feel so guilty or disgusted", "I feel incredibly guilty"],
    ["I feel like I have control", "I have difficulty stopping",
     "I can't seem to stop"],   # listed most-severe first in S1; reversed here
    ["I eat normally", "I tend to eat slightly faster", "I eat much faster"],
    ["I don't eat any more than usual", "Sometimes I eat more",
     "I often eat large amounts"],
    ["I don't eat in secret", "Sometimes I prefer to eat alone",
     "I often eat in secret"],
    ["I never feel driven", "Sometimes I feel driven", "I often feel a strong"],
    ["I rarely think about food", "I sometimes find myself thinking",
     "I am constantly preoccupied"],
]
PSS_STEMS = ["unable to control the important", "confident about your ability",
             "things were going your way", "difficulties were piling up"]
PSS_MAP = {"Never": 0, "Almost Never": 1, "Sometimes": 2, "Fairly Often": 3,
           "Very Often": 4}


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "aljabry_s2.csv")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def english(v):
    """The English half of a bilingual label ('Never       ?????' -> 'Never')."""
    s = re.split(r"\s{3,}|/|\?", str(v))[0]
    return re.sub(r"\s+", " ", s).strip(" .")


def map_col(series, mapping, label):
    eng = series.map(english)
    out = eng.map(mapping)
    bad = sorted(set(eng[out.isna()]))
    assert not bad, (label, bad)
    return out.astype(int)


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s), largest distinct-value count "
          f"{max(df[c].nunique() for c in strings)}")
    assert len(strings) == 45, len(strings)
    # every string column is a closed option list, not free text
    assert max(df[c].nunique() for c in strings) <= 9


def emit(long, name, permitted, extra=()):
    assert len(name) <= 40
    long = long[["id", "item", "resp", *extra] + COV_OUT]
    assert long["resp"].notna().all()
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-"
          f"{long['resp'].max()}")
    return len(long)


COV_OUT = ["cov_age", "cov_gender", "cov_year", "cov_height_cm",
           "cov_weight_kg", "cov_ed_diagnosis"]


def convert():
    raw = pd.read_csv(fetch())
    assert raw.shape == (558, 47), raw.shape
    screen_for_pii(raw)
    assert int(raw.isna().sum().sum()) == 0
    ndup = int(raw.duplicated().sum())
    assert ndup == 5, ndup
    df = raw.drop_duplicates().reset_index(drop=True)
    print(f"dropped {ndup} exact duplicate rows -> {len(df)} respondents")
    cols = list(df.columns)
    df.insert(0, "id", df.index + 1)

    cov = pd.DataFrame({"id": df["id"]})
    cov["cov_age"] = df[cols[0]].astype(str)
    cov["cov_gender"] = df[cols[1]].map(english)
    assert set(cov["cov_gender"]) == {"Female", "Male"}
    cov["cov_year"] = df[cols[2]].str.extract(r"(\d)")[0].astype(int)
    cov["cov_height_cm"] = df[cols[3]]
    cov["cov_weight_kg"] = df[cols[4]]
    cov["cov_ed_diagnosis"] = df[cols[46]].map(english)
    assert set(cov["cov_ed_diagnosis"]) == {"Yes", "No"}
    assert "eating disorder" in cols[46]

    used = set(range(5)) | {46}
    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0

    # FFQ
    wide = {}
    for j, (key, code) in enumerate(FFQ):
        c = cols[5 + j]
        assert key in c, (key, c[-80:])
        wide[code] = map_col(df[c], FFQ_MAP, code)
        used.add(5 + j)
    total += emit(melt(wide, cov), "aljabry_2026_msg_ffq", list(range(0, 5)))

    # YFAS
    wide = {}
    for j, stem in enumerate(YFAS_STEMS):
        c = cols[22 + j]
        assert stem in c, (stem, c[-80:])
        wide[f"yfas_{j + 1:02d}"] = map_col(df[c], YFAS_MAP, stem)
        used.add(22 + j)
    assert cols[33].startswith("The problems I had with these foods caused me significant distress")
    assert cols[34].startswith("The problems I had with these foods interfered")
    wide["yfas_distress"] = map_col(df[cols[33]], YN_MAP, "distress")
    wide["yfas_impairment"] = map_col(df[cols[34]], YN_MAP, "impairment")
    used |= {33, 34}
    perm = {f"yfas_{j:02d}": list(range(0, 5)) for j in range(1, 12)}
    perm.update({"yfas_distress": [0, 1], "yfas_impairment": [0, 1]})
    total += emit(melt(wide, cov), "aljabry_2026_yfas", perm)

    # BES, with resp_raw
    parts, perm = [], {}
    for j, opts in enumerate(BES):
        c = cols[35 + j]
        assert c.startswith("Please select the statement you most relate to.")
        eng = df[c].map(english)
        score = pd.Series(pd.NA, index=df.index, dtype="Int64")
        for k, prefix in enumerate(opts):
            hit = eng.str.startswith(prefix)
            assert hit.any() or k == 0, (j, prefix)
            score[hit] = k
        assert score.notna().all(), (j, sorted(set(eng[score.isna()])))
        code = f"bes_{j + 1:02d}"
        perm[code] = list(range(len(opts)))
        parts.append(pd.DataFrame({"id": df["id"], "item": code,
                                   "resp": score.astype(int), "resp_raw": eng}))
        used.add(35 + j)
    long = pd.concat(parts, ignore_index=True).merge(cov, on="id", how="left")
    total += emit(long, "aljabry_2026_bes", perm, extra=("resp_raw",))

    # PSS-4
    wide = {}
    for j, stem in enumerate(PSS_STEMS):
        c = cols[42 + j]
        assert stem in c, (stem, c[-80:])
        wide[f"pss_{j + 1}"] = map_col(df[c], PSS_MAP, stem)
        used.add(42 + j)
    total += emit(melt(wide, cov), "aljabry_2026_pss4", list(range(0, 5)))

    assert used == set(range(47)), sorted(set(range(47)) - used)
    assert total == len(df) * (17 + 13 + 7 + 4), total
    print(f"4 tables, {total} responses; all 47 source columns accounted for")


def melt(wide, cov):
    w = pd.DataFrame(wide)
    w.insert(0, "id", cov["id"].values)
    long = w.melt(id_vars=["id"], var_name="item", value_name="resp")
    return long.merge(cov, on="id", how="left")


if __name__ == "__main__":
    convert()
