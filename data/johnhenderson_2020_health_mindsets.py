from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0242902
# DOI: 10.1371/journal.pone.0242902
# John-Henderson et al. (2020), "The relationship between health
# mindsets and health protective behaviors: An exploratory investigation
# in a convenience sample of American Indian adults during the COVID-19
# pandemic". S1 Dataset. CC BY 4.0. N=192. Two scales: health mindset
# (hm_1-3, 1-6) and disinfection behavior (handsan/handwash/cleanphone/
# disinfectwipes, 1-5 -- one isolated out-of-range value (11) on
# disinfectwipes, an otherwise strict 1-5 item, dropped as a data-entry
# error). `phys_dist` (single item) and derived composite columns
# (healthmindset/avg_disinfbehav) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0242902.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"age": "cov_age", "sex": "cov_sex", "income": "cov_income"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "subjectid": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    mindset = df.melt(id_vars=["id"] + cov_cols, value_vars=["hm_1", "hm_2", "hm_3"],
                       var_name="item", value_name="resp")
    mindset["resp"] = pd.to_numeric(mindset["resp"], errors="coerce")
    mindset = mindset.dropna(subset=["resp"]).reset_index(drop=True)
    mindset = mindset[["id", "item", "resp"] + cov_cols]
    mindset.to_csv(OUT_DIR / "johnhenderson_2020_health_mindset.csv", index=False)
    print(f"johnhenderson_2020_health_mindset: rows={len(mindset)} ids={mindset['id'].nunique()} "
          f"items={mindset['item'].nunique()} resp={mindset['resp'].min():.0f}-{mindset['resp'].max():.0f}")

    behav_cols = ["handsan", "handwash", "cleanphone", "disinfectwipes"]
    behav = df.melt(id_vars=["id"] + cov_cols, value_vars=behav_cols, var_name="item", value_name="resp")
    behav["resp"] = pd.to_numeric(behav["resp"], errors="coerce")
    behav = behav[(behav["resp"] >= 1) & (behav["resp"] <= 5)]
    behav = behav.dropna(subset=["resp"]).reset_index(drop=True)
    behav = behav[["id", "item", "resp"] + cov_cols]
    behav.to_csv(OUT_DIR / "johnhenderson_2020_disinfection_behavior.csv", index=False)
    print(f"johnhenderson_2020_disinfection_behavior: rows={len(behav)} ids={behav['id'].nunique()} "
          f"items={behav['item'].nunique()} resp={behav['resp'].min():.0f}-{behav['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
