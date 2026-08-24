"""
Process the Personality Change Intervention Study (Krämer et al., 2025, JPSP)
raw .rda exports into IRW-format (id, item, resp, wave, cov_*) long tables.

INPUT   df_sbsa.rda, df_sbsa2.rda, df_sbsa3.rda   (Studies 1, 2, 3)
OUTPUT  personalitychange_kramer_2025_[construct].csv

USAGE
    # Default: looks for the .rda files next to this script, writes to ./output
    python process_irw.py

    # Or point it anywhere:
    python process_irw.py --input-dir path/to/rda_files --output-dir path/to/out

REQUIREMENTS
    pip install pyreadr pandas numpy
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import pyreadr
except ImportError:
    sys.exit(
        "Missing dependency 'pyreadr' (needed to read .rda files).\n"
        "Install it with:  pip install pyreadr pandas numpy"
    )


# ---------------------------------------------------------------------------
# Configuration (no hardcoded absolute paths — see parse_args below)
# ---------------------------------------------------------------------------

# Resolve defaults relative to THIS FILE, so the script behaves the same
# whether it's launched from VS Code, a terminal, or another directory.
SCRIPT_DIR = Path(__file__).resolve().parent

DEMO_COLS = ["age", "gender", "ethnicity", "country", "student", "employed"]

# Source files, in study order. Only the filename is fixed here — the
# directory comes from --input-dir.
STUDY_FILES = {
    1: "df_sbsa.rda",
    2: "df_sbsa2.rda",
    3: "df_sbsa3.rda",
}

OUT_PREFIX = "personalitychange_kramer_2025"


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Convert Krämer et al. (2025) .rda exports to IRW long format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--input-dir",
        type=str,
        default=str(SCRIPT_DIR),
        help="Directory containing df_sbsa.rda, df_sbsa2.rda, df_sbsa3.rda",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default=str(SCRIPT_DIR / "output"),
        help="Directory to write the processed CSVs into (created if missing)",
    )
    args = p.parse_args(argv)
    args.input_dir = Path(args.input_dir).expanduser().resolve()
    args.output_dir = Path(args.output_dir).expanduser().resolve()
    return args


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load(input_dir: Path, fname: str) -> pd.DataFrame:
    """Read a single-object .rda file and return its DataFrame.

    Takes whatever object the file contains rather than assuming the R object
    name matches the filename, so a re-exported/renamed .rda still works.
    """
    path = input_dir / fname
    if not path.exists():
        sys.exit(
            f"Could not find {fname} in {input_dir}\n"
            f"Pass the right folder with:  --input-dir /path/to/rda_files"
        )
    result = pyreadr.read_r(str(path))
    if not result:
        sys.exit(f"{fname} contained no R objects.")
    key = list(result.keys())[0]
    if len(result) > 1:
        print(f"  [note] {fname} holds {len(result)} objects; using '{key}'")
    return result[key]


def clean_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Recode the -9 'missing' sentinel to NaN across all numeric columns."""
    df = df.copy()
    for c in df.columns:
        if df[c].dtype != object:
            df[c] = df[c].replace(-9, np.nan)
    return df


def save(df: pd.DataFrame | None, name: str, output_dir: Path) -> None:
    if df is None or len(df) == 0:
        print(f"  [skip] {name}: no data")
        return
    path = output_dir / f"{name}.csv"
    df.to_csv(path, index=False)
    print(
        f"  [saved] {name}: {len(df)} rows, "
        f"{df['id'].nunique()} ids, {df['item'].nunique()} items"
    )
    # Guard: confirm resp is fully numeric. Catches free-text columns being
    # pulled into resp (the sa13_01 bug from an earlier version of this script).
    bad = pd.to_numeric(df["resp"], errors="coerce").isna().sum()
    if bad:
        print(
            f"  [!!] WARNING: {bad} non-numeric resp values in {name} — "
            f"check for an accidentally included free-text column"
        )


# ---------------------------------------------------------------------------
# Reshaping
# ---------------------------------------------------------------------------

