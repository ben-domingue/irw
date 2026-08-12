#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11067892
# DOI: 10.7717/peerj.17265
#
# Abdullah et al. (2024), "Structural equation models of health
# behaviour, psychological well-being, symptom severity and quality of
# life in abdominal bloating." PeerJ. CC BY 4.0. N=323.
#
# The raw file bundles item-reduced item sets from several distinct named
# instruments (per the paper's Instruments section):
#   - HB-Bloat (health belief for bloating, Abdullah et al. 2020), a
#     32-item scale with 3 subscales: attitudes (13 items, file retains
#     A1/A7/A10), subjective norm (8 items, file retains
#     SN2/3/5/6/8), perceived behavioural control (11 items, file retains
#     PCB6/7/9). 1-5 Likert, strongly agree(1)-strongly disagree(5).
#   - HPB-Bloat (health promoting behaviour for bloating), 35 items over
#     5 subscales: diet (D1-3), health awareness (HA1/2/4), physical
#     activity (PA2-4), stress management (SM2/4/8), alternative
#     treatment (T3-5). 1-5 Likert, never(1)-very often(5).
#   - BSQ-M (Malay Bloating Severity Questionnaire): general severity
#     (SevGen, sevG_1/SEVG_3-7, item-specific ranges per the paper: items
#     1/3/4/5/6 are 1-5, item 7 is 1-7 -- item 2 is not in the file) and
#     past-24h severity (Sev24, SEV24_1-5, 1-5 except item5 which is
#     1-8 per the paper). `SEV24_1_1` is dropped: it correlates -1.0 with
#     SEV24_1 (an exact reverse-coded duplicate of the same raw item, not
#     a second item).
#   - SS-Bloat (social support), SS1-6, 1-5 Likert.
#   - BLQoL-M (Malay Bloating Quality of Life), QOL1_R-QOL5_R, 1-7
#     Likert.
#
# Excluded as single-item constructs (datastandard.md / no-single-item-
# scale policy): I1 (the standalone "intention" item) and P5 (an isolated
# item with no paired items under its own code, unclear subscale
# membership from the paper text).
# Excluded as aggregates: meanBELIEVE_2020, meanSN_2020, meanPCB_2020,
# DIET, HA, PA, SM, TRE, total_Anxiety, total_depression,
# total_IPAQ_new_dev1000, SEVG, SEV24, QOL, meanHADS, meanSS (all
# pre-computed subscale/scale totals -- note HADS's raw items are not in
# the file at all, only its aggregate total, so HADS cannot be shipped
# from this file).
#
# Two isolated out-of-stated-range values (data-entry errors, dropped
# per datastandard.md): sevG_1 has a single 6 (item 1 is documented 1-5,
# 1 of 323 respondents), SS3 has a single 6 (SS-Bloat is documented 1-5,
# 1 of 323 respondents).
#
# Covariates (age, sex, BMI, living area) carried through; no PII.

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11067892/supplementaryFiles"
MEMBER = "peerj-12-17265-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "abdullah_2024_bsq_sevgen": (["sevG_1", "SEVG_3", "SEVG_4", "SEVG_5", "SEVG_6", "SEVG_7"], (1, 7)),
    "abdullah_2024_bsq_sev24": (["SEV24_1", "SEV24_2", "SEV24_3", "SEV24_4", "SEV24_5"], (1, 8)),
    "abdullah_2024_hbbloat_attitude": (["A1", "A7", "A10"], (1, 5)),
    "abdullah_2024_hbbloat_subjnorm": (["SN2", "SN3", "SN5", "SN6", "SN8"], (1, 5)),
    "abdullah_2024_hbbloat_pbc": (["PCB6", "PCB7", "PCB9"], (1, 5)),
    "abdullah_2024_hpbbloat_diet": (["D1", "D2", "D3"], (1, 5)),
    "abdullah_2024_hpbbloat_awareness": (["HA1", "HA2", "HA4"], (1, 5)),
    "abdullah_2024_hpbbloat_physact": (["PA2", "PA3", "PA4"], (1, 5)),
    "abdullah_2024_hpbbloat_stress": (["SM2", "SM4", "SM8"], (1, 5)),
    "abdullah_2024_hpbbloat_treat": (["T3", "T4", "T5"], (1, 5)),
    "abdullah_2024_ssbloat": (["SS1", "SS2", "SS3", "SS4", "SS5", "SS6"], (1, 5)),
    "abdullah_2024_blqol": (["QOL1_R", "QOL2_R", "QOL3_R", "QOL4_R", "QOL5_R"], (1, 7)),
}

COV_RENAME = {
    "age": "cov_age",
    "sex": "cov_sex",
    "BMI": "cov_bmi",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_spss(tmp.name)

    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    assert df["id"].nunique() == len(df)

    cov_lookup = {c.lower(): c for c in df.columns}
    cov_cols = []
    for src, out in COV_RENAME.items():
        match = cov_lookup.get(src.lower())
        if match:
            df = df.rename(columns={match: out})
            cov_cols.append(out)

    for out_name, (items, (lo, hi)) in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
