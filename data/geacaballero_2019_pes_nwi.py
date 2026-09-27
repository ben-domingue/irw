#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6660900
# DOI: 10.7717/peerj.7369
#
# "Development of a short questionnaire based on the Practice Environment
# Scale-Nursing Work Index." PeerJ. CC BY 4.0. N=269.
# Raw file bundles two parallel item sets over the same 30 constructs:
# the original PES-NWI-style 4-point Likert items, and a proposed short
# yes/no version being validated against it -- split into two IRW files
# per datastandard.md's "one file per scale" rule (geacaballero_2019_pes_nwi
# and geacaballero_2019_pes_nwi_short). A couple of Likert categories have
# raw typos ("alsolutely disagree", "absolutely disagree.") normalized to
# their intended category before mapping.
#
# #2097: the Likert block used to be a hard-coded list of 30 names that
# omitted item 18 (`education`). It is now derived from the data, as the
# yes/no block already was: every non-X column whose answers all fall in
# LIKERT_MAP. The source carries 31 such items.

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6660900/supplementaryFiles"
MEMBER = "peerj-07-7369-s002.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {
    "absolutely disagree": 1, "alsolutely disagree": 1, "absolutely disagree.": 1,
    "slightly disagree": 2,
    "slightly agree": 3,
    "absolutely agree": 4,
}
YESNO_MAP = {"NO": 0, "YES": 1}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_spss(tmp.name)
    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df)
    x_items = [c for c in df.columns if c.startswith("X")]
    likert_items = [
        c for c in df.columns
        if c != "id" and not c.startswith("X")
        and df[c].dropna().astype(str).str.strip().str.lower().isin(LIKERT_MAP).all()
    ]
    assert len(likert_items) == 31, likert_items

    for c in likert_items:
        df[c] = df[c].astype(str).str.strip().str.lower().map(LIKERT_MAP)
    for c in x_items:
        df[c] = df[c].astype(str).str.strip().str.upper().map(YESNO_MAP)

    for out_name, item_cols in [
        ("geacaballero_2019_pes_nwi", likert_items),
        ("geacaballero_2019_pes_nwi_short", x_items),
    ]:
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
