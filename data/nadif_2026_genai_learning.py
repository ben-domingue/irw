#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/34754553
# DOI: 10.6084/m9.figshare.34754553.v2 (data); paper 10.32674/vt55r634
#   Nadif, Zemrani, Ait Hammou, Mansour, Fakhrou & Bouih (2026). "Employing
#   generative AI applications in learning: A factor analysis of motivations
#   and effects among Moroccan university students." American Journal of STEM
#   Education. Data deposited by Mohammed Zemrani.
# Data: Data_UseGenAI-206_V1.xlsx, one sheet (206 rows x 36 columns). The
#   record description is the codebook (construct for each prefix).
# License: CC BY 4.0 (figshare record and article).
#
# Checked against the paper: N = 206 (matches).
#
# Item text: not shipped -- headers are codes only; the record's description
#   names the constructs, not the items. The scale was "prepared for this
#   study" (abstract); wording would be in the article.
#
# SCALE: plain 1-5 on every item, every code used.
#
# Tables (one per construct, the record's codebook):
#   nadif_2026_genai_use         UGAI1-7  use of generative AI
#   nadif_2026_study_pressure    SP1-4
#   nadif_2026_time_pressure     TP1-4
#   nadif_2026_reward_seeking    SR1-3    search for rewards and quality
#   nadif_2026_performance       SQ1-3    academic performance / learning
#   nadif_2026_procrastination   Pr1-4
#   nadif_2026_memory_loss       ML1-3    memory loss / cognitive reliance
#   nadif_2026_integrity         AP1-3    academic integrity perceptions
# Dropped, with reasons:
#   Current Education Level        1-4 codes, unlabelled in the deposit
#   Current University/Institution free text (156 distinct spellings)
# Covariates: cov_gender (F/M), cov_age_group. id = the deposit's N.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://ndownloader.figshare.com/files/70533366"
SCALES = {
    "nadif_2026_genai_use": ("UGAI", 7),
    "nadif_2026_study_pressure": ("SP", 4),
    "nadif_2026_time_pressure": ("TP", 4),
    "nadif_2026_reward_seeking": ("SR", 3),
    "nadif_2026_performance": ("SQ", 3),
    "nadif_2026_procrastination": ("Pr", 4),
    "nadif_2026_memory_loss": ("ML", 3),
    "nadif_2026_integrity": ("AP", 3),
}
ALLOWED = {1, 2, 3, 4, 5}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (206, 36), d.shape
    assert d["N"].is_unique

    d = d.rename(columns={"N": "id", "Gender": "cov_gender",
                          "Age Group": "cov_age_group"})
    cov_cols = ["cov_gender", "cov_age_group"]
    for c in cov_cols:
        d[c] = d[c].astype(str).str.strip()
    items_all = []
    for table, (pre, n) in SCALES.items():
        items_all += [f"{pre}{i}" for i in range(1, n + 1)]
    dropped = [c for c in d.columns
               if c not in items_all and c not in cov_cols and c != "id"]
    print(f"[drop] {dropped}")
    assert len(dropped) == 2, dropped

    for table, (pre, n) in SCALES.items():
        cols = [f"{pre}{i}" for i in range(1, n + 1)]
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - ALLOWED
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: ALLOWED for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
