#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/3cgh2fsgn4/4
# DOI: 10.17632/3cgh2fsgn4.4
#   Agusta, E. (2023). Dataset of Intrinsic Motivation Students while Online
#   Learning in South Sumatera, Indonesia [Dataset]. Mendeley Data.
# Data: two workbooks, 1,037 and 599 students, the same 22-item instrument on
#   a 1-7 scale administered to two samples.
# License: CC BY 4.0 (verified on the Mendeley record and DataCite, 2026-10-19).
# Item text: NOT shipped. The workbooks carry no wording at all -- the item
#   columns are numbered 1-22 in a header row and nothing names them, so the
#   stems are in the paper only.
#
# THE HEADER IS SPLIT ACROSS TWO ROWS, which is what deferred this deposit.
#   Row 0 holds the section names ("Identity", "Gender", ..., "Items") and row
#   1 holds the item numbers 1-22 under the "Items" cell; a default read makes
#   the first item column "Items" and the rest "Unnamed: 11".."Unnamed: 31".
#   This script reads with no header and takes the item columns as the ones
#   whose ROW 1 cell is a number, asserting there are 22 of them and that they
#   run 1-22 in order -- so the mapping comes from the file, not from a
#   position guess. The two workbooks have different leading columns (the
#   599-row one adds "No" and drops "Faculty"), which is why the item block is
#   found rather than sliced at a fixed offset.
#
# ONE table: the two samples merged under `cov_study`, because the instrument
#   and the scale are identical -- 22 items, 1-7, numbered the same way in both
#   files. 1,635 respondents, 35,970 responses. One row of the 1,037 workbook
#   holds demographics and no item response at all and is dropped; no row is
#   partially answered, which the script asserts.
#
# NOT SHIPPED: the identity columns (an opaque 4-column block in the 1,037
#   file, 5 in the 599 one, all small integers the deposit never names) and
#   `No`, a row counter.
#
# id: the row index across the merged file, 1-1,636. Neither workbook carries
#   a respondent id, and the two samples are different people, so ids do not
#   collide.
# Covariates: cov_study (1 = the 1,037 sample, 2 = the 599 sample), cov_gender,
#   cov_age, cov_semester, cov_level (bachelor/postgraduate) and cov_faculty,
#   which only the first workbook records and is therefore missing for the
#   second sample.
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
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "3cgh2fsgn4" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATASET = "3cgh2fsgn4"
FILES = {1: ("Dataset Motivation 1037.xlsx", 1037),
         2: ("Dataset Motivation 559.xlsx", 599)}
N_ITEMS = 22
SCALE = set(range(1, 8))
COV_NAMES = {"Gender": "cov_gender", "Age": "cov_age",
             "Semester": "cov_semester", "Faculty": "cov_faculty",
             "Bachelor/Postgraduate": "cov_level"}
TABLE = "agusta_2023_intrinsic_motivation"


def fetch(name: str) -> Path:
    p = RAW_DIR / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get("https://data.mendeley.com/public-api/datasets/"
                         f"{DATASET}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"]
               if f["filename"] == name][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def read_one(path: Path, study: int, n_rows: int) -> pd.DataFrame:
    head = pd.read_excel(path, header=None, nrows=2)
    body = pd.read_excel(path, header=None, skiprows=2)
    assert len(body) == n_rows, (path.name, len(body))

    # The item columns are the ones numbered in row 1; the section names are
    # in row 0. Both come from the file.
    numbered = [(i, int(v)) for i, v in head.iloc[1].items()
                if pd.notna(v) and float(v).is_integer()]
    assert len(numbered) == N_ITEMS, (path.name, len(numbered))
    assert [n for _, n in numbered] == list(range(1, N_ITEMS + 1)), numbered
    sections = {str(v).strip(): i for i, v in head.iloc[0].items() if pd.notna(v)}
    assert "Items" in sections or "Item" in sections, sections

    out = pd.DataFrame({f"item{n:02d}": pd.to_numeric(body[i])
                        for i, n in numbered})
    for src, dest in COV_NAMES.items():
        if src in sections:
            v = pd.to_numeric(body[sections[src]], errors="coerce")
            out[dest] = v.astype("Int64")
        else:
            out[dest] = pd.Series([pd.NA] * len(out), dtype="Int64")
    out["cov_study"] = study
    return out


def main():
    parts = [read_one(fetch(name), study, n)
             for study, (name, n) in FILES.items()]
    df = pd.concat(parts, ignore_index=True)
    items = [f"item{n:02d}" for n in range(1, N_ITEMS + 1)]
    assert len(df) == sum(n for _, n in FILES.values()) == 1636, len(df)
    # One row of the 1,037 workbook (row 78) carries demographics and no item
    # response at all. Dropped on the all-blank test, not by position, and
    # asserted to be the only one -- a PARTIAL row would be a different
    # problem and must not pass silently.
    blank = df[items].isna().all(axis=1)
    partial = df[items].isna().any(axis=1) & ~blank
    assert not partial.any(), f"{int(partial.sum())} partially answered row(s)"
    assert blank.sum() == 1, blank.sum()
    df = df[~blank].reset_index(drop=True)
    print(f"dropped {int(blank.sum())} row with no item response at all")
    print(f"merged {len(parts)} workbooks on cov_study: "
          f"{[n for _, n in FILES.values()]} respondents, {N_ITEMS} items each")
    print("not shipped: the unnamed identity block and the `No` row counter")

    df["id"] = range(1, len(df) + 1)
    cov_cols = [*COV_NAMES.values(), "cov_study"]
    df["cov_study"] = df["cov_study"].astype("Int64")

    t = (df[["id", *cov_cols, *items]]
         .melt(id_vars=["id", *cov_cols], value_vars=items,
               var_name="item", value_name="resp"))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the 1-7 scale: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 1635 and t["item"].nunique() == N_ITEMS
    assert len(t) == 1635 * N_ITEMS

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:150]}")
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
