from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0216544
# DOI: 10.1371/journal.pone.0216544
# Robbins, Roberts, Weary et al. (2019), "Factors influencing public
# support for dairy tie stall housing in the US". S1/S2 Files. CC BY 4.0.
# Two between-subjects survey samples with identical belief-item wording
# (S1 N=430 "hours" framing, S2 N=372 "willingness-to-pay" framing) --
# merged here with ids offset per sample and a cov_framing column, per
# datastandard.md's "same instrument administered to multiple sub-studies"
# convention.
#
# Column-name structure (b1_*/b2_*/has*) makes the item split clear even
# without the exact question wording (not found in the article text):
# b1_* (morerisky/lowerquality/harmenviro) are risk/quality/environmental-
# harm beliefs about tie-stall housing; b2_* (borganic/bfamfarm/
# bsmallfarm) are beliefs about organic/family-farm/small-farm status --
# a different content domain, so shipped as a separate 3-item scale rather
# than combined with b1. has1-3's exact content is unconfirmed from the
# file alone (ships under a generic name). All three are 1-7 Likert.
FILES = [
    ("https://journals.plos.org/plosone/article/file"
     "?type=supplementary&id=10.1371/journal.pone.0216544.s001", "hours"),
    ("https://journals.plos.org/plosone/article/file"
     "?type=supplementary&id=10.1371/journal.pone.0216544.s002", "wtp"),
]
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"age": "cov_age", "female": "cov_female", "region": "cov_region",
           "rural": "cov_rural", "ed": "cov_education", "liberal": "cov_liberal"}

SCALES = {
    "robbins_2019_risk_quality_belief": ["b1_morerisky", "b1_lowerquality", "b1_harmenviro"],
    "robbins_2019_farmtype_belief": ["b2_borganic", "b2_bfamfarm", "b2_bsmallfarm"],
    "robbins_2019_has_belief": ["has1", "has2", "has3"],
}


def fetch() -> pd.DataFrame:
    frames = []
    offset = 0
    for url, framing in FILES:
        r = requests.get(url, headers=UA, timeout=120)
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content))
        df["id"] = range(offset + 1, offset + 1 + len(df))
        df["cov_framing"] = framing
        offset += len(df)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def convert():
    df = fetch().rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns] + ["cov_framing"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
