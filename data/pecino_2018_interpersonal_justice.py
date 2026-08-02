from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0207458
# DOI: 10.1371/journal.pone.0207458
# Pecino et al. (2018), "Interpersonal justice climate, extra-role
# performance and work family balance: A multilevel mediation model of
# employee well-being". S1 Dataset. CC BY 4.0. N=442. 40 "cl"-prefixed
# columns (unlabeled sub-construct codes ap/in/me/re) actually span two
# different text-coded 6-point response scales, confirmed by inspecting
# each column's category set: items 1-6 use a "how many coworkers"
# climate scale (No one..Everyone, matching the paper's "justice climate"
# construct), items 7-40 use a personal frequency scale (Never..Always,
# matching extra-role performance/work-family balance). Shipped as two
# separate tables rather than mixing scales in one resp column.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0207458.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age": "cov_age", "Gender": "cov_gender", "Education": "cov_education"}
CLIMATE_MAP = {"No one": 1, "Few": 2, "Someone": 3, "Quite": 4, "Considerable": 5, "Everyone": 6}
FREQ_MAP = {"Never": 1, "Hardly ever": 2, "A few times": 3, "Sometimes": 4, "Almost always": 5, "Always": 6}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def _ship(df, out_name, item_cols, likert_map, cov_cols):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(str).map(likert_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    item_cols = [c for c in df.columns if c.startswith("cl")]
    climate_cols = [c for c in item_cols if set(df[c].dropna().unique()) & set(CLIMATE_MAP)]
    freq_cols = [c for c in item_cols if c not in climate_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _ship(df, "pecino_2018_justice_climate", climate_cols, CLIMATE_MAP, cov_cols)
    _ship(df, "pecino_2018_extrarole_wfb", freq_cols, FREQ_MAP, cov_cols)


if __name__ == "__main__":
    convert()
