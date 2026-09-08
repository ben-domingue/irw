#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133254
# DOI: 10.1371/journal.pone.0133254
# Data: S1 File (xlsx, sheet "data")
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0133254.s001
# License: CC BY 4.0 (PLOS ONE)
#
# Miron-Shatz et al. (2015), "Milestone Age Affects the Role of Health and
# Emotions in Life Satisfaction". N=810 across four sites (Columbus OH,
# France, Denmark, Austin TX).
#
# The deposit's header is four stacked rows, which is why automatic triage
# could not map it: row 0 is a section banner ("DEPENDENT VARIABLES",
# "DEMOGRAPHICS", "VALUES/ATTITUDES"), row 1 is the full item wording, row 2
# a partial survey-question name, and row 3 the short variable code that the
# data rows are keyed to. This script reads with header=None and takes row 3
# as the column names and row 1 as the item text.
#
# Nine item blocks, each a distinct instrument or question set:
#
#   st1-st5            Satisfaction With Life Scale (Diener), 5 items, 1-7
#   ay-jy              overall feeling yesterday, 10 mood adjectives, 0-6
#   v5exp*-v8exp*      happy / tired / tense across four day types (typical
#                      working weekday, non-working weekday, Sunday,
#                      Saturday), 12 items, 0-6. Sparse by design: the v5
#                      (working weekday) items were asked only of
#                      respondents in work.
#   self1-self12       self-description adjectives, 12 items, -3 to 3
#   joy1-joy33         33 life domains rated as a source of joy, 1-3
#   pain1-pain33       the same domains rated as a source of pain, 1-3.
#                      NOTE the two lists are not the same 33 domains -- joy
#                      has "Creative hobbies", "Home improvement, gardening"
#                      and "Your future career" where pain has "Hobbies
#                      around house & garden" and "The politics of the
#                      country" -- so they are kept as separate tables with
#                      their own item text rather than merged on an assumed
#                      correspondence.
#   pair1-pair6        paired comparisons against "most people", 6 items, 0/1
#   cheerful/friendly/polite/intel
#                      what the respondent wishes most for their child or
#                      grandchild, 4 items, 1-4
#   state1-state7      beliefs about happiness, 7 items, 1-4
#
# Excluded as composites, not responses: satscale (sum of st1-st5), diener,
# mood (weighted mood sum), ntaffy (net affect), negself / posself /
# neg_self / pos_self / affdisp (averages over the self* adjectives),
# SumPair (sum of the paired comparisons), and the dwa-dwj duration-weighted
# recodes of the ay-jy adjectives.
#
# Item text: not shipped, and this is the one deposit in the batch where that
# is a close call worth writing down. The stems ARE here -- row 1 carries the
# full English wording for every item, and this script assigns the item codes,
# so the join key would be known rather than reconstructed, which is the
# expensive part. Two things stop it:
#
#   1. Administered language. The study ran at four sites (Columbus OH,
#      France, Denmark, Austin TX). Row 1 is English throughout, but the
#      French and Danish respondents did not answer English items, and the
#      deposit carries no translated wording -- there is a `d2` (US education
#      levels) / `d2f` (France education levels) split that shows the
#      instrument was localised. Shipping row 1 as the administered text for
#      all 810 respondents would assert something false for two of the four
#      sites. Language is a schema rule owned by itemtext_standard.md, not
#      something to improvise here.
#   2. No response-option wording anywhere in the deposit, so `option_text`
#      would be NA for every row of every table.
#
# Held for a proper irw-auto-itemtext pass with itemtext_standard.md in hand.
# The wording is at row 1 of the "data" sheet of S1 File, keyed to the row 3
# variable codes this script already uses as `item` -- a later pass starts
# from that mapping, not from a re-derivation. Separately, st1-st5 are the
# Satisfaction With Life Scale, a third-party instrument, and would stay held
# on rights grounds even once the language question is settled.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0133254.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "country": "cov_country",   # 1 Columbus, 2 France, 3 Denmark, 4 Austin
    "age":     "cov_age",
    "d2":      "cov_education",
    "d3":      "cov_marital_status",
}

DAY_AFFECT = [f"v{v}exp{i}" for v in (5, 6, 7, 8) for i in (1, 2, 3)]

# out_name -> (item columns, valid resp range)
SCALES = {
    "mironshatz_2015_swls":
        (["st1", "st2", "st3", "st4", "st5"], (1, 7)),
    "mironshatz_2015_mood_yesterday":
        (list("abcdefghij"), (0, 6)),          # expanded to ay..jy below
    "mironshatz_2015_day_type_affect":
        (DAY_AFFECT, (0, 6)),
    "mironshatz_2015_self_description":
        ([f"self{i}" for i in range(1, 13)], (-3, 3)),
    "mironshatz_2015_sources_of_joy":
        ([f"joy{i}" for i in range(1, 34)], (1, 3)),
    "mironshatz_2015_sources_of_pain":
        ([f"pain{i}" for i in range(1, 34)], (1, 3)),
    "mironshatz_2015_paired_comparison":
        ([f"pair{i}" for i in range(1, 7)], (0, 1)),
    "mironshatz_2015_child_wishes":
        (["cheerful", "friendly", "polite", "intel"], (1, 4)),
    "mironshatz_2015_happiness_beliefs":
        ([f"state{i}" for i in range(1, 8)], (1, 4)),
}
SCALES["mironshatz_2015_mood_yesterday"] = (
    [f"{c}y" for c in "abcdefghij"], (0, 6))


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = requests.get(SI_URL, headers=UA, timeout=180)
    raw.raise_for_status()
    book = pd.read_excel(io.BytesIO(raw.content), sheet_name="data", header=None)

    codes = [str(x).strip() for x in book.iloc[3].tolist()]

    df = book.iloc[4:].reset_index(drop=True)
    df.columns = codes
    df = df.rename(columns={"pid2": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    if df["id"].nunique() != len(df):
        raise SystemExit("pid2 is not unique")
    df["id"] = df["id"].astype(int)
    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    for out_name, (item_cols, (lo, hi)) in SCALES.items():
        missing = [c for c in item_cols if c not in df.columns]
        if missing:
            raise SystemExit(f"{out_name}: missing columns {missing}")
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")



if __name__ == "__main__":
    convert()
