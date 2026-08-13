#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7908888
# DOI: 10.7717/peerj.10752
#
# Habibi et al. (2021), "Psychometric properties of the Multi-group Ethnic
# Identity Measure (MEIM) in a sample of Iranian young adults." PeerJ.
# CC BY 4.0.
# Supplementary file peerj-09-10752-s001.csv holds the raw 12-item MEIM
# (Methods: "The MEIM (Phinney, 1992) contains 12 items ... rated on a
# four-point Likert-type scale ... 1 'strongly disagree' to 4 'strongly
# agree'"), one row per respondent, no id column -- confirmed n=426 final
# analytic sample (Methods: "the final sample included 426 students");
# row index used as id since no person identifier exists in the file.
# peerj-09-10752-s002.csv holds only pre-computed subscale/outcome
# composites (Identity, Commit, Exploration, Wellbeing, PositiveA,
# NegativeA, SWL) and is not used. Blank-string cells are missing
# responses and are dropped. No PII (no names/ids present at all).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7908888/supplementaryFiles"
MEMBER = "peerj-09-10752-s001.csv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"Q{i}" for i in range(1, 13)]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_csv(io.BytesIO(zf.read(MEMBER)), dtype=str)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "habibi_2021_meim.csv"
    long.to_csv(out_path, index=False)
    print(f"habibi_2021_meim: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
