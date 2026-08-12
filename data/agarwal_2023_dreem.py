#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10621590
# DOI: 10.7717/peerj.16184
#
# Agarwal et al. (2023), "Navigating post COVID-19 education: an
# investigative study on students' attitude and perception of their new
# normal learning environment." PeerJ. CC BY 4.0. N=300. A modified
# Dundee Ready Education Environment Measure (DREEM) -- the paper's
# Methods confirms 50 items across 5 domains, 5-point Likert (strongly
# agree=4, agree=3, uncertain=2, disagree=1, strongly disagree=0),
# administered 3 times (precovid/covid/postcovid prefixes) -- a 3-wave
# design, not the 2-wave/2-condition split the deferred-candidate note
# guessed at (the file actually has 50 items per wave, not 24; the note's
# "24-item" description does not match the raw file or the paper's own
# item count). Some items are reverse-scored per the paper (items 4, 9,
# 13, 17, 25, 35, 39, 48, 50) but datastandard.md does not require
# recoding reverse-scored items, so raw per-item direction is kept as-is.
# SPL/SPT/SASP/SPA/SSSP are pre-computed domain/subscale total columns
# (matching Table 2's five DREEM domain scores), excluded as aggregates.
# No covariates/demographics present in the file, no PII.

import io
import re
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10621590/supplementaryFiles"
MEMBER = "peerj-11-16184-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {
    "strongly agree": 4,
    "agree": 3,
    "uncertain": 2,
    "disagree": 1,
    "strongly disagree": 0,
}

WAVE_MAP = {"precovid": 1, "covid": 2, "postcovid": 3}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_spss(tmp.name)

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    assert df["id"].nunique() == len(df)

    # exact-suffix match via regex (q<n> + wave label, with one source typo:
    # "q37precobid" for the precovid wave), so "covid" doesn't also match
    # "precovid"/"postcovid" columns.
    WAVE_PATTERNS = {
        "precovid": re.compile(r"^q(\d+)(precovid|precobid)$", re.IGNORECASE),
        "covid": re.compile(r"^q(\d+)covid$", re.IGNORECASE),
        "postcovid": re.compile(r"^q(\d+)postcovid$", re.IGNORECASE),
    }

    long_frames = []
    for suffix, wave in WAVE_MAP.items():
        pattern = WAVE_PATTERNS[suffix]
        item_cols = [c for c in df.columns if pattern.match(c)]
        assert len(item_cols) == 50, f"{suffix}: expected 50 items, got {len(item_cols)}"
        sub = df.melt(id_vars=["id"], value_vars=item_cols,
                       var_name="item", value_name="resp")
        sub["item"] = sub["item"].apply(
            lambda c: f"q{pattern.match(c).group(1)}"
        )
        sub["wave"] = wave
        if suffix == "precovid":
            # precovid columns are stored as text labels
            sub["resp"] = sub["resp"].astype(str).str.strip().str.lower().map(LIKERT_MAP)
        else:
            # covid/postcovid columns are already the same 0-4 numeric
            # codes (verified against the paper's 0-4 Likert scheme:
            # strongly disagree=0 ... strongly agree=4), just without
            # SPSS value labels attached.
            sub["resp"] = pd.to_numeric(sub["resp"], errors="coerce")
        long_frames.append(sub)

    long = pd.concat(long_frames, ignore_index=True)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "wave"]
    long = long[out_cols]

    out_path = OUT_DIR / "agarwal_2023_dreem.csv"
    long.to_csv(out_path, index=False)
    print(f"agarwal_2023_dreem: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
