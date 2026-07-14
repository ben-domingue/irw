from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("The psychometric properties of a new oral health illness "
         "perception measure for adults aged 62 years and older "
         "(Nelson et al., 2019, PLOS ONE)")
URL   = "https://plos.figshare.com/articles/dataset/The_psychometric_properties_of_a_new_oral_health_illness_perception_measure_for_adults_aged_62_years_and_older/7977755"
DOI   = "10.1371/journal.pone.0214082"
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/14864528"

# 4=married/partnered, 1/2/3 = other marital-status categories per S1 codebook;
# kept as a coded covariate rather than decoded (no label mapping in the deposit).
COV_COLS = {
    "marital_status": "cov_marital_status",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(pd.io.common.BytesIO(r.content),
                        sheet_name="R21_198_PLoS_One_Data&Codebook")
    df = df.rename(columns={"id_number": "id"})
    return df


def convert():
    print("Downloading pone.0214082.s004.xlsx ...")
    raw = fetch_data()
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)
    cov_cols = list(cov.columns.drop("id"))

    # Illness Perception Questionnaire - Revised for Dental use (IPQ-RDE),
    # 43 items, 1-5 Likert (strongly agree..strongly disagree). -9 = missing/not
    # administered sentinel per S1 Text; filter before melting so it never
    # enters resp.
    item_cols = [c for c in raw.columns if c.startswith("ipq_rd_") and c.split("_")[-1].isdigit()]
    items = raw[["id"] + item_cols].merge(cov, on="id")
    long = items.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"] != -9]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "nelson2019_ipqrd.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
