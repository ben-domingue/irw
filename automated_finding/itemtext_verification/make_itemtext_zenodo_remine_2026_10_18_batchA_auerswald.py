"""Item text for auerswald_2024_online_learning (zenodo.10731829).

The four Corona_* variable labels carry the authors' English wording followed by
the administered German in typographic quotes, so BOTH languages come from the
deposit. The value labels give each item's own five anchors -- and the anchors
RUN IN OPPOSITE DIRECTIONS on Corona_1/3 vs Corona_2/4, so each item gets its
own option_text rather than one shared set. German anchors go in option_text
(administered) and the English in option_text_translated.
"""
import csv, os, re, sys

import pyreadstat

HERE = os.environ.get("IRW_BATCHA_RAW", os.path.dirname(os.path.abspath(__file__)))
OUT = ("/home/ben/Dropbox/projects/irw/src/.claude/worktrees/"
       "remine-3077-zenodo-leads/automated_finding/itemtext_output")
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]
TABLE = "auerswald_2024_online_learning"
# The authors' own German anchors, translated to English by IRW for the
# _translated column. Recorded as IRW's English in the provenance note.
EN = {"Trifft nicht zu": "Does not apply",
      "Trifft eher nicht zu": "Rather does not apply",
      "Weder noch": "Neither",
      "Trifft eher zu": "Rather applies",
      "Trifft zu": "Applies"}


def main():
    d, meta = pyreadstat.read_sav(
        os.path.join(HERE, "raw/10731829/Auerswald_et_al_SJOP.sav"),
        apply_value_formats=False)
    labs, vals = meta.column_names_to_labels, meta.variable_value_labels
    rows = []
    for i in range(1, 5):
        c = f"Corona_{i}"
        full = labs[c]
        # "1.I feel ... [“Das selbstorganisierte ...”]" -> English stem + German stem
        m = re.match(r"^\s*\d+\.\s*(.*?)\s*\[\s*[“\"](.*?)[”\"]\s*\]\s*$", full, re.S)
        assert m, (c, full[:120])
        en, de = m.group(1).strip(), m.group(2).strip()
        assert en and de, c
        vl = vals[c]
        for resp in sorted(vl):
            de_opt = str(vl[resp]).strip()
            assert de_opt in EN, (c, de_opt)
            rows.append({
                "table": TABLE, "section_id": f"{TABLE}_1", "item": c,
                "instrument": ("Experience of the switch to online-only university "
                               "teaching during COVID-19 (author-developed)"),
                "language": "German",
                "instructions": "", "section_prompt": "",
                "item_text": de, "correct_response": "",
                "option_text": de_opt, "resp": int(resp),
                "instructions_translated": "", "section_prompt_translated": "",
                "item_text_translated": en,
                "option_text_translated": EN[de_opt],
            })
    p = os.path.join(OUT, f"{TABLE}__items.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL,
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (r[k] if r[k] != "" else "NA") for k in COLS})
    print(f"{TABLE}__items.csv: {len(rows)} rows, "
          f"{len({r['item'] for r in rows})} items")
    # The reversal is the point of this table; show it.
    for i in (1, 2):
        c = f"Corona_{i}"
        lo = [r for r in rows if r["item"] == c and r["resp"] == 0][0]
        print(f"   {c}: resp 0 = {lo['option_text']!r} ({lo['option_text_translated']})")


if __name__ == "__main__":
    main()
