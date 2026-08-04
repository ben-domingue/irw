#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0186045
# DOI: 10.1371/journal.pone.0186045
# Supporting Information: journal.pone.0186045_S1_Dataset.xls
#
# Team members' ratings of their team leader on 4 leadership-skill items
# (management, moderation, empathy, motivation), each on a documented 0-10
# scale with 99 = no data (per the file's own DataDictionary sheet), rated
# at two time points (Time I = month 3, Time II = month 9). N=258 team
# members across 45 teams -- matches paper's stated "258 team members".
# Melted with a `wave` column (1=Time I, 2=Time II) rather than duplicate
# item names, since it's the same person rating the same leader on the same
# 4 items at two points in time.
#
# The "SelfEvaluation" sheet (leaders rating themselves, same 4 items, same
# two waves) is NOT shipped: it has only 45 leaders, below IRW's N>=50
# floor.
#
# Also excluded from this file (all present in the raw OtherEvaluation
# sheet but not raw multi-item responses):
#   - OOE1/OOE2 (single-item "overall other-evaluation") -- a single-item
#     measure, never shipped per project rule even though clean/valid.
#   - FutureL1/"Future L2" -- a single binary team-cohesiveness/network
#     question ("Would you choose this person to work with you in a new
#     team?"), not part of the 4-item leadership-skill battery and itself
#     a single item.
#   - O_Attendance2 -- only collected at wave 2 (no wave-1 counterpart),
#     an attendance covariate rather than a skill-rating item.
#   - NameL, NamesM -- PII (leader/team-member names), dropped entirely,
#     never carried into id or cov_*.
#   - Duplicate columns "Gender M"/"Gender L" (typo duplicates of
#     GenderM/GenderL) -- dropped, kept the canonical GenderM/GenderL as
#     covariates.
#
# Response scale is a clean 0-10 integer scale; 99 is an explicit
# documented missing-value sentinel (confirmed via the file's own
# DataDictionary sheet, not inferred) and is filtered before saving.

import os
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file?"
          "type=supplementary&id=10.1371/journal.pone.0186045.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = ["Management", "Moderation", "Empathy", "Motivation"]
COV_RENAME = {"GenderM": "cov_gender", "TeamNumber": "cov_team_number"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="OtherEvaluation")

    df = df.rename(columns={"ParticipantNumber": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id not unique"

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    frames = []
    for wave, suffix in enumerate(["1", "2"], start=1):
        cols = [f"O_{it}{suffix}" for it in ITEMS]
        sub = df[["id"] + cov_cols + cols].copy()
        sub = sub.rename(columns={f"O_{it}{suffix}": it for it in ITEMS})
        sub["wave"] = wave
        frames.append(sub)

    long_wide = pd.concat(frames, ignore_index=True)
    long = long_wide.melt(id_vars=["id", "wave"] + cov_cols, value_vars=ITEMS,
                           var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # 99 = documented "no data" sentinel; valid scale is 0-10
    long = long[(long["resp"] >= 0) & (long["resp"] <= 10)].reset_index(drop=True)

    long = long[["id", "item", "resp", "wave"] + cov_cols]

    OUT_DIR_abs = OUT_DIR
    os.makedirs(OUT_DIR_abs, exist_ok=True)
    out_name = "pietraszkiewicz_2017_leader_eval"
    out_path = os.path.join(OUT_DIR_abs, out_name + ".csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
