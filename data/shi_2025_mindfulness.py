from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331084
# DOI: 10.1371/journal.pone.0331084
# RCT (mindfulness intervention vs. control, N=98/98) of Chinese
# university students, 3 waves (pre/post/third=follow-up). "组别" (Group)
# kept as cov_group rather than treat -- the paper confirms a 98/98
# intervention/control split but never states which numeric code (1 or 2)
# in the raw file corresponds to which arm, same ambiguity as
# wakui_2023_who5 in batch 9. Five
# instruments each administered at all 3 waves: MAAS (Mindful Attention
# Awareness Scale, 15 items), BRUMS (Brunel Mood Scale, 23 items), DASS
# (Depression Anxiety Stress Scales-21, 21 items), RRS (Ruminative
# Response Scale, 22 items), Resilience (27 items). Column names are
# Chinese-labeled instrument prefixes with numeric suffixes -- no item
# text is embedded in the raw file's column names themselves.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0331084.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

WAVES = ["pre", "post", "third"]
# (source column prefix, n_items, valid (min, max) range). Each scale's
# range is internally consistent across all its items except MAAS item 9
# (one 42, one 8 on item 8) and RRS items 9/16 (one 5 each) -- isolated
# single data-entry errors against hundreds of legitimate 1-6 / 1-4
# responses on those same items, filtered out below rather than kept.
SCALES = {
    "shi_2025_maas": ("MAAS", 15, (1, 6)),
    "shi_2025_brums": ("BRUMS", 23, (0, 5)),
    "shi_2025_dass21": ("DASS", 21, (0, 4)),
    "shi_2025_rrs": ("RRS", 22, (1, 4)),
    "shi_2025_resilience": ("Resilience", 27, (1, 5)),
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch()
    df = df.rename(columns={"编号": "id", "组别": "cov_group"})
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, (prefix, n_items, (lo, hi)) in SCALES.items():
        frames = []
        for wave, wave_prefix in enumerate(WAVES):
            cols = [f"{wave_prefix}{prefix}{i}" for i in range(1, n_items + 1)]
            cols = [c for c in cols if c in df.columns]
            long = df.melt(id_vars=["id", "cov_group"], value_vars=cols,
                           var_name="src_col", value_name="resp")
            long["item"] = "item" + long["src_col"].str.replace(f"{wave_prefix}{prefix}", "", regex=False)
            long["wave"] = wave
            frames.append(long.drop(columns=["src_col"]))
        long = pd.concat(frames, ignore_index=True)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "wave", "cov_group"]]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
