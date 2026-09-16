"""Pop et al. (2023), media narratives and microplastics risk perception --
PeerJ 11:e16338, CC BY 4.0.

The survey's 11 substantive questions run on two different response scales, so
they become two tables rather than one:

  * `pop_2023_mp_concern`, questions 1-3, binary (heard of microplastics; two
    concern questions)
  * `pop_2023_mp_media`, questions 4-11, 1-7 ("which of the following
    information do you know from the media?")

Melting all eleven together would put a yes/no scale and a 7-point scale in one
`resp` column. The deposit carries the full English item wording as its column
headers; items are numbered here from the source's own `N)` prefix.
"""
from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import pandas as pd
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.7717/peerj.16338"
PMCID = "PMC10625762"
MEMBER = "peerj-11-16338-s001.xlsx"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "pop_2023_mp_concern": (range(1, 4), (0, 1)),
    "pop_2023_mp_media":   (range(4, 12), (1, 7)),
}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)),
                             sheet_name="English_Recoded")


def convert() -> None:
    raw = fetch().reset_index(drop=True)
    number = {}
    for c in raw.columns:
        m = re.match(r"^\s*(\d+)\)", str(c))
        if m:
            number[int(m.group(1))] = c

    ids = pd.Series(raw.index + 1, name="id")
    cov = pd.DataFrame({"id": ids,
                        "cov_gender": raw[number[12]].values,
                        "cov_age": raw[number[13]].values})
    cov_cols = ["cov_gender", "cov_age"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (qs, (lo, hi)) in SCALES.items():
        item_cols = [number[q] for q in qs]
        wide = raw[item_cols].copy()
        wide.columns = [f"q{q}" for q in qs]
        wide.insert(0, "id", ids)

        long = wide.merge(cov, on="id").melt(
            id_vars=["id"] + cov_cols, value_vars=list(wide.columns[1:]),
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
