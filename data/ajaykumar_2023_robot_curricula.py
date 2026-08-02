from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0294786
# DOI: 10.1371/journal.pone.0294786
# Ajaykumar et al. (2023), "Curricula for teaching end-users to
# kinesthetically program collaborative robots". CC BY 4.0. N=28 (small).
# Two clean scales shipped from the paper's 6 bundled SI files:
# the standard NASA Task Load Index (NASA-TLX, S1 Dataset, 6 items, 1-5)
# and a prior-experience rating block (S6 Dataset, 5 items, 1-5). The
# other 4 files (per-task unsuccessful-demo counts, task times,
# suboptimality/force-torque deltas, body-part interaction counts) are
# derived/per-task-condition metrics rather than a single clean item set
# and are not shipped.
S1_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0294786.s004")
S6_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0294786.s009")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

TLX_ITEMS = ["TLXMental", "TLXPhysical", "TLXTemporal", "TLXPerformance",
             "TLXEffort", "TLXFrustration"]
EXP_ITEMS = ["ExpHands", "ExpRobots", "ExpTech", "ExpProg", "ExpProgRob"]


def _fetch(url: str) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df1 = _fetch(S1_URL).rename(columns={"UserID": "id", "Condition": "cov_condition"})
    long1 = df1.melt(id_vars=["id", "cov_condition"], value_vars=TLX_ITEMS,
                      var_name="item", value_name="resp")
    long1["resp"] = pd.to_numeric(long1["resp"], errors="coerce")
    long1 = long1.dropna(subset=["resp"]).reset_index(drop=True)
    long1 = long1[["id", "item", "resp", "cov_condition"]]
    long1.to_csv(OUT_DIR / "ajaykumar_2023_nasa_tlx.csv", index=False)
    print(f"ajaykumar_2023_nasa_tlx: rows={len(long1)} ids={long1['id'].nunique()} "
          f"items={long1['item'].nunique()} resp={long1['resp'].min():.0f}-{long1['resp'].max():.0f}")

    df6 = _fetch(S6_URL).rename(columns={"UserID": "id"})
    long6 = df6.melt(id_vars=["id"], value_vars=EXP_ITEMS, var_name="item", value_name="resp")
    long6["resp"] = pd.to_numeric(long6["resp"], errors="coerce")
    long6 = long6.dropna(subset=["resp"]).reset_index(drop=True)
    long6 = long6[["id", "item", "resp"]]
    long6.to_csv(OUT_DIR / "ajaykumar_2023_experience.csv", index=False)
    print(f"ajaykumar_2023_experience: rows={len(long6)} ids={long6['id'].nunique()} "
          f"items={long6['item'].nunique()} resp={long6['resp'].min():.0f}-{long6['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
