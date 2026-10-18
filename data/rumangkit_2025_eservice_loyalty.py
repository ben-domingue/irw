"""E-service quality, customer experience, satisfaction, WOM and loyalty.

Source: https://zenodo.org/records/16009389
DOI: 10.5281/zenodo.16009389
Data: 54_Ferdinand et al_ICOBIRD_2025.xlsx (222 respondents x 29 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped. The workbook's single sheet carries positional codes
  only (ESQ1 .. EDU1) with no stem, and the deposit ships no codebook or
  questionnaire. The constructs are standard marketing scales whose wording
  would have to come from the ICOBIRD paper, which the record does not link.

Five blocks, all 1-5, one table each:

  esq   10 items  e-service quality
  cex    5 items  customer experience
  csat   5 items  customer satisfaction
  wom    4 items  positive word of mouth
  cloy   4 items  customer loyalty

`EDU1` is a single education question, not an item of any of the five blocks,
so it ships as cov_education.

RIGHTS: none of these five blocks matches a register row, and all are named
third-party marketing constructs whose published wording is not in the deposit.
The response table ships because the codes are positional and no item text is
shipped -- BATCH_LOG 2026-10-18i's ProQOL reasoning. Nothing is flagged as a
new register-row request because the deposit does not identify which published
scale each block came from.
"""
import os

import pandas as pd

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402
_RAW_BASE = _Path(__file__).resolve().parent.parent / \
    "automated_finding" / "runs" / "raw"

RAW = os.environ.get(
    "RUMANGKIT_ESQ_RAW",
    str(_RAW_BASE / "54_Ferdinand_et_al_ICOBIRD_2025.xlsx"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {
    "esq":  [f"ESQ{i}" for i in range(1, 11)],
    "cex":  [f"CEX{i}" for i in range(1, 6)],
    "csat": [f"CSAT{i}" for i in range(1, 6)],
    "wom":  [f"WOM{i}" for i in range(1, 5)],
    "cloy": [f"CLOY{i}" for i in range(1, 5)],
}
SCALE = {1, 2, 3, 4, 5}


def main():
    d = pd.read_excel(RAW)
    d.columns = [str(c).strip() for c in d.columns]
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")
    used = {"EDU1"}
    for cols in SCALES.values():
        used |= set(cols)
    unaccounted = [c for c in d.columns if c not in used]
    for c in unaccounted:
        print(f"  UNACCOUNTED {c!r}")
    assert not unaccounted
    print("  EDU1 -> cov_education (a single question, not a scale item)")

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()
    for name, cols in SCALES.items():
        assert all(c in d.columns for c in cols), name
        long = d.melt(id_vars=["id", "EDU1"], value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - SCALE
            assert not bad, f"{name}/{it}: {sorted(bad)}"
        assert long["id"].nunique() >= 100 and long["item"].nunique() > 1
        long = long.rename(columns={"EDU1": "cov_education"})
        table = f"rumangkit_2025_{name}"
        assert table not in written
        written.add(table)
        # The shared checks, which the script's own assertions are not
        # (irw_validate.contract `no_validator`). Fails block; the
        # warnings here are legitimate and are printed.
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, _fails
        for _c in _checks:
            if _c.status == "warn":
                print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
        long[["id", "item", "resp", "cov_education"]].to_csv(
            os.path.join(OUT, f"{table}.csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
