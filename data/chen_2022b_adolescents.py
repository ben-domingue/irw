from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

DOI   = "10.3389/fpsyg.2022.852256.s001"
TITLE = ("Psychological Abuse and Social Support in Chinese Adolescents: "
         "The Mediating Effect of Self-Esteem")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/34495295"

COV_MAP = {
    "age":           "cov_age",
    "gender":        "cov_gender",       # 1/2
    "onlychild":     "cov_only_child",   # 1/2
    "familyincome":  "cov_family_income",
}

SCALE_RANGES = {
    "abuse":   (1, 5),
    "support": (1, 7),
    "esteem":  (1, 4),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    from io import BytesIO
    return pd.read_csv(BytesIO(r.content))


def convert():
    print("Downloading psychological abuse / social support dataset …")
    df = fetch_data()

    # The source 'number' column resets across respondents (not a stable
    # per-person id, confirmed: same number maps to different age/gender
    # combinations across rows) -- use row index as id instead, per
    # datastandard.md's "missing person ID" guidance.
    df = df.drop(columns=["number"]).reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    cols = df.columns.tolist()
    item_start = 1 + len(cov_cols)  # after id + cov cols
    abuse_cols   = cols[item_start:item_start + 14]
    support_cols = cols[item_start + 14:item_start + 26]
    esteem_cols  = cols[item_start + 26:item_start + 36]

    SCALES = {
        "chen2022b_psychabuse":   (abuse_cols, "abuse"),
        "chen2022b_socsupport":   (support_cols, "support"),
        "chen2022b_selfesteem":   (esteem_cols, "esteem"),
    }

    for out_name, (item_cols, scale_key) in SCALES.items():
        lo, hi = SCALE_RANGES[scale_key]
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        col_order = ["id", "item", "resp"] + cov_cols
        long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fname = f"{out_name}.csv"
        long.to_csv(OUT_DIR / fname, index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
