#!/usr/bin/env python3
# Source: https://zenodo.org/records/20017889
# DOI: none recorded on the deposit (no related identifiers).
#   Zhu, B., & Cheng, H. (2026). "A dataset of questionnaire on the domestic
#   image of China and media use for China's post-90s and post-00s." Zenodo.
# Data: Zenodo 20017889, "SurveyData-China-Post90s.csv" (357 x 31) and
#       "SurveyData-China-Post00s.csv" (1672 x 44). The record also holds the
#       .xlsx twins of both (identical content, checked) and, per cohort, a
#       Readme PDF and the questionnaire in English and Chinese.
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# NOT MERGED, deliberately. The two cohorts did not take the same
#   instrument: post-90s has LSitem1-21, post-00s has LSitem1-25, and the
#   deposit ships a SEPARATE questionnaire PDF for each cohort. The
#   same-instrument merge rule (datastandard.md, "Confirmed identical
#   administration") needs identical items and response format; four extra
#   items is not that, and nothing in the deposit says LSitem_k is the same
#   question in both versions. So two tables, not one file on cov_study.
#
# Item text: NOT shipped here, but this is the best-placed candidate in the
#   batch and the reason is only cost. The deposit ships
#   "Questionnaire-China-Post90s.pdf" / "-Post00s.pdf" in ENGLISH plus
#   "-CN.pdf" in Chinese -- so the administered Chinese wording AND the
#   authors' own English translation both exist, which is the one
#   configuration that needs no IRW-generated translation and no issues-page
#   callout. What it needs is PDF text extraction and an item-by-item
#   alignment of 21 and 25 stems against the LSitem numbering, which the
#   Readme may or may not fix. That is a bounded piece of work on a known
#   source, not a hunt, and it is where the text is.
#
# Tables:
#   zhu_2026_china_image_post90s  LSitem1-21, 1-5, 357 respondents.
#   zhu_2026_china_image_post00s  LSitem1-25, 1-5, 1672 respondents.
#
# Dropped, with reasons (printed at run time):
#   Num / serial-num   row number -> becomes `id`
#   MUitem*            the media-use block is NOT shipped: its response
#       widths are not uniform (MUitem1-8 run 1-4, MUitem9-10 run 1-5), so
#       it is a set of independent questions rather than one scale, and
#       deciding which of them form a scale needs the deposited
#       questionnaire. In post-00s, Muitem5.A-D are additionally constant
#       columns (every value 1, 2, 3, 4 respectively) -- a multi-select
#       expansion carrying no respondent variation at all.
#   Gender, Age, Education, Employment, Location -> cov_*
# id: the file's own row-number column, prefixed per cohort ("p90-"/"p00-")
#   so the two tables' ids cannot be mistaken for each other if they are
#   ever stacked downstream.
# Covariates: cov_gender, cov_age_band, cov_education, cov_employment,
#   cov_location -- integer codes as given; the deposit's Readme names them.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/20017889/files/"
ALLOWED = {1, 2, 3, 4, 5}
COVS = {"Gender": "cov_gender", "Age": "cov_age_band",
        "Education": "cov_education", "Employment": "cov_employment",
        "Location": "cov_location"}
COHORTS = {
    "zhu_2026_china_image_post90s": ("SurveyData-China-Post90s.csv", "p90", 21, 357),
    "zhu_2026_china_image_post00s": ("SurveyData-China-Post00s.csv", "p00", 25, 1672),
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for table, (fname, tag, n_items, n_resp) in COHORTS.items():
        r = requests.get(BASE + fname.replace(" ", "%20") + "/content",
                         headers=UA, timeout=300)
        r.raise_for_status()
        d = pd.read_csv(io.BytesIO(r.content), encoding_errors="replace")
        d.columns = [str(c).lstrip("﻿").strip() for c in d.columns]
        assert d.shape[0] == n_resp, (table, d.shape)

        items = sorted((c for c in d.columns if re.fullmatch(r"LSitem\d+", c)),
                       key=lambda c: int(c[6:]))
        assert len(items) == n_items, (table, len(items))
        idcol = next(c for c in d.columns if c in ("Num", "serial-num"))
        mu = [c for c in d.columns if c.lower().startswith("muitem")]
        known = set(items) | set(COVS) | set(mu) | {idcol}
        assert set(d.columns) == known, set(d.columns) ^ known
        print(f"[{table}] {len(items)} items, {len(COVS)} covariates, "
              f"id={idcol}, {len(mu)} MUitem column(s) dropped")
        for c in mu:
            k = d[c].nunique(dropna=True)
            note = " (constant -- no variation)" if k == 1 else ""
            print(f"  [drop] {c}{note}")

        assert d[idcol].is_unique and d[idcol].notna().all()
        d["id"] = tag + "-" + d[idcol].astype(int).astype(str)
        d = d.rename(columns=COVS)
        cov_cols = list(COVS.values())
        for c in cov_cols:
            d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - ALLOWED
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == n_items
        assert long["id"].nunique() == n_resp

        checks = run_qc(long, permitted_values={i: ALLOWED for i in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [warn] {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")
        total += len(long)
    print(f"[total] {total} responses across {len(COHORTS)} tables")


if __name__ == "__main__":
    main()
