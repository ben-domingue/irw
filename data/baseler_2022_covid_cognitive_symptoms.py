#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0269353
# DOI: 10.1371/journal.pone.0269353
# Paper: Baseler HA, Aksoy M, Salawu A, Green A, Asghar AUR (2022). The
#   negative impact of COVID-19 on working memory revealed using a rapid
#   online quiz. PLoS ONE 17(11): e0269353.
# Data: PLOS Supporting Information S1 File (journal.pone.0269353.s001,
#   "Participants data"), 5,428 adults who took the online survey and memory
#   quiz, mostly UK.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 4.
#
# TWO output tables. The survey asked "During the COVID-19 pandemic, have you
# had MORE problems with: ..." for 16 functions, each rated None / Mild /
# Moderate / Severe (the paper), stored 1-4. The paper's principal-components
# analysis separates the cognitive items from the sensory ones, and the
# deposit's own column prefixes do the same:
#   baseler_2022_cognitive  9 items (remembering things, concentrating on
#     simple tasks, concentrating on complex tasks, having a conversation,
#     thinking quickly, thinking clearly, getting tired easily after mental
#     effort, low mood, fatigue)
#   baseler_2022_sensory    7 items (vision, hearing, smell, taste, touch or
#     pain, balance, dizziness)
# Item codes are the deposit's column names cut at the first line break
#   (the examples in brackets dropped) and lower-cased, e.g.
#   memory_remembering_things.
# Covariates: age range, the deposit's codes 1-8 labelled with the paper's
#   eight bands in order (18-24 ... 85+).
# Dropped: the participant code ("Response IDs", P01...; replaced by the row
#   index); the COVID group (codes 1-4) and gender (codes 8-11), neither
#   labelled in the deposit; country and UK region codes (2026-10-20
#   geography ruling); the symptom checkboxes, vaccination and the durations;
#   the memory-quiz total score (a single score, no item-level quiz data).
# `id` is the row index.
#
# Item text: NOT SHIPPED. The column names hold the wording; the stem and
#   response labels are in the article.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0269353.s001"
RAW = os.environ.get("BASELER_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
AGE = {1: "18-24", 2: "25-34", 3: "35-44", 4: "45-54", 5: "55-64", 6: "65-74", 7: "75-84", 8: "85+"}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name="S1_data")


def convert():
    df = load()
    assert df.shape == (5428, 42), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == ["Response IDs"]
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    assert set(df["Age_range"]) <= set(AGE)
    df["cov_age_range"] = df["Age_range"].map(AGE)
    covs = ["cov_age_range"]
    code = {c: c.split("\n")[0].strip().lower() for c in df.columns if str(c).startswith(("Memory_", "Sensory_"))}
    groups = {"cognitive": [c for c in code if c.startswith("Memory_")],
              "sensory": [c for c in code if c.startswith("Sensory_")]}
    assert len(groups["cognitive"]) == 9 and len(groups["sensory"]) == 7
    for name, cols in groups.items():
        sub = df[["id"] + covs + cols].rename(columns=code)
        items = [code[c] for c in cols]
        long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4}
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"baseler_2022_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} {items[:3]}")


if __name__ == "__main__":
    convert()
