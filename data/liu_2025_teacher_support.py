from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0314338
# DOI: 10.1371/journal.pone.0314338
# Liu, Yan & Li (2025). Physical education teachers' competence support and
# middle school students' participation in sports: the chain mediating role
# of basic psychological needs and exercise persistence. PLOS ONE.
# Data: Dryad (https://doi.org/10.5061/dryad.brv15dvkd), shared as S1 File (SAV).
#
# The raw SAV file contains 879 middle-school students x 7 raw item groups
# (identified by Chinese-pinyin column prefixes) plus a trailing block of
# already-computed subscale sums/means (JSZZZC, YDLQ, YDCY, XLJK, JSNLZC,
# JSGLZC, YDJC, NLGZ, JJQX, JSZC) which are EXCLUDED here as composites, not
# raw responses. Only the raw per-item columns (integer-valued, prefix+digit)
# are shipped. Because the paper's English text only explicitly names 4
# instruments (teacher competence support, perceived competence, exercise
# persistence, PARS-3) while the data contains 7 distinct item-prefix groups,
# we ship each prefix group as its own file using a neutral label built from
# the original abbreviation rather than guessing an English construct name
# beyond what the paper confirms. Original column names are preserved as
# item ids for downstream item-text matching.
#
# QC fix (2026-08-12, ben-domingue catch): YDCY1 is constant (resp=1 for
# all 879 respondents, confirmed within every cov_grade level) -- a
# gating/filter question, not a real scale item -- so it's excluded from
# the item set. YDCY3's zero values (58/879, ~7% of that item's non-null
# responses) are isolated to that single item with no 0s anywhere else in
# the YDCY block -- the exact cross-item data-entry-error signature
# datastandard.md describes -- so YDCY's valid range is tightened to 1-5
# and those zeros are filtered out rather than kept as a genuine anchor.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SAV_URL = "https://doi.org/10.1371/journal.pone.0314338.s001"

COV_COLS = {"GENDERS": "cov_gender", "AGE": "cov_age", "GRADE": "cov_grade"}

# prefix -> (output file suffix, expected item count, valid resp range)
SCALES = {
    "JSZC": ("teacher_support", 15, (1, 7)),
    "YDJC": ("perceived_competence", 4, (1, 5)),
    "YDLQ": ("ydlq", 10, (1, 5)),
    "NLGZ": ("nlgz", 4, (1, 5)),
    "YDCY": ("ydcy", 4, (1, 5)),  # YDCY1 excluded (constant column, see note above)
    "JJQX": ("jjqx", 10, (1, 5)),
    "XLJK": ("xljk", 12, (0, 1)),
}


def fetch_data() -> pd.DataFrame:
    import pyreadstat

    r = requests.get(SAV_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = OUT_DIR.parent / "_tmp_liu2025.sav"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(r.content)
    df, _ = pyreadstat.read_sav(str(tmp))
    tmp.unlink(missing_ok=True)
    return df


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"编号": "id"})
    df = df.rename(columns=COV_COLS)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"

    cov_cols = [c for c in COV_COLS.values() if c in df.columns]

    for prefix, (suffix, n_expected, (lo, hi)) in SCALES.items():
        item_cols = [c for c in df.columns if c.startswith(prefix) and c[len(prefix):].isdigit()]
        item_cols = sorted(item_cols, key=lambda c: int(c[len(prefix):]))
        if prefix == "YDCY":
            item_cols = [c for c in item_cols if c != "YDCY1"]  # constant column, not a real item
        else:
            assert len(item_cols) == n_expected, f"{prefix}: expected {n_expected} items, found {len(item_cols)}"

        long = df[["id"] + cov_cols + item_cols].melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        col_order = ["id", "item", "resp"] + cov_cols
        long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"liu_2025_{suffix}.csv"
        write_scale(long, fname)


if __name__ == "__main__":
    convert()