def build_long(df, id_col, item_cols, wave_series, group_series,
               study_prefix, extra_cov=None):
    """Melt wide item columns into id/item/resp long format, attaching wave,
    group, and demographic covariates.

    Columns not present in df are silently skipped, which handles studies
    where a given item was never administered.
    """
    item_cols = [c for c in item_cols if c in df.columns]
    if not item_cols:
        return None

    sub = df[[id_col] + item_cols].copy()
    sub["wave"] = wave_series
    sub["cov_group"] = group_series
    for d in DEMO_COLS:
        sub[f"cov_{d}"] = df[d] if d in df.columns else np.nan
    if extra_cov:
        for name, val in extra_cov.items():
            sub[name] = val

    id_vars = [id_col, "wave", "cov_group"] + [f"cov_{d}" for d in DEMO_COLS]
    if extra_cov:
        id_vars += list(extra_cov.keys())

    long = sub.melt(
        id_vars=id_vars, value_vars=item_cols, var_name="item", value_name="resp"
    )
    long = long.dropna(subset=["resp"])
    long = long.rename(columns={id_col: "id"})
    long["id"] = f"{study_prefix}_" + long["id"].astype(str)
    return long.sort_values(["id", "wave", "item"]).reset_index(drop=True)


def bfi_items(prefix):
    return [f"{prefix}_{i:02d}" for i in range(1, 61)]


INSTRUMENTS_COMMON = {
    "swls": [f"sw06_{i:02d}" for i in range(1, 6)],
    "rses": [f"rs01_{i:02d}" for i in range(1, 11)],
    "sccs": [f"sc01_{i:02d}" for i in range(1, 13)],
    "mls": [f"ml01_{i:02d}" for i in range(1, 11)],
}
BFI_CURRENT_ITEMS = bfi_items("bf05")
BFI_IDEAL_ITEMS = bfi_items("bf06")


def build_bfi_combined(df, wave, group, study_prefix):
    """BFI-2 current + ideal, combined with a cov_reference column."""
    cur = build_long(df, "pid", BFI_CURRENT_ITEMS, wave, group, study_prefix,
                     extra_cov={"cov_reference": "current"})
    ideal = build_long(df, "pid", BFI_IDEAL_ITEMS, wave, group, study_prefix,
                       extra_cov={"cov_reference": "ideal"})
    parts = [p for p in (cur, ideal) if p is not None]
    if not parts:
        return None
    combined = pd.concat(parts, ignore_index=True)
    cols = (
        ["id", "wave", "cov_group", "cov_reference"]
        + [f"cov_{d}" for d in DEMO_COLS]
        + ["item", "resp"]
    )
    return combined[cols].sort_values(
        ["id", "wave", "cov_reference", "item"]
    ).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Self-improvement / self-acceptance item lists (Studies 1 & 2 only)
#
# STUDY-SPECIFIC ITEM AVAILABILITY (verified directly against each study's
# columns, not assumed from the codebook):
#   - "Personal project dimensions" (post: SB13_01/02, SA12_01/02) was
#     administered in Study 1 ONLY — these columns don't exist in Study 2.
#   - "Perceived effectiveness of intervention" (SB16_01/SA16_01) was
#     administered in Study 2 ONLY (asked at T3).
#   - Free-text columns SB08/SB09/SA08/SA09 (adjective goals) and SB14_01/
#     SA13_01 (open-response change descriptions) have no persistent item
#     identifier and are excluded everywhere.
#     NOTE: an earlier version mistakenly used SA13_01 (free text) instead of
#     SA12_01/02 (numeric) — fixed below; save() now guards against this.
# ---------------------------------------------------------------------------

def si_pre_cols():
    return (["sb05", "sb06_01"]
            + [f"sb07_{i:02d}" for i in range(1, 16)]
            + ["sb01_01", "sb01_02"])


def si_post_cols(study):
    cols = [f"sb12_{i:02d}" for i in range(1, 16)] + ["sb04_01", "sb04_02", "sb04_03"]
    if study == 1:
        cols += ["sb13_01", "sb13_02"]   # personal project dims (Study 1 only)
    if study == 2:
        cols += ["sb16_01"]              # perceived effectiveness (Study 2 only)
    return cols


def sa_pre_cols():
    return (["sa05", "sa06_01"]
            + [f"sa07_{i:02d}" for i in range(1, 16)]
            + ["sa01_01", "sa01_02"])


