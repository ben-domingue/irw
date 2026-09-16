"""Acevedo-Triana et al. (2017), running wheel training, neurogenesis and
working memory in adult rats -- PeerJ 5:e2976, CC BY 4.0.

One trial-level table from the T-maze: 21 rats, five sessions of 20 trials.

`id` is the rat; 21 is below the 100-id floor in datastandard.md. Taken on
ben-domingue's ruling of 2026-09-16 (irw#2220) -- see the note in
`data/martinez_2024_capuchin.py` for the reasoning.

**`resp` is which arm the rat entered, not whether it was right.** This is a
spontaneous-alternation T-maze: no arm is correct, and the construct the
authors measure (alternation) is a property of consecutive trials rather than
of any one trial. `resp` is 1 for the right arm and 0 for the left. Do not
model it as accuracy. The deposit's own `Alternation` column is a per-session
total that lives on summary rows, not a trial-level response, and is not used.

Three things about the deposited sheet:

  * It carries summary rows where `Animals` is the literal string "TOTAL"; those
    hold the session totals and are dropped.
  * `Right` and `Left` are one-hot on trial rows, but only 1,077 of 2,100 trials
    have a choice recorded. The other 1,022 have both columns 0 -- the rat did
    not enter an arm within the time limit. Those are non-responses, not a
    choice, and are dropped rather than scored. One further row has BOTH columns
    set to 1, which cannot be a single choice, and is dropped as a data error.
  * The `Hab*` habituation phases have one row per animal and no trials, so only
    the `Forz` and `Ele1`-`Ele4` phases appear here.
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

DOI = "10.7717/peerj.2976"
PMCID = "PMC5426350"
MEMBER = "peerj-05-2976-s001.xlsx"
SHEET = "BASE COMPLETA"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE = "acevedo_triana_2017_tmaze"
TRIAL_PHASES = ["Forz", "Ele1", "Ele2", "Ele3", "Ele4"]


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)), sheet_name=SHEET)


def convert() -> None:
    raw = fetch()
    raw = raw[raw["Animals"].astype(str).str.strip() != "TOTAL"]
    raw = raw[raw["Phase"].astype(str).str.strip().isin(TRIAL_PHASES)]

    right = pd.to_numeric(raw["Right"], errors="coerce")
    left = pd.to_numeric(raw["Left"], errors="coerce")
    chose = (right + left) == 1          # drops 1,022 no-entries and 1 double

    long = pd.DataFrame({
        "id": raw["Animals"].astype(str).str.strip(),
        "item": (raw["Phase"].astype(str).str.strip() + "_"
                 + raw["Trial"].astype(int).astype(str).str.zfill(2)),
        "resp": right.where(chose),
        "trial": pd.to_numeric(raw["Trial"], errors="coerce").astype("Int64"),
        "rt": pd.to_numeric(raw["Response Time"], errors="coerce"),
        "date": (pd.to_datetime(raw["Date"], errors="coerce")
                 - pd.Timestamp("1970-01-01")).dt.total_seconds(),
        # "Control " with a trailing space is in the source.
        "cov_group": raw["Group"].astype(str).str.strip(),
        "cov_weight_g": pd.to_numeric(raw["Weight"], errors="coerce"),
    })
    n_dropped = int((~chose).sum())
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
          f"items={long['item'].nunique()} pct_right={long['resp'].mean():.3f} "
          f"(dropped {n_dropped} trials with no arm entry)")


if __name__ == "__main__":
    convert()
