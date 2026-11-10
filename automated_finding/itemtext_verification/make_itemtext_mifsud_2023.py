#!/usr/bin/env python3
"""Item text for mifsud_2023_worldviews (10.1371/journal.pone.0288451, PLOS SI
S1 .sav, CC BY 4.0).

Source, level 1: the .sav variable labels, completed from the article's Table 3
(four labels are truncated at SPSS's label length). Each of the five vignette variables
is labelled with the worldview's name in capitals followed by the vignette as
shown, e.g. "LOCALISED The future depends on us and the choices we make. ...".
The response table (data/mifsud_2023_worldviews_values.py) takes the item code
from that same leading word, lower-cased, so code and text are tied at the
source; the builder strips the name and asserts the code set.

Instructions and anchors from the article's Methods: participants rated "the
extent to which they believed that each vignette applied to themselves using a
Likert scale ranging from 1 (not at all) to 5 (completely)"; 2-4 unlabelled,
blank. The instructions field paraphrases that sentence (the exact on-screen
prompt is not deposited), so it is left blank and the anchors carry the scale.

Rights: the vignettes were written for this research ("created and eventually
refined through a preliminary study", Methods) -- study-authored, under the
article's CC BY 4.0. English administration (Prolific, OECD residents).

Run: RAW=<path to s001 .sav> RESP_DIR=<irw_output dir> python3 make_itemtext_mifsud_2023.py
"""
import csv
import os
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt", "item_text",
        "correct_response", "option_text", "resp"]
# Full vignettes, transcribed from the article's Table 3 (an image), which
# names each vignette's worldview. Four .sav labels are cut at SPSS's label
# length; each label must be a prefix of its Table 3 text (asserted), so the
# label ties the code and the table supplies the cut-off tail.
TABLE3 = {
    "localised": "The future depends on us and the choices we make. Every problem has a solution. Each and every one of us can make an effort to fix the laws and institutions so that they can be just and equal for everyone. Like this we can better address the needs of people and society.",
    "orthodox": "To succeed in life, we need to follow the rules and local customs in order to maintain social order. We also need to show respect to each other and carry out our duties. Like this we can help others in our community.",
    "pragmatist": "In life we must adapt ourselves to our circumstances and sometimes we need to go with the flow in order to avoid trouble. The rich and powerful protect their own interests, whereas the kind-hearted suffer. Sometimes you have to work around the rules to help your loved ones.",
    "reward": "In life, you get what you deserve. Life's challenges are overcome with the efforts we make, and these may offer new opportunities. One must co-operate with others, respect authority, and carry out one's duties. Our efforts will eventually lead to success.",
    "survivor": "In life, things rarely end up well. People are what they are, and good people usually suffer and are exploited. It is best for one to keep his/her head down and get on with it.",
}
WV = ["LOCALISED", "PRAGMATIST", "ORTHODOX", "REWARD", "SURVIVOR"]
TABLE = "mifsud_2023_worldviews"


def main():
    _, meta = pyreadstat.read_sav(os.environ["RAW"], metadataonly=True)
    texts = {}
    for lab in meta.column_names_to_labels.values():
        first = (lab or "").split(" ")[0]
        if first in WV:
            texts[first.lower()] = lab[len(first):].strip()
    assert len(texts) == 5
    for k, lab in texts.items():
        assert TABLE3[k].startswith(lab), k
    texts = dict(TABLE3)
    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    assert set(resp["item"]) == set(texts)
    anchors = {1: "not at all", 5: "completely"}
    rows = []
    for code in WV:
        code = code.lower()
        for v in range(1, 6):
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                         "instrument": "Worldview vignettes (Mifsud & Sammut 2023)", "instructions": "",
                         "section_prompt": "", "item_text": texts[code], "correct_response": "",
                         "option_text": anchors.get(v, ""), "resp": v})
    assert {r["resp"] for r in rows} >= set(resp["resp"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / f"{TABLE}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{TABLE}__items.csv: {len(rows)} rows")


if __name__ == "__main__":
    main()
