from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0303965
# DOI: 10.1371/journal.pone.0303965
# Wang et al. (2024), "Investigating latent mean differences in
# achievement emotions among Chinese secondary EFL learners: A gender
# and grade perspective". S1 File. CC BY 4.0. N=1460. 5 column-coded
# achievement-emotion subscales (VAR1x-VAR5x, 3-4 items each), 1-5
# Likert; construct names not in the file (no item text), shipped under
# generic emotion1-5 labels.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0303965.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"gender": "cov_gender", "grade": "cov_grade"}

SCALES = {
    "wang_2024_emotion1": ["VAR11", "VAR12", "VAR13", "VAR14"],
    "wang_2024_emotion2": ["VAR21", "VAR22", "VAR23", "VAR24"],
    "wang_2024_emotion3": ["VAR31", "VAR32", "VAR33", "VAR34"],
    "wang_2024_emotion4": ["VAR41", "VAR42", "VAR43"],
    "wang_2024_emotion5": ["VAR51", "VAR52", "VAR53", "VAR54"],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
