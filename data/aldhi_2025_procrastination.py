#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/cg77typtk4/1
# DOI: 10.17632/cg77typtk4.1
#   Aldhi, I. F., Suhariadi, F., Rahmawati, E., Supriharyanti, E.,
#   Hardaningtyas, D., Sugiarti, R., Abbas, A., & Trihantoyo, S. (2025).
#   Psychometric Dataset on Disorganization, Fear of Failure, Academic
#   Procrastination, and Academic Performance among Indonesian Higher
#   Education Students [Dataset]. Mendeley Data.
# Data: "Data IFA07a 13052025.xlsx" -- 2,111 higher-education students across
#   East and Central Java, surveyed August-December 2024. 19 Likert items,
#   1-5, in four labelled blocks.
# License: CC BY 4.0 (verified on the Mendeley record, 2026-10-20).
# Item text: NOT shipped. The workbook carries bare codes (DIS1..APR4) as its
#   only headers -- no label level exists in .xlsx -- and the deposit ships no
#   codebook. The deposit description names the four constructs but not the
#   stems, and cites no paper DOI. The wording is in the authors' own
#   instrument, which this deposit does not reproduce; that is where it is.
#
# FOUR tables, one per construct block, because the deposit describes four
#   distinct constructs rather than four subscales of one instrument:
#     DIS1-DIS5  Disorganization
#     FOF1-FOF5  Fear of Failure
#     APC1-APC5  Academic Procrastination
#     APR1-APR4  Academic Performance (self-reported, Likert -- these are
#                items, not a grade; no aggregate column is present)
#
# id: the row index. The file carries no respondent identifier at all.
# Covariates: none. The deposit ships items only -- no demographics.
#
# Duplicate response vectors: 8 of 2,111 rows repeat another row exactly.
#   Checked rather than waved through: the repeats are scattered through the
#   file (rows 102/181/516, 334/379, ...), not a contiguous block, and each is
#   a flat straightlining pattern (all 4s on DIS, all 5s on FOF and APC) of
#   the kind that genuinely recurs across respondents. Not a copy-paste
#   artefact, so no row is dropped.
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
    REPO_ROOT / "automated_finding" / "runs" / "mendeley" / "cg77typtk4"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATASET, VERSION, FNAME = "cg77typtk4", 1, "Data IFA07a 13052025.xlsx"
SCALE = set(range(1, 6))
SCALES = [
    ("aldhi_2025_disorganization", [f"DIS{i}" for i in range(1, 6)]),
    ("aldhi_2025_fear_of_failure", [f"FOF{i}" for i in range(1, 6)]),
    ("aldhi_2025_acad_procrastination", [f"APC{i}" for i in range(1, 6)]),
    ("aldhi_2025_acad_performance", [f"APR{i}" for i in range(1, 5)]),
]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        api = (f"https://data.mendeley.com/public-api/datasets/{DATASET}"
               f"/files?folder_id=root&version={VERSION}")
        files = requests.get(api, headers=UA, timeout=120).json()
        url = next(f["content_details"]["download_url"] for f in files
                   if f["filename"] == FNAME)
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch())
    expected = {c for _, cols in SCALES for c in cols}
    assert set(df.columns) == expected, set(df.columns) ^ expected
    assert len(df) == 2111, len(df)
    assert not df.isna().any().any(), "deposit is documented as complete"

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, items in SCALES:
        t = (df[["id", *items]]
             .melt(id_vars=["id"], value_vars=items,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{table}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{table}: resp outside the documented 1-5 scale: {bad}"
        t = t[["id", "item", "resp"]]
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() == 2111
        assert t["item"].nunique() == len(items) >= 2

        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {table}: {c.name}: {c.detail[:150]}")
        report = irw_validate.validate_frame(
            t, label=table, profile="upload",
            context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            [(f.check, f.message) for f in report.errors]

        t.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
