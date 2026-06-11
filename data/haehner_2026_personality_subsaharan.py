from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd

try:
    import pyreadr
except ImportError:
    pyreadr = None


DEFAULT_RDATA = os.path.join("osfstorage-archive (2)", "Data", "data_scored.RData")
OUTPUT_DIR = "haehner_2026_personality_subsaharan"


def _norm_col(c: str) -> str:
    return str(c).strip().lower().replace(" ", "_").replace(".", "_")


WAVE_RE = re.compile(r"_w(\d+)$")


def _irw_column_order(df: pd.DataFrame) -> pd.DataFrame:
    core = ["id", "item", "resp"]
    extra_order = [c for c in ("wave",) if c in df.columns]
    itemcovs = sorted(c for c in df.columns if c.startswith("itemcov_"))
    covs = sorted(c for c in df.columns if c.startswith("cov_"))
    accounted = set(core + extra_order + itemcovs + covs)
    leftover = [c for c in df.columns if c not in accounted]
    return df[core + extra_order + leftover + itemcovs + covs]


def _melt_irw(df: pd.DataFrame, item_cols: list[str], outfile: Path) -> int:
    cov_cols = [c for c in df.columns if c.startswith("cov_")]
    id_vars = ["id"] + cov_cols
    long = df.melt(id_vars=id_vars, value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].astype(str)

    wave_match = long["item"].str.extract(WAVE_RE.pattern)
    long["wave"] = pd.to_numeric(wave_match[0], errors="coerce").astype("Int64")
    long["item"] = long["item"].str.replace(WAVE_RE, "", regex=True)

    long = _irw_column_order(long)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(outfile, index=False)
    return len(long)


def _b2i_item_columns(norm_cols: list[str]) -> list[str]:
    wave = re.compile(r"_w[135]$")
    out = []
    for c in norm_cols:
        if not c.startswith("b2i_"):
            continue
        if "_cmn" in c or "_agy" in c:
            continue
        if not wave.search(c):
            continue
        out.append(c)
    return sorted(set(out))


def _ecq_item_columns(norm_cols: list[str]) -> list[str]:
    raw = re.compile(r"^ecq\d+_w[45]$")
    return sorted(c for c in norm_cols if raw.match(c))


def cov_source_columns(norm_cols: list[str]) -> list[str]:
    want = [
        "country",
        "age",
        "gender",
        "education",
        "finance",
        "look_employ",
        "english_w3",
        "overall_response_control_w1",
    ]
    return [c for c in want if c in norm_cols]


def convert_saharan_to_irw(
    rdata_path: Path | None = None,
    out_dir: Path | None = None,
) -> None:
    if pyreadr is None:
        print("Missing pyreadr. Run: pip install pyreadr", file=sys.stderr)
        sys.exit(1)

    base = Path(__file__).resolve().parent
    inp = Path(rdata_path) if rdata_path else base / DEFAULT_RDATA
    if not inp.is_file():
        print(f"RData not found: {inp}", file=sys.stderr)
        sys.exit(1)

    out = Path(out_dir) if out_dir else base / OUTPUT_DIR

    rd = pyreadr.read_r(str(inp))
    if not rd:
        print("Empty RData", file=sys.stderr)
        sys.exit(1)
    if "data" in rd:
        df = rd["data"]
    elif len(rd) == 1:
        df = next(iter(rd.values()))
    else:
        k, df = next(iter(rd.items()))
        print(f"Note: multiple objects in RData; using `{k}`.", file=sys.stderr)

    df = df.rename(columns=lambda c: _norm_col(str(c)))

    if "id" not in df.columns:
        raise ValueError("Expected `id` column after normalization.")

    cov_src = cov_source_columns(list(df.columns))
    cov_rename = {c: f"cov_{c}" for c in cov_src}
    df = df.rename(columns=cov_rename)

    all_nc = sorted(df.columns)
    b2i_items = _b2i_item_columns(all_nc)
    ecq_items = _ecq_item_columns(all_nc)

    if not b2i_items:
        raise ValueError("No B2I item columns matched (unexpected RData schema).")

    cov_present = sorted(c for c in df.columns if c.startswith("cov_"))
    slim = df[["id"] + cov_present + b2i_items + ecq_items].copy()

    b2i_name = "haehner_2026_personality_subsaharan_b2i.csv"
    ecq_name = "haehner_2026_personality_subsaharan_ecq.csv"

    n_b = _melt_irw(slim, b2i_items, out / b2i_name)
    print(f"{b2i_name}: rows={n_b}, cols items={len(b2i_items)}")

    if ecq_items:
        n_e = _melt_irw(slim, ecq_items, out / ecq_name)
        print(f"{ecq_name}: rows={n_e}, cols items={len(ecq_items)}")
    else:
        print(f"{ecq_name}: skipped (no ECQ columns)")


def main() -> None:
    ap = argparse.ArgumentParser(description="ALLS scored RData → IRW CSV")
    ap.add_argument(
        "--input",
        "-i",
        type=Path,
        default=None,
        help=f"Path to data_scored.RData (default: {DEFAULT_RDATA} under script dir)",
    )
    ap.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help=f"Directory for CSV output (default: {OUTPUT_DIR} under script dir)",
    )
    args = ap.parse_args()
    convert_saharan_to_irw(rdata_path=args.input, out_dir=args.output_dir)


if __name__ == "__main__":
    main()
