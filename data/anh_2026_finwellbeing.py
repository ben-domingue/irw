from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0340002
# DOI: 10.1371/journal.pone.0340002
# Anh (2026), "An integrated model of financial socialization, technology,
# and financial capability in predicting financial well-being". S1 File
# (.s001, CSV). CC BY 4.0. N=306. All items 5-point Likert (1-5). Six
# distinct constructs -> 6 separate tables per datastandard.md's "multiple
# scales in one file" rule:
#   FS (7 items): Family Financial Socialization
#   AI (8 items): Artificial-Intelligence-enabled finance adoption
#   FB (9 items): Financial Behavior
#   FW (7 items): Financial Well-being
#   FL (8 items): Financial Literacy
#   DT (6 items): Digital Trust

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0340002.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Area": "cov_area",
    "Education": "cov_education",
    "Occupation": "cov_occupation",
    "Income": "cov_income",
}

SCALES = {
    "anh_2026_finsocialization": [f"FS{i}" for i in range(1, 8)],
    "anh_2026_ai_adoption":      [f"AI{i}" for i in range(1, 9)],
    "anh_2026_finbehavior":      [f"FB{i}" for i in range(1, 10)],
    "anh_2026_finwellbeing":     [f"FW{i}" for i in range(1, 8)],
    "anh_2026_finliteracy":      [f"FL{i}" for i in range(1, 9)],
    "anh_2026_digitaltrust":     [f"DT{i}" for i in range(1, 7)],
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", **COV_COLS})
    assert df["id"].is_unique and df["id"].notna().all()

    cov_names = list(COV_COLS.values())
    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_names]
        path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
