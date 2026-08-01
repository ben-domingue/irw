from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214082
# DOI: 10.1371/journal.pone.0214082
# Nelson et al. (2019). The 43-item Illness Perception Questionnaire -
# Revised, Dental Edition (IPQ-RDE), a new instrument (based on the CSM
# framework) for older adults' (62+) perception of their dental
# conditions, N=198. Raw items are ipq_rd_1..ipq_rd_43, 1-5 Likert scale
# (direction/labels not given in the raw file or its own codebook sheet,
# consistent with the paper's mention of reverse-scored items across its
# 10 CSM constructs -- direction is allowed to vary across items per
# datastandard.md). -9 is a sparse (27/8514 cells, spread across 17 of the
# 43 items, 1-4 occurrences each) out-of-range sentinel for missing/
# not-answered, filtered out. The file's other columns (pqx_*: depression/
# social support/OHQOL sub-instruments; ohs_*: clinician-administered
# dental screening findings, not self-report) are separate constructs not
# shipped here.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0214082.s004")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"ipq_rd_{i}" for i in range(1, 44)]


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name=0)
    df = df.rename(columns={"id_number": "id", "marital_status": "cov_marital_status"})
    return df


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id", "cov_marital_status"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[long["resp"] != -9]  # out-of-range sentinel, see header note
    long = long.reset_index(drop=True)
    long = long[["id", "item", "resp", "cov_marital_status"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "nelson_2019_ipqrde.csv"
    long.to_csv(out_path, index=False)
    print(f"nelson_2019_ipqrde: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
