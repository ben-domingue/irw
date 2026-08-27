#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250590
# S1 Data: https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0250590.s002&type=supplementary
# DOI: 10.1371/journal.pone.0250590
#
# Beck et al. (2021) "Prevalence and factors associated with psychological
# burden in COVID-19 patients and their relatives: A prospective
# observational cohort study." Wide-format file with one row per
# patient-relative dyad; item columns are prefixed PP_ (patient) or PR_
# (relative). Four validated instruments are shipped, each combining the
# patient and relative samples into one file with a cov_role covariate
# (the two groups are different people, not repeated measures of the same
# person, so ids are kept distinct via the source study codes):
#   - HADS (14 items, PP_D30_HADS1-14 / PR_D30_HADS1-14)
#   - IES-R (22 items, PP_D30_IESR1-22 / PR_D30_IESR1-22)
#   - PSS-10 (10 items, PP_D30_PSS_*_n / PR_D30_PSS_*_n)
#   - CD-RISC-10 (10 items, PP_RISC_1-10 / PR_RISC_1-10)
# All item columns loaded as-is are already numeric Likert codes (not
# text-coded) — the triage note's "text-coded" columns (PP_gender,
# PP_inclusion, PP_cci, etc.) are demographic/clinical covariates, not
# instrument items, and are excluded here.
# Paper reports MICE imputation was used only for the regression/prediction
# models, not for the shared raw item-level data; per-item missingness is
# still present in the raw columns (confirmed non-zero NaNs among included
# patients), consistent with this being the raw, non-imputed file.

import io
import os
import re

import pandas as pd
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_URL = ("https://journals.plos.org/plosone/article/file"
           "?id=10.1371/journal.pone.0250590.s002&type=supplementary")
UA = {"User-Agent": "irw-batch/1.0 (research)"}
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")


def fetch_raw():
    r = requests.get(RAW_URL, headers=UA, timeout=300)
    r.raise_for_status()
    return io.BytesIO(r.content)


def item_number(colname, prefix_pattern):
    m = re.search(r"(\d+)$", colname)
    return m.group(1)


def build_instrument(df, pp_cols, pr_cols, out_name):
    pp = df[["PP_id"] + pp_cols].rename(columns={"PP_id": "id"})
    pp["cov_role"] = "patient"
    pr = df[["PR_id"] + pr_cols].rename(columns={"PR_id": "id"})
    pr["cov_role"] = "relative"

    rename_pp = {c: item_number(c, None) for c in pp_cols}
    rename_pr = {c: item_number(c, None) for c in pr_cols}
    pp = pp.rename(columns=rename_pp)
    pr = pr.rename(columns=rename_pr)

    item_names = sorted(set(rename_pp.values()) | set(rename_pr.values()), key=int)

    pp_long = pp.melt(id_vars=["id", "cov_role"], value_vars=item_names,
                       var_name="item", value_name="resp")
    pr_long = pr.melt(id_vars=["id", "cov_role"], value_vars=item_names,
                       var_name="item", value_name="resp")

    long = pd.concat([pp_long, pr_long], ignore_index=True)
    long = long.dropna(subset=["id"]).reset_index(drop=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["item"] = out_name.split("_")[-1] + "_" + long["item"].astype(str)

    long = long[["id", "item", "resp", "cov_role"]]
    path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_excel(fetch_raw(), sheet_name="STATA")

    hads_pp = [c for c in df.columns if c.startswith("PP_D30_HADS")]
    hads_pr = [c for c in df.columns if c.startswith("PR_D30_HADS")]
    build_instrument(df, hads_pp, hads_pr, "beck_2021_hads")

    iesr_pp = [c for c in df.columns if c.startswith("PP_D30_IESR")]
    iesr_pr = [c for c in df.columns if c.startswith("PR_D30_IESR")]
    build_instrument(df, iesr_pp, iesr_pr, "beck_2021_iesr")

    pss_pp = [c for c in df.columns if c.startswith("PP_D30_PSS_")]
    pss_pr = [c for c in df.columns if c.startswith("PR_D30_PSS_")]
    build_instrument(df, pss_pp, pss_pr, "beck_2021_pss10")

    risc_pp = [c for c in df.columns if c.startswith("PP_RISC_")]
    risc_pr = [c for c in df.columns if c.startswith("PR_RISC_")]
    build_instrument(df, risc_pp, risc_pr, "beck_2021_cdrisc10")


if __name__ == "__main__":
    convert()
