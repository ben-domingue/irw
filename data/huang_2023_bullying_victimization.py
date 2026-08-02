from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0290452
# DOI: 10.1371/journal.pone.0290452
# Huang et al. (2023), "The healthy context paradox of bullying
# victimization and academic adjustment among Chinese adolescents: A
# moderated mediation model". S1 Dataset. CC BY 4.0. N=631.
# Four column-prefix scale blocks (no item text in the file): b1-12
# (1-5), c1-30 (binary 1-2), d1-9 (1-7), e1-25 (1-4). Blocks c and e each
# had a handful of out-of-range values (22/44/11/33 etc.) on otherwise
# strictly binary/4-point items -- a digit-duplication data-entry pattern
# (e.g. "2" mistyped as "22") -- filtered as errors.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0290452.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"age": "cov_age", "gander": "cov_gender"}

SCALES = {
    "huang_2023_b_scale": ([f"b{i}" for i in range(1, 13)], (1, 5)),
    "huang_2023_c_scale": ([f"c{i}" for i in range(1, 31)], (1, 2)),
    "huang_2023_d_scale": ([f"d{i}" for i in range(1, 10)], (1, 7)),
    "huang_2023_e_scale": ([f"e{i}" for i in range(1, 26)], (1, 4)),
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "XH": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, (item_cols, (lo, hi)) in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
