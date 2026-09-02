#!/usr/bin/env python3
"""Disclosure pass for irw#1777: name the administered language on published tables that
ship English.

These are the tables where the study was run in another language, the administered wording
could not be recovered from the deposit or the paper's own supplements, and an English
rendering shipped instead. Nothing about the text changes. What changes is that the table
now says so: `language` names the administered language, and the four `_translated` columns
are present and empty -- which is the schema's documented signal that the base text fields
are NOT the wording respondents read (itemresponsewarehouse.org/itemtext.html).

Each language below is established in the table's own provenance note, not inferred here.
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

LANGUAGE = {
    "algner2022_cse": "German",
    "almuqbil_2022_epds": "Arabic",
    "avilesgonzalez2019_ces": "Italian",
    "bang_2023_self_esteem": "Korean",
    "beck_2021_pss10": "German",
    "bukurov_2022_sf36": "Serbian",
    "buzgova_2023_gai": "Czech",
    "buzgova_2023_lsita": "Czech",
    "buzgova_2023_rses": "Czech",
    "buzgova_2023_soc": "Czech",
    "chen_2022_sasc": "Chinese",
    "abdullah_2024_bsq_sev24": "Malay",
    "ALSECYPIAMH_WU_2022_SDQ": "Chinese",
    "ALSECYPIAMH_WU_2022_PHQ": "Chinese",
    "altahla_2024_swls": "Chinese",
    "altahla_2024_whoqol": "Chinese",
    "brederecke_2020_phq4": "German",
}

def main():
    n = 0
    for t, lang in sorted(LANGUAGE.items()):
        src = os.path.join(HERE, "published", f"{t}__published.csv")
        with open(src, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        out = []
        for r in rows:
            r = dict(r)
            r["language"] = lang
            for c in ("instructions_translated", "section_prompt_translated",
                      "item_text_translated", "option_text_translated"):
                r[c] = "NA"
            out.append(r)
        dst = os.path.join(HERE, "staging", f"{t}__items.csv")
        with open(dst, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            for r in out:
                w.writerow({c: r.get(c, "NA") for c in COLS})
        # the text itself must be untouched
        for a, b in zip(rows, out):
            for c in ("item", "resp", "item_text", "option_text", "instructions",
                      "section_prompt", "instrument", "correct_response", "section_id"):
                assert (a.get(c) or "") == (b.get(c) or ""), f"{t}: {c} changed"
        print(f"  {t:<34} {lang:<8} {len(out):>4} rows")
        n += 1
    print(f"\n{n} tables written to staging/")

if __name__ == "__main__":
    main()
