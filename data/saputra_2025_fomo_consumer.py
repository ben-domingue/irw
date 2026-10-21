"""
Fear of missing out and the digital consumer experience: 14 purchase-journey
statements answered by 100 Indonesian Nike consumers.

Source: Saputra, N. (2025). Dataset of Fear of Missing Out and the Digital
        Consumer Experience: Gender-Specific Analysis of Digital Moment of
        Truth [Dataset]. Zenodo.
DOI: 10.5281/zenodo.15363490
Data: https://zenodo.org/records/15363490 ("DAtaset NIKE 100 ISICO.xlsx",
        sheet "Form Responses 1")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id =
        cc-by-4.0)
Item text: shipped. The workbook's "BUAT SMARTPLS" sheet carries the same
        responses under full Indonesian stems, so code and wording are tied by
        EXACT VALUE EQUALITY across all 100 rows -- each coded column matches
        exactly one text-headed column and vice versa -- not by position.
        instrument: stems match no published scale (searched verbatim); they
        are Nike-specific purchase-journey statements written for this study
        ("Saya memposting produk Nike yang baru saya beli ..."), so this is
        NOT the Przybylski FoMO Scale, which is registered `block`; rights:
        study-authored under the deposit's CC BY 4.0.

Output: one table. All 14 items share one 1-5 agreement scale and were
administered as one questionnaire; the FM/FP/ZM/SM/UM prefixes are its
moment-of-truth stages.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = (Path(sys.argv[1]) if len(sys.argv) > 1
       else Path("DAtaset NIKE 100 ISICO.xlsx"))
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "saputra_2025_fomo_consumer"

ITEMS = ["FM02", "FM03", "FP01", "ZM02", "ZM03", "FM013", "FM024", "FM035",
         "SM01", "SM02", "SM03", "UM01", "UM02", "UM03"]
COV_MAP = {
    "FM01": "cov_gender",
    "PR02": "cov_purchase_frequency",
    "PR03": "cov_birth_year",
    "PR04": "cov_education",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # PR01 (domicile region), PR02, PR04 and FM01 are closed-answer; no name,
    # email, phone, address or date-of-birth column anywhere in the sheet.
    assert set(text_cols) <= {"PR01", "PR02", "PR04", "FM01"}, text_cols


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Form Responses 1")
    print("raw shape", df.shape)
    pii_screen(df)

    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    for c in ITEMS:
        assert c in df.columns, c

    used = {"id"} | set(COV_MAP) | set(covs) | set(ITEMS)
    skipped = {
        "Timestamp": "form submission time, not an item",
        "PR01": "domicile region within Indonesia (5 categories, e.g. "
                "'Daerah Khusus Jakarta Raya') -- sub-national geography, "
                "dropped rather than carried as a covariate under the "
                "2026-10-20 ruling",
    }
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")

    long = df[["id"] + covs + ITEMS].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
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
