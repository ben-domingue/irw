"""
EFL teachers' affective and cognitive responses to ChatGPT in higher
education: a 35-item questionnaire administered to 187 teachers.

Source: Wang, C. (2026). Understanding EFL Teachers' Affective and Cognitive
        Responses to ChatGPT in Higher Education [Dataset]. Mendeley Data.
DOI: 10.17632/zbmd5x98gp
Data: https://data.mendeley.com/datasets/zbmd5x98gp ("Questionnaire Data.xlsx")
License: CC BY 4.0 (verified on the Mendeley record, data_licence.short_name =
        "CC BY 4.0")
Item text: not shipped -- the workbook is item CODES only (PU1, PEU1, ATU1,
        BI1, TC1, ANX1, FC1, SE1, AIE1 ...) with no stems and no codebook
        file in the deposit. The wording would have to come from the article,
        which is not "already in hand".

Not to be confused with `wang_2026_efl_tam` (Wang et al. 2026, PLOS ONE,
digital game-based learning, N=500) -- a different deposit by different
authors that happens to share the TAM column-prefix convention.

Output: one table. All 35 items share one 1-5 agreement scale and were
administered together; the nine blocks (PU, PEU, ATU, BI, TC, ANX, FC, SE,
AIE) are its subscales, not separate instruments.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Questionnaire Data.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "wang_2026_chatgpt_acceptance"

# prefix -> number of items, in the workbook's own order.
BLOCKS = [("PU", 4), ("PEU", 3), ("ATU", 4), ("BI", 4), ("TC", 4),
          ("ANX", 4), ("FC", 4), ("SE", 4), ("AIE", 4)]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # Every column is numeric: a sequential ID plus the 35 coded items. No
    # demographics, no free text, nothing identifying.
    assert not text_cols, f"unexpected text columns: {text_cols}"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Sheet1")
    print("raw shape", df.shape)
    pii_screen(df)

    # The deposit's own ID is already 1..187, one row per teacher.
    assert df["ID"].is_unique, "ID is not one row per respondent"
    df = df.rename(columns={"ID": "id"})

    items = [f"{p}{i}" for p, n in BLOCKS for i in range(1, n + 1)]
    for c in items:
        assert c in df.columns, c
    assert len(items) == 35, len(items)

    leftover = [c for c in df.columns if c not in set(items) | {"id"}]
    assert not leftover, f"unaccounted source columns: {leftover}"

    long = df[["id"] + items].melt(id_vars=["id"], var_name="item",
                                   value_name="resp")
    write(long, TABLE, OUT)


def write(long: pd.DataFrame, table: str, out: Path) -> None:
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(float)
    assert not (long["resp"] % 1 != 0).any(), "fractional Likert values"
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"])
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
