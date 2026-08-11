#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264797
# DOI: 10.1371/journal.pone.0264797
# Supporting Information: https://doi.org/10.1371/journal.pone.0264797.s001
#
# S1 Data (XLSX), sex-differences-in-fear-extinction study (Binette, Totty,
# and Maren 2022). Two sheets, one per rat strain (Long-Evans "LE IED" and
# Wistar "Wistar IED & Renewal"), each with trial/block-level percent-time-
# freezing measurements. Both strains share an identical three-phase core
# design (Conditioning BL+T1-T5, Extinction BL+Blk1-9, Retrieval
# BL+Blk1-9, same freezing-percent measurement throughout) - the paper's
# whole design compares strain and sex on this shared measure, so the two
# sheets are merged into one file with a cov_strain covariate rather than
# shipped as two <50-N files. Wistar animals were additionally run through
# an "Extinction 2" and "Renewal" phase not administered to LE rats - those
# extra items are included too; they simply have no rows for LE ids (valid
# in long format, not a forced correspondence).
#
# `id` is offset by strain (Wistar id + 100000) per datastandard.md's
# multi-sample-merge guidance, since raw Rat IDs restart at 1 in each
# sheet and do not refer to the same animals.
#
# Excluded: one LE rat explicitly marked "(excluded)*" in the raw sheet
# (technical issue during conditioning, no shock delivered - matches the
# paper's "1 female Long-Evans rat ... excluded" note) and the Wistar
# "Trials 1-2 avg" column (composite, not a raw trial).
#
# `resp` is the raw per-trial/block percent freezing (continuous 0-100),
# not an aggregate - each row is one measurement occasion.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0264797.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def _parse_sheet(content, sheet_name, id_col, cov_col_idx, item_start_col,
                  strain, id_offset):
    raw = pd.read_excel(content, sheet_name=sheet_name, header=None)
    phase_row = raw.iloc[0].ffill()
    trial_row = raw.iloc[1]
    data = raw.iloc[2:].reset_index(drop=True)
    data.columns = range(data.shape[1])

    ids = pd.to_numeric(data[id_col], errors="coerce")
    covs = {name: data[idx] for idx, name in cov_col_idx.items()}

    frames = []
    for col in range(item_start_col, data.shape[1]):
        trial_label = str(trial_row[col]).strip().lower()
        if "avg" in trial_label:
            continue  # composite column (e.g. "Trials 1-2 avg"), not a raw trial
        phase = str(phase_row[col]).strip().lower().replace(" ", "_")
        item_name = f"{phase}_{trial_label.replace(' ', '_')}"
        vals = pd.to_numeric(data[col], errors="coerce")
        row = {"id": ids, "item": item_name, "resp": vals, "cov_strain": strain}
        row.update(covs)
        frames.append(pd.DataFrame(row))

    long = pd.concat(frames, ignore_index=True)
    long = long.dropna(subset=["id", "resp"]).reset_index(drop=True)
    long["id"] = long["id"].astype(int) + id_offset
    return long


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    content = io.BytesIO(r.content)

    le = _parse_sheet(
        content, "LE IED", id_col=0,
        cov_col_idx={1: "cov_sex", 2: "cov_ext_group"},
        item_start_col=3, strain="LE", id_offset=0,
    )
    wistar = _parse_sheet(
        content, "Wistar IED & Renewal", id_col=0,
        cov_col_idx={1: "cov_ext_group", 2: "cov_ext_condition",
                     3: "cov_genotype", 4: "cov_sex",
                     5: "cov_renewal_context"},
        item_start_col=6, strain="Wistar", id_offset=100000,
    )

    long = pd.concat([le, wistar], ignore_index=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 100)]

    cov_cols = ["cov_strain", "cov_sex", "cov_ext_group", "cov_ext_condition",
                "cov_genotype", "cov_renewal_context"]
    for c in cov_cols:
        if c not in long.columns:
            long[c] = pd.NA
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "binette_2022_extinction.csv"
    long.to_csv(out_path, index=False)
    print(f"binette_2022_extinction: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
