#!/usr/bin/env python3
"""Item text for zhao_2024_{phq9,gad7} (Chinese) and chinvararak_2022_gad7 (Thai),
from the official PHQ-9 / GAD-7 translations on phqscreeners.com.

Rights: register row "PHQ and GAD screener family" (ship): "All PHQ, GAD-7
screeners and translations are downloadable from this website and no permission
is required to reproduce, translate, display or distribute them." Each PDF's
footer repeats the grant in its own language.

Neither study prints the items or deposits their wording (zhao_2024: S1 xlsx
headers PHQ1..PHQ9 / GAD1..GAD7, no labels; chinvararak_2022: S1 .dta variable
labels "GAD-7 [Q1]".."GAD-7 [Q7]", no value labels). Item codes are the deposit
column names, numbered as the form prints them, so code k = printed item k.

Sources (phqscreeners.com, /images/sites/g/files/g10060481/f/201412/...):
  PHQ9_Simplified Chinese for Mainland China.pdf   zhao_2024_phq9 base fields
  GAD7_Simplified Chinese for Mainland China.pdf   zhao_2024_gad7 base fields
  GAD7_Thai for Thailand.pdf                       chinvararak_2022_gad7 base
  PHQ-9_English.pdf, GAD-7_English.pdf             *_translated
Every hard-coded string below is asserted to occur in the text extracted from
its PDF (whitespace removed, so wrapped lines join), read with `mutool draw -F
text` (reading order; the Chinese and English PDFs carry a ToUnicode map). The
Thai PDF uses CordiaNew with Windows-Thai private-use positional glyphs (U+F70A
= low MAI EK, etc.), so its PUA code points are mapped back
to the Thai combining marks (THAI_PUA) and NIKHAHIT+SARA AA recomposed to SARA
AM; the result was checked by eye against a 200-dpi render of the page.

Verbatim notes: the Simplified Chinese PHQ-9 prints the traditional form 沒 in
"从来沒有" and items 4 ("沒有活力"), and draws the dash in items 6 and 8 as two
U+2500 box-drawing characters; both kept as printed. The paper-form marking
line ("请用...勾选您的答案") and the PHQ-9 difficulty question are not shipped
(neither is an item in the response table).

Coding: zhao_2024 stores 1-4 (the published 0-3 plus one; data/zhao_2024_nurses_phq_gad.py
asserts sum-minus-n equals the deposit's own total on every row), so resp 1 carries
the 0 anchor, ..., resp 4 the 3 anchor. chinvararak_2022_gad7 stores 0-3 as printed.

Run: RESP_DIR_5=<leads-batch-5 irw_output> RESP_DIR_7=<leads-batch-7 irw_output>
     [PDF_DIR=<dir with the five PDFs, names as above>] python3 make_itemtext_phq_gad_2026_11_08.py
Then run normalize_nulls.R on the output.
"""
import csv
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP5 = Path(os.environ.get("RESP_DIR_5", HERE / "irw_output"))
RESP7 = Path(os.environ.get("RESP_DIR_7", HERE / "irw_output"))
PDF_DIR = os.environ.get("PDF_DIR")
BASE = "https://www.phqscreeners.com/images/sites/g/files/g10060481/f/201412/"
PDFS = {
    "phq9_zh": "PHQ9_Simplified Chinese for Mainland China.pdf",
    "gad7_zh": "GAD7_Simplified Chinese for Mainland China.pdf",
    "gad7_th": "GAD7_Thai for Thailand.pdf",
    "phq9_en": "PHQ-9_English.pdf",
    "gad7_en": "GAD-7_English.pdf",
}
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]

