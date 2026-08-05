#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0294238
# DOI: 10.1371/journal.pone.0294238
#
# Salleh H, Avoi R, Abdul Karim H, Osman S, Kaur N, Dhanaraj P (2023)
# Translation, Cross-Cultural Adaptation to Malay, and psychometric
# evaluation of the AIM-IAM-FIM questionnaire: Measuring the
# implementation outcome of a community-based intervention programme.
# PLoS ONE 18(11).
#
# Data availability points to two Harvard Dataverse DOIs (EFA sample n=170;
# CFA/scale-evaluation sample claimed n=235: 10.7910/DVN/FZFVRY), and PLOS
# hosts two SI files (S1 Dataset .s001 "For EFA", S1 Dataset .s002 "For
# CFA"). All four sources (PLOS s001, PLOS s002, and the Dataverse
# EKF8BH/FZFVRY .tab files) were checked and are byte-identical -- only the
# n=170 EFA/factor-extraction sample is actually available; the n=235
# scale-evaluation sample described in the paper text was never actually
# linked. Shipping the one genuine raw dataset that exists (n=170).
#
# 12 raw items on a 1-5 Likert scale, Malay-language survey about a
# community health programme (MIICA/KOSPEN) implementation outcome. The
# paper's final validated instrument used only 7 of these items in a
# single dimension ("acceptability of a community-based intervention"),
# but the shared raw file has all 12 pre-reduction items -- kept all 12
# since this is raw response data, not the paper's derived/reduced scale.
# Source column names are the (truncated) Malay item text; mapped to
# item_01..item_12 below, mapping preserved here for future item-text
# matching:
#   item_01: Program MIICA / KOSPEN memenuhi persetujuan saya
#   item_02: Program MIICA/ KOSPEN menarik minat saya
#   item_03: Saya suka program MIICA/ KOSPEN
#   item_04: Saya menyambut program MIICA/ KOSPEN dengan baik
#   item_05: Program MIICA/ KOSPEN kelihatan bertepatan dengan objektif
#   item_06: Program MIICA/ KOSPEN kelihatan bersesuaian dengan masyarakat
#   item_07: Program MIICA/ KOSPEN kelihatan boleh digunapakai oleh masyarakat
#   item_08: Program MIICA/ KOSPEN kelihatan berpadanan baik dengan program imunisasi/ kesihatan sedia ada
#   item_09: Program MIICA/KOSPEN kelihatan boleh dilaksanakan dalam masyarakat
#   item_10: Program MIICA/ KOSPEN kelihatan boleh dijalankan oleh masyarakat
#   item_11: Program MIICA/ KOSPEN kelihatan boleh dilakukan oleh komuniti dan sukarelawan
#   item_12: Program MIICA/ KOSPEN kelihatan mudah untuk dijalankan

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0294238.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(pd.io.common.BytesIO(r.content))


def convert():
    print("Fetching S1 Dataset (CSV, EFA sample)...")
    raw = fetch_raw()
    raw = raw.rename(columns={"Respondent ID": "id"})

    item_cols = [c for c in raw.columns if c != "id"]
    item_map = {c: f"item_{i+1:02d}" for i, c in enumerate(item_cols)}

    d = raw[["id"] + item_cols].copy()
    for c in item_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["item"] = long["item"].map(item_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "salleh_2023_aim_iam_fim.csv")
    long.to_csv(out_path, index=False)
    print(f"salleh_2023_aim_iam_fim.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
