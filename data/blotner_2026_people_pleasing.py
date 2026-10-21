#!/usr/bin/env python3
# Source: https://osf.io/4n8sk/ (public companion node)
# DOI (paper): 10.1007/s12144-026-09519-2  -- Current Psychology 45, Article 952, CC BY 4.0
# DOI (data):  none issued; OSF node carries no node-level license, licence
#              inherited from the CC BY 4.0 article, as for blotner_2023_sd4_*.
#
# Blotner, C. (2026), "Valuing others over oneself: development and validation
# of a people pleasing scale in two German samples." Two raw files, both German
# samples:
#
#   Study 1  data_PP_S1.csv  (https://osf.io/download/vth7k/)  2,031 rows
#   Study 2  dataS2.csv      (https://osf.io/download/bm8tc/)  1,427 rows
#
# Five instruments are co-administered across the two files, each written here
# as its own table. Item labels are the deposit's own column names (including
# the authors' `_R` suffix on reverse-keyed items) so they join to the source
# codebook; responses are left as administered -- reverse-keyed items are NOT
# recoded (datastandard: direction may vary across items).
#
# People Pleasing Scale: Study 1 is the 15-item pool, administered to a 670-row
# subsample of that file -- the other 1,361 rows answered only the HEXACO
# domains, so the file holds two sub-samples and the PPS table keeps just the
# 670. Study 2 re-administered the same 15-item pool. Item-to-subscale keying
# for the final 10-item scale is taken from the authors' own CFA in
# "R script People Pleasing_S1.R":
#   Responsibility        PP12 PP13 PP14
#   Neglect of own needs  PP3 PP5 PP8 PP15
#   Others' expectations  PP2 PP7 PP11
# The five pool items not retained (PP1 dropped a priori, PP4/PP6/PP9/PP10 for
# cross-loadings) are kept and marked itemcov_subscale = not_retained.
#
# HEXACO: the German HEXACO-60, 10 items per domain. Study 1 administered three
# domains (HH, A, N) to all 2,031 respondents; Study 2 administered all six to
# all 1,427, so the single table is a planned-missing cross of the two samples.
# NOTE the deposit's prefixes are not mnemonic in English: `E*` is eXtraversion
# and `N*` is Emotionality. Confirmed from the facet keying in both R scripts
# (fit_E = SE/bold/soc/live on E*, fit_N = fear/anx/dep/sent on N*), which is
# identical across the two studies -- hence one table, with cov_study.
#
# LSRP (primary 16 + secondary 10, 1-4), Basic Empathy Scale (affective 11 +
# cognitive 9, 1-5) and the SVO Slider (6 items, 1-9 ordered allocations) were
# administered in Study 2 only.
#
# Not carried over: the four `Endowment_*` columns (continuous money
# allocations from the ultimatum/dictator games, between-subjects so ~710
# missing each) are behavioural outcomes, not scale items; the attention-check
# and seriousness-check columns are used for exclusions, not shipped as items;
# and the pre-computed subscale means in the R scripts are composites.
#
# Exclusions, following the authors' own scripts:
#   Study 1  Check4 == 4            (plus Check1 == 1 for the PPS table)
#   Study 2  Check4 == 4 and seriousness_check == 1
#   both     18 <= age <= 100
# The age bounds reproduce the published rule -- "participants were excluded if
# they reported an age below 18 years ... One participant reporting an
# implausible age (198 years) was also excluded" -- which the deposited R
# scripts only partly implement (no age filter at all in Study 1). With them,
# the PPS table yields 571 Study 1 and 1,323 Study 2 respondents, matching the
# paper's reported n1 = 571 and n2 = 1,323 exactly.
# `resp` of 0 in Study 1 is a no-answer sentinel, not a scale point: the scale
# is 1-5 per the paper, Study 2 stores the same scales as 1-5, and 0 occurs
# 1-9 times per column against hundreds per real category. Dropped.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
S1_URL = "https://osf.io/download/vth7k/"
S2_URL = "https://osf.io/download/bm8tc/"

