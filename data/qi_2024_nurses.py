"""Qi et al. (2024), stress coping and somatization in nurses -- PeerJ
12:e18658, CC BY 4.0.

Five instruments, each its own table:

  * PHQ-9, 9 items, 0-3
  * SSS (somatic symptoms), 15 items, 1-4
  * PSS-10, 10 items, 0-4
  * PSSS (MSPSS, perceived social support), 12 items, 1-7
  * CISS, 21 items, 1-5

Two things about the deposited header. Its `* Total score` columns are the
authors' composites and are excluded. And five columns sit inside the SSS block
carrying PHQ/GAD names (`PHQ3.1`, `PHQ4.1`, `PHQ1.1`, `GAD1`, `PHQ7.1` after
pandas de-duplicates them) while holding the SSS block's 1-4 response scale.
SSS1..SSS15 are all present and complete without them, so those five columns are
left out: they are mislabelled somewhere, and guessing which SSS item each one
is would invent item identities the deposit does not support. `PSS0` is a
straightforward typo for PSS4 -- it sits in position 4 of an otherwise complete
PSS1..PSS10 -- and is renamed, not dropped.
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

DOI = "10.7717/peerj.18658"
PMCID = "PMC11627075"
MEMBER = "peerj-12-18658-s001.xlsx"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "qi_2024_phq9":       (r"^PHQ\d+$",  (0, 3)),
    "qi_2024_somatic":    (r"^SSS\d+$",  (1, 4)),
    "qi_2024_pss10":      (r"^PSS\d+$",  (0, 4)),
    "qi_2024_mspss":      (r"^PSSS\d+$", (1, 7)),
    "qi_2024_ciss":       (r"^CISS\d+$", (1, 5)),
}

COV_COLS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Title": "cov_professional_title",
    "Work Experience": "cov_work_experience",
    "Residence": "cov_residence",
}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)))


def convert() -> None:
    raw = fetch()
    # The header has stray inner spaces ("Age ", "PSSS 2"); collapse them so the
    # scale patterns below match what the instrument actually names.
    raw.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in raw.columns]
    raw.columns = [re.sub(r"^(PSSS|PSS|SSS|PHQ|CISS) (\d+)$", r"\1\2", c)
                   for c in raw.columns]
    raw = raw.rename(columns={"PSS0": "PSS4", "Number": "id"})

    present = {src: dst for src, dst in COV_COLS.items() if src in raw.columns}
    cov = raw[["id"] + list(present)].rename(columns=present)
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (pattern, (lo, hi)) in SCALES.items():
        # PSS and PSSS share a prefix, so match the whole name, not a startswith.
        item_cols = [c for c in raw.columns if re.match(pattern, c)]
        wide = raw[["id"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(lo, hi).all(), \
            f"{table}: resp outside {lo}-{hi}: {sorted(long['resp'].unique())}"
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
