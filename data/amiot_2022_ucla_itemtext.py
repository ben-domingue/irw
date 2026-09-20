#!/usr/bin/env python3
"""Item text for amiot_2022_ucla_loneliness, from the deposit's own labels.

Source: https://www.nature.com/articles/s41598-022-10019-z (CC BY 4.0)
Data:   https://osf.io/56sbh/ -- "Leger sociodresub.sav"

mapping_basis = data_labels. The SPSS file ties every item code to its own
stem in the variable label and every `resp` value to its anchor in the value
labels, so nothing is reconstructed: `lone7`'s text is whatever `lone7`'s
label says, and resp=3 is "Sometimes" because the file says so.

Rights: shippable. `itemtext/instrument_rights_register.csv` carries the
UCLA Loneliness Scale as `ship` (2026-09-20) -- the quote test found no
restriction to quote, and Fetzer's own UCLA pages reproduce the scale with no
permission, copyright or distribution statement at all, in pointed contrast
to the DSES copy in the same collection.

Two things the labels need handling for:

1. SPSS truncates a variable label at 256 characters, and these labels are
   "<code>: <stem> - <block instruction>", so the instruction tail is cut on
   most items. The stem always survives (it comes first) and is taken from
   the label directly. The instruction is reconstructed from `lone4`, whose
   short stem leaves the label under the limit so its instruction is intact;
   every other item's truncated instruction is checked to be a prefix of it.

2. 418 of the 2,424 respondents (17.2%) chose to answer in French, so the
   administration is bilingual. The deposit contains only the English
   wording, so `language` lists both and the base fields hold English, per
   the multi-language rule in itemtext_standard.md. The French version is not
   recoverable from the deposit and is NOT invented; that is what the
   public_note records.
"""
import csv
import sys
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
TABLE = "amiot_2022_ucla_loneliness"
SECTION = f"{TABLE}_1"
DATA_URL = ("https://osf.io/download/2wpxc/"
            "?view_only=bbca7561fdff46618666454a0d66c892")
UA = {"User-Agent": "irw-batch/1.0 (research)"}
SAV = Path("/tmp/irw_amiot_itemtext.sav")

INSTRUMENT = "UCLA Loneliness Scale (Version 3), Russell (1996)"
LANGUAGE = "English; French"
FIELDS = ["table", "section_id", "item", "instrument", "language",
          "instructions", "section_prompt", "item_text", "correct_response",
          "option_text", "resp"]
ITEMS = [f"lone{i}" for i in range(1, 21)]


def main() -> None:
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    SAV.write_bytes(r.content)
    _, meta = pyreadstat.read_sav(str(SAV), metadataonly=True)
    SAV.unlink()

    labels = {c: meta.column_names_to_labels[c] for c in ITEMS}

    # lone4's label is short enough to escape SPSS's 256-char truncation, so
    # it carries the block instruction in full.
    full = labels["lone4"].split(" - ", 1)[1].strip()
    assert full.endswith("during the COVID-19 pandemic."), full

    stems, seen = {}, set()
    for code, lab in labels.items():
        head, instr = lab.split(" - ", 1)
        prefix, stem = head.split(": ", 1)
        assert prefix == code, f"{code}: label names {prefix}"
        assert full.startswith(instr.strip()), (
            f"{code}: instruction is not a prefix of lone4's full text")
        stem = stem.strip()
        assert stem not in seen, f"{code}: duplicate stem, would conflate items"
        seen.add(stem)
        stems[code] = stem

    options = meta.variable_value_labels["lone1"]
    for code in ITEMS:
        assert meta.variable_value_labels[code] == options, (
            f"{code}: different anchors from lone1")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{TABLE}__items.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL,
                           lineterminator="\n")
        w.writeheader()
        for code in ITEMS:
            for value, text in sorted(options.items()):
                w.writerow({
                    "table": TABLE, "section_id": SECTION, "item": code,
                    "instrument": INSTRUMENT, "language": LANGUAGE,
                    "instructions": full, "section_prompt": "NA",
                    "item_text": stems[code], "correct_response": "NA",
                    "option_text": text, "resp": int(value),
                })
    print(f"{out.name}: {len(ITEMS)} items x {len(options)} options = "
          f"{len(ITEMS) * len(options)} rows")


if __name__ == "__main__":
    sys.exit(main())
