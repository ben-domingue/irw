from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268124
# DOI: 10.1371/journal.pone.0268124
# Kitayama & Sakuramoto (2022), "Development and initial validation of the
# Japanese healthy work environment assessment tool for critical care
# settings" (HWE-AT-J). CC BY 4.0. 18 items (Q1-Q18), 1-5 Likert.
# Two files: S2 Data (s004, N=202, single administration) is the main
# validation sample; S1 Data (s003, N=50) is a test-retest sample with
# separate "1st"/"2nd" administration blocks, shipped with a wave column.
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
S2_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0268124.s004")
S1_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0268124.s003")


def convert_main():
    r = requests.get(S2_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={df.columns[0]: "id"})
    item_cols = [c for c in df.columns if c.startswith("Q")]
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    long.to_csv(OUT_DIR / "kitayama_2022_hweat.csv", index=False)
    print(f"kitayama_2022_hweat: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert_retest():
    r = requests.get(S1_URL, headers=UA, timeout=120)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), header=None)
    # Row 0: "1st"/"2nd" wave labels; row 1: item names (Q1..Q18 repeated
    # twice); row 2+: data, id in column 0.
    item_names = raw.iloc[1]
    wave_labels = raw.iloc[0].ffill()
    data = raw.iloc[2:].reset_index(drop=True)
    data.columns = raw.iloc[1].values

    frames = []
    for wave_idx, wave_label in enumerate(["1st", "2nd"]):
        cols = [i for i in range(len(item_names)) if str(wave_labels.iloc[i]).strip() == wave_label]
        block = raw.iloc[2:, cols].copy()
        block.columns = [str(item_names.iloc[i]).strip() for i in cols]
        block["id"] = raw.iloc[2:, 0].values
        block["wave"] = wave_idx + 1
        frames.append(block)

    combined = pd.concat(frames, ignore_index=True)
    item_cols = [c for c in combined.columns if c.startswith("Q")]
    long = combined.melt(id_vars=["id", "wave"], value_vars=item_cols,
                          var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long["id"] = pd.to_numeric(long["id"], errors="coerce")
    long = long.dropna(subset=["resp", "id"]).reset_index(drop=True)
    long["id"] = long["id"].astype(int)
    long = long[["id", "item", "resp", "wave"]]
    long.to_csv(OUT_DIR / "kitayama_2022_hweat_retest.csv", index=False)
    print(f"kitayama_2022_hweat_retest: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f} "
          f"waves={sorted(long['wave'].unique())}")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_main()
    convert_retest()


if __name__ == "__main__":
    convert()
