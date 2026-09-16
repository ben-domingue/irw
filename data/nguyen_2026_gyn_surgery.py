#!/usr/bin/env python3
"""Reproduce the five existing Nguyen 2026 IRW response tables.

Source: https://doi.org/10.7910/DVN/X2C2PL, published version 1 (CC0).
File: gycosurganx_data_censored.xlsx, Harvard Dataverse file 14113156.
Download: https://dataverse.harvard.edu/api/access/datafile/14113156
The MD5 below is the checksum published by Dataverse for that exact file.
Dependencies: install this repository with `pip install -e .`, plus openpyxl.

Preserve source IDs, source variable names as item IDs, and recorded numeric
responses. Keep one table per instrument. No imputation, reverse scoring,
normalization, joining, row filtering, or deduplication is applied here.
This says nothing about processing that preceded the published workbook.

MSPSS: 12 items, 1--7; PIC: 9 items, 1--5; GAD-7: 7 items, 0--3;
ISI: 7 items, 0--4 (workbook vars/codes sheets). Barthel: 10 numeric
weighted item scores; preserve their unequal point ceilings. Do not rescale.
The workbook's codes sheet does not define individual Barthel item ceilings.

The 14 demographic, clinical, and pain fields are not items in these five
scales and are omitted, preserving the existing id,item,resp-only outputs.
Derived totals/groups listed in vars are absent from the data sheet.
Item tuples below follow source instrument order; final rows are sorted by
id,item, matching the existing CSVs, including lexicographic item ordering.

Example:
  python nguyen_2026_gyn_surgery.py --input gycosurganx_data_censored.xlsx \
      --out-dir new_output
Refuses a different source checksum or an existing output file.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import pandas as pd
from irw_validate import format_report, validate_frame

SOURCE_MD5 = "304a3442b9e3b0700410e65612f89602"
ITEMS = {
    "mspss": tuple(f"mspss_{i}" for i in range(1, 13)),
    "pic": tuple(f"pic_{i}" for i in range(1, 10)),
    "gad7": tuple(f"gad_{i}" for i in range(1, 8)),
    "barthel": (
        "bi_anuong", "bi_tam", "bi_chamsoccanhan", "bi_macquanao",
        "bi_daitien", "bi_tieutien", "bi_nhavesinh", "bi_dichuyen",
        "bi_dilai", "bi_cauthang",
    ),
    "isi": (
        "isi_vaogiac", "isi_duytri", "isi_daysom", "isi_hailong",
        "isi_clcs", "isi_lolang", "isi_sinhhoat",
    ),
}


def convert(input_path: Path, out_dir: Path) -> list[Path]:
    checksum = hashlib.md5(input_path.read_bytes()).hexdigest()
    if checksum != SOURCE_MD5:
        raise ValueError(f"Source checksum differs: expected {SOURCE_MD5}, got {checksum}")
    source = pd.read_excel(input_path, sheet_name="data")
    selected = ["ID", *(item for items in ITEMS.values() for item in items)]
    if source.shape != (394, 60) or not set(selected).issubset(source.columns):
        raise ValueError("Unexpected source dimensions or columns")
    if source["ID"].isna().any() or source["ID"].duplicated().any():
        raise ValueError("Source ID is missing or duplicated")
    if source[selected].isna().any().any():
        raise ValueError("Unexpected missing source ID or response; do not fill or drop it")
    if not all(pd.api.types.is_integer_dtype(source[c]) for c in selected):
        raise ValueError("Expected integer source IDs and item scores; refusing coercion")

    targets = [out_dir / f"nguyen_2026_{scale}.csv" for scale in ITEMS]
    if any(p.exists() for p in targets):
        raise FileExistsError("Output already exists; choose a new --out-dir")
    # Prepare and validate every table before writing any output.
    tables = []
    for scale, items in ITEMS.items():
        table = source[["ID", *items]].melt(
            id_vars="ID", value_vars=list(items), var_name="item", value_name="resp"
        ).rename(columns={"ID": "id"})
        table = table.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
        if len(table) != len(source) * len(items) or table.duplicated(["id", "item"]).any():
            raise ValueError(f"Unexpected participant-item layout for {scale}")
        report = validate_frame(table, label=f"nguyen_2026_{scale}", profile="upload")
        print(format_report(report))
        if not report.ok:
            raise ValueError(f"IRW validation failed for {scale}; no files written")
        tables.append(table)

    out_dir.mkdir(parents=True, exist_ok=True)
    for target, table in zip(targets, tables):
        # Exclusive creation protects pre-existing output files.
        with target.open("x", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["id", "item", "resp"])
            writer.writerows(table.itertuples(index=False, name=None))
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    for path in convert(args.input, args.out_dir):
        print(path.name)


if __name__ == "__main__":
    main()
