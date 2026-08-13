#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC12229148
# DOI: 10.7717/peerj.19587
#
# Hen-Herbst & Fogel (2025), "Exploring changes in family routines and
# family quality of life among Israeli families during the COVID-19
# pandemic." PeerJ. CC BY 4.0. N=253 parents.
# Supplementary file peerj-13-19587-s001.sav bundles two documented raw-item
# instruments, each administered twice (once retrospectively for "before
# COVID-19", once for "during COVID-19" -- confirmed in Methods: "coded the
# FRI and FQOL Scale twice"), split per datastandard.md's "one file per
# scale" and "wave" rules:
#   - Family Routines Inventory (FRI) frequency subscale: 28 items, 1
#     (rarely) - 4 (always/every day)
#   - FRI importance subscale: 28 items, 1 (not important) - 3 (very
#     important)
#   - FQOL Scale (modified, 21 items after removing 4 disability-specific
#     items): 1 (very unsatisfied) - 5 (very satisfied)
# wave=1 is "before COVID-19" (_B columns), wave=2 is "during COVID-19"
# (_K columns).
# The .sav file also contains an F-COPES-style "FCOPE_*" item battery that
# is never described, scaled, or cited in this paper's Methods -- its
# response meaning is unconfirmed here, so it is excluded rather than
# guessed at. All *_total/_M/_forcing/_new aggregate and demographic
# columns are excluded as composites/covariates. No PII (place-of-birth
# columns are coded region categories, not addresses).

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12229148/supplementaryFiles"
MEMBER = "peerj-13-19587-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    data = zf.read(MEMBER)
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(data)
        tmp.flush()
        df, meta = pyreadstat.read_sav(tmp.name)
    df = df.rename(columns={"No": "id"})
    assert df["id"].nunique() == len(df)
    return df


def build_scale(df: pd.DataFrame, prefix: str, n_items: int, out_name: str):
    frames = []
    for wave, suffix in [(1, "B"), (2, "K")]:
        cols = [f"{prefix}{suffix}_Q{i}" for i in range(1, n_items + 1)]
        sub = df[["id"] + cols].copy()
        sub.columns = ["id"] + [f"{prefix}_Q{i}" for i in range(1, n_items + 1)]
        long = sub.melt(id_vars="id", var_name="item", value_name="resp")
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def build_fqol(df: pd.DataFrame, out_name: str):
    frames = []
    for wave, suffix in [(1, "B"), (2, "K")]:
        cols = [f"FQL_{suffix}_Q{i}" for i in range(1, 22)]
        sub = df[["id"] + cols].copy()
        sub.columns = ["id"] + [f"FQL_Q{i}" for i in range(1, 22)]
        long = sub.melt(id_vars="id", var_name="item", value_name="resp")
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_raw()
    build_scale(df, "FRI_routine", 28, "hen-herbst_2025_family_routine_freq.csv")
    build_scale(df, "FRI_important", 28, "hen-herbst_2025_family_routine_import.csv")
    build_fqol(df, "hen-herbst_2025_family_qol.csv")


if __name__ == "__main__":
    convert()
