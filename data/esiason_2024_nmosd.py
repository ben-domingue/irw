#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0300777
# DOI: 10.1371/journal.pone.0300777
# Supporting Information: Patients https://doi.org/10.1371/journal.pone.0300777.s001
#                         Caregivers https://doi.org/10.1371/journal.pone.0300777.s002
#
# REDCap export (title row + real header on row 2) covering NMOSD caregivers
# (S1, N=21) and patients (S2, N=37), each given the identical
# instrument battery: AAQ-II (Acceptance and Action Questionnaire, 7
# items), a 13-item Cognitive Fusion Questionnaire item pool, BAI (Beck
# Anxiety Inventory, 21 items), BDI (Beck Depression Inventory, 21 items
# -- items 16/18 use a wider 1-7 code to capture both "increase" and
# "decrease" directions of change, a known BDI-II digitization quirk, not
# a data error), the Valued Living Questionnaire (10 life domains rated on
# both importance and consistency), and a 10-item ACE (Adverse Childhood
# Experiences) screen. Since the same instruments were confirmed
# administered identically to both samples, each is combined into one
# file spanning patients+caregivers, with a cov_group covariate and the
# caregiver sample's id offset by 1000 to keep the combined id space
# unique (patient ids run 1-21, caregiver ids 1-37). The REDCap
# "*_complete" status columns and the 94 acoping___N/bcoping___N checkbox
# fields (a coping word-pair checklist with no accompanying codebook) are
# excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# WHICH FILE IS WHICH SAMPLE (corrected 2026-09-05, irw#1971).
#
# This mapping was the other way round, and cov_group therefore labelled every
# respondent as the opposite of what they are. Three independent signals agree,
# and none of them is the file name:
#
#   * The paper reports "Patients endorsed a mean BDI-II score of 14 (SD = 9.5)"
#     and "Caregivers endorsed a mean BDI-II score of 7.2 (SD = 5.9)". Scoring the
#     deposit's BDI block gives s001 = 6.67 and s002 = 15.57.
#   * It reports 22 caregivers against roughly 31 patients. s001 has 21 rows,
#     s002 has 37.
#   * Direction: the chronically ill sample scoring markedly higher on depression
#     than their caregivers is the expected ordering, and it is s002 that does.
#
# The files themselves cannot settle it -- both carry byte-identical column sets,
# with no role, diagnosis or relationship field to read.
#
# The ID OFFSETS DELIBERATELY STAY WITH THE FILES, not with the labels: s001 keeps
# offset 0 and s002 keeps 1000, so the corrected tables carry exactly the id values
# the published ones already do. Only cov_group changes. Swapping the offsets too
# would have renumbered every respondent for no reason.
SI_URLS = {
    "caregiver": "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0300777.s001",
    "patient": "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0300777.s002",
}
ID_OFFSET = {"caregiver": 0, "patient": 1000}

VLQ_IMPORTANCE = ["fam1", "marr1", "par1", "fri1", "wor1", "edu1", "rec1", "spi1", "cit1", "phys1"]
VLQ_CONSISTENCY = ["fam2", "marr2", "par2", "fri2", "wor2", "edu2", "rec2", "spi2", "cit2", "phsy2"]
ACE_ITEMS = ["swear", "push", "touch", "loved", "eat", "divorced", "mother", "drugs", "depressed", "prison"]


def load(group):
    r = requests.get(SI_URLS[group], headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), header=1)
    df = df.rename(columns={"record_id": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce") + ID_OFFSET[group]
    df["cov_group"] = group
    return df


def write_scale(dfs, item_cols, out_name, valid_range):
    frames = []
    for df in dfs:
        sub = df[["id", "cov_group"] + item_cols]
        long = sub.melt(id_vars=["id", "cov_group"], value_vars=item_cols,
                         var_name="item", value_name="resp")
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= valid_range[0]) & (long["resp"] <= valid_range[1])]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "cov_group"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    # s001 first, s002 second -- the file order the published tables were built in,
    # kept so the corrected output differs only where it is meant to.
    caregiver = load("caregiver")
    patient = load("patient")
    dfs = [caregiver, patient]

    # The AAQ-II is a 1-7 instrument. valid_range was (1, 5) here, which silently
    # dropped every 6 and 7 -- 37 of 389 responses, 9.5%, all from the patient
    # sample -- and presented a 7-point scale as a 5-point one. The sibling calls
    # below already carry the instrument's own range; this one did not (irw#1971).
    write_scale(dfs, [f"aaq{i}" for i in range(1, 8)], "esiason_2024_aaqii", valid_range=(1, 7))
    write_scale(dfs, [f"cfq{i}" for i in range(1, 14)], "esiason_2024_cfq", valid_range=(1, 7))
    write_scale(dfs, [f"bai{i}" for i in range(1, 22)], "esiason_2024_bai", valid_range=(1, 4))
    write_scale(dfs, [f"bdi{i}" for i in range(1, 22)], "esiason_2024_bdi", valid_range=(1, 7))
    write_scale(dfs, VLQ_IMPORTANCE, "esiason_2024_vlq_importance", valid_range=(1, 10))
    write_scale(dfs, VLQ_CONSISTENCY, "esiason_2024_vlq_consistency", valid_range=(1, 10))
    write_scale(dfs, ACE_ITEMS, "esiason_2024_ace", valid_range=(0, 1))


if __name__ == "__main__":
    convert()
