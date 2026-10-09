#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/Q9SNRD
# DOI: 10.7910/DVN/Q9SNRD (dataset; the record cites no paper)
#   chen, cthomas (2026). The associations between loneliness and social anxiety:
#   mediating role of smartphone addiction and moderating role of university clubs
#   [Data set]. Harvard Dataverse.
# Data: "loneliness-20260725-ENG.xlsx" (file 14097203), Sheet1 -- 243 university students
#       x serial number, five background codes, 34 item columns whose headers are the
#       English item stems prefixed by questionnaire number ("6.1 In class, I get
#       distracted ...", "Part 2. 7.1 UCLA SCALE Do you often feel like you lack
#       friends?"), and a total. Part 1 (6.x) mobile phone addiction, Part 2 (7.x) UCLA
#       loneliness, Part 3 (8.x) social anxiety, Part 4 (9.x) club participation -- the
#       record's four variables.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The stems are in the xlsx headers (no value labels; anchors
#   undocumented), but the file is an English rendering ("-ENG") of a questionnaire
#   administered in Chinese, so shipping it would be a translated_substitute fallback
#   with an unconfirmed translation source; the administered Chinese wording is not
#   deposited. The stems are recoverable from the headers when wanted.
#
# Item codes: q<part>_<k> from each header's leading "<part>.<k>" (reversible; the header
#   text is the stem).
# Tables (as stored; reverse-worded items such as q8_3, q8_8, q8_13 kept as worded):
#   chen_2026_clubs_phone_addiction  q6_1-q6_7, 1-5
#   chen_2026_clubs_ucla_loneliness  q7_1-q7_7, 1-4
#   chen_2026_clubs_social_anxiety   q8_1-q8_13, 1-5
#   chen_2026_clubs_participation    q9_1-q9_7, 1-5
#   The clubs_ infix keeps these apart from the published chen_2026_* tables of the same
#   author's other deposit (DVN/QS5D8C: chen_2026_social_anxiety, 195 students, 11 items).
# Skipped: 总分 (a total that matches no plain or reverse-keyed sum of the items).
# Covariates (codes as stored, undocumented): cov_gender, cov_grade, cov_residence,
#   cov_major, cov_only_child.
# id: Serial number (unique 1-243).

import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "q9snrd"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/14097203?format=original"
P = "chen_2026_clubs_"
PARTS = {"6": ("phone_addiction", 7, range(1, 6)), "7": ("ucla_loneliness", 7, range(1, 5)),
         "8": ("social_anxiety", 13, range(1, 6)), "9": ("participation", 7, range(1, 6))}
COVS = {"1. Gende": "cov_gender", "2. Grade": "cov_grade", "3. Residence": "cov_residence",
        "4. Major": "cov_major", "5. Only child": "cov_only_child"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (243, 41) and d["Serial number"].is_unique
    code = {}
    for c in d.columns:
        m = re.match(r"(?:Part\s*\d\.\s*)?(\d)\.(\d+)\s", c)
        if m:
            code[c] = f"q{m.group(1)}_{m.group(2)}"
    assert len(code) == 34 and len(set(code.values())) == 34
    accounted = {"Serial number", "总分"} | set(COVS) | set(code)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    print("  [skip] 总分: total, matches no item sum")
    d = d.rename(columns={"Serial number": "id", **COVS, **code})
    covs = list(COVS.values())
    names = [P + v[0] for v in PARTS.values()]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for part, (suf, k, rng) in PARTS.items():
        name = P + suf
        its = [f"q{part}_{i}" for i in range(1, k + 1)]
        assert set(its) <= set(d.columns)
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[list(code.values())].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
