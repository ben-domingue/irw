from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Perceived family support as a double-edged sword: A moderated "
         "mediation model of attachment on spiritual well-being among "
         "Chinese older adults (Gao, 2025, figshare)")
URL  = "https://figshare.com/articles/dataset/Perceived_family_support_as_a_double-edged_sword_A_moderated_mediation_model_of_attachment_on_spiritual_well-being_among_Chinese_older_adults/28737626"
DOI  = "10.6084/m9.figshare.28737626"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

# Two figshare deposits (28737626, 30048610) share this exact title and
# contain byte-identical data (confirmed via df.equals()) -- processed once
# here; the duplicate was not.
FILE_URL = "https://ndownloader.figshare.com/files/57648064"

SCALES = {
    "gao2025_attachment_avoidance": ("CAvoidance", 6),  # 1-7 Likert
    "gao2025_attachment_anxiety": ("CAnxiety", 3),       # 1-7 Likert
    "gao2025_spiritual_wellbeing": ("SWB", 12),          # 1-5 Likert
    "gao2025_family_support": ("PFS", 4),                # 1-7 Likert
    "gao2025_sse": ("SSE", 6),                           # 1-5 Likert
}

COV_COLS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "MaritalStatus": "cov_marital_status",
}


def convert():
    print("Downloading data.sav ...")
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    raw = pd.read_spss(pd.io.common.BytesIO(r.content), convert_categoricals=False)
    raw = raw.rename(columns={"ID": "id"})
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)
    cov_cols = list(cov.columns.drop("id"))

    for table, (prefix, n_items) in SCALES.items():
        item_cols = [f"{prefix}{i}" for i in range(1, n_items + 1)]
        items = raw[["id"] + item_cols].merge(cov, on="id")
        long = items.melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        col_order = ["id", "item", "resp"] + cov_cols
        long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fname = f"{table}.csv"
        long.to_csv(OUT_DIR / fname, index=False)
        print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
