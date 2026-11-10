#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/FF5NYZ
# DOI (data): 10.7910/DVN/FF5NYZ
# DOI (paper): 10.3352/jeehp.2026.23.23
# Data: Seo, D. G., Choi, J., Kim, M. Y., & Huh, S. (2026). Psychometric
#   characteristics of Korean Medical Licensing Examination items from 2012 to
#   2022 analyzed using the Rasch model and 2-parameter logistic model. Journal
#   of Educational Evaluation for Health Professions, 23, 23. Harvard Dataverse
#   file "Dataset 1. Response data from the Korean Medical Licensing
#   Examination" (a zip of eleven CSVs, "<year> response dat.csv", one per
#   administration 2012-2022; columns no_1..no_K, one row per examinee, no id).
# License: CC0 1.0, verified via the Dataverse API (latestVersion.license).
#   Paper CC BY 4.0. The data come from the Korea Health Personnel Licensing
#   Examination Institute (the folder is named "국시원 문항 비공개 raw data",
#   "KHPLEI raw data, items not disclosed").
#
# Found 2026-11-10 (lane C) from a Harvard Dataverse search for JEEHP
#   deposits after the repos sweep ("medical licensing examination") reached
#   the KMLE through DVN/X2DRTE; the sweep's own triage saw FF5NYZ as
#   no_usable_file because the zip has no file extension.
#
# TEN output tables, seo_2026_kmle_<year>, one per administration: each year
#   is a different form taken by a different cohort, so the item codes no_k
#   name different items in different years and are not linked across tables.
#   resp is 0/1 (1 = correct); items keep the deposit's codes no_1..no_K.
#     2012: 450 items, 2013-2016: 400, 2018-2021: 360, 2022: 320.
#   2015: four examinees answered nothing (all 400 cells empty) and drop out.
# 2017 is NOT built here: the January 2017 KMLE already ships as
#   seo_2018_kmle from DVN/PETWZF (3,259 examinees, with the DINA Q-matrix).
#   This deposit's 2017 file is the same administration (3,263 examinees,
#   overall p = .7207 in both) with the items in a different order and no
#   Q-matrix, so shipping it too would duplicate a table.
# `id` is the row index within each year. No covariates exist.
#
# Item text: NOT SHIPPED. The items are secure licensing-exam items ("문항
#   비공개", items not disclosed).

import io
import os
import re
import sys
import zipfile

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/14118633"
EXPECT = {2012: (3364, 450), 2013: (3177, 400), 2014: (3287, 400), 2015: (3226, 400),
          2016: (3271, 400), 2017: (3263, 360), 2018: (3289, 360), 2019: (3193, 360),
          2020: (3098, 360), 2021: (3163, 360), 2022: (3305, 320)}
SKIP = {2017}


def convert():
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    files = {}
    for n in z.namelist():
        m = re.search(r"(20\d\d) response dat\.csv$", n)
        if m:
            files[int(m.group(1))] = n
    assert sorted(files) == sorted(EXPECT), sorted(files)
    os.makedirs(OUT_DIR, exist_ok=True)
    for year in sorted(files):
        d = pd.read_csv(z.open(files[year]))
        assert d.shape == EXPECT[year], (year, d.shape)
        if year in SKIP:
            continue
        items = list(d.columns)
        assert items == [f"no_{k}" for k in range(1, len(items) + 1)]
        d = d.copy()
        d.insert(0, "id", range(1, len(d) + 1))
        long = d.melt(id_vars="id", var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {0, 1}
        long = long[["id", "item", "resp"]]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [0, 1] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (year, fails)
        name = f"seo_2026_kmle_{year}"
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()} "
              f"p={long['resp'].mean():.3f}")


if __name__ == "__main__":
    convert()
