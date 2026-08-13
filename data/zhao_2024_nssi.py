#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11466236
# DOI: 10.7717/peerj.18134
#
# Zhao H, Zhou A (2024), "Longitudinal relations between non-suicidal
# self-injury and both depression and anxiety among senior high school
# adolescents: a cross-lagged panel network analysis." PeerJ. CC BY 4.0.
#
# Supplementary file peerj-12-18134-s001.sav is a two-wave (T1/T2) panel of
# senior high school students with three raw-item instruments administered
# at both waves:
#   - Depression: T1D1..T1D6 / T2D1..T2D6 (0-4 frequency scale)
#   - Anxiety:    T1A1..T1A6 / T2A1..T2A6 (0-4 frequency scale)
#   - NSSI:       T1NSSI1..T1NSSI12 / T2NSSI1..T2NSSI12 (0-4 frequency scale)
# Aggregate columns T1D/T2D/T1A/T2A/T1N/T2N are pre-computed subscale totals
# and excluded per datastandard.md. Each instrument becomes its own IRW file
# with a `wave` column (1=T1, 2=T2) rather than separate T1/T2 item names, per
# datastandard.md's longitudinal-data convention.

import io
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11466236/supplementaryFiles"
MEMBER = "peerj-12-18134-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "zhao_2024_depression": ("D", 6),
    "zhao_2024_anxiety": ("A", 6),
    "zhao_2024_nssi": ("NSSI", 12),
}


def load_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        data = f.read()
    tmp = Path("/tmp") / MEMBER
    tmp.write_bytes(data)
    df, _meta = pyreadstat.read_sav(str(tmp))
    tmp.unlink(missing_ok=True)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def make_scale(df: pd.DataFrame, prefix: str, n_items: int, out_name: str):
    frames = []
    for wave, tprefix in [(1, "T1"), (2, "T2")]:
        items = [f"{tprefix}{prefix}{i}" for i in range(1, n_items + 1)]
        items = [c for c in items if c in df.columns]
        long = df[["id"] + items].melt(id_vars=["id"], value_vars=items,
                                        var_name="item", value_name="resp")
        # strip wave prefix so item names match across waves
        long["item"] = long["item"].str.replace(f"^{tprefix}", "", regex=True)
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]

    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_raw()
    for out_name, (prefix, n_items) in SCALES.items():
        make_scale(df, prefix, n_items, out_name)


if __name__ == "__main__":
    convert()
