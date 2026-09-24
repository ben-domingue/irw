#!/usr/bin/env python3
# Source: https://bmcpublichealth.biomedcentral.com/articles/10.1186/s12889-022-14147-z
# DOI: 10.1186/s12889-022-14147-z
# "Validity and reliability of knowledge, attitude, and practice regarding
# exercise and exergames experiences questionnaire among high school students"
# (Abdulkader Mohamed, Abdul Rahim, Mohamad & Ahmad Yusof, 2022), BMC Public
# Health 22:1743.
# Data: 12889_2022_14147_MOESM1_ESM.xlsx (Additional file 1, the ONLY
#       supplementary file on the article), fetched via the Europe PMC
#       supplementaryFiles endpoint for PMC9472413.
# License: CC BY 4.0 (BMC; Europe PMC full-text <license> element). Article-
#          attached SI, so the article licence is the source licence.
#
# Item text: shipped for all three tables (the workbook's column headers ARE
#   the full English item stems; the questionnaire was administered in English
#   per Methods; anchors are the cell values). Codes are positional -- see the
#   ITEM MAP below, which records header -> code.
#
# Layout: one sheet, 188 rows x 33 columns, one row per respondent, headers are
# the question wording, cells are the response labels. No id, no demographics
# (Part 1 of the questionnaire is not in the deposit). id = row index.
#
# Tables (split by ADMINISTERED block, i.e. by the response format each block
# was given -- Methods: "three-point Likert scale (agree, neutral, disagree) for
# the knowledge domain, a five-point scale ... for the attitude domain, (yes, no,
# open answer) for participation domain, and (yes, no) for experiences domain"):
#   abdulkader_mohamed_2022_exer_knowledge  cols 0-8,   9 items, 1-3
#   abdulkader_mohamed_2022_exer_attitude   cols 9-18, 10 items, 1-5
#   abdulkader_mohamed_2022_exergame_exp    cols 28-32, 5 items, 0/1
# The paper's EFA (Table 4) afterwards MOVED items between domains (two
# attitude items into knowledge, two knowledge items into attitude) and dropped
# three attitude items and one experience item. That is a post-hoc scoring
# model; it mixes 3- and 5-point items, so the tables follow the administered
# blocks and keep every administered item. Dictionary Notes say so.
#
# Coding: knowledge Disagree=1, Netural(sic)=2, Agree=3 (agreement with the
# statement, NOT right/wrong -- several statements are false, e.g. "Exercise
# does more harm than good"; direction differs across items, which is allowed).
# Attitude strongly disagree=1 .. strongly agree=5. Experiences no=0, yes=1.
#
# Skipped: cols 19-27, the practice (participation) block -- three yes/no
# screeners ("Do you walk ... at least 10 minutes"), each followed by days per
# week (0-7) and minutes per day (0-480). Those are GPAQ-style behaviour
# counts, not responses on a common ordinal scale, and the screeners are
# logically nested with their own day counts. Not item-response data.
#
# Duplicates: rows 72 and 74 are exact copies (all 33 columns, including the
# free minute counts) of rows 70 and 63 -- double submissions of the online
# link. The later copy is dropped, leaving 186 respondents.
#
# Header typos: the workbook's headers have had every "no" replaced with "2"
# ("e2ugh", "2rmal", "k2w", "I have 2 time") -- a find-and-replace artefact.
# Irrelevant to the response table (codes are positional); corrected in the
# item text and disclosed there.

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9472413/supplementaryFiles"
XLSX = "12889_2022_14147_MOESM1_ESM.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

KNOW = {"Disagree": 1, "Netural": 2, "Agree": 3}
ATT = {"strongly disagree": 1, "disagree": 2, "neither agree nor disagree": 3,
       "agree": 4, "strongly agree": 5}
YN = {"no": 0, "yes": 1}

# (table, column positions, code prefix, value map, permitted values)
BLOCKS = [
    ("abdulkader_mohamed_2022_exer_knowledge", range(0, 9), "know", KNOW, [1, 2, 3]),
    ("abdulkader_mohamed_2022_exer_attitude", range(9, 19), "att", ATT, [1, 2, 3, 4, 5]),
    ("abdulkader_mohamed_2022_exergame_exp", range(28, 33), "exg", YN, [0, 1]),
]
SKIPPED = {i: "practice block: yes/no screener + days/week + minutes/day "
              "behaviour counts, not ordinal item responses" for i in range(19, 28)}


def load() -> pd.DataFrame:
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(XLSX))
                with z.open(name) as fh:
                    return pd.read_excel(BytesIO(fh.read()))
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


def item_map(df):
    """code -> source header, for every shipped item (the positional map)."""
    out = {}
    for _, cols, pfx, _, _ in BLOCKS:
        for k, j in enumerate(cols, start=1):
            out[f"{pfx}_{k}"] = df.columns[j]
    return out


def convert() -> None:
    raw = load()
    assert raw.shape == (188, 33), raw.shape

    # Books: every column is in exactly one block or skipped with a reason.
    used = {j for _, cols, *_ in BLOCKS for j in cols}
    assert used.isdisjoint(SKIPPED) and used | set(SKIPPED) == set(range(33))
    for j, why in SKIPPED.items():
        print(f"  [skip] col {j} {raw.columns[j][:50]!r}: {why}")

    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)
    dup = raw.drop(columns="id").duplicated(keep="first")
    assert sorted(raw.index[dup]) == [72, 74], raw.index[dup].tolist()
    print(f"  [drop] rows {raw.index[dup].tolist()}: exact 33-column copies "
          "of rows 70/63 (double submission)")
    raw = raw[~dup].reset_index(drop=True)
    raw["id"] = raw.index + 1

    for code, hdr in item_map(raw.drop(columns="id")).items():
        print(f"  {code:7s} <- {hdr[:70]}")

    written = set()
    for table, cols, pfx, vmap, permitted in BLOCKS:
        src = [raw.columns[j + 1] for j in cols]  # +1: id inserted at 0
        d = raw[["id"] + src].copy()
        d.columns = ["id"] + [f"{pfx}_{k}" for k in range(1, len(src) + 1)]
        long = d.melt(id_vars=["id"], var_name="item", value_name="resp_lbl")
        lbl = long["resp_lbl"].astype(str).str.strip()
        if vmap is ATT:
            lbl = lbl.str.lower()
        long["resp"] = lbl.map(vmap)
        unmapped = long.loc[long["resp"].isna(), "resp_lbl"].unique()
        assert len(unmapped) == 0, f"{table}: unmapped labels {unmapped}"
        long = long[["id", "item", "resp"]].copy()
        long["resp"] = long["resp"].astype(int)
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].isin(permitted).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(src) > 1

        bad = [c for c in run_qc(long, permitted_values=permitted)
               if c.status == "fail"]
        assert not bad, (table, [(c.name, c.detail) for c in bad])
        report = irw_validate.validate_frame(long, label=table, profile="upload")
        assert report.conforms and not report.errors, \
            [(f.name, f.detail) for f in report.errors]

        assert table not in written, f"duplicate output name {table}"
        written.add(table)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():g}-{long['resp'].max():g}")


if __name__ == "__main__":
    convert()
