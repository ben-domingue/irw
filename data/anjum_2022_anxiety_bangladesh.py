from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0262716
# DOI: 10.1371/journal.pone.0262716
# Anjum et al. (2022), "Anxiety among urban, semi-urban and rural school
# adolescents in Dhaka, Bangladesh: Investigating prevalence and
# associated factors". S1 Data. CC BY 4.0. N=2313. All 7 GAD-7 raw items
# (E20_Anxiety, E21-E26). E20_Anxiety is GAD-7 item 1 ("Feeling nervous,
# anxious"), confirmed by its SPSS variable label and by the fact that the
# file's own E_GAD7_Total_Score equals the sum of E20_Anxiety + E21..E26
# for 100% of respondents (it matches E21..E26 alone for only 49%).
# Text-coded 4-point frequency scale ("Not at all".."Nearly every day")
# recoded 0-3. Derived score/category columns
# (E_GAD7_Total_Score/Cat_GAD7/Recat_GAD7 etc.) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0262716.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"A2_age": "cov_age", "A3_gender": "cov_gender", "School_area": "cov_school_area"}
LIKERT_MAP = {"Not at all": 0, "Several days": 1, "More than half of the days": 2, "Nearly every day": 3}
ITEM_COLS = ["E20_Anxiety", "E21", "E22", "E23", "E24", "E25", "E26"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "Questionnaire_ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(str).map(LIKERT_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "anjum_2022_gad7.csv"
    long.to_csv(out_path, index=False)
    print(f"anjum_2022_gad7: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
