#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0204494
# DOI: 10.1371/journal.pone.0204494
# Supporting Information: Study 1 https://doi.org/10.1371/journal.pone.0204494.s004
#                         Study 2 https://doi.org/10.1371/journal.pone.0204494.s005
#
# Two studies comparing traditional vs. virtual-reality perspective-taking
# interventions about homelessness. The paper's Methods text confirms the
# Interpersonal Reactivity Index (IRI, 3 of its 4 subscales present here --
# Empathic Concern/Perspective Taking/Personal Distress, 7 items each) and
# the 12-item Beliefs about Empathy scale (C1-6 + IT1-6, 7-point) were
# administered identically pre-intervention in both studies, so both are
# combined into single cross-study files (Study 2's id offset by 1000 to
# keep the combined id space unique; source PID strings collide across
# unrelated respondents in both studies -- confirmed by mismatched ages on
# the same PID string -- so row index is used as id instead per
# datastandard.md's uniqueness fallback). cov_study (1/2) and cov_condition
# (the raw group code -- Study 1: 1=traditional/NPT, 2=VR/VRPT; Study 2:
# 1=traditional, 2=desktop, 3=VR, 4=control/fact-only, per the Methods
# text) are carried as covariates rather than `treat`, since Study 2 has
# 4 arms, not a simple treatment/control pair.
# `SJ1-8` (Study 2 only, 1-9 scale) matches the paper's 7-item "Attitudes
# toward the Homeless" scale on both Likert range and topic (the 7-vs-8
# item-count mismatch is a likely off-by-one in the paper's own count,
# not re-verified against the raw questionnaire). `SE1-4`/`D1-4` (Study 2
# only) could not be matched to a named instrument in the text and are
# kept as their own file under their original source labels. The
# Inclusion of Other in the Self scale (`ios`) and the Ascent-of-Man
# Dehumanization scale (`dehumanization`) are both single-item measures
# in the source and are excluded entirely -- IRW does not accept
# single-item scales regardless of data quality (confirmed by
# ben-domingue 2026-07-29).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SI_URLS = {
    1: "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0204494.s004",
    2: "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0204494.s005",
}
ID_OFFSET = {1: 0, 2: 1000}

IRI_ITEMS = ([f"EC{i}" for i in range(1, 8)]
             + [f"PT{i}" for i in range(1, 8)]
             + [f"PD{i}" for i in range(1, 8)])
BELIEFS_ITEMS = [f"C{i}" for i in range(1, 7)] + [f"IT{i}" for i in range(1, 7)]
SJ_ITEMS = [f"SJ{i}" for i in range(1, 9)]
SED_ITEMS = ["SE1", "SE2", "SE3", "SE4", "D1", "D2", "D3", "D4"]


def load(study):
    r = requests.get(SI_URLS[study], headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1 + ID_OFFSET[study]
    df["cov_study"] = study
    if study == 1:
        df["cov_condition"] = df["Condition"]
    else:
        df["cov_condition"] = pd.to_numeric(df["PID"].str.extract(r"c0?(\d+)$")[0], errors="coerce")
    df["cov_age"] = df["age"]
    df["cov_gender"] = df["gender"]
    return df


def write_scale(dfs, item_cols, out_name, valid_range):
    cov_cols = ["cov_study", "cov_condition", "cov_age", "cov_gender"]
    frames = []
    for df in dfs:
        if all(c in df.columns for c in item_cols):
            sub = df[["id"] + cov_cols + item_cols]
            frames.append(sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                                    var_name="item", value_name="resp"))
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= valid_range[0]) & (long["resp"] <= valid_range[1])]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    s1 = load(1)
    s2 = load(2)

    write_scale([s1, s2], IRI_ITEMS, "herrera_2018_iri", valid_range=(1, 5))
    write_scale([s1, s2], BELIEFS_ITEMS, "herrera_2018_beliefs_about_empathy", valid_range=(1, 7))
    write_scale([s2], SJ_ITEMS, "herrera_2018_attitudes_homeless", valid_range=(1, 9))
    write_scale([s2], SED_ITEMS, "herrera_2018_se_d_items", valid_range=(1, 7))


if __name__ == "__main__":
    convert()
