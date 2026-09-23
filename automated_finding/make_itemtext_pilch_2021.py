#!/usr/bin/env python3
"""Item text for the four pilch_2021 (peerj.11263) tables.

The deposit's own "Materials" sheet carries every item in the administered
Polish with an English translation beside it, plus the response anchors for
each block -- the cheap case in Step 3.5.

pilch_2021_fcv19s_validation was held on 2026-09-22 because the Fear of
COVID-19 Scale had no row in itemtext/instrument_rights_register.csv. Ben
cleared it 2026-09-23 (register row FCV-19S, verdict ship: Ahorsu et al.
published the scale in their own CC BY 4.0 article), and it is block 4 below.

Administered language is Polish, so the base text fields hold the Polish and
the English goes in the parallel *_translated fields (itemtext_standard.md,
"Administered language").
"""
import csv
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8083179/supplementaryFiles"
XLSX = "peerj-09-11263-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]


def materials():
    import time
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(XLSX))
                with z.open(name) as fh:
                    return pd.ExcelFile(BytesIO(fh.read())).parse("Materials")
        time.sleep(5 * (attempt + 1))
    raise RuntimeError("could not fetch the deposit")


def clean(s):
    """The sheet wraps most items in brackets and pads them unevenly."""
    s = str(s).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    s = s.strip()
    # Leading "1. " survives the bracket strip on the preventive block; the
    # number is the item code, not part of what was asked.
    while s[:1].isdigit() and "." in s[:3]:
        s = s.split(".", 1)[1].strip()
    return s


def build(table, items, options, instrument, mat):
    """items: [(item_code, materials_row)]. options: [(resp, pl, en)]."""
    rows = []
    section = f"{table}_1"
    for code, r in items:
        pl, en = clean(mat.iloc[r, 0]), clean(mat.iloc[r, 1])
        for resp, opt_pl, opt_en in options:
            rows.append({
                "table": table, "section_id": section, "item": code,
                "instrument": instrument, "language": "Polish",
                "instructions": "", "section_prompt": "",
                "item_text": pl, "correct_response": "",
                "option_text": opt_pl, "resp": resp,
                "instructions_translated": "", "section_prompt_translated": "",
                "item_text_translated": en, "option_text_translated": opt_en,
            })
    return rows


def write(table, rows):
    # Gate the item/resp sets against the STAGED response CSV before writing,
    # so a mismatch is caught here rather than by validate_items.R afterwards.
    resp = pd.read_csv(RESP_DIR / f"{table}.csv")
    got_items = {r["item"] for r in rows}
    want_items = set(resp["item"].astype(str))
    assert got_items == want_items, (
        f"{table}: item set mismatch\n  only in items: {sorted(got_items - want_items)}"
        f"\n  only in resp:  {sorted(want_items - got_items)}")
    got_resp = {float(r["resp"]) for r in rows}
    want_resp = set(resp["resp"].astype(float))
    assert got_resp == want_resp, (
        f"{table}: resp set mismatch\n  only in items: {sorted(got_resp - want_resp)}"
        f"\n  only in resp:  {sorted(want_resp - got_resp)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{table}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} rows, {len(got_items)} items, "
          f"{len(got_resp)} response options")


def main():
    mat = materials()

    # ---- 1. Preventive behaviour, Sample 1 (1-5 agreement) ----------------
    # Materials rows 5-8 are numbered [1.]-[4.], matching Preventive1-4.
    # Anchors at rows 11-15 label all five points in both languages.
    agree = [(i, clean(mat.iloc[10 + i, 0]), clean(mat.iloc[10 + i, 1]))
             for i in range(1, 6)]
    write("pilch_2021_preventive_behavior",
          build("pilch_2021_preventive_behavior",
                [(f"Preventive{i}", 4 + i) for i in range(1, 5)],
                agree,
                "Engagement in preventive behavior during the pandemic "
                "(author-constructed, 4 items)", mat))

    # ---- 2. IPIP-BFM-20, Sample 2 (1-5 accuracy) -------------------------
    # Materials rows 42-61 are the 20 items in the order the sheet's own
    # heading names them ("IPIP-IPIP1 - IPIP-IPIP20"), and row 42 is the
    # canonical IPIP marker "Am the life of the party".
    #
    # Row 63 labels only the ENDPOINTS in Polish ("1-całkowicie nietrafnie
    # mnie opisuje, 5-całkowicie trafnie mnie opisuje") while its English
    # gloss labels all five. The administered wording is the Polish, so
    # points 2-4 were unlabeled and their option_text stays blank -- padding
    # them from the English would publish anchors no respondent saw, and
    # audit_batch.R warns on exactly that. option_text_translated is left
    # blank in step with its base field.
    acc = [(1, "całkowicie nietrafnie mnie opisuje", "very inaccurate"),
           (2, "", ""), (3, "", ""), (4, ""  , ""),
           (5, "całkowicie trafnie mnie opisuje", "very accurate")]
    write("pilch_2021_ipip20_validation",
          build("pilch_2021_ipip20_validation",
                [(f"IPIP{i}", 41 + i) for i in range(1, 21)],
                acc,
                "International Personality Item Pool Big-Five Markers, 20-item "
                "Polish adaptation (IPIP-BFM-20)", mat))

    # ---- 3. Preventive behaviour VAS, Sample 2 (0-100 slider) ------------
    # Only the two endpoints carry labels (row 21). Every observed slider
    # value still needs a row so the resp sets match; the unlabeled points
    # in between are blank, which is required rather than a defect.
    resp_vals = sorted(set(pd.read_csv(RESP_DIR / "pilch_2021_preventive_vas.csv")
                           ["resp"].astype(float)))
    vas = [(v,
            "zdecydowanie nie" if v == 0 else ("zdecydowanie tak" if v == 100 else ""),
            "definitely not" if v == 0 else ("definitely yes" if v == 100 else ""))
           for v in resp_vals]
    write("pilch_2021_preventive_vas",
          build("pilch_2021_preventive_vas",
                [(f"Beh{i}", 17 + i) for i in range(1, 4)],
                vas,
                "Preventive behaviors during the pandemic "
                "(author-constructed, 3 items, 0-100 visual analogue scale)", mat))

    # ---- 4. FCV-19S, Sample 2 (1-5 agreement) ----------------------------
    # Materials rows 24-30 are numbered [1.]-[7.] under the heading "Fear of
    # Covid-19, POLISH (fear 1-fear 7) Sample 1, Sample 2", matching fear1-7.
    # The English column is Ahorsu et al.'s Appendix wording verbatim.
    # Anchors at rows 33-37 label all five points in both languages; their
    # leading "1 " .. "5 " is the resp code, not part of what was shown.
    #
    # Items 5-7 in this sheet differ in wording from the paper's own Table 1
    # (which the live pilch_2021_fear_covid19 carries): Table 1 adds "w
    # mediach spolecznosciowych" to item 5 and rephrases 6 and 7. The sheet
    # is the deposited questionnaire for both samples, so it is what was
    # administered and it is what ships (the cordova2019 ruling, 2026-09-19).
    fear = [(i, clean(mat.iloc[32 + i, 0]).split(" ", 1)[1],
             clean(mat.iloc[32 + i, 1]).split(" ", 1)[1]) for i in range(1, 6)]
    write("pilch_2021_fcv19s_validation",
          build("pilch_2021_fcv19s_validation",
                [(f"fear{i}", 23 + i) for i in range(1, 8)],
                fear,
                "Fear of COVID-19 Scale (FCV-19S), Polish version", mat))


if __name__ == "__main__":
    main()