THAI_PUA = {0xF700: 0x0E10, 0xF701: 0x0E34, 0xF702: 0x0E35, 0xF703: 0x0E36, 0xF704: 0x0E37,
            0xF705: 0x0E48, 0xF706: 0x0E49, 0xF707: 0x0E4A, 0xF708: 0x0E4B, 0xF709: 0x0E4C,
            0xF70A: 0x0E48, 0xF70B: 0x0E49, 0xF70C: 0x0E4A, 0xF70D: 0x0E4B, 0xF70E: 0x0E4C,
            0xF70F: 0x0E0D, 0xF710: 0x0E31, 0xF711: 0x0E4D, 0xF712: 0x0E47, 0xF713: 0x0E48,
            0xF714: 0x0E49, 0xF715: 0x0E4A, 0xF716: 0x0E4B, 0xF717: 0x0E4C, 0xF718: 0x0E38,
            0xF719: 0x0E39, 0xF71A: 0x0E3A}

PHQ9_EN_INSTR = "Over the last 2 weeks, how often have you been bothered by any of the following problems?"
GAD7_EN_INSTR = "Over the last 2 weeks, how often have you been bothered by the following problems?"
EN_OPTS = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
PHQ9_EN = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading the newspaper or watching television",
    "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so "
    "fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead or of hurting yourself in some way",
]
GAD7_EN = [
    "Feeling nervous, anxious or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it is hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen",
]

PHQ9_ZH_INSTR = "在过去两周，您经常受到以下问题的困扰吗？"
PHQ9_ZH_OPTS = ["从来沒有", "有几天", "刚超过一半天数", "接近每天"]
PHQ9_ZH = [
    "做任何事都觉得沉闷或者根本不想做任何事",
    "情绪低落、抑郁或绝望",
    "难于入睡；半夜会醒，或相反，睡觉时间过多",
    "觉得疲倦或沒有活力",
    "胃口极差或饮食过量",
    "不喜欢自己──觉得自己做得不好、对自己失望或有负家人期望",
    "难于集中精神做事，例如看报纸或看电视",
    "其它人反映你行动或说话迟缓；或者相反，你比平常活动更多──坐立不安、停不下来",
    "想到自己最好去死或者自残",
]
GAD7_ZH_INSTR = "在过去两周，您经常受到以下问题的困扰吗？"
GAD7_ZH_OPTS = ["从来没有", "有几天", "刚超过一半天数", "接近每天"]
GAD7_ZH = [
    "感觉心神不安、焦虑或高度紧张",
    "不能停止或控制担心",
    "为各种各样的事情过度担心",
    "难以放松",
    "非常不安静以至于难以坐定",
    "变得易恼火或易急躁",
    "害怕发生可怕的事情",
]
GAD7_TH_INSTR = "ในช่วง 2 สัปดาห์ที่ผ่านมา ท่านถูกรบกวนด้วยปัญหาต่อไปนี้บ่อยเพียงใด"
GAD7_TH_OPTS = ["ไม่เคยเลย", "หลายวัน", "มากกว่าครึ่งหนึ่งของวันทั้งหมด", "เกือบทุกวัน"]
GAD7_TH = [
    "รู้สึกกระวนกระวายใจ วิตกกังวล หรือตึงเครียดมาก",
    "ไม่สามารถหยุดหรือควบคุมตนเองไม่ให้วิตกกังวลได้",
    "วิตกกังวลมากเกินไปในเรื่องต่าง ๆ กัน",
    "ทำตัวให้ผ่อนคลายได้ยาก",
    "กระสับกระส่ายมากจนแทบจะนั่งไม่ติด",
    "กลายเป็นคนรำคาญง่ายหรืออารมณ์เสียง่าย",
    "รู้สึกกลัว เหมือนกับว่าอาจจะมีเรื่องเลวร้ายเกิดขึ้น",
]


def pdf_path(key, tmp):
    if PDF_DIR:
        return os.path.join(PDF_DIR, PDFS[key])
    r = requests.get(BASE + PDFS[key].replace(" ", "%20"), headers={"User-Agent": "Mozilla/5.0"}, timeout=120)
    r.raise_for_status()
    assert r.content[:4] == b"%PDF", key
    p = os.path.join(tmp, key + ".pdf")
    with open(p, "wb") as f:
        f.write(r.content)
    return p


