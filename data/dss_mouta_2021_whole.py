#!/usr/bin/env python3
"""
Convert Decision Styles Scale (DSS) raw data to the IRW long-format standard.

Drop this script in the folder holding the raw files and run it with no arguments:

    python dss_mouta_2021.py

It reads from its own folder and writes to an `output` subfolder next to itself.
Override either with --input-dir / --output-dir if the files live elsewhere.

"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================================
# CONFIG — the only part that is specific to this dataset
# ============================================================================

# Column holding the respondent identifier. First one present in the file wins.
ID_COLUMNS = ["ID", "COD.", "id"]

# How to recognise a wide item column, and how to pull its number out.
ITEM_PATTERN = re.compile(r"^v(\d+)$", re.IGNORECASE)

# Prefix for item ids in the output: item 3 -> dss_03
ITEM_PREFIX = "dss"

# Output table name: <TABLE_STEM>.csv
TABLE_STEM = "dss_mouta_2021"

# Which item numbers belong to which construct (Fig. 1 of the paper).
CONSTRUCTS = {
    "rational": [1, 3, 5, 7, 9],
    "intuitive": [2, 4, 6, 8, 10],
}

# Column recording which construct each item measures. This is an item-level
# covariate (invariant for the probe), so it takes the IRW itemcov_ prefix.
CONSTRUCT_COLUMN = "itemcov_construct"

# Valid range for `resp`. Set to None to skip the range check.
RESP_RANGE = (1, 5)

# Author-computed sum-score columns, used only to validate the conversion.
# They are never written to the output.
SCORE_COLUMNS = {"rational": "Racional_A", "intuitive": "Intuitivo_A"}

# Covariates: source column -> output name + cleaning rules. Any source column
# missing from a given file is simply skipped.
COVARIATES = [
    ("sexo", "cov_sex", {"map": {"Feminino": "female", "Masculino": "male"}}),
    ("idade", "cov_age", {"numeric": True}),
    # decimal comma in the raw file; "16,17" looks like two values typed into
    # one cell, so it is dropped rather than guessed at
    ("escol", "cov_edu_years", {"decimal_comma": True, "na_values": ["16,17"], "numeric": True}),
    ("estado", "cov_state", {"split_take": (" - ", 0)}),  # "AM - Amazonas" -> "AM"
    ("css", "cov_ses_score", {"numeric": True}),
    ("csc", "cov_ses_class", {"replace": {"D-E": "DE"}}),
]

# Columns known to be empty or derived; listed so the script reports on them
# rather than silently ignoring them.
EXPECTED_DROPS = ["prof", "ec", "Racional_A", "Intuitivo_A"]

ENCODINGS = ["utf-8", "utf-8-sig", "latin-1"]

# File types that are never tabular input; skipped without attempting a parse.
SKIP_SUFFIXES = {".pdf", ".doc", ".docx", ".zip", ".png", ".jpg", ".jpeg",
                 ".sav", ".dta", ".rds", ".rdata", ".xls", ".xlsx"}

# ============================================================================


def read_any_csv(path: Path) -> pd.DataFrame:
    """Read a delimited text file, sniffing encoding and delimiter."""
    raw, encoding = None, None
    for enc in ENCODINGS:
        try:
            raw = path.read_text(encoding=enc)
            encoding = enc
            break
        except (UnicodeDecodeError, ValueError):
            continue
    if raw is None:
        raise ValueError(f"could not decode with any of {ENCODINGS}")

    sample = "\n".join(raw.splitlines()[:20])
    try:
        sep = csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
    except csv.Error:
        sep = max(";,\t|", key=sample.count)

    df = pd.read_csv(path, sep=sep, encoding=encoding)
    df.attrs["encoding"] = encoding
    df.attrs["sep"] = sep
    return df


def find_id_column(df: pd.DataFrame) -> str | None:
    for candidate in ID_COLUMNS:
        if candidate in df.columns:
            return candidate
    return None


def find_item_columns(df: pd.DataFrame) -> dict[int, str]:
    """Map item number -> column name for every wide item column present."""
    found = {}
    for col in df.columns:
        match = ITEM_PATTERN.match(str(col).strip())
        if match:
            found[int(match.group(1))] = col
    return found


def clean_covariate(series: pd.Series, rules: dict) -> pd.Series:
    out = series
    if "na_values" in rules:
        out = out.replace(rules["na_values"], np.nan)
    if "map" in rules:
        return out.map(rules["map"])
    if "replace" in rules:
        out = out.replace(rules["replace"])
    if "split_take" in rules:
        delim, index = rules["split_take"]
        out = out.astype(str).str.split(delim).str[index].replace("nan", np.nan)
    if rules.get("decimal_comma"):
        out = out.astype(str).str.strip().replace("nan", np.nan)
        out = out.str.replace(",", ".", regex=False)
    if rules.get("numeric"):
        out = pd.to_numeric(out, errors="coerce")
    return out


def build_covariates(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    cov = pd.DataFrame({"id": df[id_col].astype(str).str.strip()})
    for source, target, rules in COVARIATES:
        if source in df.columns:
            cov[target] = clean_covariate(df[source], rules).values
    return cov


def to_long(df: pd.DataFrame, id_col: str, item_cols: dict[int, str],
            numbers: list[int], cov: pd.DataFrame) -> pd.DataFrame:
    """Melt the selected wide item columns into IRW long format."""
    cols = [item_cols[n] for n in numbers]
    wide = df[[id_col] + cols].copy()
    wide[id_col] = wide[id_col].astype(str).str.strip()

    long = wide.melt(id_vars=id_col, var_name="item", value_name="resp")
    long = long.rename(columns={id_col: "id"})

    # item ids preserve the original numbering so they map back to the
    # published item text
    lookup = {col: f"{ITEM_PREFIX}_{n:02d}" for n, col in item_cols.items()}
    long["item"] = long["item"].map(lookup)

    long["resp"] = pd.to_numeric(long["resp"], errors="coerce").astype("Int64")

    long = long.merge(cov, on="id", how="left")
    long = long.sort_values(["id", "item"], kind="mergesort").reset_index(drop=True)

    ordered = ["id", "item", "resp"] + [c for c in cov.columns if c != "id"]
    return long[ordered]


def validate(long: pd.DataFrame, n_persons: int, n_items: int, label: str) -> None:
    problems = []
    if long["resp"].isna().any():
        problems.append(f"{int(long['resp'].isna().sum())} missing responses")
    if RESP_RANGE is not None:
        lo, hi = RESP_RANGE
        vals = long["resp"].dropna()
        bad = vals[(vals < lo) | (vals > hi)]
        if len(bad):
            problems.append(f"{len(bad)} responses outside {lo}-{hi}")
    if long.duplicated(["id", "item"]).any():
        problems.append(f"{int(long.duplicated(['id', 'item']).sum())} duplicate id/item pairs")
    if len(long) != n_persons * n_items:
        problems.append(f"expected {n_persons * n_items} rows, got {len(long)}")
    if problems:
        raise ValueError(f"{label}: " + "; ".join(problems))


def process_file(path: Path, out_dir: Path) -> list[Path]:
    if path.suffix.lower() in SKIP_SUFFIXES:
        print(f"  skipped - {path.suffix} is not a tabular data file")
        return []

    df = read_any_csv(path)
    id_col = find_id_column(df)
    item_cols = find_item_columns(df)

    if id_col is None:
        print(f"  skipped - no id column (looked for {ID_COLUMNS})")
        return []
    if not item_cols:
        print("  skipped - no item-level response columns; nothing to put in `resp`")
        return []

    print(f"  read as {df.attrs['encoding']}, '{df.attrs['sep']}'-separated: "
          f"{len(df):,} rows x {len(df.columns)} cols")

    ids = df[id_col].astype(str).str.strip()
    if not ids.is_unique:
        print(f"  skipped - {int(ids.duplicated().sum())} duplicate ids in {id_col}")
        return []

    dropped = [c for c in EXPECTED_DROPS if c in df.columns]
    empty = [c for c in df.columns if df[c].isna().all()]
    if dropped:
        note = f" (fully empty: {', '.join(empty)})" if empty else ""
        print(f"  not carried through: {', '.join(dropped)}{note}")

    cov = build_covariates(df, id_col)
    pieces = []

    for construct, numbers in CONSTRUCTS.items():
        present = [n for n in numbers if n in item_cols]
        if not present:
            continue
        if len(present) < len(numbers):
            missing = sorted(set(numbers) - set(present))
            print(f"  warning - {construct}: items {missing} absent from this file")

        long = to_long(df, id_col, item_cols, present, cov)
        validate(long, len(df), len(present), construct)

        # item-level covariate: which subscale the item belongs to. IRW uses the
        # itemcov_ prefix for covariates invariant for the measurement probe.
        long.insert(3, CONSTRUCT_COLUMN, construct)
        pieces.append(long)

        score_col = SCORE_COLUMNS.get(construct)
        if score_col and score_col in df.columns:
            recon = long.groupby("id")["resp"].sum()
            orig = df.set_index(ids)[score_col].reindex(recon.index)
            agree = (recon == orig).mean()
            flag = "" if agree == 1 else "   <-- CHECK"
            print(f"  {construct:10s} sum-score check vs {score_col}: "
                  f"{agree:.1%} exact match{flag}")

    if not pieces:
        print("  skipped - no configured items found in this file")
        return []

    combined = pd.concat(pieces, ignore_index=True)
    combined = combined.sort_values(["id", "item"], kind="mergesort").reset_index(drop=True)

    # each item belongs to exactly one construct
    per_item = combined.groupby("item")[CONSTRUCT_COLUMN].nunique()
    if (per_item > 1).any():
        raise ValueError("an item is assigned to more than one construct")
    validate(combined, len(df), combined["item"].nunique(), "combined")

    dest = out_dir / f"{TABLE_STEM}.csv"
    combined.to_csv(dest, index=False)
    print(f"  wrote {dest.name}: {len(combined):,} rows | "
          f"{combined.id.nunique():,} persons | {combined.item.nunique()} items")
    counts = combined.groupby(CONSTRUCT_COLUMN)["item"].nunique()
    for construct, n_items in counts.items():
        rows = int((combined[CONSTRUCT_COLUMN] == construct).sum())
        print(f"    {CONSTRUCT_COLUMN}={construct:10s} {n_items} items, {rows:,} rows")
    written = [dest]

    print("\n  response distribution by item:")
    table = pd.crosstab([combined[CONSTRUCT_COLUMN], combined["item"]],
                        combined["resp"]).to_string()
    print("    " + table.replace("\n", "\n    "))
    print("\n  covariate completeness (person level):")
    person = combined.drop_duplicates("id")
    for col in [c for c in person.columns if c.startswith("cov_")]:
        print(f"    {col:20s} {person[col].notna().mean() * 100:5.1f}%")

    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input-dir", type=Path, default=None,
                        help="folder containing the raw files "
                             "(default: the folder this script is in)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="where to write the IRW tables "
                             "(default: an 'output' folder next to this script)")
    parser.add_argument("--pattern", default="*",
                        help="glob for candidate raw files (default: *)")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    input_dir = (args.input_dir or here).resolve()
    output_dir = (args.output_dir or here / "output").resolve()

    print(f"reading from : {input_dir}")
    print(f"writing to   : {output_dir}")

    if not input_dir.is_dir():
        print(f"error: {input_dir} is not a directory", file=sys.stderr)
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)

    # don't re-ingest tables from a previous run
    produced = {f"{TABLE_STEM}.csv"}
    candidates = sorted(
        p for p in input_dir.glob(args.pattern)
        if p.is_file()
        and p.name not in produced
        and p.resolve().parent != output_dir
        and p.suffix.lower() != ".py"
    )
    if not candidates:
        print(f"error: no candidate files matching '{args.pattern}' in {input_dir}",
              file=sys.stderr)
        return 1

    written = []
    for path in candidates:
        print(f"\n{path.name}")
        try:
            written += process_file(path, output_dir)
        except Exception as exc:  # keep going through the rest of the folder
            print(f"  FAILED - {exc}")

    print(f"\n{'=' * 60}\n{len(written)} table(s) written to {output_dir}")
    for path in written:
        print(f"  {path.name}")
    return 0 if written else 1


if __name__ == "__main__":
    sys.exit(main())