def sa_post_cols(study):
    cols = [f"sa14_{i:02d}" for i in range(1, 16)] + ["sa04_01", "sa04_02", "sa04_03"]
    if study == 1:
        cols += ["sa12_01", "sa12_02"]   # personal project dims (Study 1 only)
    if study == 2:
        cols += ["sa16_01"]              # perceived effectiveness (Study 2 only)
    return cols


def backfill_baseline_group(df, group, baseline_label, post_mask):
    """Baseline rows share one survey label for everyone, so the randomized
    arm is only visible at later waves. Back-fill T1 from each pid's first
    post-baseline assignment."""
    pid2group = (
        df.loc[post_mask, ["pid", "questnnr"]]
        .drop_duplicates("pid")
        .set_index("pid")["questnnr"]
    )
    mask = df["questnnr"] == baseline_label
    return mask, pid2group


# ---------------------------------------------------------------------------
# Cross-study combination
# ---------------------------------------------------------------------------

def combine_across_studies(parts_by_study, name, output_dir):
    """Combine the same instrument across studies, tagged with cov_study.

    Safe because item wording/response scales are identical across studies,
    `id` is already study-prefixed (no participant collisions), and `wave`
    still tracks within-study time order.
    """
    frames = []
    for study_label, df in parts_by_study.items():
        if df is None:
            continue
        df = df.copy()
        df.insert(1, "cov_study", study_label)  # right after 'id'
        frames.append(df)
    if not frames:
        save(None, name, output_dir)
        return
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["cov_study", "id", "wave"]).reset_index(drop=True)
    save(combined, name, output_dir)


