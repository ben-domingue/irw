#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/32414913
# DOI: 10.6084/m9.figshare.32414913
#   Kembara, M. D. (2026). Anonymised Survey Dataset: Student Perceptions of
#   Wellbeing and Structural Civic Agency in Higher Education -- Beyond Active
#   Citizenship (CSE-26-0013) [Dataset]. figshare.
# Data: "CSE_Appendix_Data_Statistics.xlsx", sheet "A1. Raw Data" -- 392
#   Indonesian undergraduate and postgraduate students, a 6-item
#   author-written questionnaire scored 1-5, administered in Indonesian.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: extraction is SOLVED but not shipped in this batch. Sheet
#   "A6. Survey Instrument" gives each item's Indonesian stem, the author's own
#   English translation and the 1-5 anchors, and names the dimension each item
#   measures. The items are the study's own (six single-item dimensions:
#   structural powerlessness, pedagogical stagnation, civic self-efficacy,
#   structural civic competence, expression-construction gap, civic knowledge
#   valuation) -- so unlike the rest of this batch there is no third-party
#   instrument and nothing for the rights register to rule on. It is held only
#   because this batch ships no item text at all; this is the one table in it
#   that could ship item text immediately. See TODO.md.
#
# OFFSET HEADER: rows 1-2 are the appendix title and the study code; the
#   header is row 3. Read with header=2.
#
# PII: none. The open-ended column holds the students' own civic-action plans
#   and was scanned for emails, Indonesian mobile numbers, +62 numbers,
#   student-number markers (NIM) and self-naming phrases -- no hits. It is not
#   shipped either way (free text is not a response).
#
# ONE table, 392 respondents:
#   kembara_2026_civic_agency   Q1-Q6, 1-5 (6 items)
# id: the deposit's own No. serial (1-392).
# Covariates: cov_level (S1 undergraduate / S2 postgraduate) and
#   cov_programme (the study programme, as the source's own label).
# Dropped: Total and Mean (composites), the open-ended response, its length,
#   and the author's "Complexity" coding of it.
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
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "32414913" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 32414913, "CSE_Appendix_Data_Statistics.xlsx"
NAME, SHEET = "kembara_2026_civic_agency", "A1. Raw Data"
SCALE = set(range(1, 6))

ITEMS = [f"Q{i}" for i in range(1, 7)]
COVS = {"Level": "cov_level", "Prodi/Programme": "cov_programme"}
DROPPED = ["Total", "Mean", "Open-Ended (truncated)", "Response Length",
           "Complexity"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch(), sheet_name=SHEET, header=2)
    known = set(ITEMS + list(COVS) + DROPPED + ["No."])
    for c in known:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns if c not in known]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"dropped, composites and free text: {DROPPED}")

    df = df[pd.to_numeric(df["No."], errors="coerce").notna()]
    assert len(df) == 392, len(df)
    df = df.rename(columns={"No.": "id", **COVS})
    df["id"] = pd.to_numeric(df["id"]).astype(int)
    assert df["id"].is_unique
    cov_cols = list(COVS.values())

    t = (df[["id", *cov_cols, *ITEMS]]
         .melt(id_vars=["id", *cov_cols], value_vars=ITEMS,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 1-5 scale: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
