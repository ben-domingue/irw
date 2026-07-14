from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = "Teacher AI Literacy for ML Learner Instruction (Chowdhury & Sain, 2026)"
URL   = "https://figshare.com/articles/dataset/Teacher_AI_Literacy_for_ML_Learner_Instruction/31427369"
DOI   = "10.6084/m9.figshare.31427369.v1"
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/62202986"

# Public quant-only deposit; participant_id is a de-identified string
# (P001...), safe to use directly after stripping the "P" prefix.
COV_COLS = {
    "teach_ML": "cov_teaches_ml",
    "ml_percent_cat": "cov_ml_percent",
    "role_cat": "cov_role",
    "years_teaching_bin": "cov_years_teaching",
    "prior_ai_pd_cat": "cov_prior_ai_pd",
    "ai_policy_exists": "cov_ai_policy_exists",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    # keep_default_na=False: prior_ai_pd_cat uses the literal string "None"
    # as a real category ("no prior AI PD"), not a missing-data marker —
    # pandas' default na_values list would otherwise silently turn it to NaN.
    df = pd.read_csv(pd.io.common.BytesIO(r.content), keep_default_na=False, na_values=[""])
    df["id"] = df["participant_id"].str.replace("P", "", regex=False).astype(int)
    return df


def _melt_scale(raw: pd.DataFrame, item_cols: list[str], cov: pd.DataFrame) -> pd.DataFrame:
    items = raw[["id"] + item_cols]
    cov_cols = list(cov.columns.drop("id"))
    long = items.merge(cov, on="id").melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


def convert():
    print("Downloading data_deidentified_public_quant_only.csv ...")
    raw = fetch_data()
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    # Teacher AI Literacy scale, 12 items, 1-5 Likert (strongly disagree..strongly agree)
    ail_cols = [c for c in raw.columns if c.startswith("AIL") and c[3:].isdigit()]
    write_scale(_melt_scale(raw, ail_cols, cov), "chowdhury2026_ai_literacy.csv")

    # Responsible AI-Use Intentions scale, 4 items, 1-5 Likert
    int_cols = [c for c in raw.columns if c.startswith("INT") and c[3:].isdigit()]
    write_scale(_melt_scale(raw, int_cols, cov), "chowdhury2026_ai_intentions.csv")

    # Vignette decision-quality indicators, 4 items, binary (1=best-practice choice, 0=other)
    vig_cols = [c for c in raw.columns if c.startswith("VIG") and c[3:].isdigit()]
    write_scale(_melt_scale(raw, vig_cols, cov), "chowdhury2026_ai_vignette.csv")


if __name__ == "__main__":
    convert()
