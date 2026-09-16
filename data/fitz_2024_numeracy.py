"""Fitz & Kim (2024), objective numeracy and framing effects in decision-making
under risk -- Scientific Reports 14, CC BY 4.0.

The article is CC BY; the data are deposited separately at Harvard Dataverse
(doi:10.7910/DVN/MMOGJI) and reached from the paper's Data Availability
statement. Two tables:

  * `fitz_2024_polknow`  -- 6 political knowledge items, already 0/1 in the
    deposit.
  * `fitz_2024_numeracy` -- 11 objective numeracy items, 0/1.

The numeracy items are free-text in the deposit: `numeracy1` holds answers like
"50%", "half the time", "about 500". Scoring them is not a judgment call made
here -- the authors' own replication .do file enumerates, item by item, every
string they counted as correct, and this script parses that file at run time
and applies it, so the scoring is the published one rather than a
reimplementation. `numeracy4` and `numeracy5` are multiple choice and the .do
recodes them by option number (3 and 2 correct respectively); those two rules
are transcribed below because they are two lines rather than a list.

One deliberate difference from the authors' Stata. Their `recode nN (1=1)
(nonmiss=0) (miss=0)` scores a BLANK response as incorrect. A blank is a
non-response, not a wrong answer, so blanks are dropped here instead. That
affects 14-33 responses per item out of 2,813.

`resp_raw` carries the original free-text answer, which `resp` loses.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.1038/s41598-024-61099-y"
DATA_DOI = "10.7910/DVN/MMOGJI"
DATAVERSE = "https://dataverse.harvard.edu/api/access/datafile/{fid}"
DATA_FILE, DO_FILE = 10172169, 10172168
UA = {"User-Agent": "irw-batch/1.0 (research)"}

PK_ITEMS = [f"pk{i}" for i in range(1, 7)]
# From the .do file: `recode num4x (1=0) (2=0) (3=1)`, `recode num5x (2=1)`.
MC_CORRECT = {"numeracy4": 3, "numeracy5": 2}

COV_COLS = {"gender": "cov_gender", "age_1": "cov_age", "education": "cov_education",
            "income": "cov_income", "race": "cov_race", "ideology": "cov_ideology"}

##  // replace n1x = "1" if numeracy1 == "50% of the time"
KEY_RE = re.compile(
    r'replace\s+n\d+[ab]?x\s*=\s*"1"\s*if\s+(numeracy\d+[ab]?)\s*==\s*"(.*?)"\s*$',
    re.M)


def _get(fid: int) -> bytes:
    r = requests.get(DATAVERSE.format(fid=fid), headers=UA, timeout=180)
    r.raise_for_status()
    return r.content


def correct_strings() -> dict:
    do = _get(DO_FILE).decode("utf-8", errors="replace")
    keys: dict = {}
    for item, value in KEY_RE.findall(do):
        keys.setdefault(item, set()).add(value)
    assert len(keys) == 9, sorted(keys)      # 1,2,3,6,7,8a,8b,9,10
    return keys


def convert() -> None:
    raw = pd.read_csv(io.BytesIO(_get(DATA_FILE)), sep="\t",
                      low_memory=False, dtype=str)
    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)

    cov = raw[["id"] + [c for c in COV_COLS if c in raw.columns]].rename(columns=COV_COLS)
    cov_cols = [c for c in cov.columns if c != "id"]

    keys = correct_strings()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- political knowledge: already scored in the deposit
    pk = raw[["id"] + PK_ITEMS].merge(cov, on="id").melt(
        id_vars=["id"] + cov_cols, value_vars=PK_ITEMS,
        var_name="item", value_name="resp")
    pk["resp"] = pd.to_numeric(pk["resp"], errors="coerce")
    pk = pk.dropna(subset=["resp"])
    pk["resp"] = pk["resp"].astype(int)
    _emit("fitz_2024_polknow", pk[["id", "item", "resp"] + cov_cols], cov_cols, (0, 1))

    # --- numeracy: score free text by the authors' key, MC by option number
    rows = []
    for item in list(keys) + list(MC_CORRECT):
        v = raw[item].fillna("")
        blank = v.str.strip() == ""
        if item in MC_CORRECT:
            scored = (pd.to_numeric(v, errors="coerce") == MC_CORRECT[item]).astype(int)
        else:
            scored = v.isin(keys[item]).astype(int)
        rows.append(pd.DataFrame({
            "id": raw["id"], "item": item,
            "resp": scored.where(~blank), "resp_raw": v.where(~blank)}))
    num = pd.concat(rows, ignore_index=True).dropna(subset=["resp"])
    num["resp"] = num["resp"].astype(int)
    num = num.merge(cov, on="id")
    _emit("fitz_2024_numeracy",
          num[["id", "item", "resp", "resp_raw"] + cov_cols], cov_cols, (0, 1))


def _emit(table: str, long: pd.DataFrame, cov_cols: list, bounds: tuple) -> None:
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    lo, hi = bounds
    assert long["resp"].between(lo, hi).all(), table
    assert not long.duplicated(["id", "item"]).any(), table
    assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]
    long.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} mean_resp={long['resp'].mean():.3f}")


if __name__ == "__main__":
    convert()
