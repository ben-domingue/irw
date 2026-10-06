#!/usr/bin/env python3
# STATUS: HELD (ben-domingue, 2026-10-06) -- not shipped. Items are keyed by raw
#   column position and the deposit's column-to-image tie does not reproduce its own
#   30-item file. Resolve the mapping (e.g. with the author) before shipping.
# Source: https://figshare.com/articles/dataset/33332604
# DOI: 10.6084/m9.figshare.33332604 (dataset; no paper DOI found)
#   Tang (2026). "Development and preliminary psychometric validation of a Chinese
#   Version of the Reading the Mind in the Eyes Test" (RMET-C) [data set], figshare.
# Data: Phase2-Raw-47Items.csv (file 68349946): 288 healthy Chinese adults x 197
#       columns. Headers are positional ("7, ", "8, ", ...); README.docx (file
#       68394001) documents the blocks: column 6 = practice, columns 7-54 = the
#       target-word matching task on 47 candidate eye images (scored 1 = correct,
#       0 = incorrect) with an attention-check item at column 47 (correct = 4, all
#       288 pass -- failers were already excluded), columns 55-103 sex judgment,
#       104-153 valence rating, 154-156 post-test evaluation.
# License: CC0 (figshare record).
#
# Shipped: one table, the target-word matching task (the RMET proper): 47 items,
#   0/1. item = "tw_c<column number>" -- the raw file's own column position,
#   because that is the only identifier the file carries.
#   The tie from column to image is NOT verified: Supplementary Material 2 maps
#   the final 30 items to "47-item No.", but taking column 7+k-1 (skipping the
#   attention column) as 47-item No. k does not reproduce rmet_30itemdata.csv
#   (2 of 30 columns match); rmet_30itemdata.csv's 30 columns are raw columns
#   8,9,13,14,16,17,18,20,21,23,25-31,34-40,42,43,45,46,48,52, in raw order.
#   So the item codes identify a response column, not a stimulus number.
# Not shipped: sex judgment (1/2 = which sex the face is judged to be -- a
#   classification, not a scored response), valence ratings (block 3 has 50
#   columns against 47 images + practice + attention, so its layout is not
#   resolvable from the README), the 32 unnamed retest columns (95 of 288 rows),
#   post-test items 154-156.
#
# Item text: not shipped. The file has no labels (CSV, positional headers); the
#   mental-state word options are in Supplementary Materials 5/6 and the images
#   in the deposit, but the column-to-image tie is unverified (above).
# Covariates (README): gender 1 male 2 female; age band 1 <=18, 2 18-25, 3 26-30,
#   4 31-40, 5 41-50, 6 51-60, 7 61+; education 1 high school .. 4 master's+.
#   MentalHistory dropped (constant 2 = no history).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "tang_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/68349946"
NAME = "tang_2026_rmet_c"


def fetch() -> Path:
    p = RAW_DIR / "raw47.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    assert d.shape == (288, 197), d.shape
    cols = d.columns.tolist()
    assert cols[5].endswith("Practice1") and cols[54].endswith("Practice2")
    assert (d[cols[46]] == 4).all()  # attention check, column 47
    pos = list(range(7, 47)) + list(range(48, 55))
    assert len(pos) == 47
    items = {cols[i - 1]: f"tw_c{i:02d}" for i in pos}
    assert d[list(items)].isin([0, 1]).all().all()
    assert d[cols[0]].is_unique and (d[cols[4]] == 2).all()

    w = d[[cols[0], cols[1], cols[2], cols[3]] + list(items)].rename(
        columns={cols[0]: "id", cols[1]: "cov_gender", cols[2]: "cov_age_band",
                 cols[3]: "cov_education", **items})
    covs = ["cov_gender", "cov_age_band", "cov_education"]
    t = w.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert len(t) == 288 * 47 and not t.duplicated(["id", "item"]).any()
    pv = {i: {0, 1} for i in items.values()}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
