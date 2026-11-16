#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0355478
# DOI: 10.1371/journal.pone.0355478
# Paper: Lee H, Oh H, Jeong Y (2026). Conforming to AI vs. humans: The
#   moderating effects of social exclusion and task type. PLoS ONE 21(8):
#   e0355478.
# Data: PLOS SI S1 Dataset (journal.pone.0355478.s002, .xlsx, Sheet1; also
#   osf.io/74sb3), 354 Korean adults. Sheet2 shows gen 0 = 남성 (male),
#   1 = 여성 (female).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# TWO output tables, 1-5, items as answered:
#   lee_2026_social_exclusion  Social Exclusion Experience Scale (Gilman et
#     al.; Korean adaptation), 16 items: ign_1..8 (Ignored) and exc_1..8
#     (Excluded). The paper reverse-codes Excluded; the deposit holds the raw
#     answers (Ignored-Excluded mean r = -0.34), kept as answered.
#   lee_2026_loneliness  de Jong Gierveld Loneliness Scale (Korean), 11
#     items: eml_1..6 (emotional) and sol_1..5 (social; positively worded,
#     raw: sol-eml mean r = -0.30), in the deposit's interleaved order.
# Dropped: the conformity-task ratings (experiment trials) and consent items.
# Covariates: gender, age group, source_group (HU = human / AI advice
#   condition; the condition the participant was assigned to in the later
#   conformity task).
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0355478.s002"
RAW = os.environ.get("LEE2026_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_lee2026_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="Sheet1")
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, mapping, name):
    src = list(mapping)
    long = df[["id"] + covs + src].rename(columns=mapping).melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(range(1, 6))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(range(1, 6)))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert len(df) == 354
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_gender"] = df["gen"].map({0: "male", 1: "female"})
    df["cov_age_group"] = df["age_group"]
    df["cov_source_group"] = df["source_group"]
    covs = ["cov_gender", "cov_age_group", "cov_source_group"]
    sees = {f"ign0{i}": f"ign_{i}" for i in range(1, 9)}
    sees.update({f"exc0{i}": f"exc_{i}" for i in range(1, 9)})
    lone = [c for c in df.columns if c.startswith(("sol0", "eml0"))]
    assert len(lone) == 11
    save(df, covs, sees, "lee_2026_social_exclusion")
    save(df, covs, {c: c[:3] + "_" + str(int(c[3:])) for c in lone}, "lee_2026_loneliness")


if __name__ == "__main__":
    convert()
