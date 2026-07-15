from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Raw Data: Body Image, Self-Esteem, Peer Support, and Physical "
         "Activities Motivation in Adolescents (Chen, 2025, figshare)")
URL  = "https://figshare.com/articles/dataset/Raw_Data_Body_Image_Self-Esteem_Peer_Support_and_Physical_Activities_Motivation_in_Adolescents/30093970"
DOI  = "10.6084/m9.figshare.30093970"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/57825856"

COV_COLS = {
    "性别": "cov_gender",
    "年龄": "cov_age",
    "@3、您的身高（cm）": "cov_height_cm",
    "@4、您的体重（kg）": "cov_weight_kg",
    "BMI": "cov_bmi",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(pd.io.common.BytesIO(r.content))
    df = df.rename(columns={"序号": "id"})
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
    print("Downloading Raw Data_Body Image...sav ...")
    raw = fetch_data()
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    # Body Image scale, 23 items, 1-5 Likert
    write_scale(_melt_scale(raw, [f"BI{i}" for i in range(1, 24)], cov),
                "chen2025_body_image.csv")
    # Physical Activity Motivation scale, 15 items, 1-5 Likert
    write_scale(_melt_scale(raw, [f"MOT{i}" for i in range(1, 16)], cov),
                "chen2025_activity_motivation.csv")
    # Peer Support scale, 5 items, 1-5 Likert
    write_scale(_melt_scale(raw, [f"PS{i}" for i in range(1, 6)], cov),
                "chen2025_peer_support.csv")
    # Self-Esteem scale, 10 items, 1-5 Likert
    write_scale(_melt_scale(raw, [f"SE{i}" for i in range(1, 11)], cov),
                "chen2025_self_esteem.csv")


if __name__ == "__main__":
    convert()
