from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("How Does Parental Early Maladaptive Schema Affect Adolescents' "
         "Social Adaptation? Based on the Perspective of Intergenerational "
         "Transmission (Shi et al., 2024, Behavioral Sciences)")
URL  = "https://doi.org/10.7910/DVN/7CYIQG"
DOI  = "10.3390/bs14100928"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://dataverse.harvard.edu/api/access/datafile/6477164"

# 序号/身份证号 are unreliable (duplicated/missing) or PII (ID-card number,
# names) — use row index as id and drop all name/ID-card columns entirely.
COV_COLS = {
    "@2.您的户口所在地": "cov_hukou",
    "@3.您的文化程度":   "cov_parent_education",
    "@4.家庭月收入":     "cov_family_income",
    "@5.家庭类型":       "cov_family_type",
    "父母的教养方式":     "cov_parenting_style",
    "性别":             "cov_caregiver_gender",
    "性别.1":           "cov_child_gender",
    "年龄":             "cov_child_age",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Sheet1")
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
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
    print("Downloading EMS & Social adaptation.xlsx ...")
    raw = fetch_data()
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    # Young Schema Questionnaire (short form), 75 items, 1-6 Likert,
    # answered separately by the caregiver (PSC*) and the adolescent (CSC*)
    psc_cols = [c for c in raw.columns if c.startswith("PSC")]
    csc_cols = [c for c in raw.columns if c.startswith("CSC")]
    write_scale(_melt_scale(raw, psc_cols, cov), "shi2024_ysq_parent.csv")
    write_scale(_melt_scale(raw, csc_cols, cov), "shi2024_ysq_adolescent.csv")

    # Adolescent Social Adaptation Scale (Chen et al., 2016), 33 items, 1-5
    csa_cols = [c for c in raw.columns if c.startswith("CSA")]
    write_scale(_melt_scale(raw, csa_cols, cov), "shi2024_sas.csv")


if __name__ == "__main__":
    convert()
