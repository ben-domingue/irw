#!/usr/bin/env python3
# Source: https://doi.org/10.5068/D17D58 (Dryad), mirrored at
#   https://zenodo.org/records/6532900
# DOI: 10.5068/D17D58 (data); paper 10.1177/19485506221094086
# Paper: Manson JH, Chua KJ, Rodriguez NN, Barlev M, Durkee PK, Lukaszewski AW
#   (2022). Sex differences in fearful personality traits are mediated by
#   physical strength. Social Psychological and Personality Science 14:763-771.
# Data: five undergraduate samples (Sample_1..Sample_5_corrected.csv) with
#   README_Manson-et-al_corrected.txt, which gives every item's wording, the
#   keying, and the covariate codes. Samples 1-2 UC Santa Barbara; 3 Oklahoma
#   State; 4 UT Austin; 5 Arizona State.
# License: CC0 1.0 (verified on the Dryad/Zenodo record).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3), worked
# from leads/repos_leads_2026-11-02.csv the same day (BATCH_LOG.md).
#
# TWO output tables (two different instruments, so not merged):
#   manson_2022_ipip_hexaco_emo  Samples 1-2 (n = 175 + 209), the 40
#     IPIP-HEXACO Emotionality items (anxiety, emotional dependence,
#     fearfulness, sentimentality; e_anx_1..e_sen_10), 7-point scale, raw
#     answers (items 6-10 of anxiety, fearfulness and sentimentality are
#     negatively keyed and NOT reversed). cov_study = sample.
#   manson_2022_hexaco100_emo  Samples 3-5 (n = 370 + 340 + 305), the 16
#     HEXACO-100 Emotionality items (hex_5 .. hex_95), 5-point scale, raw
#     answers (29, 35, 41, 59, 77, 89, 95 are reverse-keyed and NOT
#     reversed). cov_study = sample.
#   Direction: higher = more agreement. The README does not print the anchors,
#   so this is checked on the data: in every sample women score higher than
#   men on the positively keyed items and lower on the negatively keyed ones,
#   the paper's central and well-replicated sex difference.
#   SAMPLE 4 IS DEPOSITED WITH ITS SEVEN REVERSE-KEYED ITEMS ALREADY REVERSED:
#   on all seven both the sex difference and the correlation with a same-facet
#   forward item have the opposite sign from Samples 3 and 5 (checked below).
#   They are put back to raw answers here (6 - x), so the stacked table is on
#   one coding. Sample 4's 7 blank cells are dropped.
# Covariates: female (README: 1 = female, 0 = male), age where recorded,
#   grip strength (kg), chest strength (kg; Samples 1-3). Ethnicity is not
#   carried: its codes differ by sample and Sample 4/2 have none.
# `id` is "s<sample>_<p_id>" (p_id repeats across samples). Sample 3's p_id is
#   a lab code (PLH001 ...); its two rows the authors marked EXCL are dropped.
#
# Item text: not shipped. The README holds every stem (IPIP items are public
#   domain; HEXACO-100 items are Lee & Ashton's), but not the response
#   anchors of either scale, so option rows could not be written.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW_DIR = os.environ.get("MANSON_RAW_DIR", ".")
IPIP = [f"e_{s}_{k}" for s in ["anx", "dep", "fear", "sen"] for k in range(1, 11)]
HEX = [f"hex_{k}" for k in [5, 11, 17, 23, 29, 35, 41, 47, 53, 59, 65, 71, 77, 83, 89, 95]]
HEX_R = ["hex_29", "hex_35", "hex_41", "hex_59", "hex_77", "hex_89", "hex_95"]
FILES = {1: "Sample_1.csv", 2: "Sample_2.csv", 3: "Sample_3.csv", 4: "Sample_4.csv", 5: "Sample_5_corrected.csv"}
NON_ITEM = {"p_id", "age", "female", "ethnicity", "grip", "chest"}


def sex_gap(d, cols):
    g = d.groupby("female")[cols].mean()
    return g.loc[1] - g.loc[0]


def load(sample):
    d = pd.read_csv(os.path.join(RAW_DIR, FILES[sample]))
    txt = [c for c in d.columns if pd.api.types.is_string_dtype(d[c])]
    print(f"PII screen sample {sample}: {len(txt)} text columns of {len(d.columns)} examined: {txt}")
    assert len(d.columns) > 0 and set(txt) <= {"p_id"}
    if txt:  # lab codes: Sample 3 PLH001 ... (two rows marked EXCL by the authors), Sample 5 e.g. 312A
        assert d["p_id"].str.fullmatch(r"(PLH|EXCL)?\d{3}[AB]?").all()
        d = d[~d["p_id"].str.startswith("EXCL")].copy()
    assert d["p_id"].is_unique
    items = IPIP if sample <= 2 else HEX
    assert set(d.columns) - NON_ITEM == set(items), sample
    if sample >= 3:
        gap = sex_gap(d, HEX_R)
        if sample == 4:
            assert (gap > 0).all(), gap
            assert d["hex_5"].corr(d["hex_29"]) > 0
            d[HEX_R] = 6 - d[HEX_R]
        assert (sex_gap(d, HEX_R) < 0).all(), sample
        assert d["hex_5"].corr(d["hex_29"]) < 0
    d["id"] = [f"s{sample}_{p}" for p in d["p_id"]]
    d["cov_study"] = f"sample {sample}"
    d["cov_female"] = d["female"].astype(int)
    d["cov_age"] = d["age"] if "age" in d else pd.NA
    d["cov_grip_kg"] = d["grip"]
    d["cov_chest_kg"] = d["chest"] if "chest" in d else pd.NA
    return d, items


def build(samples, permitted, name):
    covs = ["cov_study", "cov_female", "cov_age", "cov_grip_kg", "cov_chest_kg"]
    frames = []
    for s in samples:
        d, items = load(s)
        frames.append(d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp"))
    long = pd.concat(frames, ignore_index=True).dropna(subset=["resp"])
    assert set(long["resp"]) <= set(permitted)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: list(permitted) for c in long["item"].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
    return long


def convert():
    out = {"manson_2022_ipip_hexaco_emo": build([1, 2], range(1, 8), "ipip"),
           "manson_2022_hexaco100_emo": build([3, 4, 5], range(1, 6), "hex100")}
    os.makedirs(OUT_DIR, exist_ok=True)
    for t, long in out.items():
        long.to_csv(os.path.join(OUT_DIR, f"{t}.csv"), index=False)
        print(f"{t}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
