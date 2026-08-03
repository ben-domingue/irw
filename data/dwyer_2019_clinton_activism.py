#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0221754
# DOI: 10.1371/journal.pone.0221754
# Supporting Information: journal.pone.0221754_S1_File.sav
#
# Longitudinal study of Clinton voters around the 2016 US election.
# Two distinct instruments in the raw file:
#  - Activist Identity and Commitment Scale (8 items, 6-pt agree/disagree,
#    stored as raw codes 1-6 = "0 Strongly disagree".."5 Strongly agree").
#    Administered at baseline (T1a/T1b); values are constant across each
#    person's repeated rows in this file, so it is shipped as a single
#    cross-sectional file (no wave column) after deduplicating to one row
#    per person.
#  - CESD (20 items, 4-pt), administered at T2 and T3 (post-inauguration
#    follow-ups). The raw file already has a `Wave` column (1=T2, 2=T3)
#    with genuinely different responses across waves -> mapped to `wave`
#    2 (T2) and 3 (T3) to preserve the study's actual wave ordering
#    (T1a=1, T1b would be 1.5-ish but isn't in this file, so 2/3 keeps
#    later-is-larger without implying T1 data is present).
#
# Excluded: Sleep_quality (a single already-aggregated PSQI score; no raw
# PSQI item columns are present in the file), IOS_candidate_T1a (single-item
# pictorial closeness measure, not a multi-item scale), preDES_n1-10
# (pre-election emotion scale -- distinct construct, see note below),
# various derived/mean/centered columns (Activist_mean, CESD is itself
# both a raw-item-name prefix and a mean column -- the 20 CESD_# columns
# are the raw items; no separate CESD total column exists in this file so
# no name collision in practice), Group/Vote/check/miss/VAR00* (QC/admin
# columns, not item responses).
#
# Note: preDES_n1-10 (Modified Differential Emotion Scale, negative
# subscale) is a real raw-item scale too but is out of scope for this pass
# (not requested); left for a future batch if desired.

import io
import os
import tempfile

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file?"
          "type=supplementary&id=10.1371/journal.pone.0221754.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def _fetch_sav_path() -> str:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    # pyreadstat needs a real filesystem path, not a file-like object.
    tmp = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
    tmp.write(r.content)
    tmp.close()
    return tmp.name

CESD_COLS = [f"CESD_{i}" for i in range(1, 21)]
ACTIVIST_COLS = [f"Activist_{i}" for i in range(1, 9)]


def _save(long, out_name):
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")
    try:
        pyreadr_save(long, out_path)
    except Exception as e:
        print(f"  ({out_name} RData export skipped: {e})")


def pyreadr_save(long, out_path):
    import pyreadr
    pyreadr.write_rdata(out_path.replace(".csv", ".RData"), long, df_name="d")


def convert():
    src = _fetch_sav_path()
    try:
        df, meta = pyreadstat.read_sav(src)
    finally:
        os.unlink(src)
    df = df.rename(columns={"ID": "id", "Age": "cov_age", "Gender": "cov_gender"})
    cov_cols = ["cov_age", "cov_gender"]

    # ---- CESD (longitudinal, T2/T3) ----
    cesd = df.dropna(subset=["Wave"]).copy()
    cesd["wave"] = cesd["Wave"].map({1.0: 2, 2.0: 3})
    long_cesd = cesd.melt(
        id_vars=["id", "wave"] + cov_cols,
        value_vars=CESD_COLS,
        var_name="item",
        value_name="resp",
    )
    long_cesd["resp"] = pd.to_numeric(long_cesd["resp"], errors="coerce")
    long_cesd = long_cesd.dropna(subset=["resp"]).reset_index(drop=True)
    long_cesd = long_cesd[(long_cesd["resp"] >= 1) & (long_cesd["resp"] <= 4)]
    long_cesd = long_cesd[["id", "item", "resp", "wave"] + cov_cols]
    _save(long_cesd, "dwyer_2019_clinton_cesd.csv")

    # ---- Activist Identity and Commitment Scale (baseline, cross-sectional) ----
    activist_src = df.dropna(subset=ACTIVIST_COLS, how="all").drop_duplicates(subset=["id"])
    long_act = activist_src.melt(
        id_vars=["id"] + cov_cols,
        value_vars=ACTIVIST_COLS,
        var_name="item",
        value_name="resp",
    )
    long_act["resp"] = pd.to_numeric(long_act["resp"], errors="coerce")
    long_act = long_act.dropna(subset=["resp"]).reset_index(drop=True)
    long_act = long_act[(long_act["resp"] >= 1) & (long_act["resp"] <= 6)]
    long_act = long_act[["id", "item", "resp"] + cov_cols]
    _save(long_act, "dwyer_2019_clinton_activist.csv")


if __name__ == "__main__":
    convert()
