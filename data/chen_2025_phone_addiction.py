#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WEY2CA
# DOI: 10.7910/DVN/WEY2CA (dataset; the record cites no paper)
#   chen, cthomas (2025). The study on the relationship between mobile phone addiction
#   and social anxiety in college students: The moderating effects of student club
#   participation [Data set]. Harvard Dataverse.
# Data: "MobilePhobeAddiction-ENG20250123.xlsx" (file 10844461), sheet 復原_工作表1 -- 214
#       college students x ordinal number, five background codes, items 7.1-7.12 (mobile
#       phone addiction), 8.1-8.7 (social anxiety) and 9.1-9.5 (club participation) with
#       English stems as headers, followed by ~30 derived totals, means and centred terms.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. English stems are in the xlsx headers (no value labels), but the
#   file is an English rendering ("-ENG") of a questionnaire administered in Chinese
#   (the sheet name is Traditional Chinese); the administered wording is not deposited.
#
# Item codes: q<part>_<k> from each header's leading "<part>.<k>" (reversible).
# Tables:
#   chen_2025_phone_addiction  q7_1-q7_12, 1-5. Two cells of -2 (one each on q7_6 and
#                              q7_12, against 200+ valid responses per item) are dropped as
#                              entry errors.
#   chen_2025_social_anxiety   q8_1, q8_2, q8_4, q8_6, 1-5 (the four positively worded items).
# Skipped:
#   q8_3, q8_5, q8_7 -- the reverse-worded social-anxiety items are stored on 1-3 only
#     (q8_7 also has two -2s): a lossy recode of a 1-5 response, not the response.
#   q9_1-q9_5 (club participation) -- 0 is meant to mark non-members, but it disagrees with
#     the file's own club-membership column in 39 rows, so which cells are responses is
#     unknown.
#   All derived columns (totals, means, centred and interaction terms).
# Covariates (codes as stored, undocumented): cov_gender, cov_grade, cov_origin,
#   cov_only_child, cov_club (joined a student club, 1/2).
# id: Ordinal number (unique).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "wey2ca"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/10844461?format=original"
P = "chen_2025_"
TABLES = {"phone_addiction": [f"q7_{i}" for i in range(1, 13)],
          "social_anxiety": ["q8_1", "q8_2", "q8_4", "q8_6"]}
SKIP_ITEMS = {"q8_3": "reverse item stored on 1-3 (lossy recode)",
              "q8_5": "reverse item stored on 1-3 (lossy recode)",
              "q8_7": "reverse item stored on 1-3 (lossy recode)",
              **{f"q9_{i}": "club item; 0/non-member coding inconsistent" for i in range(1, 6)}}
COVS = {"Gender": "cov_gender", "Grade": "cov_grade", "Origin": "cov_origin",
        "Whether one is an only child? ": "cov_only_child",
        "Whether or not to join a student club?": "cov_club"}


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
    assert d.shape == (214, 57) and d["Ordinal number"].is_unique
    code = {}
    for c in d.columns:
        m = re.match(r"(\d)\.(\d+)\s", c)
        if m:
            code[c] = f"q{m.group(1)}_{m.group(2)}"
    assert len(code) == 24
    derived = [c for c in d.columns if c not in code and c not in COVS and c != "Ordinal number"]
    assert len(derived) == 27, len(derived)
    print(f"  [skip] {len(derived)} derived columns (totals, means, centred terms)")
    d = d.rename(columns={"Ordinal number": "id", **COVS, **code})
    items = [c for v in TABLES.values() for c in v]
    assert set(items) | set(SKIP_ITEMS) == set(code.values())
    for c, why in SKIP_ITEMS.items():
        print(f"  [skip] {c}: {why}")
    for c in ("q8_3", "q8_5", "q8_7"):
        assert d[c].max() == 3
    bad = d[items] == -2
    assert int(bad.sum().sum()) == 2 and set(bad.columns[bad.any()]) == {"q7_6", "q7_12"}
    d[items] = d[items].mask(bad)
    print("  dropped 2 cells of -2 (q7_6, q7_12)")
    covs = list(COVS.values())
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in its}
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
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
