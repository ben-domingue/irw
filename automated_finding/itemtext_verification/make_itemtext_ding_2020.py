#!/usr/bin/env python3
"""Item text for ding_2020_covid_knowledge and ding_2020_covid_risk_perception
(PLOS ONE 10.1371/journal.pone.0237626).

Cheap case: the questionnaire is in the deposit. S1 File (.docx) is the Chinese
questionnaire as administered; S2 File is the authors' own English version. Both
number the questions 1-20 and letter the options A-I, and the data file's column
headers carry the same question numbers ("10.Transmission route") with the option
letter in a second header row, which is how data/ding_2020_covid_students.py derives
the item codes (Q10A, Q11, Q17 ...). So each code is tied to its wording by the
source's own numbering, not by position.

Knowledge table: every tick-all-that-apply option is its own binary item, scored
against the questionnaire's printed key (resp 1 = tick matches the key). The option
rows therefore describe the respondent's tick (Q11, a single-choice item, carries its
stem in item_text and its six options as rows): for a keyed-correct option, resp 1 =
ticked; for a distractor, resp 1 = left unticked. raw_resp carries the tick itself
(1/0), and for Q11 (single choice) the option number 1-6, matching resp_raw in the
response table. The English text is the authors' (S2 File), transcribed verbatim,
including its rough spots.
"""
import csv
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "itemtext_output"
RESP = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "section_prompt_translated",
        "item_text", "item_text_translated", "correct_response", "option_text",
        "option_text_translated", "resp", "raw_resp"]
LANG = "Chinese"

# ---------------------------------------------------------------- knowledge
K_TABLE = "ding_2020_covid_knowledge"
K_INSTR = "以下问题是为了了解您对新型冠状病毒感染的肺炎的认识程度，请根据您的自身情况选择合适答案。此部分共20分。"
K_INSTR_EN = ("The following questions are based on your knowledge of COVID-19. Please choose "
              "an appropriate answer according to your situation. (The full score is 20)")
K_INSTRUMENT = ("COVID-19 knowledge items (Part three) of the authors' cognition-attitude "
                "survey of Chinese college students, Ding et al. (2020)")
# question: (stem_zh, stem_en, {letter: (opt_zh, opt_en)}, key)
Q = {
    "Q10": ("据您了解新型冠状病毒的传播途径有哪些 [多选题]",
            "According to your knowledge, what are the transmission ways of COVID-19? [multiple choice]",
            {"A": ("飞沫传播", "droplet transmission"), "B": ("接触传播", "contact transmission"),
             "C": ("蚊虫传播", "mosquito transmission"), "D": ("粪口传播", "fecal mouth transmission"),
             "E": ("不知道", "I don't know")}, "AB"),
    "Q11": ("据您了解新型冠状病毒的易感人群是 [单选题]",
            "It is known to you that COVID-19 is susceptible to [single choice]",
            {"A": ("儿童易感", "children susceptible"), "B": ("青壮年人群易感", "young and middle-aged people susceptible"),
             "C": ("中年人群易感", "middle-aged people susceptible"), "D": ("老年人群易感", "the elderly are susceptible"),
             "E": ("人群普遍易感", "the general population is susceptible"), "F": ("不知道", "do not know")}, "E"),
    "Q12": ("据您了解新型冠状病毒感染常见的症状有哪些？ [多选题]",
            "What do you know about the common symptoms of COVID-19 infection? [multiple choice]",
            {"A": ("干咳", "dry cough"), "B": ("发热", "fever"),
             "C": ("呼吸急促、甚至困难", "shortness of breath, even difficulty"), "D": ("乏力", "fatigue"),
             "E": ("精神差、食欲差", "poor spirit, poor appetite"), "F": ("不知道", "I don't know")}, "ABCDE"),
    "Q13": ("您认为以下哪些是预防新型冠状病毒感染的有效措施？ [多选题]",
            "Which of the following do you think is an effective measure to prevent COVID-19 infection? [multiple choice]",
            {"A": ("尽量少出门，不参加聚会", "go out as little as possible, do not attend parties"),
             "B": ("避免接触武汉返乡人员及发热人员", "avoid contact with Wuhan returnees and fever"),
             "C": ("勤用洗手液、肥皂等洗手", "wash hands with hand sanitizer, soap, etc."),
             "D": ("勤开窗通风", "open Windows frequently for ventilation"),
             "E": ("外出时佩戴口罩", "wear a mask when you go out"),
             "F": ("服用病毒灵、达菲等", "Take virion, tamiflu, etc."),
             "G": ("熏醋", "Fumigation vinegar"),
             "H": ("使用医用酒精对衣物、随身物品等进行消毒", "use medical alcohol to disinfect clothing, personal effects, etc."),
             "I": ("打喷嚏或咳嗽时用纸巾或手肘捂住口鼻", "cover your mouth and nose with a tissue or elbow when sneezing or coughing")},
            "ABCDEHI"),
    "Q16": ("您认为以下关于新型冠状病毒感染的肺炎的说法正确的是？ [多选题]",
            "What do you think is true about COVID-19? [multiple choice]",
            {"A": ("潜伏期一般为3-7天，最长不超过14天", "The incubation period is usually 3-7 days, with the longest not exceeding 14 days"),
             "B": ("在潜伏期，新型冠状病毒也具有传染性", "COVID-19 is also infectious during the incubation period"),
             "C": ("不知道", "I do not know.")}, "AB"),
}
TICK = {1: ("勾选", "Ticked"), 0: ("未勾选", "Not ticked")}


