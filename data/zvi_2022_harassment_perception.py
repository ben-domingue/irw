from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0272606
# DOI: 10.1371/journal.pone.0272606
# Zvi & Shechory Bitton (2022), "In the eye of the beholder: Decision-making
# of lawyers in cases of sexual harassment". S1 File. CC BY 4.0. N=211
# (91 lawyers + 120 law students). Three distinct scales/response families
# in the same file, shipped as three separate tables per datastandard.md's
# "multiple scales in one file" rule:
#   - q1-q11 (11 items, 1-5): perception of the harassment vignette
#   - c1-c24 (24 items, 1-5): Rational-Experiential Inventory cognitive style
#   - J1-J27 (27 items, 1-7): legal judgment ratings
COV_COLS = {
    "grp": "cov_group",       # 1/2 vignette condition
    "perp": "cov_perpetrator",
    "vict": "cov_victim",
    "Age": "cov_age",
    "Country": "cov_country",
    "gend": "cov_gender",
    "famst": "cov_family_status",
    "chi_yn": "cov_has_children",
    "Religios": "cov_religiosity",
    "Education": "cov_education",
    "profession": "cov_profession",
    "years_of_employment": "cov_years_employment",
}

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0272606.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    cov_names = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"] + cov_names]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"no": "id", **COV_COLS})

    q_cols = [c for c in df.columns if c.startswith("q") and c[1:].isdigit()]
    c_cols = [c for c in df.columns if c.startswith("c") and c[1:].isdigit()]
    j_cols = [c for c in df.columns if c.startswith("J") and c[1:].isdigit()]

    for name, cols in [
        ("zvi_2022_harassment_perception", q_cols),
        ("zvi_2022_rei", c_cols),
        ("zvi_2022_legal_judgment", j_cols),
    ]:
        long = build_long(df, cols)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
