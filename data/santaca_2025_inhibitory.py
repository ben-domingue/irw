"""Santaca et al. (2025), "Lizards and tortoises show evidence of low inhibitory
control" -- Scientific Reports 15:23446, CC BY 4.0.

A detour task: the animal must go around a transparent barrier rather than
approach the reward directly. One table, 32 reptiles x 20 trials, complete.

`id` is the animal; 32 is below the 100-id floor in datastandard.md. Taken on
ben-domingue's ruling of 2026-09-16 (irw#2220) -- see the note in
`data/martinez_2024_capuchin.py` for the reasoning.

`item` is the trial in order (1-20, the deposit's own `Trial.order`, which is
`Day` 1-4 crossed with `Trial.day` 1-5). Each animal meets each trial exactly
once, so the matrix is complete and needs no occasion column. Read the items as
a learning sequence rather than as distinct probes: trial 1 is the first
exposure to the apparatus for every animal.

`resp` is the deposit's `Performance`, 1 = detoured successfully.

`id` is the species prefixed onto the deposit's `Subject`. The two species are
identified differently there -- the eight bearded dragons by name ("Oscar"), the
24 tortoises by number (1-25 with gaps) -- so a bare `Subject` would put opaque
integer ids beside names. The 32 values are already unique without the prefix;
it is for legibility, not disambiguation.

The deposit's `Time_log` is NOT emitted as `rt`. datastandard.md requires `rt`
in seconds, and the column is a logarithm whose base is not stated: read as
log10 the latencies run 3-256s, read as a natural log they run 1.6-11.1s, and
both are plausible for this apparatus. Guessing would publish wrong seconds, so
the column is left out.
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

DOI = "10.1038/s41598-025-08373-9"
PMCID = "PMC12222717"
MEMBER = "41598_2025_8373_MOESM1_ESM.xlsx"
SHEET = "Dataset inhibitory control"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE = "santaca_2025_inhibitory_control"


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        blob = z.read(MEMBER)
    sheets = pd.ExcelFile(io.BytesIO(blob)).sheet_names
    name = next(s for s in sheets if s.strip().startswith("Dataset inhibit"))
    return pd.read_excel(io.BytesIO(blob), sheet_name=name)


def convert() -> None:
    raw = fetch()
    long = pd.DataFrame({
        "id": (raw["Species"].astype(str).str.strip().str.lower().str.rstrip("s")
               + "_" + raw["Subject"].astype(str).str.strip()),
        "item": "trial_" + raw["Trial.order"].astype(int).astype(str).str.zfill(2),
        "resp": pd.to_numeric(raw["Performance"], errors="coerce"),
        "cov_species": raw["Species"].astype(str).str.strip(),
        "cov_sex": raw["Sex"].astype(str).str.strip(),
    })
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert long["resp"].isin([0, 1]).all()
    assert not long.duplicated(["id", "item"]).any()
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} pct_correct={long['resp'].mean():.3f}")


if __name__ == "__main__":
    convert()
