#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.6g7j6 (Zenodo mirror: https://zenodo.org/records/5011627)
# DOI: 10.1371/journal.pone.0172040
#   Dishman, R. K., Dowda, M., McIver, K. L., Saunders, R. P., & Pate, R. R. (2017).
#   "Naturally-occurring changes in social-cognitive factors modify change in physical
#   activity during early adolescence", PLOS ONE 12(2): e0172040.
# Data: Dryad 10.5061/dryad.6g7j6, "TRACK COHORT 857 PLOS ONE short.csv": 857 children
#       (TRACK cohort, South Carolina) x 219 columns, one row per child, three annual
#       waves side by side (5th grade: no suffix; 6th: suffix "b"; 7th: suffix "c";
#       case varies, e.g. MALEADb, r8b). "README_for_TRACK COHORT 857 PLOS ONE
#       short.pdf" is the SPSS variable view: labels truncated to ~40 characters, no
#       value labels, missing = 999.
# License: CC0 1.0 (Dryad record).
#
# Item text: not shipped. Levels checked: the CSV has no labels; the README's variable
#   labels are cut at ~40 characters ("I can be physically active during my fre"), and
#   there are no value labels. Full wording is in the TRACK instruments cited by the
#   paper.
#
# Tables (wave = 1, 2, 3 for grades 5, 6, 7; id = row order; item codes are the wave-1
#   names). Blocks from the README labels; ranges as observed and uniform within block:
#   dishman_2017_self_efficacy      SE1-8                        1-4  "I can be physically
#                                                                     active ..." etc.
#   dishman_2017_barriers           B3, B5, B8, B9, B10          1-4  "I'm chosen last for
#                                                                     teams", "I might get
#                                                                     hurt or sore", ...
#   dishman_2017_motives            R2, R7, R16, R8, R12, R25,   1-4  "Because it's fun",
#                                   R31                               "Because my friends
#                                                                     want me to", ...
#   dishman_2017_parent_support     Maleen..Malehl, FeMaleen..   1-5  "During a normal week,
#                                   FeMalehl (10)                     how often does he/she
#                                                                     ..." (male and female
#                                                                     adult; 999 where the
#                                                                     child reported no such
#                                                                     adult)
#   dishman_2017_peer_support       Peerenc, Peerwith, Peertell  1-5
#   dishman_2017_neighborhood       E1-5, E8-10, parkclos        1-4  perceived neighbourhood
#                                                                     environment
# Skipped: school / middle-school labels (wave-varying), grade, the per-wave repeats of
#   gender/ethnicity/race, Malead/Femalead (routing: is there an adult male/female),
#   bmi, BMIZ and the accelerometer summaries (tothours*, totlight*, totmvpa*; measured
#   outcomes, not item responses), age6/age7 (later-wave ages), M5-M7 (maturity, not in
#   the README) and PCTPOVERTY (not in the README).
# Covariates (wave 1): cov_gender (1/2), cov_hispanic (ethnic 1/2), cov_race1 (code),
#   cov_race_group (nrace2: 1 non-Hispanic black, 2 non-Hispanic white, 3 Hispanic,
#   4 other, per its label), cov_parent_education (Q78), cov_age_grade5 (age5). Codes as in the file; 999 ->
#   missing.

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "dishman_2017"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/5011627/files/"
       "TRACK%20COHORT%20857%20PLOS%20ONE%20short.csv/content")

TABLES = {
    "dishman_2017_self_efficacy": ([f"SE{i}" for i in range(1, 9)], range(1, 5)),
    "dishman_2017_barriers": (["B3", "B5", "B8", "B9", "B10"], range(1, 5)),
    "dishman_2017_motives": (["R2", "R7", "R16", "R8", "R12", "R25", "R31"], range(1, 5)),
    "dishman_2017_parent_support": (["Maleen", "Malewi", "Maletr", "Malewa", "Malehl",
                                     "FeMaleen", "FeMalewi", "FeMaletr", "FeMalewa",
                                     "FeMalehl"], range(1, 6)),
    "dishman_2017_peer_support": (["Peerenc", "Peerwith", "Peertell"], range(1, 6)),
    "dishman_2017_neighborhood": (["E1", "E2", "E3", "E4", "E5", "E8", "E9", "E10",
                                   "parkclos"], range(1, 5)),
}
COVS = {"gender": "cov_gender", "ethnic": "cov_hispanic", "race1": "cov_race1",
        "nrace2": "cov_race_group", "Q78": "cov_parent_education", "age5": "cov_age_grade5"}
SUFFIX = {1: "", 2: "b", 3: "c"}


def fetch() -> Path:
    p = RAW_DIR / "data.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    assert d.shape == (857, 219), d.shape
    lower = {c.lower(): c for c in d.columns}
    assert len(lower) == len(d.columns)
    col = {}  # (item, wave) -> source column
    for its, _ in TABLES.values():
        for it in its:
            for w, s in SUFFIX.items():
                col[(it, w)] = lower[(it + s).lower()]
    used = set(col.values()) | set(COVS)
    skipped = [c for c in d.columns if c not in used]
    pat = re.compile(r"^(school|mschool[bc]|grade[bc]|gender[bc]|ethnic[bc]|race1[bc]|"
                     r"nrace2[bc]|q78[bc]|(fe)?malead[bc]?|parkclos_never|bmi[bc]?|bmiz[bc]?|"
                     r"tot(hours|light|mvpa)[2-7][bc]?|age[67]|m[567]|pctpoverty)$", re.I)
    assert all(pat.match(c) for c in skipped), [c for c in skipped if not pat.match(c)]
    print(f"  skip {len(skipped)} columns: school/grade labels, wave repeats of demographics,"
          " Malead/Femalead routing, bmi/BMIZ, accelerometer summaries, age6/7, M5-7 (maturity),"
          " PCTPOVERTY (undocumented)")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].where(d[c] != 999)
        if c != "cov_age_grade5":
            d[c] = d[c].astype("Int64")
    d["cov_age_grade5"] = d["cov_age_grade5"].round(2)  # decimal years
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        frames = []
        for w in SUFFIX:
            cmap = {col[(it, w)]: it for it in its}
            m = d[["id"] + covs + list(cmap)].rename(columns=cmap).melt(
                id_vars=["id"] + covs, var_name="item", value_name="resp")
            m["wave"] = w
            frames.append(m)
        t = pd.concat(frames)
        t = t[t["resp"].notna() & (t["resp"] != 999)]
        assert t["resp"].isin(list(rng)).all(), (name, sorted(t["resp"].unique()))
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
        t = t.reset_index(drop=True)
        assert not t.duplicated(["id", "item", "wave"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn" and c.name != "dup_id_item":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()} "
              f"ids/wave={t.groupby('wave')['id'].nunique().to_dict()}")


if __name__ == "__main__":
    main()
