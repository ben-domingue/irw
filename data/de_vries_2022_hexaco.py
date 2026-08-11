#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0272095
# DOI: 10.1371/journal.pone.0272095
# SI file: S1 Data (SPSS .sav)
#   https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0272095.s007&type=supplementary
#
# "Self-, other-, and meta-perceptions of personality: Relations with burnout
# symptoms and eudaimonic workplace well-being" (de Vries et al., 2022).
#
# The raw SPSS file has 434 rows (one per focal employee) and 1086 columns.
# It bundles several distinct self-report/other-report instruments, all
# administered on Likert scales, identified by a facet/instrument code +
# item number + rater-slot suffix:
#   P<H|E|X|A|C|O><facet>{item}_1    -> self-rating          (n=96 HEXACO-PI-R items)
#   P<H|E|X|A|C|O><facet>{item}_21/_22/_23 -> other-rating by colleague-informant 1/2/3
#   P<H|E|X|A|C|O><facet>{item}_3    -> meta-perception rating ("my colleagues think I...")
#   P<...>{item}_1R / _21R / ... etc -> reverse-scored DUPLICATE of the same raw item
#       (verified: POaesa1_1R == 6 - POaesa1_1) -- these are dropped, we keep only
#       the original (non-R) raw response so each item is represented once.
#   batuit/batmen/batcog/batemoo{item}_1 -> BAT-23 core burnout symptoms (self-report)
#   batspan/batsoma{item}_1              -> BAT secondary symptoms (self-report)
#   EWWSinter{item}_1 / EWWSintra{item}_1 -> Eudaimonic Workplace Well-being Scale
#       (bare "EWWSinter"/"EWWSintra" columns with no item number/suffix are
#       precomputed subscale totals -- excluded)
#
# Response scales (confirmed from paper Methods):
#   HEXACO-PI-R: 1 (strongly disagree) - 5 (strongly agree)
#   BAT (core + secondary): 1 (never) - 5 (always)
#   EWWS: 1 (strongly disagree) - 5 (strongly agree)
# No imputation is described in the paper (no "imput"/"MICE"/"mean
# substitution"/"LOCF" language found); missing responses are simply NaN in
# the raw file and are dropped here.
#
# No person-ID column exists in the raw file (informed-consent/background
# columns only) -- the row index is used as `id`. Final published analytic
# sample was N=359 after listwise exclusions for the paper's own models; all
# 434 raw rows have complete HEXACO self-ratings and are retained here since
# they are genuine, non-imputed responses.

import io
import re

import pandas as pd
import pyreadstat
import requests

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0272095.s007&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

HEXACO_ITEM_RE = re.compile(r"^(P[OCAXEH][a-z]+\d+)_(1|21|22|23|3)$")

BAT_CORE_PREFIXES = ["batuit", "batmen", "batcog", "batemoo"]
BAT_SECONDARY_PREFIXES = ["batspan", "batsoma"]
EWWS_PREFIXES = ["EWWSinter", "EWWSintra"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _meta = pyreadstat.read_sav(io.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def melt_and_save(df, item_cols, out_name, extra_id_vars=None, rater_map=None):
    id_vars = ["id"] + (extra_id_vars or [])
    long = df.melt(id_vars=id_vars, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    if rater_map is not None:
        long["rater"] = long["item"].map(rater_map)
    out_cols = ["id", "item", "resp"] + (["rater"] if rater_map is not None else [])
    long = long[out_cols]
    path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(path, index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_raw()

    # ---- HEXACO-PI-R: identify raw (non-R) item columns per rater slot ----
    hexaco_cols = {"1": [], "21": [], "22": [], "23": [], "3": []}
    for c in df.columns:
        m = HEXACO_ITEM_RE.match(c)
        if m:
            hexaco_cols[m.group(2)].append(c)

    # Self-perception
    self_cols = sorted(hexaco_cols["1"])
    self_df = df[["id"] + self_cols].copy()
    for c in self_cols:
        self_df.rename(columns={c: c[:-2]}, inplace=True)  # strip "_1"
    melt_and_save(self_df, [c[:-2] for c in self_cols], "de_vries_2022_hexaco_self")

    # Meta-perception
    meta_cols = sorted(hexaco_cols["3"])
    meta_df = df[["id"] + meta_cols].copy()
    for c in meta_cols:
        meta_df.rename(columns={c: c[:-2]}, inplace=True)  # strip "_3"
    melt_and_save(meta_df, [c[:-2] for c in meta_cols], "de_vries_2022_hexaco_meta")

    # Other-perception (up to 3 colleague informants) -> stack with rater col
    other_frames = []
    for slot, rater_label in [("21", "colleague1"), ("22", "colleague2"), ("23", "colleague3")]:
        cols = sorted(hexaco_cols[slot])
        sub = df[["id"] + cols].copy()
        rename = {c: c[:-len(f"_{slot}")] for c in cols}
        sub = sub.rename(columns=rename)
        item_cols = list(rename.values())
        long = sub.melt(id_vars=["id"], value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["rater"] = rater_label
        other_frames.append(long)
    other_long = pd.concat(other_frames, ignore_index=True)[["id", "item", "resp", "rater"]]
    out_name = "de_vries_2022_hexaco_other"
    path = OUT_DIR / f"{out_name}.csv"
    other_long.to_csv(path, index=False)
    print(f"{out_name}.csv: rows={len(other_long)} ids={other_long['id'].nunique()} "
          f"items={other_long['item'].nunique()} resp={other_long['resp'].min():.0f}-{other_long['resp'].max():.0f}")

    # ---- BAT core burnout symptoms ----
    bat_core_cols = [c for c in df.columns
                      if any(c.startswith(p) for p in BAT_CORE_PREFIXES) and c.endswith("_1")]
    melt_and_save(df[["id"] + bat_core_cols], bat_core_cols, "de_vries_2022_bat_burnout_core")

    # ---- BAT secondary symptoms ----
    bat_sec_cols = [c for c in df.columns
                     if any(c.startswith(p) for p in BAT_SECONDARY_PREFIXES) and c.endswith("_1")]
    melt_and_save(df[["id"] + bat_sec_cols], bat_sec_cols, "de_vries_2022_bat_secondary")

    # ---- EWWS (eudaimonic workplace well-being) ----
    ewws_item_re = re.compile(r"^(EWWSinter|EWWSintra)\d+_1$")
    ewws_cols = [c for c in df.columns if ewws_item_re.match(c)]
    melt_and_save(df[["id"] + ewws_cols], ewws_cols, "de_vries_2022_eudaimonic_wellb")


if __name__ == "__main__":
    convert()
