"""Lev-Ari et al. (2021), "Eating for numbing" -- trauma exposure, emotion
dysregulation and disordered eating. PeerJ 9:e11899, CC BY 4.0.

Three instruments, each its own table:

  * DERS (Difficulties in Emotion Regulation Scale), 36 items, 1-5
  * EDE-Q (Eating Disorder Examination Questionnaire), 22 items, 0-6
  * DES (Dissociative Experiences Scale), 14 items, 1-11

The deposit's `LEC` block (85 columns) is excluded: every one of its cells is
the constant 1, so it carries no responses.

**`id` does not link people across waves.** The file has a `time` column with
two values, and a `code` column that looks like a participant identifier but is
not usable as one -- it is null for 5 rows, literally 0 for 70 more, and 75
(code, time) pairs are duplicated. So row position is the id, `wave` carries
`time`, and the same person appearing at both waves appears here as two
unlinked ids. Anyone needing the repeated-measures structure has to go back to
the deposit.
"""
from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.7717/peerj.11899"
PMCID = "PMC8349516"
MEMBER = "peerj-09-11899-s001.sav"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "lev_ari_2021_ders": (r"^DERS\d+$", (1, 5)),
    "lev_ari_2021_edeq": (r"^EDEQ\d+$", (0, 6)),
    "lev_ari_2021_des":  (r"^DES\d+$",  (1, 11)),
}

COV_COLS = {"sex": "cov_gender", "birth": "cov_birth_year",
            "education": "cov_education_years", "family": "cov_family_status",
            "child": "cov_n_children", "religion": "cov_religion"}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        data = z.read(MEMBER)
    df, _ = pyreadstat.read_sav(io.BytesIO(data))
    return df


def convert() -> None:
    raw = fetch().reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)
    raw["wave"] = pd.to_numeric(raw["time"], errors="coerce").astype("Int64")

    present = {s: d for s, d in COV_COLS.items() if s in raw.columns}
    cov = raw[["id"] + list(present)].rename(columns=present)
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (pattern, (lo, hi)) in SCALES.items():
        item_cols = [c for c in raw.columns if re.match(pattern, str(c))]
        wide = raw[["id", "wave"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id", "wave"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp", "wave"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "wave"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(lo, hi).all(), \
            f"{table}: {sorted(long['resp'].unique())}"
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
