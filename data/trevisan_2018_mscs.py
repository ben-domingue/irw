from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206800
# DOI: 10.1371/journal.pone.0206800
# Trevisan, Tafreshi, Slaney et al. (2018), "A psychometric evaluation of
# the Multidimensional Social Competence Scale (MSCS)". S2 File. CC BY 4.0.
# N=1178, almost entirely self-report (MSCS_Respondant==8, 16 NaN).
#
# No participant-id column in the raw file -- row position used as id.
# Two instruments -> two output files:
#   trevisan_2018_mscs: 77 raw MSCS items, 1-5. "_R"-suffixed columns
#     (e.g. MSCS_1_R) are reverse-scored recoded duplicates -- excluded,
#     along with the SM1/SI1/DEC1/SK1/VCS1/NSS1/ER1/TOTAL1 subscale-total
#     columns. Two isolated data-entry errors dropped (caught in QC,
#     2026-08-01): MSCS_54==3.88 (respondent row 589) and MSCS_66==3.64
#     (row 884) -- the only 2 fractional values among 90,706 otherwise-
#     integer cells, different respondents/items, neighboring items for
#     both are clean integers.
#   trevisan_2018_aq: Autism Quotient (AQ-50), 50 items, binary 0/1.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0206800.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age_yr": "cov_age", "Sex": "cov_sex"}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df


def ship(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    if out_name == "trevisan_2018_mscs":
        long = long[long["resp"] % 1 == 0]
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch().rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    mscs_items = [f"MSCS_{i}" for i in range(1, 78) if f"MSCS_{i}" in df.columns]
    ship(df, cov_cols, mscs_items, "trevisan_2018_mscs")

    aq_items = [f"AQ_{i}" for i in range(1, 51) if f"AQ_{i}" in df.columns]
    ship(df, cov_cols, aq_items, "trevisan_2018_aq")


if __name__ == "__main__":
    convert()
