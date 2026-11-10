#!/usr/bin/env python3
"""Item text for lam_2015_gses (10.1371/journal.pone.0142620, PLOS SI,
CC BY 4.0).

Instrument: the General Self-Efficacy Scale (Schwarzer & Jerusalem 1995), 10
items, administered in Hong Kong in its Chinese version (CGSES; the article
cites Cheung & Sun 1999, the Hong Kong validation of the Zhang & Schwarzer 1995
Chinese adaptation), 4-point scale. Identified from the article's Methods
("The General Self-Efficacy Scale (GSES) is a 10-item measure ... validated for
use in the Hong Kong Chinese community (CGSES)"); the deposit has no labels, so
there are no stems to search.

Rights: register row GSE (ship; the originators' FAQ, userpage.fu-berlin.de/
health/faq_gse.pdf, sha256 fdc6c30d...: "We hereby grant you permission to use
and reproduce the General Self-Efficacy Scale for your study, given that
appropriate recognition of the source of the scale is made"). The Chinese
wording is neither in the deposit (two CSVs, numeric codes only) nor in the
article or its SI (S1/S2 Table are demographics), and the CGSES translation's
own terms are unestablished, so per the GSE row's note and itemtext_standard.md
(irw#2121) the ORIGINATORS' ENGLISH ships as a stand-in:
text_source=translated_substitute, language=Chinese, _translated empty,
translation_source=official_instrument_english.

Wording: the English version printed in the appendix of the originators' own
GSE page, https://userpage.fu-berlin.de/health/engscal.htm ("English version
by Ralf Schwarzer & Matthias Jerusalem, 1995"), items 1-10 and the response
format 1 = Not at all true .. 4 = Exactly true.

Mapping: POSITIONAL. The deposit's columns are gses1..gses10 (kept as the item
codes by data/lam_2015_cancer_predisposition.py), and gsesK is taken to be the
scale's item K. The Chinese adaptation is a straight item-by-item translation
keeping the original order, but no file in the deposit or article ties the
numbers to wording. verify_lam_2015.py records why no statistical route can
test the order (one polarity, one factor): NO_ROUTE.

Run: RESP_DIR=<dir> RAW=<engscal.htm> python3 make_itemtext_lam_2015.py
"""
import csv
import html
import os
import re
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
RAW = os.environ.get("RAW", "https://userpage.fu-berlin.de/health/engscal.htm")
TABLE = "lam_2015_gses"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]
INSTRUMENT = ("General Self-Efficacy Scale (GSE), Schwarzer & Jerusalem (1995); "
              "administered in its Chinese version (CGSES), English original shown")
# the register row GSE's match_item_text, in item order
REGISTER = ["i can always manage to solve difficult problems if i try hard enough",
            "if someone opposes me i can find the means and ways to get what i want",
            "it is easy for me to stick to my aims and accomplish my goals",
            "i am confident that i could deal efficiently with unexpected events",
            "thanks to my resourcefulness i know how to handle unforeseen situations",
            "i can solve most problems if i invest the necessary effort",
            "i can remain calm when facing difficulties because i can rely on my coping abilities",
            "when i am confronted with a problem i can usually find several solutions",
            "if i am in trouble i can usually think of a solution",
            "i can usually handle whatever comes my way"]


def page_text():
    if RAW.startswith("http"):
        req = urllib.request.Request(RAW, headers={"User-Agent": "IRW-Finder/1.0"})
        raw = urllib.request.urlopen(req, timeout=60).read()
    else:
        raw = Path(RAW).read_bytes()
    t = raw.decode("cp1252", errors="replace")
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).replace("\xa0", " ")


def main():
    t = page_text()
    app = t[t.index("English version by Ralf Schwarzer & Matthias Jerusalem, 1995"):]
    body, fmt = app.split("Response Format", 1)
    items = re.findall(r"(?:^|\s)(\d{1,2}) (.+?)(?=\s\d{1,2} [A-Z]|\s*$)", body.split("1995", 1)[1])
    assert [int(k) for k, _ in items] == list(range(1, 11)), items
    texts = [s.strip() for _, s in items]
    norm = [re.sub(r"[^a-z ]", "", s.lower()) for s in texts]
    assert norm == REGISTER, list(zip(norm, REGISTER))
    opts = re.findall(r"(\d) = ([A-Za-z ]+?)(?=\s+\d =|\s*$)", fmt.strip()[:120])
    opts = [(int(k), v.strip()) for k, v in opts]
    assert opts == [(1, "Not at all true"), (2, "Hardly true"),
                    (3, "Moderately true"), (4, "Exactly true")], opts
    rows = []
    for k, text in enumerate(texts, start=1):
        for resp, lab in opts:
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": f"gses{k}",
                         "instrument": INSTRUMENT, "language": "Chinese",
                         "instructions": "", "section_prompt": "", "item_text": text,
                         "correct_response": "", "option_text": lab, "resp": resp,
                         "instructions_translated": "", "section_prompt_translated": "",
                         "item_text_translated": "", "option_text_translated": ""})
    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    assert {r["item"] for r in rows} == set(resp["item"])
    assert {r["resp"] for r in rows} == set(resp["resp"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / f"{TABLE}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{TABLE}__items.csv: {len(rows)} rows, {len(rows) // 4} items")
    for r in rows[::4]:
        print("   ", r["item"], "|", r["item_text"])


if __name__ == "__main__":
    main()
