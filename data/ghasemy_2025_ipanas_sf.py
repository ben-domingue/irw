#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/BVA71C
# DOI: 10.7910/DVN/BVA71C
#   Ghasemy, M. (2025). Replication Data for: Measuring Lecturers' Emotions
#   Using the International Positive and Negative Affect Schedule Short Form:
#   A Two-Dimensional Graded Response Model in the Item Response Theory
#   Framework [Dataset]. Harvard Dataverse.
# Data: "data for sharing n = 577.csv" -- 577 university lecturers answering
#   the revised 9-item I-PANAS-SF. The deposit's own description names the
#   instrument: "the 9-item revised I-PANAS-SF scale".
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped. The file carries item CODES only (pa1, na1, ...) and
#   no codebook or label level of any kind; the I-PANAS-SF's ten affect
#   adjectives are in Thompson (2007), not in this deposit. The published
#   analysis is what names the scale, not the file.
#
# ONE table, because the I-PANAS-SF is one instrument: its positive and
#   negative affect items are the two dimensions of the graded response model
#   the paper fits, not two separately administered scales. Nine items ship --
#   pa1, pa3, pa4, pa5, na1-na5. `pa2` is absent from the deposit, which is
#   what "revised 9-item" means: the tenth item was dropped in revision, so
#   the gap in the numbering is the instrument's, not a missing column.
#
# The scale is coded 0-4 in the deposit (5 points, as administered). Four of
#   the nine items use only 1-4; no response is outside 0-4 and no cell is
#   blank -- all 577 x 9 = 5,193 responses are present.
#
# id: the row index. The deposit carries no respondent id column at all, and
#   under the 2026-09-20 narrowing a row index is the correct substitute.
# Covariates: cov_leader, cov_gender, cov_age_binary, cov_experience -- all
#   0/1 in the deposit, which does not document which level is which, so they
#   ship as given with no recoding.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "bva71c" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 10851728, "data for sharing n = 577.csv"
ITEMS = ["pa1", "pa3", "pa4", "pa5", "na1", "na2", "na3", "na4", "na5"]
COVS = {"leader": "cov_leader", "gender": "cov_gender",
        "age_binary": "cov_age_binary", "Exper": "cov_experience"}
SCALE = set(range(0, 5))
TABLE = "ghasemy_2025_ipanas_sf"


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.harvard.edu/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_csv(fetch())
    assert list(df.columns) == list(COVS) + ITEMS, list(df.columns)
    assert len(df) == 577, len(df)
    assert not df.isna().any().any(), "the deposit is complete; a blank is new"
    assert "pa2" not in df.columns, "pa2 present: this is not the 9-item form"

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        assert set(df[cov]) <= {0, 1}, (cov, sorted(set(df[cov])))
        df[cov] = df[cov].astype("Int64")

    t = (df[["id", *cov_cols, *ITEMS]]
         .melt(id_vars=["id", *cov_cols], value_vars=ITEMS,
               var_name="item", value_name="resp"))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the administered 0-4 scale: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 577 and t["item"].nunique() == 9
    assert len(t) == 577 * 9

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
