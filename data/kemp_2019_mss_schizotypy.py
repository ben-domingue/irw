#!/usr/bin/env python3
# Source: https://osf.io/xjgyd/
# DOI (data): 10.17605/OSF.IO/XJGYD
# DOI (paper): 10.1080/00223891.2019.1591425
# Kemp, Gross & Kwapil (2019/2020), "Psychometric Properties of the
# Multidimensional Schizotypy Scale and Multidimensional Schizotypy
# Scale-Brief: Item and Scale Test-Retest Reliability and Concordance of
# Original and Brief Forms", Journal of Personality Assessment.
#
# Study 1 (n=245, MTurk) completed the full-length MSS (77 items) at T1 and
# T2 (~2-7 week retest interval). Study 2 (3 independently-recruited
# samples, A/B/C, total n=339) completed the actual MSS-Brief item subset
# at T1; samples B and C were also given the full-length MSS at T2 to test
# concordance between forms (PubMed abstract, PMID 31012748). Item wording
# for every shared item code (e.g. DIS001) is byte-identical across all
# four raw files' data dictionaries -- confirming the same fixed 77-item
# MSS item bank underlies every sample, just with different subsets
# administered per sample/wave. The MSS has three subscales that reflect
# distinct schizotypy dimensions (Disorganized/Negative/Positive) and are
# reported separately in the paper, so each becomes its own IRW file per
# datastandard.md's "one file per scale (or subscale treated as a distinct
# construct)" rule; within each subscale file the four samples are merged
# (id offset per sample) since the underlying item content is confirmed
# identical wherever it overlaps.
#
# Raw item values are already binary-scored per the data dictionary's
# header note: "MSS items are scored: 1 = schizotypic response,
# 0 = nonschizotypic response" -- confirmed 0/1-only across all four files.
#
# Sex/EFL ("English as first language") coding: the dictionary documents
# "0 = male, 1 = female" and "0 = no, 1 = yes" identically in all four
# sheets, but Study 2 Samples A and B actually store these as {1, 2} in
# the raw .sav (Study 1 and Sample C use {0, 1}). Recoded A/B down by 1 so
# cov_sex/cov_efl are consistent with the documented scale across the
# merged file (order-preserving: lower code stays "male"/"no").

import io
import os
import re
import pyreadstat
import pandas as pd
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# (OSF direct-download URL, cov_study label, per-sample id offset, has real T1/T2 dates)
SAMPLES = [
    ("https://osf.io/download/j24xq/", "study1",          0,      True),   # Study 1 sample
    ("https://osf.io/download/vc4uj/", "study2_sampleA",  100000, False),  # Study 2 Sample A
    ("https://osf.io/download/y27r8/", "study2_sampleB",  200000, False),  # Study 2 Sample B
    ("https://osf.io/download/ezyfx/", "study2_sampleC",  300000, False),  # Study 2 Sample C
]

SUBSCALES = {
    "kemp_2019_mss_disorganized": "DIS",
    "kemp_2019_mss_negative":     "NEG",
    "kemp_2019_mss_positive":     "POS",
}


def _load_sample(url, study_label, id_offset, has_dates):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    df.columns = [c.upper() for c in df.columns]

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1 + id_offset)

    # Normalize sex/EFL to the documented 0/1 scale where the raw file
    # instead used {1, 2} (Samples A and B; see header note).
    for cov in ("SEX", "EFL"):
        col = f"T1_{cov}"
        if col in df.columns and set(df[col].dropna().unique()) == {1.0, 2.0}:
            df[col] = df[col] - 1

    waves = []
    for t, wave_num in (("T1", 1), ("T2", 2)):
        age_col = f"{t}_AGE"
        if age_col not in df.columns:
            continue
        wdf = pd.DataFrame({
            "id": df["id"],
            "wave": wave_num,
            "cov_study": study_label,
            "cov_age": df[age_col],
            "cov_sex": df["T1_SEX"],
            "cov_ethnic": df["T1_ETHNIC"],
            "cov_efl": df["T1_EFL"],
        })
        if "INTERVAL" in df.columns:
            wdf["cov_retest_interval_days"] = df["INTERVAL"]
        date_col = f"{t}_DATE"
        if has_dates and date_col in df.columns:
            wdf["date"] = df[date_col].astype("int64") // 10**9  # Unix seconds
        # item columns present for this wave
        item_pat = re.compile(rf"^{t}_(DIS|NEG|POS)(\d{{3}})$")
        for c in df.columns:
            m = item_pat.match(c)
            if m:
                wdf[f"{m.group(1)}{m.group(2)}"] = df[c]
        waves.append(wdf)

    return pd.concat(waves, ignore_index=True)


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_samples = [_load_sample(url, label, offset, has_dates)
                   for url, label, offset, has_dates in SAMPLES]
    merged = pd.concat(all_samples, ignore_index=True)

    id_vars = ["id", "wave", "cov_study", "cov_age", "cov_sex", "cov_ethnic",
               "cov_efl"]
    id_vars += [c for c in ("cov_retest_interval_days", "date") if c in merged.columns]

    for out_name, prefix in SUBSCALES.items():
        item_cols = [c for c in merged.columns if c.startswith(prefix)]
        long = merged.melt(id_vars=id_vars, value_vars=item_cols,
                            var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        cov_cols = [c for c in id_vars if c not in ("id", "wave", "date")]
        out_cols = ["id", "item", "resp", "wave"]
        if "date" in id_vars:
            out_cols.append("date")
        out_cols += cov_cols
        long = long[out_cols]

        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
