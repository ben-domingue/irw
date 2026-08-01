from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199480
# DOI: 10.1371/journal.pone.0199480
# Silva, Campos, Maroco et al. (2018), "Impact of inherent aspects of body
# image, eating behavior and perceived health competence on quality of
# life of university students". S1 Dataset. CC BY 4.0. N~2096 Brazilian
# university students.
#
# "Code_identification" is NOT a reliable person id (spot-checked several
# duplicate codes and found different Age/Sex under the same code --
# coincidental collisions, not repeated measurements of the same person),
# so row position is used as id instead.
#
# Five instruments, each confirmed via its own item-number suffixes and a
# plausible response range -> five output files:
#   silva_2018_mbds: Male/Muscle Body Dissatisfaction-type scale, 12 items,
#     continuous 0.1-5.0 (VAS-style, fractional throughout the
#     distribution, not isolated errors).
#   silva_2018_bsq: Body Shape Questionnaire (BSQ-8 short form, item
#     numbers 5/11/15/20/21/22/25/28 match the published short form), 8
#     items, 1-6.
#   silva_2018_whoqol: WHOQoL-BREF (abbreviated item set), 20 items, 1-5.
#   silva_2018_phcs: Perceived Health Competence Scale, 8 items, 1-5.
#   silva_2018_tfeq: Three-Factor Eating Questionnaire (abbreviated item
#     set), 21 items, 0-5.

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0199480.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age": "cov_age", "Sex": "cov_sex", "Country": "cov_country"}


def fetch() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])
    df["id"] = range(1, len(df) + 1)
    return df


def ship(df: pd.DataFrame, cov_cols: list[str], prefix: str, out_name: str):
    item_cols = [c for c in df.columns if c.startswith(prefix)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.1f}-{long['resp'].max():.1f}")


def convert():
    df = fetch().rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ship(df, cov_cols, "MBDS", "silva_2018_mbds")
    ship(df, cov_cols, "BSQ", "silva_2018_bsq")
    ship(df, cov_cols, "WHOQoL", "silva_2018_whoqol")
    ship(df, cov_cols, "PHCS", "silva_2018_phcs")
    ship(df, cov_cols, "TFEQ", "silva_2018_tfeq")


if __name__ == "__main__":
    convert()
