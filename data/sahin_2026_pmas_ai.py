#!/usr/bin/env python3
# Source: https://zenodo.org/records/21236702
# DOI: 10.1080/10447318.2026.2719186
#   Sahin, M., Gultekin, M. H., Erdogdu, F., & Cesur, S. (2026).
#   "Psychometric Evaluation of the Turkish Version of the Perceived Moral
#   Agency Scale for Artificial Intelligence." International Journal of
#   Human-Computer Interaction. (Paper not read: tandfonline serves a bot
#   wall; Unpaywall lists only this Zenodo deposit as its OA copy.)
#   Deposit: Sahin, M., Gultekin, M. H., Erdogdu, F., & sevim (2026). Zenodo.
# Data: Zenodo 21236702 -- Study1.sav (203 rows x 98 columns), study2.sav
#       (480 x 14), test_retest_data.sav (52 x 28). Turkish adults.
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. Both label levels checked in all three files:
#   variable labels exist only on the FIRST item of each block, naming the
#   construct ("morality", "dependency", "social desirability",
#   "satisfaction", "negative_attitude", "positive_attitude",
#   "mindattribution", "conspiracy"); no value labels on any item (only on
#   gender/education/income). Item stems are in the paper (bot-walled) and
#   the published instruments (PMAS: Banks 2019, Computers in Human Behavior).
#
# Tables. Scale identities come from the variable labels and the deposit
# title only; the paper could not be read, so NO permitted-value set is
# asserted for any table (values are checked to be whole numbers only), and
# the observed ranges below are observations, not documentation.
#   sahin_2026_pmas                10 items  Perceived Moral Agency Scale for
#                                  AI, Turkish: m1-m6 morality, d1-d4
#                                  dependency. Study 1 and Study 2 merged
#                                  (cov_study). Study 1's morality1-6 ->
#                                  m1-m6 and dependency7-10 -> d1-d4 (same
#                                  order; Study 2's own names kept as codes).
#                                  Observed 1-7. morality_altboyut and
#                                  dependency_altboyut equal the Study 1
#                                  block sums (asserted).
#   sahin_2026_social_desirability 13 items (begenirlik1-13), observed 1/2
#                                  (13 binary items, consistent with a
#                                  Marlowe-Crowne short form; unverified).
#   sahin_2026_life_satisfaction    5 items (doyum1-5), observed 1-5.
#   sahin_2026_ai_attitudes        12 items: olumsuz1-7 (negative attitude)
#                                  and olumlu1-5 (positive attitude) toward
#                                  AI, observed 1-5; no reverse-coded copies.
#   sahin_2026_mind_attribution    17 items (isitme .. secimyapma: hearing,
#                                  planning, reasoning, thinking, aggression,
#                                  hostility, seeing, pleasure, fear,
#                                  happiness, anger, imagining, wanting,
#                                  needing, desiring, intending, choosing),
#                                  observed 1-7. Codes are the source names
#                                  transliterated to ASCII (akilyurutme,
#                                  saldirganlik, gorme, ofke), reversibly.
#   sahin_2026_conspiracy          23 items (komplo1-23), observed 1-5; the
#                                  file's four subscale scores (hidden
#                                  powers, widespread, extraterrestrial,
#                                  government abuses) are 6/4/6/7 items.
#   Every Study 1 block total equals its item sum on complete rows
#   (asserted), so the items are stored as scored.
#
# Cleaning:
#   - Each of Study1.sav and study2.sav contains one pair of adjacent rows
#     identical on every column (Study 1 rows 35/36 over all 98 columns;
#     Study 2 rows 110/111). Treated as double entries: the second copy is
#     dropped (Study 1 -> 202 people, Study 2 -> 479).
#   - Study 1 and Study 2 share no (age + PMAS vector), so they are separate
#     samples.
#   - No fractional, sentinel or out-of-range cells; blocks that a Study 1
#     respondent skipped (3-9 people per block) are missing and drop in the
#     melt.
#
# Dropped:
#   - test_retest_data.sav: 50 of its 52 time-1 (age + PMAS) vectors occur in
#     study2.sav, so it is a re-administered subset of Study 2, not a new
#     sample; it carries no id to link a second wave, and it is N=52 alone.
#   - antropomorfizm: a single undocumented 0-4 item.
#   - Composites: morality_altboyut, dependency_altboyut, begenirlik_toplam,
#     tutum_toplam, olumlututum_toplam, olumsuztutum_toplam, doyum_toplam,
#     gg_komplo, yk_komplo, ddv_komplo, hs_komplo, komplo_toplam,
#     zihinatiflaritoplam.
# id: row index (no respondent id in either file); Study 2 ids follow
#   Study 1's.
# Covariates: cov_study (1, 2), cov_age, cov_gender (Study 1 labels:
#   1 female, 2 male; Study 2 is unlabelled), cov_education (1 elementary,
#   2 high school, 3 university student, 4 university graduate, 5 graduate
#   student, 6 graduate degree; both files), cov_income (1 low, 2 middle,
#   3 high; both files).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/21236702/files/{}/content"

PMAS = [f"m{i}" for i in range(1, 7)] + [f"d{i}" for i in range(1, 5)]
S1_PMAS = {**{f"morality{i}": f"m{i}" for i in range(1, 7)},
           **{f"dependency{i + 6}": f"d{i}" for i in range(1, 5)}}