def knowledge():
    rows = []
    for q, (stem, stem_en, opts, key) in Q.items():
        base = {"table": K_TABLE, "section_id": f"{K_TABLE}_{q}", "instrument": K_INSTRUMENT,
                "language": LANG, "instructions": K_INSTR, "instructions_translated": K_INSTR_EN,
                "section_prompt": stem, "section_prompt_translated": stem_en}
        if q == "Q11":
            for n, letter in enumerate("ABCDEF", start=1):
                oz, oe = opts[letter]
                rows.append({**base, "section_prompt": "", "section_prompt_translated": "",
                             "item": q, "item_text": stem, "item_text_translated": stem_en,
                             "correct_response": key, "option_text": f"{letter}. {oz}",
                             "option_text_translated": f"{letter}. {oe}",
                             "resp": int(letter == key), "raw_resp": n})
            continue
        for letter, (oz, oe) in opts.items():
            keyed = letter in key
            for tick in (1, 0):
                tz, te = TICK[tick]
                rows.append({**base, "item": f"{q}{letter}", "item_text": f"{letter}. {oz}",
                             "item_text_translated": f"{letter}. {oe}",
                             "correct_response": "ticked" if keyed else "not ticked",
                             "option_text": tz, "option_text_translated": te,
                             "resp": int(tick == int(keyed)), "raw_resp": tick})
    return rows


# ---------------------------------------------------------- risk perception
R_TABLE = "ding_2020_covid_risk_perception"
R_INSTR = "以下问题是为了了解您对新型冠状病毒感染的肺炎的态度，答案没有对错，请根据您的自身感受，选择最适当的答案。"
R_INSTR_EN = ("The following question is about your attitude towards COVID-19. There is no right "
              "or wrong answer. Please choose the most appropriate answer according to your own feelings.")
R_INSTRUMENT = ("COVID-19 risk perception items (Part four) of the authors' cognition-attitude "
                "survey of Chinese college students, Ding et al. (2020)")
R = {
    "Q17": ("即使一个人身体好，也可能受到新型冠状病毒感染。",
            "Even if a person is in good health, he may be infected with COVID-19",
            ["完全不可能", "不可能", "不好说", "可能", "非常可能"],
            ["not at all", "it won't happen.", "it's hard to say", "perhaps", "very likely"]),
    "Q18": ("与其他人相比,我更容易出现新型冠状病毒感染的肺炎。",
            "I am more susceptible to infected COVID-19 than any other person",
            ["完全不会", "不会出现", "不好说", "会出现", "肯定会"],
            ["not at all", "it won't happen", "it's hard to say", "will appear", "must be"]),
    "Q19": ("有人曾提醒过我小心感染新型冠状病毒。",
            "Someone once reminded me to be careful of COVID-19",
            ["从没人提醒", "偶尔提醒", "不好说", "经常有人提醒", "时刻有人提醒"],
            ["no one ever reminded me", "an occasional reminder", "it's hard to say",
             "they are often reminded", "be reminded all the time"]),
    "Q20": ("我会担心我的家人受到新型冠状病毒的感染。",
            "I would be worried about my family being infected by COVID-19",
            ["完全不担心", "不担心", "不好说", "有些担心", "非常担心"],
            ["not at all.", "don't worry", "it's hard to say", "a little worried.", "very worried"]),
}


def risk():
    rows = []
    for q, (stem, stem_en, oz, oe) in R.items():
        for n in range(1, 6):
            rows.append({"table": R_TABLE, "section_id": f"{R_TABLE}_1", "item": q,
                         "instrument": R_INSTRUMENT, "language": LANG,
                         "instructions": R_INSTR, "instructions_translated": R_INSTR_EN,
                         "section_prompt": "", "section_prompt_translated": "",
                         "item_text": stem, "item_text_translated": stem_en,
                         "correct_response": "", "option_text": oz[n - 1],
                         "option_text_translated": oe[n - 1], "resp": n, "raw_resp": ""})
    return rows


def write(table, rows):
    resp = pd.read_csv(RESP / f"{table}.csv")
    items = pd.DataFrame(rows)
    assert set(items["item"]) == set(resp["item"]), (table, set(items["item"]) ^ set(resp["item"]))
    assert set(items["resp"]) == set(resp["resp"]), table
    if "resp_raw" in resp:
        for it, g in resp.groupby("item"):
            have = set(items.loc[items["item"] == it, "raw_resp"])
            assert set(g["resp_raw"]) <= have, (it, set(g["resp_raw"]) - have)
            # the scored resp in the data equals the scoring the option rows assert
            m = items[items["item"] == it].set_index("raw_resp")["resp"]
            assert (g["resp"].values == m.loc[g["resp_raw"]].values).all(), it
    cols = COLS if "raw_resp" in items and items["raw_resp"].astype(str).str.len().gt(0).any() else COLS[:-1]
    with open(OUT / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{table}__items.csv: {len(rows)} rows, {items['item'].nunique()} items")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write(K_TABLE, knowledge())
    write(R_TABLE, risk())
