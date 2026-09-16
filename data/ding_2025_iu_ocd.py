"""Ding et al. (2025), components of intolerance of uncertainty and
obsessive-compulsive symptoms -- PeerJ 13:e19791, CC BY 4.0.

Two instruments, each its own table:

  * IUS-12 (Intolerance of Uncertainty Scale, short form), 12 items, 1-5
  * OCI-R (Obsessive-Compulsive Inventory-Revised), 18 items, 1-5

The deposited .tsv has NO header row -- its first line is a respondent, which is
why a default read loses one case and names the columns after that person's
answers. Read with `header=None` the layout is: column 0 gender, column 1 age,
columns 2-13 the twelve IU items, columns 14-31 the eighteen OCD items. 12 + 18
is exactly the two instruments the paper names, and the abstract's node labels
(`IU6`, `OCD3`, `OCD9`) confirm the numbering runs from 1 within each block.

Item numbering follows that block numbering (`IU1`..`IU12`, `OCD1`..`OCD18`),
which is what the paper reports against. The file carries no respondent
identifier, so row position is the id.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.7717/peerj.19791"
PMCID = "PMC12318506"
MEMBER = "peerj-13-19791-s001.tsv"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "ding_2025_iu":  ("IU",  range(2, 14)),
    "ding_2025_ocd": ("OCD", range(14, 32)),
}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        data = z.read(MEMBER)
    return pd.read_csv(io.BytesIO(data), sep="\t", header=None,
                       encoding="utf-8-sig")


def convert() -> None:
    raw = fetch().reset_index(drop=True)
    assert raw.shape[1] == 32, raw.shape
    ids = pd.Series(raw.index + 1, name="id")
    cov = pd.DataFrame({"id": ids, "cov_gender": raw[0].values,
                        "cov_age": raw[1].values})
    cov_cols = ["cov_gender", "cov_age"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (prefix, cols) in SCALES.items():
        wide = raw[list(cols)].copy()
        wide.columns = [f"{prefix}{i}" for i in range(1, len(list(cols)) + 1)]
        wide.insert(0, "id", ids)

        long = wide.merge(cov, on="id").melt(
            id_vars=["id"] + cov_cols, value_vars=list(wide.columns[1:]),
            var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(1, 5).all(), table
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
