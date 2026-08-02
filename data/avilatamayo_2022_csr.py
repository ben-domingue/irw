from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0266711
# DOI: 10.1371/journal.pone.0266711
# Avila-Tamayo et al. (2022), "Spanish-speaking validation of the
# internal corporate social responsibility questionnaire". S1 Dataset.
# CC BY 4.0. N=433. Text-coded 7-point Likert ("Totally disagree" ...
# "Totally agree") recoded to 1-7. 5 named subscales: Employment
# Stability (Empl_Stab, 7i), Work Environment (Work_Envir, 5i), Skills
# Development (Skills_Dev, 6i), Workforce Diversity (Workf_Div, 6i),
# Work-Life balance (Work_Life, remaining items). A stray non-integer
# value (4.368159) appearing occasionally alongside the text categories
# looks like a mean-imputed substitute for missing responses -- dropped
# (not a valid 1-7 category).
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0266711.s001")

LIKERT_MAP = {
    "Totally disagree": 1, "Disagree": 2, "Partially disagree": 3,
    "Not in disagree or agree": 4, "Partially agree": 5, "Agree": 6, "Totally agree": 7,
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns={"Identificator": "id"})
    prefixes = ["Empl_Stab", "Work_Envir", "Skills_Dev", "Workf_Div", "Work_Life"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for prefix in prefixes:
        item_cols = [c for c in df.columns if c.startswith(prefix)]
        if not item_cols:
            continue
        long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(str).map(LIKERT_MAP)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        out_name = f"avilatamayo_2022_{prefix.lower()}"
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