MIND = {"isitme": "isitme", "planlama": "planlama",
        "akılyurutme": "akilyurutme", "dusunme": "dusunme",
        "agresyon": "agresyon", "saldırganlık": "saldirganlik",
        "görme": "gorme", "haz": "haz", "korku": "korku",
        "mutluluk": "mutluluk", "öfke": "ofke", "hayaletme": "hayaletme",
        "isteme": "isteme", "ihtiyacduyma": "ihtiyacduyma",
        "arzulama": "arzulama", "niyetetme": "niyetetme",
        "secimyapma": "secimyapma"}
S1_TABLES = {
    "sahin_2026_social_desirability": [f"begenirlik{i}" for i in range(1, 14)],
    "sahin_2026_life_satisfaction": [f"doyum{i}" for i in range(1, 6)],
    "sahin_2026_ai_attitudes": [f"olumsuz{i}" for i in range(1, 8)]
                               + [f"olumlu{i}" for i in range(1, 6)],
    "sahin_2026_mind_attribution": list(MIND.values()),
    "sahin_2026_conspiracy": [f"komplo{i}" for i in range(1, 24)],
}
TOTALS = {  # total column -> items it sums
    "morality_altboyut": [f"m{i}" for i in range(1, 7)],
    "dependency_altboyut": [f"d{i}" for i in range(1, 5)],
    "begenirlik_toplam": S1_TABLES["sahin_2026_social_desirability"],
    "doyum_toplam": S1_TABLES["sahin_2026_life_satisfaction"],
    "olumsuztutum_toplam": [f"olumsuz{i}" for i in range(1, 8)],
    "olumlututum_toplam": [f"olumlu{i}" for i in range(1, 6)],
    "tutum_toplam": S1_TABLES["sahin_2026_ai_attitudes"],
    "komplo_toplam": S1_TABLES["sahin_2026_conspiracy"],
    "zihinatıflarıtoplam": list(MIND.values()),
}
SUBSCALES = {"gg_komplo", "yk_komplo", "ddv_komplo", "hs_komplo"}
S1_COVS = {"yas_age": "cov_age", "cinsiyet_gender": "cov_gender",
           "egitim_educatıon": "cov_education", "gelir_ıncome": "cov_income"}
S2_COVS = {"age": "cov_age", "gender": "cov_gender", "edu": "cov_education",
           "ıncome": "cov_income"}
COV_COLS = ["cov_study", "cov_age", "cov_gender", "cov_education",
            "cov_income"]


def load(name):
    r = requests.get(BASE.format(name), headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def drop_adjacent_dup(d, expected_pos):
    dup = d.duplicated(keep="first")
    assert list(d.index[dup]) == [expected_pos], list(d.index[dup])
    assert d.iloc[expected_pos].equals(d.iloc[expected_pos - 1])
    return d[~dup].reset_index(drop=True)


def emit(table, d, items):
    long = d.melt(id_vars=["id"] + COV_COLS, value_vars=items,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all(), table
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + COV_COLS]
    for c in COV_COLS:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(items) > 1
    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{table}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload")
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")
    return table


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    s1, _ = load("Study1.sav")
    s2, _ = load("study2.sav")
    tr, _ = load("test_retest_data.sav")
    assert s1.shape == (203, 98), s1.shape
    assert s2.shape == (480, 14), s2.shape
    assert tr.shape == (52, 28), tr.shape

    s1 = s1.rename(columns={**S1_PMAS, **MIND})
    s1_items = PMAS + [c for its in S1_TABLES.values() for c in its]
    # Balance the books.
    known1 = set(s1_items) | set(TOTALS) | SUBSCALES | set(S1_COVS) \
        | {"antropomorfizm"}
    assert set(s1.columns) == known1, set(s1.columns) ^ known1
    assert set(s2.columns) == set(PMAS) | set(S2_COVS)
    for tot, its in TOTALS.items():
        ok = s1[its].notna().all(axis=1)
        assert ok.sum() >= 194
        assert (s1.loc[ok, its].sum(axis=1) == s1.loc[ok, tot]).all(), tot

    # test-retest time 1 is a subset of Study 2 (asserted), so it is dropped.
    key = lambda d, age: set(map(tuple, d[[age] + PMAS].values))  # noqa: E731
    assert len(key(tr, "yas_age") & key(s2, "age")) == 50

    s1 = drop_adjacent_dup(s1, 35)
    s2 = drop_adjacent_dup(s2, 110)
    assert not key(s1, "yas_age") & key(s2, "age")

    s1 = s1.rename(columns=S1_COVS)
    s2 = s2.rename(columns=S2_COVS)
    s1["cov_study"] = 1
    s2["cov_study"] = 2
    s1.insert(0, "id", s1.index + 1)
    s2.insert(0, "id", s2.index + 1 + len(s1))

    names = [emit("sahin_2026_pmas",
                  pd.concat([s1[["id"] + COV_COLS + PMAS],
                             s2[["id"] + COV_COLS + PMAS]],
                            ignore_index=True), PMAS)]
    for table, its in S1_TABLES.items():
        names.append(emit(table, s1, its))
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
