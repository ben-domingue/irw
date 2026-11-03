#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0354474
# DOI: 10.1371/journal.pone.0354474
# Paper: Elsokkary EM (2026). Psychometric properties of the Arabic Perceived
#   Digital Well-Being Scale (PDWS) in Saudi young adults. PLOS ONE.
# Data: Zenodo 10.5281/zenodo.18882971 (CC BY 4.0, verified on the deposit
#   record itself): EFA.sav and CFA.sav, 225 + 225 Saudi adults aged 18-25,
#   Riyadh, online survey March-May 2025, administered in Arabic.
#   PDWS_Codebook.xlsx and README_PDWS_Zenodo.txt document every variable.
# License: CC BY 4.0 (deposit; the article is CC BY 4.0 too).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 5, BATCH_LOG.md).
#
# ONE output table, both files stacked with cov_subsample: the paper says the
# 450 participants were "randomly split into two independent analytic
# subsamples", so the two files are one administration of one instrument
# (and no row appears in both):
#   elsokkary_2026_pdws  Perceived Digital Well-Being Scale, 17 bipolar
#     items, E1-E7 emotional, S8-S13 social, C14-C17 cognitive; 1 = left
#     pole .. 5 = right pole, higher = better digital well-being, no
#     reverse-coded items under this coding (README).
# Composites Emotional, Social, Cognitive, PDWS, SWLS and FoMO (totals of
#   two convergent measures whose items are not in the deposit) not shipped.
# Covariates (value labels): gender, age (years, fractional as deposited),
#   education, marital status, subsample (EFA / CFA).
# `id` is "efa_<row>" / "cfa_<row>".
#
# Item text: NOT SHIPPED. The English PDWS (both poles of every item) is
#   S1 Appendix of the article (journal.pone.0354474.s001, CC BY 4.0); the
#   administered Arabic wording is not in the deposit.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW_DIR = os.environ.get("ELSOKKARY_RAW_DIR", ".")
ITEMS = [f"E{i}" for i in range(1, 8)] + [f"S{i}" for i in range(8, 14)] + [f"C{i}" for i in range(14, 18)]
COMPOSITES = {"Emotional", "Social", "Cognitive", "PDWS", "SWLS", "FoMO"}
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Education": "cov_education", "Marital_Status": "cov_marital_status"}


def convert():
    parts, raw_frames = [], []
    for sub in ["EFA", "CFA"]:
        df, meta = pyreadstat.read_sav(os.path.join(RAW_DIR, f"{sub}.sav"))
        assert df.shape == (225, 27), df.shape
        txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
        print(f"PII screen [{sub}]: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
        assert len(df.columns) > 0 and txt == []
        assert set(df.columns) == set(ITEMS) | COMPOSITES | set(COVS)
        raw_frames.append(df[ITEMS + ["Age", "Gender"]])
        df = df.copy()
        df["id"] = [f"{sub.lower()}_{i}" for i in range(1, len(df) + 1)]
        for s, t in COVS.items():
            lab = meta.variable_value_labels.get(s)
            df[t] = df[s].map(lab) if lab else df[s]
        df["cov_subsample"] = sub
        covs = list(COVS.values()) + ["cov_subsample"]
        parts.append(df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp"))
    assert raw_frames[0].merge(raw_frames[1]).empty
    long = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "elsokkary_2026_pdws.csv"), index=False)
    print(f"elsokkary_2026_pdws: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
