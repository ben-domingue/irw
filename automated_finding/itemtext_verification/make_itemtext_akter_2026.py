"""Item text for the seven akter_2026_* tables, from the .sav's own labels.

Source: "Final Data.sav" in https://bridges.monash.edu/articles/dataset/33183470
(CC BY 4.0). mapping_basis=data_labels: the file ties each item code to its
stem through `column_names_to_labels`, and each block's anchors through
`variable_value_labels`. Both levels are present for every shipped item, so
there is no positional step anywhere in the chain.

Administered in English, so `language` and the `_translated` columns are left
out entirely, as the standard requires for an English administration.

Only anchors a respondent actually used get an option row: the schema defines
`resp` as a value present in the response data, and validate_items.R enforces
it as a set match.

Run:  python3 make_itemtext_akter_2026.py <sav> <out_dir> <staged_response_dir>
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pyreadstat

SAV = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
RESP_DIR = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("../irw_output")

BLOCKS = {
    "akter_2026_climate_social_norms": (
        "Social_norms_Q", "Climate-change social norms, Akter 2026"),
    "akter_2026_climate_incentives": (
        "Perceived_Incentives_Q", "Perceived government incentives, Akter 2026"),
    "akter_2026_climate_self_efficacy": (
        "Self_efficacy_Q", "Climate-change self-efficacy, Akter 2026"),
    "akter_2026_climate_risk_perception": (
        "Risk_Perception_Q", "Climate-change risk perception, Akter 2026"),
    "akter_2026_climate_adaptation": (
        "Adaptation_to_Climate_Change_Q",
        "Adaptation to climate change, Akter 2026"),
    "akter_2026_proenv_private_behaviour": (
        "Pro_Envo_Private_Behav_Q",
        "Private-sphere pro-environmental behaviour, Akter 2026"),
    "akter_2026_proenv_public_behaviour": (
        "Pro_Envo_Public_Behav_Q",
        "Public-sphere pro-environmental behaviour, Akter 2026"),
}

COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def observed(table):
    out = {}
    with open(RESP_DIR / f"{table}.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.setdefault(r["item"], set()).add(int(r["resp"]))
    return out


def main():
    _, meta = pyreadstat.read_sav(str(SAV), metadataonly=True)
    labels, vlabels = meta.column_names_to_labels, meta.variable_value_labels
    OUT.mkdir(parents=True, exist_ok=True)
    for table, (prefix, instrument) in BLOCKS.items():
        seen = observed(table)
        cols = sorted((c for c in meta.column_names
                       if re.fullmatch(rf"{re.escape(prefix)}\d+", c)),
                      key=lambda c: int(re.sub(r"\D", "", c)))
        rows = []
        for c in cols:
            stem = (labels.get(c) or "").strip()
            assert stem, c
            anchors = vlabels.get(c) or vlabels.get(cols[0]) or {}
            assert anchors, c
            for value, text in sorted(anchors.items()):
                resp = int(value)
                if resp not in seen[c.lower()]:
                    continue
                rows.append({
                    "table": table, "section_id": f"{table}_1",
                    "item": c.lower(), "instrument": instrument,
                    "instructions": "", "section_prompt": "",
                    "item_text": stem, "correct_response": "",
                    "option_text": text, "resp": resp})
        path = OUT / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"  -> {path.name}: {len(rows)} rows, {len(cols)} items")


if __name__ == "__main__":
    main()
