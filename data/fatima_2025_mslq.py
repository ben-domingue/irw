from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0319763
# DOI: 10.1371/journal.pone.0319763
# Fatima et al. (2025), "Validation of the Motivated Strategies for
# Learning Questionnaire among clinical clerkship students in Malaysia".
# S1 Dataset. CC BY 4.0. N=349. 81-item MSLQ, 1-7 Likert. Several items
# have an "r" suffix in the source (reverse-worded per the instrument);
# shipped as raw responses, not reverse-scored. The paper's S1 Appendix
# (an 8-expert content-validity panel) is a separate small-panel genre,
# not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0319763.s005")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Gender": "cov_gender", "Age": "cov_age", "Acad_yr": "cov_academic_year",
           "CL_posting": "cov_cl_posting"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns=COV_MAP)
    df["id"] = range(1, len(df) + 1)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    item_cols = [c for c in df.columns if c.startswith("Q")]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "fatima_2025_mslq.csv"
    long.to_csv(out_path, index=False)
    print(f"fatima_2025_mslq: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
