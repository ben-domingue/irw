from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0237846
# DOI: 10.1371/journal.pone.0237846
# Petrocchi et al. (2020), "'What you say and how you say it' matters:
# An experimental evidence of the role of synchronicity, modality, and
# message valence during smartphone-mediated communication". S1 File. CC
# BY 4.0. N=160. 10-item neuroticism scale (Italian, "Sempre o spesso
# falso" (always/often false) .. "Sempre o spesso vero" (always/often
# true)), recoded 1-4. The file's `Smartphone_addiction_*` items are NOT
# shipped -- >55% blank across the board (96/160 empty on item 1 alone),
# too sparse to be a reliable raw-item table.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0237846.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {
    "Sempre o spesso falso": 1, "Talvolta o abbastanza falso": 2,
    "Talvolta o abbastanza vero": 3, "Sempre o spesso vero": 4,
}
ITEM_COLS = ["Neuro_1_D", "Neuro_2_A", "Neuro_3_A", "Neuro_4_A", "Neuro_5_A",
             "Neuro_6_D", "Neuro_7_D", "Neuro_8_A", "Neuro_9_D", "Neuro_10_D"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID_progressivo": "id", "Condizione": "cov_condition", "Age": "cov_age", "Sex": "cov_sex"})


def convert():
    df = fetch()
    cov_cols = [c for c in ["cov_condition", "cov_age", "cov_sex"] if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(str).map(LIKERT_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "petrocchi_2020_neuroticism.csv"
    long.to_csv(out_path, index=False)
    print(f"petrocchi_2020_neuroticism: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
