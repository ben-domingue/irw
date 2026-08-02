from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0346791
# DOI: 10.1371/journal.pone.0346791
# Yoshimura et al. (2026), "Psychological safety as a context-sensitive
# predictor of retention intentions: Gendered effects of supervisor
# support under caregiving-assumed conditions". S1 Dataset. CC BY 4.0.
# N=522. Three column-prefix scale blocks (item text not in the file):
# es1m1-8 (8i, 1-5), isu1m9-14 (6i, 1-5), ps3m1-9 (9i, 1-7 -- "ps" =
# psychological safety per the paper title, matches the paper's own
# 1-7-scale description). `retain_care`/`retain_general` are single
# retention-intention outcome items, not shipped (no single-item scales).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0346791.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age": "cov_age", "gender": "cov_gender"}

SCALES = {
    "yoshimura_2026_es_scale": [f"es1m{i}" for i in range(1, 9)],
    "yoshimura_2026_isu_scale": [f"isu1m{i}" for i in range(9, 15)],
    "yoshimura_2026_psych_safety": [f"ps3m{i}" for i in range(1, 10)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "case_id": "id"})


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
