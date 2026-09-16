"""Arbinaga et al. (2025), psychopathological symptoms in soccer referees --
PeerJ 13:e19790, CC BY 4.0.

Three instruments, each its own table:

  * AAQ-II, 7 items, 1-7 (psychological inflexibility)
  * SAS, 45 items, 0-4 (sport anxiety)
  * MPS, 31 items, 1-5 (multidimensional perfectionism)

`MPSF*` and `SAF*` are the authors' own subscale totals, not responses, and are
excluded. The MPS block is numbered to 38 with gaps: only the 31 columns the
deposit actually carries are melted, and each keeps its source number so the
items stay matchable to the published instrument.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.7717/peerj.19790"
PMCID = "PMC12352424"
MEMBER = "peerj-13-19790-s001.sav"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

# ^NAME followed only by digits -- excludes MPSF1 from the MPS block and SAF1
# from the SAS block, which are subscale totals.
SCALES = {
    "arbinaga_2025_aaq2":         (r"^AAQ\d+$", (1, 7)),
    "arbinaga_2025_sport_anxiety": (r"^SAS\d+$", (0, 4)),
    "arbinaga_2025_perfectionism": (r"^MPS\d+$", (1, 5)),
}

COV_COLS = {"Sex": "cov_gender", "Age": "cov_age", "Years": "cov_years_refereeing"}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        data = z.read(MEMBER)
    df, _ = pyreadstat.read_sav(io.BytesIO(data))
    return df


def convert() -> None:
    raw = fetch()
    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)          # the deposit carries no id column

    present = {src: dst for src, dst in COV_COLS.items() if src in raw.columns}
    cov = raw[["id"] + list(present)].rename(columns=present)
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (pattern, (lo, hi)) in SCALES.items():
        item_cols = [c for c in raw.columns if pd.Series([c]).str.match(pattern).iat[0]]
        wide = raw[["id"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(lo, hi).all(), table
        assert not long.duplicated(["id", "item"]).any(), table
        assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, [(c.name, c.detail) for c in bad]

        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
