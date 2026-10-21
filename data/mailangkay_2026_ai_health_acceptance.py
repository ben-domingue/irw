"""
Student acceptance of AI-based healthcare applications, an extended Technology
Acceptance Model administered to 200 Indonesian students.

Source: Mailangkay, A., & Krisastianto, G. A. W. (2026). Student Acceptance of
        Artificial Intelligence-Based Healthcare Applications: An Extended
        Technology Acceptance Model Approach [Dataset].
DOI: 10.5281/zenodo.22084963
Data: https://zenodo.org/records/22084963 ("Cleaned Data.xlsx")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id =
        cc-by-4.0)
Item text: not shipped -- the deposit carries item CODES only (PEOU 1, PU 1,
        ...), no stems anywhere in the workbook and no codebook file. The
        wording would have to come from the published article, which is not
        "already in hand".

Output: one table. All 50 items share one 1-6 agreement scale and were
administered together as a single extended-TAM instrument; the ten five-item
blocks (PEOU, PU, ATT, BI, AU, TR, PR, TiT, FC, SN) are its subscales, not
separate instruments, so they stay in one file.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Cleaned Data.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "mailangkay_2026_ai_health_acceptance"

COV_MAP = {
    "Jenis Kelamin": "cov_sex",
    "Umur": "cov_age_band",
    "Tingkat Pendidikan": "cov_education",
    "Apakah anda pernah memakai aplikasi kesehatan yang berbasis AI?":
        "cov_prior_ai_health_app_use",
}

# Subscale prefixes, five items each. The source spells two codes with a
# leading space (" ATT 5", " TR 4"); the item code ships stripped.
PREFIXES = ["PEOU", "PU", "ATT", "BI", "AU", "TR", "PR", "TiT", "FC", "SN"]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # The four are closed-answer demographics (sex, age band, education level,
    # prior-use frequency); no free-text field, no identifier column.
    assert set(text_cols) == set(COV_MAP), f"unexpected text columns: {text_cols}"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Form responses 1")
    print("raw shape", df.shape)
    pii_screen(df)

    df.columns = [str(c).strip() for c in df.columns]
    cov_map = {k.strip(): v for k, v in COV_MAP.items()}

    df["id"] = range(1, len(df) + 1)
    for src, dst in cov_map.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(cov_map.values())

    items = [f"{p} {i}" for p in PREFIXES for i in range(1, 6)]
    for c in items:
        assert c in df.columns, c

    # Balance the books.
    used = set(items) | set(cov_map) | set(covs) | {"id"}
    skipped = {"Timestamp": "survey submission time, not an item"}
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")

    long = df[["id"] + covs + items].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace(" ", "_", regex=False)

    write(long, TABLE, OUT)


def write(long: pd.DataFrame, table: str, out: Path) -> None:
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(float)
    assert not (long["resp"] % 1 != 0).any(), "fractional Likert values"
    long["resp"] = long["resp"].astype(int)
    cols = ["id", "item", "resp"] + [c for c in long.columns
                                     if c.startswith("cov_")]
    long = long[cols].sort_values(["id", "item"])
    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(out / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