def combine_arm(parts, name, output_dir):
    """Combine one intervention arm's pre + post tables across both studies
    into a single table, tagged with `cov_study` and `cov_phase`.

    `parts` maps (study_label, phase) -> DataFrame.

    WHY cov_phase IS NEEDED (and isn't redundant with `wave`):
    In Study 2 the waitlist control group received the intervention between
    T2 and T3, so they answered their PRE goal items at wave 2 — the same
    wave at which the SI/SA groups answered their POST items. `wave` alone is
    therefore ambiguous at wave 2, and `cov_phase` disambiguates.

    Safe to combine because pre and post use disjoint item codes (e.g. goals
    sb07_*/sa07_* vs. perceived-change sb12_*/sa14_*), so no item identifier
    means two different things after the merge.
    """
    frames = []
    for (study_label, phase), df in parts.items():
        if df is None:
            continue
        df = df.copy()
        df.insert(1, "cov_study", study_label)
        df.insert(2, "cov_phase", phase)
        frames.append(df)
    if not frames:
        save(None, name, output_dir)
        return
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(
        ["cov_study", "id", "wave", "cov_phase", "item"]
    ).reset_index(drop=True)
    save(combined, name, output_dir)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    args = parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Input dir : {args.input_dir}")
    print(f"Output dir: {args.output_dir}\n")

    # ---------------- Study 1 ----------------
    print("STUDY 1")
    df1 = clean_missing(load(args.input_dir, STUDY_FILES[1]))

    wave1_map = {"Test_t0": 1, "Self-Improvement": 2, "Self-Acceptance": 2}
    group1_map = {"Test_t0": np.nan, "Self-Improvement": "SI", "Self-Acceptance": "SA"}
    wave1 = df1["questnnr"].map(wave1_map)
    group1 = df1["questnnr"].map(group1_map)

    mask1, pid2group1 = backfill_baseline_group(
        df1, group1, "Test_t0", df1["questnnr"] != "Test_t0"
    )
    group1.loc[mask1] = df1.loc[mask1, "pid"].map(pid2group1).map(group1_map)

    bfi1 = build_bfi_combined(df1, wave1, group1, "s1")
    common1 = {
        name: build_long(df1, "pid", cols, wave1, group1, "s1")
        for name, cols in INSTRUMENTS_COMMON.items()
    }

    arm1 = {
        ("study1", "pre"): build_long(df1, "pid", si_pre_cols(), wave1, group1, "s1"),
        ("study1", "post"): build_long(df1, "pid", si_post_cols(1), wave1, group1, "s1"),
    }
    arm1_sa = {
        ("study1", "pre"): build_long(df1, "pid", sa_pre_cols(), wave1, group1, "s1"),
        ("study1", "post"): build_long(df1, "pid", sa_post_cols(1), wave1, group1, "s1"),
    }

    # ---------------- Study 2 ----------------
    print("\nSTUDY 2")
    df2 = clean_missing(load(args.input_dir, STUDY_FILES[2]))

    wave2_map = {
        "S2_T1": 1, "S2_T2_SB": 2, "S2_T2_SA": 2, "S2_T2_CG": 2,
        "S2_T3_SB": 3, "S2_T3_SA": 3, "S2_T3_cgSA": 3, "S2_T3_cgSB": 3,
    }
    # Verified against item-level data (sb12_* vs sa14_* non-missingness):
    # SB labels = self-improvement, SA labels = self-acceptance.
    group2_map = {
        "S2_T1": np.nan, "S2_T2_SB": "SI", "S2_T2_SA": "SA", "S2_T2_CG": "CG",
        "S2_T3_SB": "SI", "S2_T3_SA": "SA",
        "S2_T3_cgSA": "CG_to_SA", "S2_T3_cgSB": "CG_to_SI",
    }
    wave2 = df2["questnnr"].map(wave2_map)
    group2 = df2["questnnr"].map(group2_map)

    mask2, pid2group2 = backfill_baseline_group(
        df2, group2, "S2_T1", df2["questnnr"].str.contains("T2")
    )
    group2.loc[mask2] = df2.loc[mask2, "pid"].map(pid2group2).map(group2_map)

    bfi2 = build_bfi_combined(df2, wave2, group2, "s2")
    common2 = {
        name: build_long(df2, "pid", cols, wave2, group2, "s2")
        for name, cols in INSTRUMENTS_COMMON.items()
    }

    arm2 = {
        ("study2", "pre"): build_long(df2, "pid", si_pre_cols(), wave2, group2, "s2"),
        ("study2", "post"): build_long(df2, "pid", si_post_cols(2), wave2, group2, "s2"),
    }
    arm2_sa = {
        ("study2", "pre"): build_long(df2, "pid", sa_pre_cols(), wave2, group2, "s2"),
        ("study2", "post"): build_long(df2, "pid", sa_post_cols(2), wave2, group2, "s2"),
    }

    # ---------------- Study 3 (no intervention -> no si_/sa_ tables) --------
    print("\nSTUDY 3")
    df3 = clean_missing(load(args.input_dir, STUDY_FILES[3]))

    wave3_map = {
        "S3_T1_Gr1": 1, "S3_T1_Gr2": 1, "S3_T1_Gr3": 1,
        "S3_T2_Gr1": 2, "S3_T2_Gr2": 2, "S3_T2_Gr3": 2,
    }
    wave3 = df3["questnnr"].map(wave3_map)
    group3 = df3["group"]  # already "Group 1/2/3"

    bfi3 = build_bfi_combined(df3, wave3, group3, "s3")
    common3 = {
        name: build_long(df3, "pid", cols, wave3, group3, "s3")
        for name, cols in INSTRUMENTS_COMMON.items()
    }

    # ---------------- Combine shared instruments across studies -------------
    print("\nCOMBINING SHARED INSTRUMENTS ACROSS STUDIES (cov_study)")
    combine_across_studies(
        {"study1": bfi1, "study2": bfi2, "study3": bfi3},
        f"{OUT_PREFIX}_bfi", args.output_dir,
    )
    for name in INSTRUMENTS_COMMON:
        combine_across_studies(
            {"study1": common1[name], "study2": common2[name], "study3": common3[name]},
            f"{OUT_PREFIX}_{name}", args.output_dir,
        )

    # ---------------- Combine each intervention arm (pre + post, both studies)
    print("\nCOMBINING INTERVENTION ARMS (cov_study + cov_phase)")
    combine_arm({**arm1, **arm2}, f"{OUT_PREFIX}_si", args.output_dir)
    combine_arm({**arm1_sa, **arm2_sa}, f"{OUT_PREFIX}_sa", args.output_dir)

    print(f"\nDone. Wrote CSVs to {args.output_dir}")


if __name__ == "__main__":
    main()