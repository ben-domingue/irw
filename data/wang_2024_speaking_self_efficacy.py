#!/usr/bin/env python3
"""Wang et al. (2024), PLOS ONE -- EFL speaking self-efficacy and its sources.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0297517
DOI: 10.1371/journal.pone.0297517
Data: S1 Data (journal.pone.0297517.s004, XLSX, five sheets)
License: CC BY 4.0
Item text: shipped (S2/S3 Appendices give the finalized items and the
    7-point anchors verbatim, in Chinese and English)

Two instruments developed and validated with Chinese non-English-major
undergraduates: the 15-item EFL Speaking Self-Efficacy Scale (EFL-SSES) and the
13-item EFL Sources of Speaking Self-Efficacy Scale (EFL-SSSES). Both are
7-point agreement scales (1 = Strongly Disagree .. 7 = Strongly Agree).

Sheets and what is kept
-----------------------
Study1-efa (227) + Study1-cfa (289)  -> wang_2024_speaking_self_efficacy
Study2-efa (224) + Study2-cfa (295)  -> wang_2024_self_efficacy_sources
Study3     (304)                     -> DROPPED, not a new sample

Each instrument was administered to two independently recruited samples (the
EFA phase and the CFA phase), with the same finalized item set in both -- the
deposit carries the retained 15/13 items for both phases, and the paper's
CFA N (289) matches the sheet exactly. They are therefore collapsed into one
file per instrument with a `cov_study` phase label, and `id` is offset by
10,000 for the CFA phase so the two samples' 1-based `Number` columns cannot
collide.

Study 3 is not a third administration. The paper says it analysed "responses
from students that participated in both Study 1 and Study 2" (N = 304), and
that is verifiable in the deposit: every one of Study3's distinct EFL-SSES
response vectors also appears in Study1-efa (168) or Study1-cfa (135), 303 of
303, and every distinct EFL-SSSES vector appears in Study2-efa (132) or
Study2-cfa (168), 300 of 300. Including the sheet would duplicate people, so
it is dropped.

Response coding
---------------
All item values are integers 1-7 with no missing cells in any of the four
sheets, matching the 7-point anchors printed in S2/S3. No sentinel or
out-of-range values to filter. The paper reports listwise-valid samples and
describes no imputation (text searched for "imput", "missing data", "MICE",
"LOCF", "mean substitution" -- no hits).

Covariates: age, gender, major, and LLE, the number of years the respondent has
been learning English (4-16), carried as `cov_english_learning_years`.

Item text
---------
S2 and S3 Appendix print each instrument in full -- the 7-point anchors and
every item stem, Chinese above English. The respondents were Chinese
non-English-major undergraduates and answered in Chinese, so the administered
Chinese goes in the base text fields and the appendices' own English goes in
the `_translated` fields, with `language = Chinese`.

Two notes on the source wording, both left as the source has them:
* The appendices' English anchor for point 4 is spelled "Uncerntain"; the
  obvious typo is corrected to "Uncertain" in the translation field. The
  Chinese anchor (不确定) is unambiguous and is what was administered.
* For VE3 the appendix's Chinese and English diverge: the English reads "...I
  can see myself speaking with perfect pronunciation and intonation in the same
  way", the Chinese "...我很佩服他/她" ("...I admire him/her"). The Chinese is
  what respondents read, so it is the base text; the English is carried as
  given rather than back-translated.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0297517.s004")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")
ITEM_DIR = os.path.join(AF_DIR, "itemtext_output")

COV_RENAME = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Major": "cov_major",
    "LLE": "cov_english_learning_years",
}
COV_COLS = ["cov_study"] + list(COV_RENAME.values())

# instrument -> (output table, [sheet, ...], [item column, ...])
TABLES = {
    "wang_2024_speaking_self_efficacy": (
        ["Study1-efa", "Study1-cfa"],
        ["LSE1", "LSE2", "LSE3", "LSE4", "LSE5",
         "SRE1", "SRE2", "SRE3",
         "DSE1", "DSE2", "DSE3",
         "PSE1", "PSE2", "PSE3", "PSE4"],
    ),
    "wang_2024_self_efficacy_sources": (
        ["Study2-efa", "Study2-cfa"],
        ["ME1", "ME2", "ME3", "ME4",
         "VE1", "VE2", "VE3",
         "SP1", "SP2", "SP3",
         "PES1", "PES2", "PES3"],
    ),
}

# id offset per phase, so the two samples' 1-based Number columns stay distinct
PHASE_OFFSET = {"efa": 0, "cfa": 10000}


# ---------------------------------------------------------------------------
# Item text (S2 / S3 Appendix) -- administered Chinese, with the appendices'
# own English as the translation.
# ---------------------------------------------------------------------------

INSTRUMENT_NAME = {
    "wang_2024_speaking_self_efficacy": (
        "EFL Speaking Self-Efficacy Scale (EFL-SSES)"),
    "wang_2024_self_efficacy_sources": (
        "EFL Sources of Speaking Self-Efficacy Scale (EFL-SSSES)"),
}

# resp -> (Chinese anchor, English anchor)
OPTIONS = [
    (1, "非常不同意", "Strongly Disagree"),
    (2, "不同意", "Disagree"),
    (3, "有点不同意", "Slightly Disagree"),
    (4, "不确定", "Uncertain"),
    (5, "有点同意", "Slightly Agree"),
    (6, "同意", "Agree"),
    (7, "非常同意", "Strongly Agree"),
]

# item -> (Chinese stem, English stem)
ITEM_TEXT = {
    "LSE1": ("在课堂上用英语发言时，我可以流利地表达自己的想法。",
             "When speaking English in the classroom, I can speak fluently."),
    "LSE2": ("在课堂上用英语发言时，我可以有逻辑地组织自己的想法。",
             "When speaking English in the classroom, I can logically organize my words."),
    "LSE3": ("在课堂上用英语发言时，我很少有停顿或磕绊（如：“嗯”、“啊”）。",
             "When speaking English in the classroom, I can speak with few pause or "
             "filler (i.e., \u201cUm,\u201d \u201cAh,\u201d or \u201cYou Know\u201d)."),
    "LSE4": ("在课堂上用英语发言时，我的语法都是正确的。",
             "When speaking English in the classroom, I can speak with grammatical accuracy."),
    "LSE5": ("在课堂上用英语发言时，我的发音、语调和连读都是正确的。",
             "When speaking English in the classroom, I can speak with correct "
             "pronunciation, intonation, and liaison."),
    "SRE1": ("在课堂上，我会积极把握用英语发言的机会。",
             "I actively participate in my speaking course to improve my speaking."),
    "SRE2": ("在课堂上用英语发言前，我已经构思好自己的内容。",
             "When speaking English in the classroom, I can think of my goals before speaking."),
    "SRE3": ("在课堂上用英语发言时，我可以评估是否向听众传递了自己的想法。",
             "When speaking English in the classroom, I can evaluate whether I achieve "
             "my goal in speaking."),
    "DSE1": ("在课堂上用英语发言时，我非常自信。",
             "When speaking English in the classroom, I can speak with confidence."),
    "DSE2": ("在课堂上用英语发言时，我没有压力。",
             "I am not stressed out when speaking English in the classroom."),
    "DSE3": ("在课堂外，我乐意和他人用英语交流。",
             "I enjoy speaking English outside the classroom."),
    "PSE1": ("我可以理解并掌握口语教学材料。",
             "I can understand the most difficult material presented in speaking course."),
    "PSE2": ("我能够出色地完成口语作业和测试。",
             "I can do an excellent job on the assignments and tests in the speaking course."),
    "PSE3": ("考虑到口语学习的难度、老师的教学方法和我的能力，我认为我可以在这门课上做得很好。",
             "Considering the difficulty of the speaking course, the teacher, and my "
             "skill, I think I can do well in this class."),
    "PSE4": ("我能够在口语考试中获得优秀的成绩。",
             "I can receive an excellent grade in speaking course."),
    "ME1": ("我曾经在课堂上流利地用英语表达我的想法。",
            "In the past, when speaking English in the classroom, I expressed my ideas fluently."),
    "ME2": ("我曾经在课堂上用正确的发音、语调和连读讲英语。",
            "In the past, when speaking English in the classroom, I spoke all words "
            "with correct pronunciation, intonation, and liaison."),
    "ME3": ("在以往的口语作业中，我有着良好的表现。",
            "In the past, I did well on Spoken English assignments."),
    "ME4": ("在以往的口语考试中，我有着很高的成绩。",
            "In the past, I got excellent grades on Spoken English tests."),
    "VE1": ("当我看到英语老师能够准确地使用复杂的句式时，我可以想象自己用同样的方法表达自己的想法。",
            "When I see how my English teacher uses complex sentences, I can picture "
            "myself using complex sentences in the same way."),
    "VE2": ("当我看到其他同学能够有逻辑地用英语表达自己的想法，我可以想象自己用同样的方法表达自己的想法。",
            "When I see how another student logically expresses their ideas, I can see "
            "myself logically expressing my ideas in the same way."),
    "VE3": ("当我看到我的朋友在英语课上表现出较好的语音语调，我很佩服他/她。",
            "When I see how my peers speak with perfect pronunciation and intonation, "
            "I can see myself speaking with perfect pronunciation and intonation in "
            "the same way."),
    "SP1": ("我的老师告诉我，我在英语口语方面很有天赋。",
            "My teachers have told me that I have a talent for speaking English."),
    "SP2": ("我的父母告诉我，我在英语口语方面做得很好。",
            "My parents have told me that I am doing well in speaking English."),
    "SP3": ("我的同学告诉我，我很擅长英语口语。",
            "My classmates have told me that I am good at speaking English."),
    "PES1": ("当在课堂上用英语发言的时候，我感到紧张。",
             "When speaking English in the classroom, I felt nervous."),
    "PES2": ("当在课堂上用英语发言的时候，我感到压力。",
             "When speaking English in the classroom, I got stressed."),
    "PES3": ("当在课堂上用英语发言的时候，我感到焦虑。",
             "When speaking English in the classroom, I got anxious."),
}


def write_item_text(out_name: str, item_cols: list[str]) -> None:
    rows = []
    for item in item_cols:
        zh, en = ITEM_TEXT[item]
        for resp, opt_zh, opt_en in OPTIONS:
            rows.append({
                "table": out_name,
                "section_id": out_name + "_1",
                "item": item,
                "instrument": INSTRUMENT_NAME[out_name],
                "language": "Chinese",
                "instructions": "",
                "section_prompt": "",
                "item_text": zh,
                "correct_response": "",
                "option_text": opt_zh,
                "resp": resp,
                "instructions_translated": "",
                "section_prompt_translated": "",
                "item_text_translated": en,
                "option_text_translated": opt_en,
            })
    df = pd.DataFrame(rows)
    path = os.path.join(ITEM_DIR, out_name + "__items.csv")
    df.to_csv(path, index=False)
    print(f"{out_name}__items: rows={len(df)} items={df['item'].nunique()}")


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0297517.s004.xlsx")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def convert() -> None:
    src = fetch()
    os.makedirs(OUT_DIR, exist_ok=True)

    for out_name, (sheets, item_cols) in TABLES.items():
        parts = []
        for sheet in sheets:
            phase = sheet.split("-")[1]
            d = pd.read_excel(src, sheet_name=sheet)
            d = d.rename(columns=COV_RENAME)
            d["id"] = d["Number"].astype(int) + PHASE_OFFSET[phase]
            d["cov_study"] = phase
            assert d["id"].is_unique, f"{sheet}: Number is not unique"
            parts.append(d[["id"] + COV_COLS + item_cols])

        wide = pd.concat(parts, ignore_index=True)
        assert wide["id"].is_unique, f"{out_name}: id collision across phases"

        long = wide.melt(id_vars=["id"] + COV_COLS, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        # 7-point agreement scale; nothing outside it in any sheet
        assert long["resp"].between(1, 7).all(), f"{out_name}: resp outside 1-7"

        long = long[["id", "item", "resp"] + COV_COLS]
        path = os.path.join(OUT_DIR, out_name + ".csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

        os.makedirs(ITEM_DIR, exist_ok=True)
        write_item_text(out_name, item_cols)


if __name__ == "__main__":
    convert()