SEX = {1: "male", 2: "female", 3: "diverse"}  # 4 = "n/a" -> missing
EDU = {
    1: "none",
    2: "lower vocational",
    3: "vocational",
    4: "some college",
    5: "university",
    6: "other",
}
STUDENT = {1: "yes", 2: "no"}

COV_COLS = ["cov_study", "cov_age", "cov_sex", "cov_education", "cov_student"]

PPS_SUBSCALE = {
    12: "responsibility", 13: "responsibility", 14: "responsibility",
    3: "neglect_own_needs", 5: "neglect_own_needs",
    8: "neglect_own_needs", 15: "neglect_own_needs",
    2: "others_expectations", 7: "others_expectations", 11: "others_expectations",
}

# HEXACO-60 facet keying, read off the CFA models in both R scripts.
HEXACO_DOMAIN = {
    "HH": "honesty_humility",
    "E": "extraversion",
    "N": "emotionality",
    "A": "agreeableness",
    "C": "conscientiousness",
    "O": "openness",
}
HEXACO_FACET = {
    "HH": {1: "sincerity", 5: "sincerity", 9: "sincerity",
           2: "fairness", 6: "fairness", 10: "fairness",
           3: "greed_avoidance", 7: "greed_avoidance",
           4: "modesty", 8: "modesty"},
    "E": {1: "social_self_esteem", 5: "social_self_esteem", 9: "social_self_esteem",
          2: "social_boldness", 6: "social_boldness", 10: "social_boldness",
          3: "sociability", 7: "sociability",
          4: "liveliness", 8: "liveliness"},
    "N": {1: "fearfulness", 5: "fearfulness", 9: "fearfulness",
          2: "anxiety", 6: "anxiety",
          3: "dependence", 7: "dependence",
          4: "sentimentality", 8: "sentimentality", 10: "sentimentality"},
    "A": {1: "forgiveness", 5: "forgiveness",
          2: "gentleness", 6: "gentleness", 9: "gentleness",
          3: "flexibility", 7: "flexibility", 10: "flexibility",
          4: "patience", 8: "patience"},
    "C": {1: "organization", 5: "organization",
          2: "diligence", 6: "diligence",
          3: "perfectionism", 7: "perfectionism", 9: "perfectionism",
          4: "prudence", 8: "prudence", 10: "prudence"},
    "O": {1: "aesthetic_appreciation", 5: "aesthetic_appreciation",
          2: "inquisitiveness", 6: "inquisitiveness",
          3: "creativity", 7: "creativity", 9: "creativity",
          4: "unconventionality", 8: "unconventionality", 10: "unconventionality"},
}

RE_PPS = re.compile(r"^PP(\d+)$")
RE_HEXACO = re.compile(r"^(HH|O|C|A|E|N)(\d+)(_R)?$")
RE_SVO = re.compile(r"^SVO(\d+)$")
RE_LSRP = re.compile(r"^LSRP_(prim|sec)(\d+)(_R)?$")
RE_BES = re.compile(r"^BES_(A|C)(\d+)(_R)?$")


