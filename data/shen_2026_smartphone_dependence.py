#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0350219
# DOI: 10.1371/journal.pone.0350219
# Data: S1 Data (xlsx, sheet "plos one")
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0350219.s001
# License: CC BY 4.0 (PLOS ONE)
#
# Shen et al. (2026), "How does self-control influence college students'
# smartphone dependence". 490 valid questionnaires from four universities in
# Hubei Province, China, January 2025.
#
# Four instruments, mapped to the paper's Methods (section 2.2) by item count
# and observed response range -- the deposit's column prefixes are not
# self-explanatory and SASA/SADS in particular are easy to swap:
#
#   SCS1-SCS19   self-control scale (Tan Shuhua), 5 dimensions, 19 items, 1-5
#   CDRS1-CDRS25 Connor-Davidson Resilience Scale, Chinese version ("mental
#                toughness"), 25 items, 0-4
#   SADS1-SADS20 social adaptability diagnostic scale (Zheng Richang), 20
#                items, scored -2 / 0 / 2. Confirmed by the scoring rule, not
#                the prefix: the paper describes exactly this three-point
#                +/-2 scheme with opposite polarity for odd and even items,
#                and the deposit orders the columns odd-then-even (SADS1,
#                SADS3, ... SADS19, SADS2, SADS4, ... SADS20) to match.
#                Left as administered -- the paper reverses the odd items
#                before summing, but per datastandard.md reverse-scored items
#                are not recoded here.
#   SASA1-SASA26 Adult Smartphone Addiction Scale (Chen Huan), 1-5.
#                NOTE: the paper says 20 items; the deposit carries 26 and
#                all 26 are on the same 1-5 scale with no missing values.
#                Shipped as deposited (26), with the discrepancy recorded
#                here rather than silently trimmed to the paper's count.
#
# No id column; the row index is the respondent id (490 rows, no missing
# values anywhere in the four blocks).
#
# Item text: not shipped. The deposit is an .xlsx with positional column
# codes and no label layer of any kind -- neither variable-label nor
# value-label equivalents exist in this format -- and the article gives only
# dimension names, not stems. All four instruments are third-party published
# scales whose wording would have to come from the source publications.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0350219.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# out_name -> (item-column regex, valid resp values)
SCALES = {
    "shen_2026_self_control":         (r"SCS\d+",  {1, 2, 3, 4, 5}),
    "shen_2026_cdrisc":              (r"CDRS\d+", {0, 1, 2, 3, 4}),
    "shen_2026_social_adaptability": (r"SADS\d+", {-2, 0, 2}),
    "shen_2026_smartphone_addiction": (r"SASA\d+", {1, 2, 3, 4, 5}),
}


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = requests.get(SI_URL, headers=UA, timeout=120)
    raw.raise_for_status()
    df = pd.read_excel(io.BytesIO(raw.content), sheet_name="plos one")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    for out_name, (pattern, valid) in SCALES.items():
        item_cols = [c for c in df.columns if re.fullmatch(pattern, str(c))]
        if not item_cols:
            raise SystemExit(f"no item columns matched {pattern}")
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[long["resp"].isin(valid)]
        long = long[["id", "item", "resp"]].reset_index(drop=True)
        checks = run_qc(long)
        failed = [c for c in checks if c.status == "fail"]
        assert not failed, (out_name, [(c.name, c.detail) for c in failed])
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
