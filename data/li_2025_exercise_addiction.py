#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/5yrz5r62wz
# DOI: 10.17632/5yrz5r62wz (v1, 10.17632/5yrz5r62wz.1)
#   li, jianye (2025). "Exploring the Interrelationship Between Exercise Addiction and
#   Eating Disorders: The Mediating Roles of Self-Esteem and Body Image
#   Dissatisfaction" [Data set]. Mendeley Data. (Sole contributor on the deposit
#   record; the data file is named "Keqiang Li data.xls".)
# Data: "Keqiang Li data.xls", Sheet1 -- 637 physically active respondents x 55 columns:
#       Gender, Year of birth, a constant survey-year column, Age, then four contiguous
#       item blocks whose headers are the instrument abbreviation + item number:
#       SES-1..SES-10 (Self-Esteem Scale, 1-4), BIS-1..BIS-9 (Body Image Scale, 1-4),
#       EAI-1..EAI-6 (Exercise Addiction Inventory, 1-5), EAT-1..EAT-26 (Eating
#       Attitudes Test-26, 1-6). The deposit description names all four instruments.
#       Sheet2 holds a stray 689-row, all-empty Age column and is ignored.
# License: CC BY 4.0 (the Mendeley Data record's `data_licence` is CC BY 4.0).
#
# Item text: not shipped. The .xls has no labels of any kind (checked both levels that
#   exist for a spreadsheet: there is no variable-label row and no value-label
#   mapping), and the headers are the bare instrument abbreviation plus a number.
#   Where the text actually is: in the four published instruments -- Rosenberg's
#   Self-Esteem Scale, the Body Image Scale, Terry/Szabo's Exercise Addiction
#   Inventory and Garner's EAT-26 -- none reproduced in this deposit.
#
# Item codes: <block>_<position>, the 1-based position of the column inside its block,
#   which is also the number its own header carries for 51 of the 55 columns. Four
#   headers are typos that repeat an earlier number -- "SES1" at position 2,
#   "SES-3.1" at position 5, and (as pandas-deduplicated names) "BIS-3.1" at position 5
#   and "BIS-4.1" at position 6 -- and each is asserted to sit at the position its
#   block's run-length requires, so the mapping stays reversible rather than guessed.
#
# Columns skipped: "Year of birth" (a year, not a date of birth; redundant with the Age
#   column that is carried as cov_age) and the unnamed constant 2020 survey-year
#   column.
# Tables:
#   li_2025_self_esteem          10 items, 1-4
#   li_2025_body_image            9 items, 1-4
#   li_2025_exercise_addiction    6 items, 1-5
#   li_2025_eat26                26 items, 1-6
# id: the file carries no respondent identifier, so id is the 1-based row index; it
#   links a respondent across all four tables.
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s3"
URL = ("https://data.mendeley.com/public-files/datasets/5yrz5r62wz/files/"
       "6d5d9841-3c35-4544-be57-a932cda4a61f/file_downloaded")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

BLOCKS = {
    "li_2025_self_esteem": ("SES", "ses", 10, [1, 2, 3, 4]),
    "li_2025_body_image": ("BIS", "bis", 9, [1, 2, 3, 4]),
    "li_2025_exercise_addiction": ("EAI", "eai", 6, [1, 2, 3, 4, 5]),
    "li_2025_eat26": ("EAT", "eat", 26, [1, 2, 3, 4, 5, 6]),
}
# Headers whose own number is a typo; value is the position the block layout requires.
TYPO_POSITIONS = {"SES1": 2, "SES-3.1": 5, "BIS-3.1": 5, "BIS-4.1": 6}
SKIP = {"Year of birth": "a birth year (not a date of birth); Age is carried instead",
        "Unnamed: 2": "constant 2020 survey-year column"}


def screen_for_pii(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] examined {df.shape[1]} columns, {len(text_cols)} of them string-typed")
    assert df.shape[1] > 0
    pats = [r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", r"\+?\d[\d \-()]{8,}",
            r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}"]
    hits = [(c, p) for c in text_cols for p in pats
            if df[c].dropna().astype(str).str.contains(p, regex=True, na=False).any()]
    assert not hits, hits
    print("[pii] no string columns carrying identifier patterns; 'Year of birth' holds "
          "a 4-digit year only and is dropped")


def block_map(df: pd.DataFrame, prefix: str, short: str, n: int) -> dict[str, str]:
    cols = [c for c in df.columns if str(c).startswith(prefix)]
    assert len(cols) == n, (prefix, len(cols), n)
    out: dict[str, str] = {}
    for pos, c in enumerate(cols, start=1):
        name = str(c)
        if name in TYPO_POSITIONS:
            assert TYPO_POSITIONS[name] == pos, (name, pos)
        else:
            m = re.search(r"(\d+)$", name)
            assert m and int(m.group(1)) == pos, (name, pos)
        out[c] = f"{short}_{pos}"
    assert len(set(out.values())) == n
    return out


def emit(name: str, t: pd.DataFrame, pv: list) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert not t.duplicated(["id", "item"]).any(), name
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3, name
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {name} {c.name}: {c.detail[:160]}")
    rep = irw_validate.validate_frame(t, label=name, profile="upload",
                                      context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, (name, [(f.check, f.message) for f in rep.errors])
    for f in rep.warnings:
        print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
          f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")
    assert df.shape == (637, 55), df.shape
    screen_for_pii(df)

    df = df.copy()
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["Gender"]
    df["cov_age"] = df["Age"]
    cov_cols = ["cov_gender", "cov_age"]
    accounted = {"Gender", "Age"} | set(SKIP)
    for c, why in SKIP.items():
        print(f"[books] skipped {c!r}: {why}")

    tables = {}
    for name, (prefix, short, n, pv) in BLOCKS.items():
        m = block_map(df, prefix, short, n)
        accounted |= set(m)
        long = (df[["id"] + cov_cols + list(m)]
                .rename(columns=m)
                .melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp"))
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all(), name
        tables[name] = (long[["id", "item", "resp"] + cov_cols].reset_index(drop=True), pv)

    leftover = [c for c in df.columns if c not in accounted
                and c not in ("id", *cov_cols)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print(f"[books] {len(accounted)} source columns accounted for "
          f"(2 covariates + 51 items + {len(SKIP)} skipped)")

    assert len(set(tables)) == len(tables)
    for name, (t, pv) in tables.items():
        emit(name, t, pv)


if __name__ == "__main__":
    convert()
