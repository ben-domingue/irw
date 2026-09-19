"""Pan et al. (2023), time perspective, self-control and mobile phone addiction
-- PeerJ 11:e16467, CC BY 4.0.

The deposit labels its item blocks only `a1..a20`, `b1..b16`, `c1..c19`. The
authors' own subscale columns, further right in the same sheet, identify them:

  * `a*`  -> ZTPI: the five subscale columns PP, PN, PH, PF, F are the
             Zimbardo Time Perspective Inventory's past-positive,
             past-negative, present-hedonistic, present-fatalistic and future
             factors. 20 items, 1-5.
  * `b*`  -> MPATS (Mobile Phone Addiction Tendency Scale): subscales ATP, HH,
             AE, RT. 16 items, 1-5, which is the instrument's published length.
  * `c*`  -> Self-Control Scale: subscales WS, S, SC, MC, IC, and the file's
             `Self-control total` runs 29-91, inside the 19-95 a 19-item 1-5
             scale allows. 19 items, 1-5.

Item numbering is kept per block (`a1`, `b1`, `c1`) because that is the only
identifier the deposit carries; no published item numbering is asserted.
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

DOI = "10.7717/peerj.16467"
PMCID = "PMC10666608"
MEMBER = "peerj-11-16467-s001.xlsx"
SHEET = "raw data "          # the trailing space is in the deposited file
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "pan_2023_time_perspective": (r"^a\d+$", 20),
    "pan_2023_phone_addiction":  (r"^b\d+$", 16),
    "pan_2023_self_control":     (r"^c\d+$", 19),
}

COV_COLS = {"gender": "cov_gender", "age": "cov_age", "grade": "cov_grade"}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)), sheet_name=SHEET)


def convert() -> None:
    raw = fetch()
    # `b8` appears twice in the deposited header; pandas renames the second to
    # `b8.1`. Positionally it is b9 -- b10..b16 follow it and b9 is otherwise
    # absent from an unbroken run -- so it is restored rather than dropped.
    raw = raw.rename(columns={"b8.1": "b9", "number": "id"})

    present = {s: d for s, d in COV_COLS.items() if s in raw.columns}
    cov = raw[["id"] + list(present)].rename(columns=present)
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (pattern, n_expected) in SCALES.items():
        item_cols = [c for c in raw.columns if re.match(pattern, str(c))]
        assert len(item_cols) == n_expected, (table, len(item_cols))
        wide = raw[["id"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(1, 5).all(), table
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
