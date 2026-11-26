#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/tv6w6yyfy8/1
# DOI: 10.17632/tv6w6yyfy8.1 (data)
#   Rexand-Galais F, Pithon L (2022). Dataset assessing three samples of French university students to
#   5 personality tests: IPO, PDQ-4+, PANAS, AQ and HADS [Data set]. Mendeley Data, V1.
# License: CC BY 4.0 (Mendeley Data)
# Data (Angers University psychology / arts students, 2021-2022; each workbook has a title row above
#   the header):
#   Study 1 Sample 1.xlsx (269 first-years) and Study 1 Sample 2.xlsx (333 second-years): the French
#     translation of Kernberg's Inventory of Personality Organization, PD1-16 primitive defenses,
#     ID1-21 identity diffusion, RT1-20 reality testing; same codes in both files, columns in a
#     different order. Collapsed into one table with cov_sample (same instrument and format).
#   Study 3 V4.xlsx (607 students): the 40-item IPO-fr developed from Studies 1-2, "IPO PD/ID1-30" and
#     "IPO RT1-10" (the deposit's IPO Codebook V2.pdf prints each item with this code). The deposited
#     IPO PD/ID score equals the sum of its 30 items in every row (IPO RT in 606 of 607).
#   All items 1 Jamais vrai .. 5 Toujours vrai (codebook).
# Tables: rexandgalais_2022_ipo (item = PD1..RT20), rexandgalais_2022_ipo_fr (item = pdid_1..30,
#   rt_1..10, from "IPO PD/ID<k>" / "IPO RT<k>").
# id: within-file row order, prefixed by sample (s1_, s2_, s3_). Study 3's respondents are a different
#   cohort; nothing links them to Study 1.
# Covariates: cov_age, cov_gender (as written; "Unspecified" kept), cov_sample (ipo only).
# Not shipped: Study 2 (scale scores only), the PDQ-4+ grouping, deposited totals.
# Item text: not shipped -- the IPO-fr wording is in the deposit's codebook PDF with explicit codes, but
#   the IPO is a third-party instrument (Clarkin, Kernberg et al.) with no register row.
import io
import json
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
BASE = "https://data.mendeley.com/public-files/datasets/tv6w6yyfy8/files/{}/file_downloaded"
FILES = {"s1": "b1431478-cb80-472f-9e05-87c3c3a928b1", "s2": "1e83f3d9-390e-48b0-ad79-eedbf17880d2",
         "s3": "a0935dbc-99a6-4a0a-bca6-46e5bd4f2d95"}


def get(fid):
    r = requests.get(BASE.format(fid), timeout=120)
    r.raise_for_status()
    c = r.content
    if c[:8] == b'{"url":"':  # Mendeley sometimes answers with a signed-URL redirect document
        c = requests.get(json.loads(c)["url"], timeout=120).content
    d = pd.read_excel(io.BytesIO(c), header=1)
    d.columns = [str(x).strip() for x in d.columns]
    return d


def ship(name, t, covs):
    t = t.dropna(subset=["resp"])
    assert t["resp"].isin([1, 2, 3, 4, 5]).all(), name
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(OUT / f"{name}.csv", index=False)
    print(name, len(t), t.id.nunique(), t.item.nunique())


def main():
    items = [f"PD{i}" for i in range(1, 17)] + [f"ID{i}" for i in range(1, 22)] + [f"RT{i}" for i in range(1, 21)]
    parts = []
    for s, label, n in [("s1", "first-year (Sample 1)", 269), ("s2", "second-year (Sample 2)", 333)]:
        d = get(FILES[s])
        assert len(d) == n and set(items) <= set(d.columns)
        d["id"] = [f"{s}_{i}" for i in range(1, len(d) + 1)]
        d["cov_age"] = d["Age"]
        d["cov_gender"] = d["Gender"].str.strip()
        d["cov_sample"] = label
        parts.append(d[["id", "cov_age", "cov_gender", "cov_sample"] + items])
    d = pd.concat(parts, ignore_index=True)
    covs = ["cov_age", "cov_gender", "cov_sample"]
    ship("rexandgalais_2022_ipo", d.melt(id_vars=["id"] + covs, var_name="item", value_name="resp"), covs)

    d = get(FILES["s3"])
    assert len(d) == 607
    rename = {f"IPO PD/ID{i}": f"pdid_{i}" for i in range(1, 31)} | {f"IPO RT{i}": f"rt_{i}" for i in range(1, 11)}
    assert set(rename) <= set(d.columns)
    assert (d[list(rename)[:30]].sum(axis=1) == d["IPO PD/ID"]).all()
    d = d.rename(columns=rename)
    d["id"] = [f"s3_{i}" for i in range(1, len(d) + 1)]
    d["cov_age"] = d["Age"]
    d["cov_gender"] = d["Gender"].str.strip()
    covs = ["cov_age", "cov_gender"]
    t = d[["id"] + covs + list(rename.values())].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    ship("rexandgalais_2022_ipo_fr", t, covs)


if __name__ == "__main__":
    main()
