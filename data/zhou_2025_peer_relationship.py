#!/usr/bin/env python3
"""Zhou et al. (2025), PLOS One -- peer relationships and physical activity intention.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0320845
DOI: 10.1371/journal.pone.0320845
Data: S1 Data (journal.pone.0320845.s001, XLSX)
License: CC BY 4.0
Item text: not shipped. The spreadsheet's item columns are bare integers
    (5..57) with no label row, and the article reproduces no item wording --
    only each scale's anchors. All four instruments are Chinese-language
    published scales cited in the Methods (Wei Yunhua's Peer Relationship
    Scale; the physical activity intention subscale of Liang Deqing et al.'s
    Physical Activity Rating Scale; Ye Yuemei & Dai Xiaoyang's Social Support
    Rating Scale; the Chen et al. revision of Motl et al.'s Exercise
    Self-Efficacy Scale), so the text is in those, not in this source.

514 Chinese college students. Four instruments in one questionnaire, all on the
same 1-5 agreement scale:

zhou_2025_peer_relationship        PR1-PR20    20 items  1-5
zhou_2025_social_support           SS1-SS17    17 items  1-5
zhou_2025_exercise_self_efficacy   ESE1-ESE8    8 items  1-5
zhou_2025_pa_intention             PAI1-PAI8    8 items  1-5

Reading the layout
------------------
The header row is a mix of covariate names and bare integers: `Gender`,
`Grade`, `Age`, then `5`..`24`, then a column literally named
`peer relationship`, then `25`..`41`, `social support`, `42`..`49`,
`Exercise self-efficacy`, `50`..`57`, and
`Behavioural intentions for physical activity`. The four named columns are
subscale scores, not items -- each is exactly the arithmetic mean of the
integer-named block immediately before it (verified numerically, not assumed),
which is what fixes the block boundaries. They are excluded as composites.

Three of the four block sizes match the Methods exactly -- peer relationship
"contains 20 questions", social support "consists of total of 17 questions",
exercise self-efficacy "consists of 8 questions". The fourth does not: the
Methods describe the physical activity intention subscale as having "a total of
12 questions", but the deposit's final block has 8 columns, and the totals
column confirms the mean is taken over those 8. The 8 that exist are shipped
and the discrepancy is left standing rather than reconciled by guesswork.

Item names are assigned per scale (PR/SS/ESE/PAI, in column order) because the
source names are bare integers, which carry position but no instrument
identity. The mapping is column 5-24 -> PR1-PR20, 25-41 -> SS1-SS17,
42-49 -> ESE1-ESE8, 50-57 -> PAI1-PAI8.

Response coding, per the Methods
--------------------------------
Each scale is a 5-point Likert scale with its own wording for the anchors
(peer relationship: 1 = not at all correct .. 5 = completely correct; social
support: 1 = not at all .. 5 = in full line with; exercise self-efficacy:
1 = complete disagreement .. 5 = complete agreement; PA intention: 1 = very
non-compliant .. 5 = very much compliant). All 53 item columns are integers
1-5 with no missing cells, no out-of-range values and no sentinel codes, so
nothing is filtered. The paper describes no imputation ("imput", "missing
data", "MICE", "LOCF", "mean substitution" all absent from the text).

The file has no participant id column, so `id` is the row index.

Covariates: `Gender` (1-2), `Grade` (1-3) and `Age` (a 1-5 band code). None of
the three codings is documented in the deposit or the paper, so the raw codes
are kept as stored.
"""

from __future__ import annotations

import os
import tempfile

import pandas as pd
import requests

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0320845.s001")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "..", "automated_finding")
OUT_DIR = os.path.join(AF_DIR, "irw_output")

COVS = {"Gender": "cov_gender", "Grade": "cov_grade", "Age": "cov_age_band"}
COV_COLS = list(COVS.values())

# table -> (source column numbers, item code prefix, name of the composite
#           column that follows the block and must equal its row mean)
TABLES = [
    ("zhou_2025_peer_relationship", range(5, 25), "PR", "peer relationship"),
    ("zhou_2025_social_support", range(25, 42), "SS", "social support"),
    ("zhou_2025_exercise_self_efficacy", range(42, 50), "ESE",
     "Exercise self-efficacy"),
    ("zhou_2025_pa_intention", range(50, 58), "PAI",
     "Behavioural intentions for physical activity"),
]


def fetch() -> str:
    path = os.path.join(tempfile.gettempdir(), "pone.0320845.s001.xlsx")
    if not os.path.exists(path):
        r = requests.get(SRC_URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def convert() -> None:
    d = pd.read_excel(fetch())
    os.makedirs(OUT_DIR, exist_ok=True)

    d = d.rename(columns=COVS).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    for out_name, cols, prefix, composite in TABLES:
        src_cols = list(cols)
        assert all(c in d.columns for c in src_cols), f"{out_name}: missing columns"
        # the block boundary is only trustworthy if the trailing named column
        # really is this block's mean -- check it rather than assume it
        assert (d[src_cols].mean(axis=1) - d[composite]).abs().max() < 1e-9, \
            f"{out_name}: '{composite}' is not the mean of {src_cols[0]}-{src_cols[-1]}"

        codes = [f"{prefix}{i}" for i in range(1, len(src_cols) + 1)]
        wide = d[["id"] + COV_COLS + src_cols].rename(
            columns=dict(zip(src_cols, codes)))

        long = wide.melt(id_vars=["id"] + COV_COLS, value_vars=codes,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert long["resp"].between(1, 5).all(), f"{out_name}: resp outside 1-5"

        long = long[["id", "item", "resp"] + COV_COLS]
        long.to_csv(os.path.join(OUT_DIR, out_name + ".csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
