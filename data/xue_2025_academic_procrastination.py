#!/usr/bin/env python3
"""Xue et al. (2025), PLOS One -- academic pressure, procrastination and coping.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0338956
DOI: 10.1371/journal.pone.0338956
Data: S1 Data (journal.pone.0338956.s001, XLSX)
License: CC BY 4.0
Item text: shipped (S3 File, "Constructs and items", lists all 59 stems with
    the AP/AS/CSS codes used here -- but in English only, for a survey
    administered in Chinese; see "Item text" below)

579 valid responses from 600 students stratified across five universities in
Hebei Province, China. One questionnaire carrying three published Chinese
instruments, so it splits into three tables:

xue_2025_academic_procrastination  19 items  AP1-AP19    1-5
xue_2025_academic_stress           20 items  AS1-AS20    1-5
xue_2025_coping_style              20 items  CSS1-CSS20  1-4

The spreadsheet numbers the item blocks Q8_1-Q8_19, Q9_1-Q9_20 and
Q10_1-Q10_20. They are renamed to the AP/AS/CSS codes that S3 File uses, in
order, so `item` matches the identifiers the source's own instrument listing
carries rather than a positional Qn_m label.

Response coding
---------------
The Methods say "Responses were recorded on a 5-point Likert scale (1 =
Strongly Disagree, 5 = Strongly Agree)". That holds for the procrastination
and stress blocks, whose values run 1-5. It does **not** hold for the coping
block: every one of the 20 CSS columns tops out at 4 across all 579
respondents, and Xie's Simplified Coping Style Questionnaire is natively a
four-point frequency scale, so the block is shipped as the 1-4 it is rather
than forced onto the paper's blanket 5-point claim. Only the two endpoint
anchors are named anywhere for AP/AS, and no anchors at all for CSS, so the
unlabelled points are left without option text rather than invented.

The file has no missing cells and no out-of-range values in any of the 59 item
columns. The paper describes no imputation (text searched for "imput",
"missing data", "MICE", "LOCF", "mean substitution" -- no hits) and reports
579 valid of 600 collected, i.e. invalid responses were dropped, not filled.

The spreadsheet's banner row labels the Q10 block "Negative coping style", but
the paper and S3 File both describe the full 20-item SCSQ, which covers
adaptive coping (CSS1-CSS12) as well as maladaptive (CSS13-CSS20). The table is
named for the whole instrument accordingly.

Covariates: none shipped. Columns Q1-Q7 are demographics, but neither the
deposit, the paper, nor S3 File says what any of them asks or how its levels
are coded, and their marginals do not match the one sample breakdown the paper
prints (Table 1's university types, 120/233/108/118, match no column). They are
dropped rather than shipped under guessed names.

Item text
---------
S3 File gives every stem, tied to the same AP/AS/CSS codes, so the mapping is
explicit rather than inferred from order. The wording it gives is English,
while the instruments are Chinese (Zhao 2007, Liu 2015, Xie 1998) and the
respondents were students in Hebei; the administered Chinese is not recoverable
from the article or its supplements, so the English is shipped in the base text
fields with `language = Chinese` and empty `_translated` columns -- the
documented `translated_substitute` fallback. Source typos (e.g. AS7's "I hope
to find a and earn money") are left verbatim.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0338956.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")
ITEM_DIR = os.path.join(AF_DIR, "itemtext_output")

# table -> (source column prefix, item code prefix, n items, valid max,
#           instrument name)
TABLES = [
    ("xue_2025_academic_procrastination", "Q8_", "AP", 19, 5,
     "College Students' Academic Procrastination Questionnaire (Zhao, 2007)"),
    ("xue_2025_academic_stress", "Q9_", "AS", 20, 5,
     "College Students' Academic Stress Scale (Liu, 2015)"),
    ("xue_2025_coping_style", "Q10_", "CSS", 20, 4,
     "Simplified Coping Style Questionnaire (Xie, 1998)"),
]

# Only the endpoints are named in the Methods, and only for the 1-5 blocks.
ENDPOINT_ANCHORS = {1: "Strongly Disagree", 5: "Strongly Agree"}

ITEM_TEXT = {
    "AP1":   "I often wait until just before class to rush to the classroom.",
    "AP2":   "I usually don\u2019t put in effort and always cram for exams at the last minute.",
    "AP3":   "I can\u2019t organize my schedule well.",
    "AP4":   "I failed to finish the books that I could have finished on time.",
    "AP5":   "I always rush to do my homework only when it\u2019s about to be due.",
    "AP6":   "Sometimes, by the end of the day, I don't even know what I\u2019ve done.",
    "AP7":   "When I study in my dormitory, I often stop to do other things.",
    "AP8":   "I make sure to organize my study materials so I can use them at any time.",
    "AP9":   "I rarely complete the tasks I set for myself on time.",
    "AP10":  "Before exams, I think about revising but never take any action.",
    "AP11":  "I never stick the study plans that I make for myself.",
    "AP12":  "For assignments or reports with deadlines, I procrastinate unless someone reminds me.",
    "AP13":  "I have a detailed plan for preparing for exams.",
    "AP14":  "I often miss opportunities because I didn\u2019t take timely action.",
    "AP15":  "I often make excuses for not completing my academic tasks on time.",
    "AP16":  "I always postpone assignments or other academic tasks.",
    "AP17":  "I only start doing academic tasks when I can no longer delay them.",
    "AP18":  "I have a study plan every day.",
    "AP19":  "I often check the tasks I should complete before entertainment or going to bed.",
    "AS1":   "I feel like there is not enough time, and thinking about it makes me anxious.",
    "AS2":   "There are too many graduates, and the job market is tough, making me feel a lot of academic pressure.",
    "AS3":   "My parents have very high expectations of my study.",
    "AS4":   "There are too many exams and certifications, and I feel stressed.",
    "AS5":   "My academic workload is too heavy, and I feel pressured.",
    "AS6":   "Work now requires comprehensive skills, making my academic pressure greater.",
    "AS7":   "I hope to find a and earn money as soon as possible to support my parents.",
    "AS8":   "I study hard to get credits.",
    "AS9":   "My self-expectations are high, but the reality is quite different.",
    "AS10":  "I am worried about my ability to adapt to society in the future.",
    "AS11":  "My parents compare me to my peers which increases my pressure.",
    "AS12":  "The competition among classmates causes me stress.",
    "AS13":  "The unsuitable study environment makes me pressured.",
    "AS14":  "The pressure from exams and studies to enter national enterprises is overwhelming.",
    "AS15":  "My family\u2019s financial situation is tight, so I must study harder.",
    "AS16":  "I am not adapting well to the school environment.",
    "AS17":  "My learning methods are unscientific and my academic ability is limited.",
    "AS18":  "I am unsure about my future role in society.",
    "AS19":  "My parents hope I find a stable job soon.",
    "AS20":  "The pressure from romantic relationships has a significant impact on studying.",
    "CSS1":  "I relieve stress through work, study, or other activities.",
    "CSS2":  "I talk to someone to vent my inner troubles.",
    "CSS3":  "I try to see the positive side of things.",
    "CSS4":  "I change my perspective and rediscover what is important in life.",
    "CSS5":  "I don\u2019t take problems too seriously.",
    "CSS6":  "I stick to my position and fight for what I want.",
    "CSS7":  "I come with different solutions to problems.",
    "CSS8":  "I seek advice from relatives, friends, classmates.",
    "CSS9":  "I change my methods or resolve personal issues.",
    "CSS10": "I learn from how others handle similar difficulties.",
    "CSS11": "I engage in hobbies or participate in cultural and sports activities.",
    "CSS12": "I try to suppress feelings of disappointment, regret, sadness, or anger.",
    "CSS13": "I try to take a break or vacation, temporarily putting the problem aside.",
    "CSS14": "I relieve stress by smoking, drinking, or eating.",
    "CSS15": "I believe time will change the situation, and the only thing I can do is wait.",
    "CSS16": "I try to forget the whole situation.",
    "CSS17": "I rely on others to solve my problems.",
    "CSS18": "I accept the reality because there is no other choice.",
    "CSS19": "I fantasize that a miracle will change the situation.",
    "CSS20": "I comfort myself.",
}


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0338956.s001.xlsx")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def load() -> pd.DataFrame:
    """Row 0 is a banner naming the scale blocks; row 1 holds the real header."""
    raw = pd.read_excel(fetch(), header=None)
    d = raw.iloc[2:].reset_index(drop=True)
    d.columns = raw.iloc[1].tolist()
    return d.apply(pd.to_numeric, errors="coerce")


def write_item_text(out_name, codes, valid_max, instrument) -> None:
    rows = []
    for code in codes:
        for resp in range(1, valid_max + 1):
            rows.append({
                "table": out_name,
                "section_id": out_name + "_1",
                "item": code,
                "instrument": instrument,
                "language": "Chinese",
                "instructions": "",
                "section_prompt": "",
                "item_text": ITEM_TEXT[code],
                "correct_response": "",
                # named only for the endpoints of the 1-5 blocks; the paper
                # names no anchor for the 1-4 coping block at all
                "option_text": (ENDPOINT_ANCHORS.get(resp, "")
                                if valid_max == 5 else ""),
                "resp": resp,
                "instructions_translated": "",
                "section_prompt_translated": "",
                "item_text_translated": "",
                "option_text_translated": "",
            })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ITEM_DIR, out_name + "__items.csv"), index=False)
    print(f"{out_name}__items: rows={len(df)} items={df['item'].nunique()}")


def convert() -> None:
    d = load()
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEM_DIR, exist_ok=True)

    d = d.dropna(subset=["index"]).reset_index(drop=True)
    d["id"] = d["index"].astype(int)
    assert d["id"].is_unique, "index column is not unique"

    for out_name, src_prefix, code_prefix, n, valid_max, instrument in TABLES:
        src_cols = [f"{src_prefix}{i}" for i in range(1, n + 1)]
        codes = [f"{code_prefix}{i}" for i in range(1, n + 1)]
        wide = d[["id"] + src_cols].rename(columns=dict(zip(src_cols, codes)))

        long = wide.melt(id_vars=["id"], value_vars=codes,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert long["resp"].between(1, valid_max).all(), \
            f"{out_name}: resp outside 1-{valid_max}"

        long = long[["id", "item", "resp"]]
        long.to_csv(os.path.join(OUT_DIR, out_name + ".csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

        write_item_text(out_name, codes, valid_max, instrument)


if __name__ == "__main__":
    convert()