def fetch(url: str, label: str) -> pd.DataFrame:
    print(f"Downloading {label} ...")
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def prepare(df: pd.DataFrame, study: int) -> pd.DataFrame:
    """Attach id/covariates and apply the authors' exclusions."""
    df = df.rename(columns={df.columns[0]: "row"})
    df["id"] = f"s{study}_" + df["row"].astype(int).astype(str)

    keep = df["Check4"] == 4
    if study == 2:
        keep &= df["seriousness_check"] == 1
    keep &= df["age"].between(18, 100)
    print(f"  study {study}: {len(df)} rows -> {int(keep.sum())} after exclusions")
    df = df[keep].copy()

    df["cov_study"] = study
    df["cov_age"] = df["age"]
    df["cov_sex"] = df["sex"].map(SEX)
    df["cov_education"] = df["edu"].map(EDU)
    df["cov_student"] = df["student"].map(STUDENT)
    return df


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    long = df.melt(
        id_vars=["id"] + COV_COLS,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"] > 0]  # drops NA and the Study 1 zero sentinel
    long["resp"] = long["resp"].astype(int)
    long["cov_age"] = long["cov_age"].astype("Int64")
    return long


def finish(long: pd.DataFrame, extra: list[str] | None = None) -> pd.DataFrame:
    cols = ["id", "item", "resp"] + COV_COLS + (extra or [])
    out = (long[cols]
           .sort_values(["cov_study", "id", "item"], kind="stable")
           .reset_index(drop=True))
    if out["cov_study"].nunique() == 1:
        # Study-2-only instruments: a constant covariate carries no
        # information, and the sample is already visible in the id prefix.
        out = out.drop(columns="cov_study")
    return out


def match_items(df: pd.DataFrame, pattern: re.Pattern) -> list[str]:
    return [c for c in df.columns if pattern.match(c)]


def convert() -> None:
    s1 = prepare(fetch(S1_URL, "data_PP_S1.csv"), 1)
    s2 = prepare(fetch(S2_URL, "dataS2.csv"), 2)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tables: dict[str, pd.DataFrame] = {}

    # --- People Pleasing Scale, 15-item pool, both samples -----------------
    # Study 1 administered the pool to a subsample; Check1 is the pool block's
    # own attention check and is missing for everyone who did not see it.
    pps_1 = s1[s1["Check1"] == 1]
    parts = []
    for part in (pps_1, s2):
        items = match_items(part, RE_PPS)
        parts.append(build_long(part, items))
    pps = pd.concat(parts, ignore_index=True)
    pps["itemcov_subscale"] = (pps["item"].str.extract(RE_PPS)[0].astype(int)
                               .map(PPS_SUBSCALE).fillna("not_retained"))
    tables["blotner_2026_people_pleasing.csv"] = finish(pps, ["itemcov_subscale"])

    # --- HEXACO-60, three domains in study 1, all six in study 2 -----------
    parts = []
    for part in (s1, s2):
        parts.append(build_long(part, match_items(part, RE_HEXACO)))
    hexaco = pd.concat(parts, ignore_index=True)
    key = hexaco["item"].str.extract(RE_HEXACO)
    domain, number = key[0], key[1].astype(int)
    hexaco["itemcov_domain"] = domain.map(HEXACO_DOMAIN)
    hexaco["itemcov_facet"] = [HEXACO_FACET[d][n] for d, n in zip(domain, number)]
    tables["blotner_2026_hexaco60.csv"] = finish(
        hexaco, ["itemcov_domain", "itemcov_facet"])

    # --- Study 2 only ------------------------------------------------------
    lsrp = build_long(s2, match_items(s2, RE_LSRP))
    lsrp["itemcov_subscale"] = lsrp["item"].str.extract(RE_LSRP)[0].map(
        {"prim": "primary", "sec": "secondary"})
    tables["blotner_2026_lsrp.csv"] = finish(lsrp, ["itemcov_subscale"])

    bes = build_long(s2, match_items(s2, RE_BES))
    bes["itemcov_subscale"] = bes["item"].str.extract(RE_BES)[0].map(
        {"A": "affective", "C": "cognitive"})
    tables["blotner_2026_bes.csv"] = finish(bes, ["itemcov_subscale"])

    tables["blotner_2026_svo.csv"] = finish(build_long(s2, match_items(s2, RE_SVO)))

    for fname, out in tables.items():
        out.to_csv(OUT_DIR / fname, index=False)
        print(f"{fname}: rows={len(out)} ids={out['id'].nunique()} "
              f"items={out['item'].nunique()} "
              f"resp={out['resp'].min()}-{out['resp'].max()}")


if __name__ == "__main__":
    convert()
