#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0351750
# DOI: 10.1371/journal.pone.0351750
# Sun (2026), "Designing the syllabus for the EAP course 'Architectural Art
# English': A needs and genre analysis-based approach", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0351750.s002
#
# The survey bundles 4 distinct question blocks under one 1-5 rating scale,
# identified by the item numbering resetting at each block (2-x, 3-x, 4-x,
# 5-x): usage-scenario importance/frequency, learning difficulties severity,
# teaching-content importance, and teaching-method effectiveness. Split into
# 4 files per datastandard.md's one-scale-per-file rule.

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0351750.s002"

BLOCK_PREFIXES = {
    "sun_2026_eap_usage": "2-",
    "sun_2026_eap_difficulty": "3-",
    "sun_2026_eap_content": "4-",
    "sun_2026_eap_methods": "5-",
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Number": "id",
                             "1、Please choose your identity": "cov_identity"})

    for out_name, prefix in BLOCK_PREFIXES.items():
        item_cols = [c for c in df.columns if c.startswith(prefix)]
        long = df.melt(id_vars=["id", "cov_identity"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "cov_identity"]]

        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
