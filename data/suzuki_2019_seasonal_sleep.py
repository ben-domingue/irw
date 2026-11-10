#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0215345
# DOI: 10.1371/journal.pone.0215345
# Paper: Suzuki M, Taniguchi T, Furihata R, Yoshita K, Arai Y, Yoshiike N,
#   Uchiyama M (2019). Seasonal changes in sleep duration and sleep problems:
#   A prospective study in Japanese community residents. PLoS ONE 14(4):
#   e0215345.
# Data: PLOS SI S3 File (journal.pone.0215345.s003, .xlsx). Rows 1-4 hold
#   code legends, rows 5-6 a two-level header (measure / season); 1,388
#   Japanese community residents aged 15-89 (Survey of Seasonal Variations
#   in Food Intakes, 2004-2007), each surveyed in spring, summer, fall and
#   winter.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# ONE output table, suzuki_2019_sleep_problems: 3 sleep-problem frequency
#   items -- dis (difficulty initiating sleep), dms_ema (difficulty
#   maintaining sleep / early morning awakening), eds (excessive daytime
#   sleepiness) -- 1 = not at all, 2 = less than once a week, 3 = once or
#   twice a week, 4 = three or more times a week; `wave` = season
#   (1 spring, 2 summer, 3 fall, 4 winter; prospective repeated measures).
#   Sleep duration (hours) is dropped.
# Covariates: sex (1 male / 2 female), age, area (1 north / 2 middle /
#   3 south).
# `id` = the deposit's running number "No." (1..1388, a study index).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0215345.s003"
RAW = os.environ.get("SUZUKI2019_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_suzuki2019_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, header=None)
    if not RAW:
        os.remove(path)
    return df


def convert():
    raw = load()
    assert [str(x).strip() for x in raw.iloc[6, :4]] == ["No.", "Sex", "Age (y)", "Area"]
    assert raw.iloc[5, 8] == "DIS" and raw.iloc[5, 12] == "DMS/EMA" and raw.iloc[5, 16] == "EDS"
    assert list(raw.iloc[6, 8:12]) == ["Spring", "Summer", "Fall", "Winter"]
    d = raw.iloc[7:].reset_index(drop=True)
    d = d[d[0].notna()].copy()
    assert len(d) == 1388 and d[0].is_unique
    base = pd.DataFrame({
        "id": d[0].astype(int),
        "cov_sex": d[1].map({1: "male", 2: "female"}),
        "cov_age": pd.to_numeric(d[2]),
        "cov_area": d[3].map({1: "north", 2: "middle", 3: "south"}),
    })
    covs = ["cov_sex", "cov_age", "cov_area"]
    parts = []
    for start, item in [(8, "dis"), (12, "dms_ema"), (16, "eds")]:
        for w in range(4):
            p = base.copy()
            p["item"] = item
            p["wave"] = w + 1
            p["resp"] = pd.to_numeric(d[start + w], errors="coerce").values
            parts.append(p)
    long = pd.concat(parts, ignore_index=True)
    long = long[long["resp"].isin([1, 2, 3, 4])].copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "suzuki_2019_sleep_problems"
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
