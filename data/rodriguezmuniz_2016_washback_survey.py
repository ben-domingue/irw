from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0167544
# DOI: 10.1371/journal.pone.0167544
# Rodriguez-Muniz et al. (2016), "Washback Effect of University Entrance
# exams in Applied Mathematics to Social Sciences". S1 File. CC BY 4.0.
# N=51 secondary-school teachers. 17-item teacher survey on exam washback,
# 1-5 Likert (item text not in the file). OA1-OA6 (open-ended text
# responses) and "Remarks" not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0167544.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Sex": "cov_sex", "Age": "cov_age", "Name of Secondary School": "cov_school"}
ITEM_COLS = [f"Q{i}" for i in range(1, 18)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns={**COV_MAP, "Questionnaire Number": "id"})
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "rodriguezmuniz_2016_washback_survey.csv"
    long.to_csv(out_path, index=False)
    print(f"rodriguezmuniz_2016_washback_survey: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
