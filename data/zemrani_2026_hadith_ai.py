#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_strong_Raw_Dataset_for_Islamic_Studies_Students_Ability_to_Distinguish_Authentic_Hadiths_from_AI-Generated_Forged_Texts_strong_/34754181
# DOI: 10.6084/m9.figshare.34754181.v2 (data; no paper DOI on the record)
#   Zemrani M (2026). Raw Dataset for: Islamic Studies Students' Ability to
#   Distinguish Authentic Hadiths from AI-Generated Forged Texts. figshare.
# Data: Data_Hadit(134).xlsx (134 x 58), a Google Forms export (Arabic
#   headers): Bachelor of Education students in Islamic Studies, ESEF, Sultan
#   Moulay Slimane University, Morocco.
# License: CC BY 4.0 (figshare record).
# Codebook: none; the record's description gives the structure (quoted below).
#
# Counts: 134 rows = the description's N = 134.
# Tables:
#   zemrani_2026_hadith_discrimination  40 texts, resp 1 = correctly
#       classified. H1-H20 are authentic hadiths, A1-A20 forged texts written by
#       Google Gemini 2.5 "imitating prophetic rhetoric" (description). In the
#       file each cell is 1 = "judged authentic"; the file's score column
#       (21-40) equals sum(H) + sum(1 - A) on every row (asserted), so the A
#       items are scored 1 - cell here, matching the depositor's own scoring.
#       Codes as deposited; the score column is dropped.
#   zemrani_2026_verification_criteria  7 items, 1-5 reliance on textual
#       indicators (1 = do not rely at all .. 5 = rely heavily, per the
#       header): vc1-vc7 in file order.
#   zemrani_2026_ai_verification_attitudes  5 items, 1-5 (header: 1 = strongly
#       agree .. 5 = strongly disagree; kept as deposited): att1-att5 in file
#       order.
#   The Likert headers are "<question> [<indicator or statement>]"; codes are
#   numbered in file order within each block and the bracketed text is checked
#   below, so the code-to-stem tie is in this file.
# id = row index. Covariates: gender, year of study, self-rated hadith
#   expertise, number of hadiths memorised, frequency of AI use (Arabic text
#   categories as deposited).
# Item text: not shipped -- the Arabic stems of the 12 Likert items are in the
#   headers and the 40 discrimination texts are not in the deposit.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/70530240"
DISC = [f"{p}{i}" for i in range(1, 21) for p in ("H", "A")]
VC_BRACKETS = ["سلامة الأسلوب اللغوي والبياني", "وضوح السند أو الإسناد",
               "توافق المعنى مع مقاصد الشريعة", "شهرة النص في المصادر الحديثية",
               "سلامة التركيب النحوي", "الإحساس بالبلاغة النبوية الخاصة",
               "وجود مبالغات أو أحكام غير منسجمة"]


def melt(d, cols, covs, allowed, table):
    long = d[["id"] + cols + covs].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp"
    ).dropna(subset=["resp"])
    assert not set(long["resp"]) - allowed, table
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    checks = run_qc(long, permitted_values={c: allowed for c in cols})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {table} {c.name}: {c.detail[:120]}")
    long.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"[write] {table}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (134, 58), d.shape
    cols = list(d.columns)
    score, covsrc = cols[0], cols[1:6]
    assert set(cols[6:46]) == set(DISC)
    H = [c for c in DISC if c.startswith("H")]
    A = [c for c in DISC if c.startswith("A")]
    assert (d[H].sum(axis=1) + (1 - d[A]).sum(axis=1) == d[score]).all()
    d[A] = 1 - d[A]  # 1 = correctly identified as forged
    vc, att = cols[46:53], cols[53:58]
    for c, b in zip(vc, VC_BRACKETS):
        assert re.search(r"\[(.*)\]", c).group(1).strip() == b, c
    assert all("1=أوافق بشدة" in c for c in att)
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    covmap = dict(zip(covsrc, ["cov_gender", "cov_year", "cov_hadith_expertise",
                               "cov_hadiths_memorised", "cov_ai_use"]))
    d = d.rename(columns={**covmap, **{c: f"vc{i}" for i, c in enumerate(vc, 1)},
                          **{c: f"att{i}" for i, c in enumerate(att, 1)}})
    covs = list(covmap.values())
    for c in covs:
        d[c] = d[c].astype(str).str.strip()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    melt(d, DISC, covs, {0, 1}, "zemrani_2026_hadith_discrimination")
    melt(d, [f"vc{i}" for i in range(1, 8)], covs, set(range(1, 6)),
         "zemrani_2026_verification_criteria")
    melt(d, [f"att{i}" for i in range(1, 6)], covs, set(range(1, 6)),
         "zemrani_2026_ai_verification_attitudes")


if __name__ == "__main__":
    main()