def pdf_text(path, thai=False):
    t = subprocess.run(["mutool", "draw", "-F", "text", "-o", "-", path],
                       capture_output=True, check=True).stdout.decode("utf-8")
    if thai:
        t = t.translate(THAI_PUA)
        t = re.sub("ํ([่-๋]?)า", lambda m: m.group(1) + "ำ", t)
    return re.sub(r"\s+", "", t)


def check(strings, text, label):
    for s in strings:
        assert re.sub(r"\s+", "", s) in text, (label, s)


def build(table, resp_path, inst, lang, instr, instr_en, items, items_en, opts, codes, offset):
    resp = pd.read_csv(resp_path)
    levels = sorted(int(v) for v in resp["resp"].unique())
    assert levels == [offset + i for i in range(4)], (table, levels)
    rows = []
    for code, txt, txt_en in zip(codes, items, items_en):
        for i in range(4):
            rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": inst,
                         "language": lang, "instructions": instr, "section_prompt": "", "item_text": txt,
                         "correct_response": "", "option_text": opts[i], "resp": offset + i,
                         "instructions_translated": instr_en, "section_prompt_translated": "",
                         "item_text_translated": txt_en, "option_text_translated": EN_OPTS[i]})
    assert {r["item"] for r in rows} == set(resp["item"]), table
    assert {r["resp"] for r in rows} == set(resp["resp"]), table
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{table}__items.csv: {len(rows)} rows, {len(codes)} items")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        txt = {k: pdf_text(pdf_path(k, tmp), thai=(k == "gad7_th")) for k in PDFS}
    check([PHQ9_ZH_INSTR] + PHQ9_ZH + PHQ9_ZH_OPTS, txt["phq9_zh"], "phq9_zh")
    check([GAD7_ZH_INSTR] + GAD7_ZH + GAD7_ZH_OPTS, txt["gad7_zh"], "gad7_zh")
    check([GAD7_TH_INSTR] + GAD7_TH + GAD7_TH_OPTS, txt["gad7_th"], "gad7_th")
    check([PHQ9_EN_INSTR] + PHQ9_EN + ["Not at all", "Several days", "Nearly every day"], txt["phq9_en"], "phq9_en")
    check([GAD7_EN_INSTR] + GAD7_EN + ["Several days"], txt["gad7_en"], "gad7_en")
    # numbering: item k is printed as "k." immediately before its stem
    for key, items in [("phq9_zh", PHQ9_ZH), ("gad7_zh", GAD7_ZH), ("gad7_th", GAD7_TH),
                       ("phq9_en", PHQ9_EN), ("gad7_en", GAD7_EN)]:
        for k, s in enumerate(items, 1):
            assert f"{k}." + re.sub(r"\s+", "", s) in txt[key], (key, k)

    build("zhao_2024_phq9", RESP5 / "zhao_2024_phq9.csv",
          "Patient Health Questionnaire-9 (PHQ-9), official Simplified Chinese version for Mainland China (phqscreeners.com)",
          "Chinese", PHQ9_ZH_INSTR, PHQ9_EN_INSTR, PHQ9_ZH, PHQ9_EN, PHQ9_ZH_OPTS,
          [f"PHQ{i}" for i in range(1, 10)], 1)
    build("zhao_2024_gad7", RESP5 / "zhao_2024_gad7.csv",
          "Generalized Anxiety Disorder-7 (GAD-7), official Simplified Chinese version for Mainland China (phqscreeners.com)",
          "Chinese", GAD7_ZH_INSTR, GAD7_EN_INSTR, GAD7_ZH, GAD7_EN, GAD7_ZH_OPTS,
          [f"GAD{i}" for i in range(1, 8)], 1)
    build("chinvararak_2022_gad7", RESP7 / "chinvararak_2022_gad7.csv",
          "Generalized Anxiety Disorder-7 (GAD-7), official Thai version for Thailand (phqscreeners.com)",
          "Thai", GAD7_TH_INSTR, GAD7_EN_INSTR, GAD7_TH, GAD7_EN, GAD7_TH_OPTS,
          [f"gad7_{i}" for i in range(1, 8)], 0)


if __name__ == "__main__":
    main()
