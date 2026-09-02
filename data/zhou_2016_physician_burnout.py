#!/usr/bin/env python3
"""Zhou et al. (2016), PLOS ONE -- anxiety and burnout among Chinese physicians.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0157013
DOI: 10.1371/journal.pone.0157013
Data: S1 Dataset (journal.pone.0157013.s001, SPSS .sav)
License: CC BY 4.0
Item text: shipped (the .sav carries an English variable label holding the full
    stem for all 103 item columns; value labels exist only for the four
    covariates, so response anchors come from the paper's Methods instead)

1,129 physicians from two tertiary grade-A hospitals in Heilongjiang Province,
recruited by random cluster sampling. The paper's Methods name all four
instruments and their scoring, and the .sav's variable labels carry the item
stems, so the block structure is read off the file rather than inferred:

zhou_2016_burnout          C1-C15   15 items  1-7  Chinese Maslach Burnout Inventory
zhou_2016_coping_style     E1-E20   20 items  1-5  Trait Coping Style Questionnaire
zhou_2016_personality      G1-G48   48 items  0-1  EPQ-Revised Short Scale (Chinese)
zhou_2016_anxiety          J1-J20   20 items  1-4  Zung Self-Rating Anxiety Scale

Response coding, per the Methods
--------------------------------
* CMBI: "each item is scored from 1 (never) to 7 (every day)". Reduced personal
  accomplishment items are reverse-scored in the instrument's own scoring; they
  are left as stored, which the standard allows (direction may vary across
  items so long as it is consistent within one).
* TCSQ: "each item is scored on a 5-point scale, where 1 means 'certainly not'
  and 5 means 'certainly'".
* EPQ-RSC: 48 forced-choice items stored 0/1. The .sav records no value labels
  for them and the paper does not say which code is "yes", so no option text is
  written rather than guessing the polarity.
* SAS: "each item scored on a 4-point scale (1, never or rarely; 2, some of the
  time; 3, frequently; and 4, most of the time)".

Data-entry errors dropped
-------------------------
Seven single-cell values fall outside their scale, each isolated to one item
and occurring once, against tens of thousands of legitimate responses -- the
cross-item pattern the standard describes for a keying slip rather than an
unexpected category: E2/E11/E15 have one `6` each on a 1-5 scale, J5 one `6`
and J9 one `5` on a 1-4 scale, and the 0/1 EPQ block has one `3` on each of
G8/G9/G10 and one `2` on each of G9/G12. No value recurs across items, so none
is a scale point the paper failed to mention. They are dropped, not recoded.

The paper reports 1,130 questionnaires returned and 1,129 retained "after
exclusion of invalid or missing data" -- deletion, not imputation; no
imputation language appears anywhere in the text ("imput", "MICE", "LOCF",
"mean substitution" all absent). The remaining 21 blank item cells are dropped
as ordinary item-level missingness.

The .sav has no participant id column, so `id` is the row index.

Covariates: A1 sex, A2 year of birth, A3 marital status, A4 education, A5
professional title, A6 night shift. Numeric codes are kept as stored, per the
standard; the .sav's value labels for A1/A3/A5/A6 name them (e.g. A5: 1 =
primary title .. 4 = senior title, 5 = none).
"""

from __future__ import annotations

import os
import re
import tempfile

import pandas as pd
import pyreadstat
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0157013.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")
ITEM_DIR = os.path.join(AF_DIR, "itemtext_output")

COVS = {"A1": "cov_sex", "A2": "cov_birth_year", "A3": "cov_marital_status",
        "A4": "cov_education", "A5": "cov_professional_title",
        "A6": "cov_night_shift"}
COV_COLS = list(COVS.values())

# prefix -> (table, n items, valid range, instrument, {resp: anchor})
SCALES = [
    ("C", "zhou_2016_burnout", 15, (1, 7),
     "Chinese Maslach Burnout Inventory (CMBI), 15-item revision",
     {1: "never", 7: "every day"}),
    ("E", "zhou_2016_coping_style", 20, (1, 5),
     "Trait Coping Style Questionnaire (TCSQ)",
     {1: "certainly not", 5: "certainly"}),
    ("G", "zhou_2016_personality", 48, (0, 1),
     "Eysenck Personality Questionnaire-Revised Short Scale for Chinese "
     "(EPQ-RSC)",
     {}),
    ("J", "zhou_2016_anxiety", 20, (1, 4),
     "Zung Self-Rating Anxiety Scale (SAS)",
     {1: "never or rarely", 2: "some of the time", 3: "frequently",
      4: "most of the time"}),
]


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0157013.s001.sav")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def stem(label: str, code: str) -> str:
    """Variable labels are 'C1.i feel very tried' -- drop the leading code."""
    text = re.sub(r"^\s*" + re.escape(code) + r"\s*[.．:]?\s*", "", label or "")
    return re.sub(r"\s+", " ", text).strip()


def convert() -> None:
    df, meta = pyreadstat.read_sav(fetch())
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEM_DIR, exist_ok=True)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COVS)

    for prefix, out_name, n, (lo, hi), instrument, anchors in SCALES:
        items = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in df.columns for c in items), f"{out_name}: missing columns"

        long = df.melt(id_vars=["id"] + COV_COLS, value_vars=items,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])

        # isolated single-cell values outside the documented scale: keying
        # slips, dropped rather than recoded (see module docstring)
        out_of_range = ~long["resp"].between(lo, hi)
        if out_of_range.any():
            print(f"  {out_name}: dropping {int(out_of_range.sum())} "
                  f"out-of-range cell(s) "
                  f"{sorted(long.loc[out_of_range, 'resp'].unique())}")
            long = long[~out_of_range]
        long = long.reset_index(drop=True)

        long = long[["id", "item", "resp"] + COV_COLS]
        long.to_csv(os.path.join(OUT_DIR, out_name + ".csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

        rows = []
        for code in items:
            text = stem(meta.column_names_to_labels.get(code, ""), code)
            assert text, f"{out_name}: no variable label for {code}"
            for resp in range(lo, hi + 1):
                rows.append({
                    "table": out_name,
                    "section_id": out_name + "_1",
                    "item": code,
                    "instrument": instrument,
                    "language": "Chinese",
                    "instructions": "",
                    "section_prompt": "",
                    "item_text": text,
                    "correct_response": "",
                    "option_text": anchors.get(resp, ""),
                    "resp": resp,
                    "instructions_translated": "",
                    "section_prompt_translated": "",
                    "item_text_translated": "",
                    "option_text_translated": "",
                })
        it = pd.DataFrame(rows)
        it.to_csv(os.path.join(ITEM_DIR, out_name + "__items.csv"), index=False)
        print(f"{out_name}__items: rows={len(it)} items={it['item'].nunique()}")


if __name__ == "__main__":
    convert()
