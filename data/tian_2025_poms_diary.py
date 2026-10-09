#!/usr/bin/env python3
# Source: https://zenodo.org/records/17874627
# DOI: 10.5281/zenodo.17874627 (dataset; the record has no description and links no paper)
#   Tian, Vanida (2025). Mood Diary Dataset - Profile of Mood State [Data set]. Zenodo.
# Data: "Mood Diary Dataset.xlsx", sheet "Mood diary" -- 123 participants (P01..P123) x 7
#       daily diaries; per day D<k>MD1..D<k>MD66 (MD22 and MD54 suffixed _R), six subscale
#       scores D<k>MD_Anger/_Confusion/_Depression/_Fatigue/_Tension/_Vigor and a total
#       D<k>_Mood; 99999 = missing.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Spreadsheet headers are positional (MD1..MD66) with no labels at
#   either level, and the record deposits no instrument. The wording is the 65-item POMS
#   (McNair, Lorr & Droppleman), which is commercially published (MHS); not deposited.
#
# How the items were identified: MD1-MD65 are the 65 POMS adjectives in the standard order,
#   0-4. Regressing each deposited subscale score on the 66 columns (841 complete
#   person-days) reproduces it EXACTLY (max residual 0) with 0/1 weights equal to the
#   published POMS key -- Tension 2,10,16,20,22R,26,27,34,41; Depression
#   5,9,14,18,21,23,32,35,36,44,45,48,58,61,62; Anger 3,12,17,24,31,33,39,42,47,52,53,57;
#   Vigor 7,15,19,38,51,56,60,63; Fatigue 4,11,29,40,46,49,65; Confusion
#   8,28,37,50,54R,59,64 -- and D<k>_Mood = the five negative subscales minus Vigor. The
#   script re-derives and asserts this. MD22_R ("relaxed") and MD54_R ("efficient") are
#   stored reverse-scored (4 - x), which is how the key adds them; kept as stored.
#
# Tables (one per POMS subscale; wave = diary day 1-7; 0-4):
#   tian_2025_poms_tension, _depression, _anger, _vigor, _fatigue, _confusion
# Skipped: MD1, MD6, MD13, MD25, MD30, MD43, MD55 (the seven POMS adjectives no subscale
#   scores); MD66 (a 0-10 rating outside the POMS, undocumented); the subscale and total
#   scores.
# id: the participant number from Participant_ID (P01 -> 1).

import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "z17874627"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/17874627/files/Mood%20Diary%20Dataset.xlsx/content"
KEY = {"Tension": [2, 10, 16, 20, "22_R", 26, 27, 34, 41],
       "Depression": [5, 9, 14, 18, 21, 23, 32, 35, 36, 44, 45, 48, 58, 61, 62],
       "Anger": [3, 12, 17, 24, 31, 33, 39, 42, 47, 52, 53, 57],
       "Vigor": [7, 15, 19, 38, 51, 56, 60, 63],
       "Fatigue": [4, 11, 29, 40, 46, 49, 65],
       "Confusion": [8, 28, 37, 50, "54_R", 59, 64]}
KEY = {s: [f"MD{i}" for i in v] for s, v in KEY.items()}
UNSCORED = [f"MD{i}" for i in (1, 6, 13, 25, 30, 43, 55)]
SUBS = ["Anger", "Confusion", "Depression", "Fatigue", "Tension", "Vigor"]


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
    assert d.shape == (123, 512) and d["Participant_ID"].is_unique
    items = [f"MD{i}" if i not in (22, 54) else f"MD{i}_R" for i in range(1, 67)]
    frames = []
    for day in range(1, 8):
        cols = [f"D{day}{c}" for c in items] + [f"D{day}MD_{s}" for s in SUBS] + [f"D{day}_Mood"]
        x = d[["Participant_ID"] + cols].copy()
        x.columns = ["pid"] + items + [f"MD_{s}" for s in SUBS] + ["Mood"]
        x["wave"] = day
        frames.append(x)
    used = {"Participant_ID"} | {c for day in range(1, 8) for c in
                                 [f"D{day}{i}" for i in items] + [f"D{day}MD_{s}" for s in SUBS]
                                 + [f"D{day}_Mood"]}
    assert used == set(d.columns), set(d.columns) ^ used
    L = pd.concat(frames, ignore_index=True).replace(99999, np.nan)
    # the published key reproduces every deposited subscale score exactly
    cc = L.dropna(subset=items)
    for s in SUBS:
        X = np.c_[np.ones(len(cc)), cc[items].values]
        b = np.linalg.lstsq(X, cc[f"MD_{s}"].values, rcond=None)[0]
        found = sorted(items[i] for i in range(len(items)) if abs(b[i + 1]) > 0.5)
        assert found == sorted(KEY[s]), (s, found)
        assert np.allclose(b[[0] + [i + 1 for i in range(len(items)) if items[i] not in KEY[s]]], 0,
                           atol=1e-6) and np.allclose(cc[KEY[s]].sum(axis=1), cc[f"MD_{s}"])
    neg = sum(cc[f"MD_{s}"] for s in SUBS if s != "Vigor") - cc["MD_Vigor"]
    assert np.allclose(neg, cc["Mood"])
    print(f"  POMS key verified on {len(cc)} complete person-days")
    for c in UNSCORED:
        print(f"  [skip] {c}: POMS adjective outside every subscale")
    print("  [skip] MD66: 0-10 rating outside the POMS, undocumented")
    assert L["MD66"].max() == 10 and L[[c for c in items if c != "MD66"]].max().max() == 4
    assert L["pid"].str.fullmatch(r"P\d+").all()
    L["id"] = L["pid"].str[1:].astype(int)
    names = [f"tian_2025_poms_{s.lower()}" for s in KEY]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for s, its in KEY.items():
        name = f"tian_2025_poms_{s.lower()}"
        t = L.melt(id_vars=["id", "wave"], value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(0, 5)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "wave"]].sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item", "wave"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(0, 5)) for i in its}
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
    scored = [c for v in KEY.values() for c in v]
    assert total == int(L[scored].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
