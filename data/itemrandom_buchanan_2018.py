"""
IRW processing: Buchanan et al. (2018), Behaviormetrika 45(2), 295-316.
"Does the delivery matter? Examining randomization at the item level."

Converts the raw wide Qualtrics exports into IRW long format, one table per
scale. Drop this file in the folder holding the CSVs and run it:

    python process_irw.py                     # reads/writes alongside this file
    python process_irw.py --indir . --outdir out

Nothing about the environment is assumed: input files are discovered by name,
item columns by pattern, the response scale by inspection, and the
reverse-coding key is derived by matching computed item means against the
published tables rather than being asserted up front.
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# --- Source file schema (describes the raw Qualtrics exports) ----------------
ID_COL = "V1"          # Qualtrics response ID; empty for paper-delivery rows
COND_COL = "Source"    # random | not random | paper
YEAR_COL = "YEAR"      # year of data collection

RANDOMIZED = "random"      # -> treat = 1
FIXED = "not random"       # -> treat = 0
PAPER = "paper"            # -> cov_mode = paper, else computer

# --- Study metadata (used only for output table names) ----------------------
STUDY, AUTHOR, PUB_YEAR = "itemrandom", "buchanan", 2018

# --- Published item means, for deriving and verifying the coding key --------
# PIL: Table 3 (1-7 scale). LPQ: Table 5 (proportions). R = randomized order,
# NR = fixed order. Reference values from the article, not from these files.
PUBLISHED = {
    "PIL": {
        "R":  [4.829, 4.929, 5.815, 5.673, 4.666, 5.425, 6.172, 5.014, 5.355,
               5.202, 5.222, 4.496, 5.745, 5.431, 4.376, 5.099, 5.422, 5.387,
               4.879, 5.343],
        "NR": [4.806, 4.600, 5.732, 5.655, 4.407, 5.338, 6.081, 5.011, 5.327,
               5.156, 5.165, 4.527, 5.738, 5.239, 4.149, 5.266, 5.399, 5.302,
               4.907, 5.210],
    },
    "LPQ": {
        "R":  [.567, .754, .864, .908, .419, .638, .775, .482, .810, .635,
               .727, .787, .965, .762, .323, .863, .847, .830, .463, .721],
        "NR": [.613, .760, .844, .868, .507, .582, .810, .467, .781, .646,
               .761, .752, .911, .769, .395, .872, .814, .828, .497, .712],
    },
}

QC_TOLERANCE = 0.15  # max acceptable deviation from a published item mean


def find_item_columns(df, prefix):
    """Item columns are the scale prefix followed by a number."""
    pat = re.compile(rf"^{prefix}\d+", re.IGNORECASE)
    cols = [c for c in df.columns if pat.match(c)]
    numbers = [int(re.search(r"\d+", c).group()) for c in cols]
    order = np.argsort(numbers)
    return [cols[i] for i in order], [numbers[i] for i in order]


def infer_scale_max(df, cols):
    """Largest v such that every integer 1..v is observed.

    Stops at the first gap, so isolated bad codes (e.g. a stray 12 among 1/2
    responses) fall outside the valid set instead of stretching the scale.
    """
    seen = {int(v) for v in pd.unique(df[cols].values.ravel())
            if pd.notna(v) and float(v).is_integer()}
    v = 1
    while v + 1 in seen:
        v += 1
    return v


def derive_reverse_key(df, cols, numbers, scale_max, published):
    """Decide per item whether raw coding or its reversal matches the article.

    Each delivery condition votes independently; a split vote means the
    reference values cannot settle the item, and is raised rather than
    silently resolved.
    """
    conds = {"R": df[COND_COL] == RANDOMIZED, "NR": df[COND_COL] == FIXED}
    reverse, margins = set(), []
    for pos, (col, num) in enumerate(zip(cols, numbers)):
        votes, item_margins = [], []
        for key, mask in conds.items():
            raw = df.loc[mask, col].mean()
            rev = (scale_max + 1) - raw
            if scale_max == 2:  # published as proportions
                raw, rev = raw - 1, rev - 1
            exp = published[key][pos]
            d_raw, d_rev = abs(raw - exp), abs(rev - exp)
            votes.append(d_rev < d_raw)
            item_margins.append(abs(d_raw - d_rev))
        if len(set(votes)) > 1:
            raise ValueError(
                f"conditions disagree on whether {col} is reverse-scored; "
                "check the published means against this file"
            )
        if votes[0]:
            reverse.add(num)
        margins.append(min(item_margins))
    weak = [n for n, m in zip(numbers, margins) if m < 0.05]
    if weak:
        print(f"  ! weak reversal evidence for items {weak}", file=sys.stderr)
    return reverse


def to_long(df, cols, numbers, scale_max, reverse, prefix):
    d = df.copy()
    valid = list(range(1, scale_max + 1))
    dropped = int((~d[cols].isin(valid) & d[cols].notna()).values.sum())
    d[cols] = d[cols].where(d[cols].isin(valid))

    long = d.melt(id_vars=["id", COND_COL, YEAR_COL], value_vars=cols,
                  var_name="_col", value_name="_raw").dropna(subset=["_raw"])

    num = long["_col"].map(dict(zip(cols, numbers)))
    long["item"] = prefix.upper() + "_" + num.astype(str).str.zfill(2)

    # Reverse flagged items so higher always means greater meaning/purpose.
    resp = np.where(num.isin(reverse), (scale_max + 1) - long["_raw"], long["_raw"])
    if scale_max == 2:
        resp = resp - 1  # binary items to 0/1
    long["resp"] = resp.astype(int)

    long["treat"] = (long[COND_COL] == RANDOMIZED).astype(int)
    long["cov_mode"] = np.where(long[COND_COL] == PAPER, "paper", "computer")
    long["cov_year"] = long[YEAR_COL].astype(int)

    out = long[["id", "item", "resp", "treat", "cov_mode", "cov_year"]]
    return out.sort_values(["id", "item"]).reset_index(drop=True), dropped


def qc(long, published):
    """Recompute item means from the processed table and compare to the article."""
    devs = []
    for key, treat in [("R", 1), ("NR", 0)]:
        sub = long[(long["treat"] == treat) & (long["cov_mode"] == "computer")]
        means = sub.groupby("item")["resp"].mean()
        for pos, item in enumerate(sorted(means.index)):
            devs.append(abs(means[item] - published[key][pos]))
    worst, avg = max(devs), sum(devs) / len(devs)
    passed = worst <= QC_TOLERANCE
    print(f"  QC vs published means: {'PASS' if passed else 'FAIL'} "
          f"(max dev {worst:.3f}, mean dev {avg:.3f}, n={len(devs)})")
    return passed


def assign_ids(frames):
    """Paper-delivery rows carry no Qualtrics ID. The exports are row-aligned,
    so a positional synthetic ID keeps a respondent linked across tables."""
    ref = next(iter(frames.values()))
    missing = ref[ID_COL].isna()
    synth = pd.Series(
        [f"{PAPER}_{i:03d}" for i in range(1, int(missing.sum()) + 1)],
        index=ref.index[missing],
    )
    for df in frames.values():
        df["id"] = df[ID_COL]
        df.loc[missing, "id"] = synth
        if not df["id"].is_unique:
            raise ValueError("duplicate respondent IDs after assignment")
    return frames


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Process raw scales into IRW format.")
    ap.add_argument("--indir", type=Path, default=here,
                    help="folder holding the raw CSVs (default: this script's folder)")
    ap.add_argument("--outdir", type=Path, default=here,
                    help="where to write IRW tables (default: this script's folder)")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    frames = {}
    for prefix in PUBLISHED:
        hits = [p for p in args.indir.glob("*.csv") if p.stem.upper() == prefix]
        if not hits:
            sys.exit(f"could not find {prefix}.csv in {args.indir}")
        frames[prefix] = pd.read_csv(hits[0])

    # The exports must line up row-for-row, or the synthetic IDs are meaningless.
    ref = next(iter(frames.values()))
    for prefix, df in frames.items():
        aligned = (
            len(df) == len(ref)
            and df[ID_COL].fillna("_").eq(ref[ID_COL].fillna("_")).all()
            and df[COND_COL].eq(ref[COND_COL]).all()
        )
        if not aligned:
            sys.exit(f"{prefix} is not row-aligned with the other export")

    frames = assign_ids(frames)

    ok = True
    for prefix, df in frames.items():
        print(f"\n{prefix}")
        cols, numbers = find_item_columns(df, prefix)
        scale_max = infer_scale_max(df, cols)
        reverse = derive_reverse_key(df, cols, numbers, scale_max, PUBLISHED[prefix])
        print(f"  {len(cols)} items, responses 1-{scale_max}")
        print(f"  reverse-scored: {sorted(reverse)}")

        long, dropped = to_long(df, cols, numbers, scale_max, reverse, prefix)
        if dropped:
            print(f"  dropped {dropped} out-of-range response(s)")
        ok &= qc(long, PUBLISHED[prefix])

        name = f"{STUDY}_{AUTHOR}_{PUB_YEAR}_{prefix}.csv"
        long.to_csv(args.outdir / name, index=False)
        print(f"  wrote {name}: {len(long):,} responses, "
              f"{long['id'].nunique():,} respondents")

    if not ok:
        sys.exit("\nQC failed - do not submit these tables")


if __name__ == "__main__":
    main()