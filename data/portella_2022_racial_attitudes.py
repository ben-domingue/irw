from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZHCTCK
# DOI: 10.7910/DVN/ZHCTCK
# Paper: Portella, Kirschbaum & Menezes-Filho (2022), "Racial social norms among
# Brazilian students: Academic performance, popularity, and racial identification",
# PNAS 119(27) e2117956119. https://doi.org/10.1073/pnas.2117956119
#
# NOTE: the dataset's own composite columns (score_racism, score_homophobia,
# score_self_esteem, scores_sdo_*, etc.) are Exploratory-Factor-Analysis scores
# computed from underlying survey items that are NOT included in the released
# replication file -- only the derived scores are. They are aggregates, not
# item responses, so they are excluded here. The only genuine raw item-level
# data in the release is q9/q12/q57/q60: four statements about race relations,
# all sharing one preamble and one 4-point agreement scale (see CODEBOOK.pdf),
# answered by the ~3,431 students who completed the questionnaire.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_ID = 5707149  # data_11.tab
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["q9", "q12", "q57", "q60"]

COV_MAP = {
    "age": "cov_age",
    "gender": "cov_gender",
    "race": "cov_race",
    "skin_color": "cov_skin_color",
    "grade": "cov_grade",
    "religion": "cov_religion",
    "school_id": "cov_school_id",
    "class_id": "cov_class_id",
}


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep="\t")


def convert():
    raw = fetch_data()

    df = raw.rename(columns={"id_student": "id", **COV_MAP})
    assert df["id"].nunique() == len(df)

    cov_cols = list(COV_MAP.values())
    long = df[["id"] + cov_cols + ITEM_COLS].melt(
        id_vars=["id"] + cov_cols,
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "portella_2022_racial_attitudes.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_path.name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
