"""
Achievement motivation, general self-efficacy and perceived social support in
990 Chinese college students.

Source: Li, N., Yang, Y., Zhao, X., & Li, Y. (2023). "The relationship between
        achievement motivation and college students' general self-efficacy: A
        moderated mediation model." Frontiers in Psychology.
DOI: 10.3389/fpsyg.2022.1031912
Data: https://doi.org/10.3389/fpsyg.2022.1031912.s001 (Table_1 ... .xlsx,
        the article's Supporting Information)
License: CC BY 4.0 (verified on the article: Crossref reports
        creativecommons.org/licenses/by/4.0/, and Frontiers publishes under
        CC BY 4.0)
Item text: IN HAND but NOT shipped -- every item column header is the full
        English stem, so the text costs nothing to read. It is held on rights,
        not on availability: the three blocks are canonical published
        instruments, not study-authored items --
          * General self-efficacy, 10 items == the General Self-Efficacy Scale
            (GSE; Schwarzer & Jerusalem 1995), Chinese version (Wang, Wu &
            Wang 2001);
          * Achievement motivation, 30 items == the Achievement Motives Scale
            (AMS; Gjesme & Nygard 1970), Chinese revision (Ye & Hagtvet 1992);
          * Perceived social support, 12 items == the Multidimensional Scale of
            Perceived Social Support (MSPSS; Zimet et al. 1988).
        Stems were searched verbatim to establish each. The deposit's CC BY
        covers the authors' own material, not a third-party instrument
        reproduced inside it, and none of the three had a row in
        itemtext/instrument_rights_register.csv when this was written, so
        silence does not ship. Rows were added there with the verdict.

Output: three tables, one per instrument -- they are three different
instruments on three different response scales (1-4, 1-5, 1-7).

Item codes are derived from the source's own numbering inside each block
("Achievement motivation—1.", "2.", ... "30."), parsed off the header rather
than assigned by position, and asserted to run 1..n with no gaps.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Table_1.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# (block header marker, n items, item-code prefix, table name)
BLOCKS = [
    ("General self-efficacy", 10, "gse", "li_2023_self_efficacy"),
    ("Achievement motivation", 30, "ams", "li_2023_achievement_motivation"),
    ("Perceived social support", 12, "mspss", "li_2023_social_support"),
]

COV_MAP = {
    "1.Gender": "cov_gender",
    "2.Grade": "cov_grade",
    "3. What sports do you like?": "cov_sport_preference",
    "4. What is the intensity of your physical exercise?":
        "cov_exercise_intensity",
    "5. How many minutes do you spend in the above-mentioned intensive sports "
    "activities?": "cov_exercise_minutes",
    "6. How many times do you do the above sports activities a month?":
        "cov_exercise_times_per_month",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # Submission time, elapsed time, submission channel, and three
    # closed-answer demographics. No free-text field, no identifier, no
    # geographic column.
    expect = {"Submission time", "Time", "Source", "Source detail",
              "1.Gender", "2.Grade", "3. What sports do you like?"}
    assert set(text_cols) == expect, f"unexpected text columns: {text_cols}"


def item_number(header: str) -> int:
    """The source's own item number, off the front of the header. Blocks are
    headed 'Instrument name—1.<stem>'; later items are '2.<stem>', and item 13
    of the AMS uses a comma instead of a period."""
    h = header.split("—")[-1].strip()
    m = re.match(r"(\d+)\s*[.,]", h)
    assert m, f"no leading item number in {header!r}"
    return int(m.group(1))


def split_blocks(cols: list[str]) -> dict[str, list[str]]:
    """Columns belonging to each instrument, in source order. A block starts at
    the header carrying its name and runs until the next block's header."""
    starts = {}
    for marker, _n, _p, _t in BLOCKS:
        hits = [c for c in cols if c.startswith(marker)]
        assert len(hits) == 1, (marker, hits)
        starts[marker] = cols.index(hits[0])
    order = sorted(starts.items(), key=lambda kv: kv[1])
    out = {}
    for i, (marker, start) in enumerate(order):
        end = order[i + 1][1] if i + 1 < len(order) else len(cols)
        out[marker] = cols[start:end]
    return out


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Sheet1")
    print("raw shape", df.shape)
    pii_screen(df)

    assert df["Order number"].is_unique, "Order number is not one row/person"
    df["id"] = df["Order number"].astype(int)

    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    # "172seconds" is time to complete the WHOLE questionnaire, not a per-item
    # response time, so it is a named covariate and never `rt`.
    df["cov_completion_time_s"] = (
        df["Time"].astype(str).str.replace("seconds", "", regex=False)
        .str.strip().astype(int))
    covs = list(COV_MAP.values()) + ["cov_completion_time_s"]

    cols = list(pd.read_excel(SRC, sheet_name="Sheet1", nrows=0).columns)
    blocks = split_blocks(cols)

    used = {"Order number", "id", "Time"} | set(COV_MAP) | set(covs)
    for marker, n, prefix, table in BLOCKS:
        bcols = blocks[marker]
        assert len(bcols) == n, (marker, len(bcols), n)
        nums = [item_number(c) for c in bcols]
        assert nums == list(range(1, n + 1)), (marker, nums)
        used.update(bcols)
        long = df[["id"] + covs + bcols].rename(
            columns={c: f"{prefix}_{k}" for c, k in zip(bcols, nums)})
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        write(long, table, OUT)

    skipped = {
        "Submission time": "questionnaire submission timestamp, not an item",
        "Source": "submission channel (mobile / WeChat), survey plumbing",
        "Source detail": "submission channel detail, one value for all 990 rows",
    }
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")


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
