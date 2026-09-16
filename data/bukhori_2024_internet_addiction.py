"""Md Bukhori & Ja'afar (2024), internet addiction among Malaysian adolescents
during COVID-19 -- PeerJ 12:e17489, CC BY 4.0.

Two Malay-language instruments, each its own table:

  * M-IAT (Malay Internet Addiction Test), 20 items, 0-5
  * M-DASS-21, 21 items, 0-3

The deposited sheet is a SurveyMonkey export with a TWO-ROW header: row 0
carries the question-block label (`MVIAT 1 - 5`, `M-DASS-21 15 - 21`) and row 1
the individual item wording, so a single-row read collapses each block into one
named column followed by `Unnamed:` columns. That is why upstream triage saw no
item structure here. Read with `header=[0, 1]` the 41 items are complete for all
420 respondents.

`Total Score` columns are the authors' composites and are excluded. Items are
numbered from the source's own numbering (`1.`, `2.`, ... inside each block),
not by position in the sheet.
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

DOI = "10.7717/peerj.17489"
PMCID = "PMC11216186"
MEMBER = "peerj-12-17489-s001.xlsx"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "bukhori_2024_iat":  (r"^MVIAT \d", "IAT",  (0, 5), 20),
    "bukhori_2024_dass": (r"^M-DASS-21", "DASS", (0, 3), 21),
}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)), header=[0, 1])


def convert() -> None:
    raw = fetch().reset_index(drop=True)
    ids = pd.Series(raw.index + 1, name="id")

    # Demographics sit under a `Response` sub-header; take the two that are
    # unambiguous and language-independent.
    cov = pd.DataFrame({"id": ids})
    for src, dst in (("UmurAge", "cov_age"), ("JantinaGender", "cov_gender")):
        col = [c for c in raw.columns if str(c[0]) == src]
        if col:
            cov[dst] = raw[col[0]].values
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (block, prefix, (lo, hi), n_expected) in SCALES.items():
        item_cols = [c for c in raw.columns if re.match(block, str(c[0]))]
        assert len(item_cols) == n_expected, (table, len(item_cols))
        wide = raw[item_cols].copy()
        # "12. Berapa kerap ..." -> IAT_12
        wide.columns = [f"{prefix}_{re.match(r'^(\d+)', str(c[1])).group(1)}"
                        for c in item_cols]
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
