#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC4957988
# DOI: 10.7717/peerj.2245
#
# Johannisson (2016), "Correlations between personality traits and
# specific groups of alpha waves in the human EEG." PeerJ. CC BY 4.0.
# N=200 healthy participants (Methods: "There were 200 participants in the
# study").
# Supplementary file peerj-04-2245-s002.xlsx is transposed: rows are
# personality items/subscales, columns are the 200 participants (each
# identified by an EEG-recording-date-based code, e.g. "081030" -- a
# session code, not a birthdate; no PII). Rows 0-48 (the 5-domain and
# 30-facet headers) are pre-computed composite/percentile scores from the
# online IPIP-NEO scoring service and are excluded as aggregates per
# datastandard.md. Rows 50-169 are the 120 raw item statements of the
# IPIP-NEO-120 (Methods: "The 120-item version of the IPIP-NEO (Johnson,
# 2014) was used, and all participants completed all items"), each rated
# on the instrument's standard 1 ("very inaccurate") - 5 ("very accurate")
# scale, confirmed by the observed 1-5 range in the raw cells.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4957988/supplementaryFiles"
MEMBER = "peerj-04-2245-s002.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_ROW_START = 50  # 0-indexed row of first raw IPIP-NEO-120 item ("Worry about things.")
N_ITEMS = 120
N_SUBJECTS = 200


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    raw = pd.read_excel(io.BytesIO(zf.read(MEMBER)), header=None)

    subject_codes = raw.iloc[4, 1:1 + N_SUBJECTS].tolist()
    item_labels = raw.iloc[ITEM_ROW_START:ITEM_ROW_START + N_ITEMS, 0].tolist()
    item_block = raw.iloc[ITEM_ROW_START:ITEM_ROW_START + N_ITEMS, 1:1 + N_SUBJECTS]
    item_block.columns = [str(c) for c in subject_codes]
    item_block.index = [f"item_{i + 1:03d}" for i in range(N_ITEMS)]

    long = item_block.reset_index().melt(id_vars="index", var_name="id", value_name="resp")
    long = long.rename(columns={"index": "item"})
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "johannisson_2016_ipip_neo.csv"
    long.to_csv(out_path, index=False)
    print(f"johannisson_2016_ipip_neo: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
