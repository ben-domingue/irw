from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0169668
# DOI: 10.1371/journal.pone.0169668
# Gholami et al. (2017). Evaluation of the Impact of a Mass Media Campaign
# on Periodontal Knowledge among Iranian Adults. PLOS ONE.
# Data: S1 File (SAV, "a minimal set of data for the study"),
# https://doi.org/10.1371/journal.pone.0169668.s001
#
# The instrument is a 3-item knowledge quiz repeated at baseline and two
# follow-ups (wave 1/2/3). Each raw item (Baseline.Knowledge.Qx etc.) stores
# the *option code chosen* from a 4-5 option multiple-choice list (nominal,
# not ordinal -- option identity, not quantity) plus sentinel codes 7="don't
# know" and 9="no answer". The paired ".recoded" column converts this into
# the analysis variable actually used in the paper: 0=incorrect/1=correct.
# Because the raw option codes are nominal, `resp` is built from the
# .recoded (correct/incorrect) columns, which is the genuine per-item
# response used for scoring, not the raw multiple-choice option index.
# No PII: `ID` is a sequential study id.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SAV_URL = "https://doi.org/10.1371/journal.pone.0169668.s001"

COV_COLS = {
    "Age": "cov_age",
    "Education": "cov_education",
    "Gender": "cov_gender",
    "NewMARITAL": "cov_marital",
    "Employment": "cov_employment",
    "Economic": "cov_economic",
}

WAVES = [
    ("Baseline", 1),
    ("Follow.1", 2),
    ("Follow.2", 3),
]

ITEM_STEMS = {
    "Knowledge.Q1": "Q1_dental_plaque",
    # note: baseline column has a typo ("Knwledge") that follow-up columns don't
    "Knwledge.Q2": "Q2_gum_disease_cause",
    "Knowledge.Q2": "Q2_gum_disease_cause",
    "Knowledge.Q3": "Q3_early_gum_sign",
}


def fetch_data() -> pd.DataFrame:
    import pyreadstat

    r = requests.get(SAV_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = OUT_DIR.parent / "_tmp_gholami2017.sav"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(r.content)
    df, _ = pyreadstat.read_sav(str(tmp))
    tmp.unlink(missing_ok=True)
    return df


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_COLS)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"

    cov_cols = [c for c in COV_COLS.values() if c in df.columns]

    frames = []
    for wave_prefix, wave_num in WAVES:
        cols_map = {}
        for stem, item_name in ITEM_STEMS.items():
            col = f"{wave_prefix}.{stem}.recoded"
            if col in df.columns:
                cols_map[col] = item_name
        if not cols_map:
            continue
        sub = df[["id"] + cov_cols + list(cols_map.keys())].rename(columns=cols_map)
        sub["wave"] = wave_num
        item_names = sorted(set(cols_map.values()))
        long = sub.melt(
            id_vars=["id", "wave"] + cov_cols,
            value_vars=item_names,
            var_name="item",
            value_name="resp",
        )
        frames.append(long)

    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 1)]
    long["resp"] = long["resp"].astype(int)

    col_order = ["id", "item", "resp", "wave"] + cov_cols
    long = long[col_order].sort_values(["id", "item", "wave"]).reset_index(drop=True)

    write_scale(long, "gholami_2017_periodontal_knowledge.csv")


if __name__ == "__main__":
    convert()
