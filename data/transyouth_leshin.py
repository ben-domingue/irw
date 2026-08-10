"""
transyouth_leshin.py

Generic command-line tool to reshape wide-format item-response CSVs
(one row per person, one column per item) into IRW-standard long-format
tables with columns: id, item, resp

USE COMMAND LINE ARGUMENT --> 
"python3 transyouth_leshin.py --input-dir . --output-dir irw_tables --prefix transyouth_leshin_2026_"

Ensure all raw files are in the same folder as the .py file. 
"""

import argparse
import glob
import os
import sys
from typing import Dict, List, Optional

import pandas as pd


def derive_table_name(path: str, rename_map: Dict[str, str], strip_suffix: str,
                       prefix: str) -> str:
    """Work out the output table name for a given input file.

    Precedence: an explicit --rename entry is used as-is (no prefix added,
    since it's a full override). Otherwise, the filename stem has
    strip_suffix removed (if present) and prefix prepended.
    """
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem in rename_map:
        return rename_map[stem]
    if strip_suffix and stem.endswith(strip_suffix):
        stem = stem[: -len(strip_suffix)]
    return f"{prefix}{stem}"


def wide_to_irw_long(path: str, id_column: Optional[str]) -> pd.DataFrame:
    """Read a wide-format CSV (id column + item columns) and return an
    IRW-standard long-format DataFrame with columns: id, item, resp.
    """
    df = pd.read_csv(path)

    if df.shape[1] < 2:
        raise ValueError(f"{path} needs at least one ID column and one item column.")

    if id_column is not None:
        if id_column not in df.columns:
            raise ValueError(
                f"id column '{id_column}' not found in {path}. "
                f"Available columns: {list(df.columns)}"
            )
        item_cols = [c for c in df.columns if c != id_column]
        df = df.rename(columns={id_column: "id"})
    else:
        # Default: treat the first column as the ID column, whatever it's named.
        df = df.rename(columns={df.columns[0]: "id"})
        item_cols = list(df.columns[1:])

    long_df = df.melt(id_vars="id", value_vars=item_cols, var_name="item", value_name="resp")

    # Preserve original item order (melt's default is alphabetical), then
    # sort by person so the file reads top-to-bottom per respondent.
    long_df["item"] = pd.Categorical(long_df["item"], categories=item_cols, ordered=True)
    long_df = long_df.sort_values(["id", "item"]).reset_index(drop=True)

    return long_df


def parse_rename_args(rename_list: Optional[List[str]]) -> Dict[str, str]:
    rename_map = {}
    for entry in rename_list or []:
        if "=" not in entry:
            raise ValueError(f"--rename entries must be formatted old=new, got: {entry}")
        old, new = entry.split("=", 1)
        rename_map[old.strip()] = new.strip()
    return rename_map


def collect_input_files(files: List[str], input_dir: Optional[str]) -> List[str]:
    collected = list(files)
    if input_dir:
        collected.extend(sorted(glob.glob(os.path.join(input_dir, "*.csv"))))
    # De-duplicate while preserving order.
    seen = set()
    unique_files = []
    for f in collected:
        if f not in seen:
            unique_files.append(f)
            seen.add(f)
    return unique_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reshape wide-format item-response CSVs into IRW-standard "
                     "long-format (id, item, resp) tables. No paths or table "
                     "names are hard-coded."
    )
    parser.add_argument("files", nargs="*", help="Specific input CSV file(s) to process.")
    parser.add_argument(
        "--input-dir",
        help="Directory containing input CSV files (every *.csv in it is processed).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write the long-format output CSVs to (created if missing).",
    )
    parser.add_argument(
        "--id-column",
        default=None,
        help="Name of the column to use as the person ID. "
             "Defaults to the first column in each file.",
    )
    parser.add_argument(
        "--rename",
        action="append",
        default=[],
        help="Override an output table name: old_filename_stem=new_name. "
             "Can be passed multiple times, one per file.",
    )
    parser.add_argument(
        "--strip-suffix",
        default="_raw",
        help='Suffix to strip from the filename stem when deriving the default '
             'table name (default: "_raw"). Pass an empty string to disable.',
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Text to prepend to every default (non --rename-overridden) output "
             "table name, e.g. --prefix transyouth_leshin_2026_ turns "
             "'youth_dep_raw.csv' into 'transyouth_leshin_2026_youth_dep.csv'.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    input_files = collect_input_files(args.files, args.input_dir)
    if not input_files:
        parser.error("No input files given. Pass one or more CSV paths and/or --input-dir.")

    rename_map = parse_rename_args(args.rename)
    os.makedirs(args.output_dir, exist_ok=True)

    input_stems = {os.path.splitext(os.path.basename(p))[0] for p in input_files}
    unmatched_renames = set(rename_map) - input_stems
    if unmatched_renames:
        print(
            f"Warning: --rename key(s) {sorted(unmatched_renames)} did not match "
            f"any input filename stem and were ignored. Rename keys must equal "
            f"the input filename without its extension, e.g. 'myfile' for "
            f"'myfile.csv'.",
            file=sys.stderr,
        )

    summary_rows = []
    for path in input_files:
        table_name = derive_table_name(path, rename_map, args.strip_suffix, args.prefix)
        try:
            long_df = wide_to_irw_long(path, args.id_column)
        except Exception as exc:
            print(f"Skipping {path}: {exc}", file=sys.stderr)
            continue

        out_path = os.path.join(args.output_dir, f"{table_name}.csv")
        long_df.to_csv(out_path, index=False)

        summary_rows.append(
            {
                "table": table_name,
                "source_file": path,
                "n_people": long_df["id"].nunique(),
                "n_items": long_df["item"].nunique(),
                "n_rows": len(long_df),
                "resp_min": long_df["resp"].min(),
                "resp_max": long_df["resp"].max(),
                "output_file": out_path,
            }
        )

    if summary_rows:
        print(pd.DataFrame(summary_rows).to_string(index=False))
    else:
        print("No files were processed successfully.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()