#!/usr/bin/env python3
# Source: https://zenodo.org/records/23585324
# DOI: 10.5281/zenodo.23585324 (data; no paper DOI on the record)
#   Gavin-Chocano, O., Gonzalez-Castellano, N., Berrios-Aguayo, B., et al.
#   (2026). "Emotional intelligence and creativity: a longitudinal study of
#   pupils in Compulsory Secondary Education." Zenodo.
# Data: "Matriz Final IE y Creatividad. NUEVO4.sav", 695 Spanish secondary
#   pupils, TMMS-24 items (V3_1..V3_24, SPSS-labelled with the Spanish
#   stems) and creativity scores, pretest and posttest.
# License: CC BY 4.0 (Zenodo record).
# Codebook: none beyond the SPSS labels.
#
# Item text: not shipped -- the Spanish stems are the SPSS variable labels,
#   but no rights-register row exists for the TMMS-24; left for an itemtext
#   pass.
#
# PRETEST ONLY. 108 of 695 pupils have a posttest row identical to their
#   pretest row on all 24 items (58% of all cells identical, pre-post total
#   r = .55), which reads as carried-forward values rather than a second
#   administration; the posttest is not shipped. See the lane hand-off.
# Tables (TMMS-24, 1-5; its three dimensions as separate tables):
#   gavinchocano_2026_tmms_attention  V3_1_pre..V3_8_pre
#   gavinchocano_2026_tmms_clarity    V3_9_pre..V3_16_pre
#   gavinchocano_2026_tmms_repair     V3_17_pre..V3_24_pre
#   Out-of-range cells (values 7 and 11 on a 1-5 item, 4 cells) are entry
#   errors and are dropped. The 1-label reads "Algo de acuerdo" twice in the
#   .sav (1 and 2); 1 is the TMMS-24's "Nada de acuerdo" anchor.
# Not shipped: creativity (scored totals only). No demographics in the file.
# id = row index.

import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = ("https://zenodo.org/api/records/23585324/files/"
            "Matriz%20Final%20IE%20y%20Creatividad.%20NUEVO4.sav/content")
ALLOWED = {1, 2, 3, 4, 5}
SPEC = {"gavinchocano_2026_tmms_attention": range(1, 9),
        "gavinchocano_2026_tmms_clarity": range(9, 17),
        "gavinchocano_2026_tmms_repair": range(17, 25)}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        d, _ = pyreadstat.read_sav(tmp.name)
    assert d.shape == (695, 74), d.shape
    d["id"] = range(1, len(d) + 1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, rng in SPEC.items():
        items = [f"V3_{i}_pre" for i in rng]
        long = d.melt(id_vars=["id"], value_vars=items, var_name="item",
                      value_name="resp").dropna(subset=["resp"])
        bad = ~long["resp"].isin(ALLOWED)
        print(f"[drop] {table}: {int(bad.sum())} out-of-range cells")
        long = long[~bad].copy()
        long["resp"] = long["resp"].astype(int)
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: ALLOWED for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
