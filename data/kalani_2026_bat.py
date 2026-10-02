#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/RODGFE
# DOI: none found for the physicians study (Harvard Dataverse deposit only;
#   no related publication in its metadata, and Crossref searches found
#   none as of 2026-10-02).
#   Kalani, S. (2026). "Replication Data for: Psychometric Properties of the
#   Burnout Assessment Tool among Physicians." Harvard Dataverse.
#   The same author's Persian BAT is published as Kalani, Esfahani &
#   Khanlari (2024), "A Persian validation of the burnout assessment tool,"
#   BMC Public Health 24, 10.1186/s12889-024-19314-y (PMC11238465) -- a
#   teacher sample (N = 580), not these data; it documents the Persian BAT's
#   5-point 1 (never) .. 5 (always) format.
# Data: Dataverse datafile 13419526, "Physicians BAT.sav" (format=original;
#       419 rows x 97 columns; Iranian physicians).
# License: CC0 1.0 (Dataverse dataset licence).
#
# Item text: not shipped. Both label levels checked: variable labels only
#   on F1-F8 ("Flourishing 1".."8"), DUBS* and DUWAS* (positional, e.g.
#   "Dutch Boredom Scale 1") and the composites; none on BAT*/UWES*. Value
#   labels carry anchors only (Persian never..always on BAT/DUBS/DUWAS,
#   English strongly disagree..strongly agree on F*). Stems are in the
#   published Persian BAT (Kalani et al. 2024), UWES-9 (Hajloo), Flourishing
#   Scale, DUBS and DUWAS.
#
# Tables (item codes are the source column names):
#   kalani_2026_bat           33 items, 1-5. BATC1-23 (BAT core symptoms:
#                             exhaustion 1-8, mental distance, cognitive and
#                             emotional impairment) + BATS1-10 (secondary
#                             symptoms). Range: value labels (1 never ..
#                             5 always) and the Persian BAT paper.
#   kalani_2026_uwes           9 items (UWES1-9), Utrecht Work Engagement
#                             Scale-9. No labels at either level, and the
#                             physicians' coding is undocumented: observed
#                             1-6, whereas the UWES (and the 2024 teacher
#                             paper) use 0 (never) .. 6 (always). No
#                             permitted-value set asserted.
#   kalani_2026_flourishing    8 items (F1-F8), Flourishing Scale, 1-7 per
#                             the value labels (strongly disagree ..
#                             strongly agree).
#   kalani_2026_boredom        8 items (DUBS1-8), Dutch Boredom Scale, 1-5
#                             per the value labels (never .. always).
#   kalani_2026_workaholism   10 items (DUWAS1-10), Dutch Work Addiction
#                             Scale, 1-5 per the value labels (never ..
#                             always; the original DUWAS is 4-point, so this
#                             is the administered 5-point format).
#
# Cleaning:
#   - The last row (index 418) has no Code, no covariates and no BAT
#     responses, only UWES/F/DUBS/DUWAS answers; it sits outside the
#     depositor's 1..418 coding and matches no other row. Dropped as an
#     uncoded stray, so every table has 418 ids.
#   - cov_age: three cells hold 33.39 (non-integer, identical); treated as
#     fills and set to NA.
# Dropped: composites BATC.Exhustion, BATC.mentaldistance, BATC.cognitive,
#   BATC.emotional, BATS.psychological, BATS.psychosomatic, BATC, BATS,
#   BAT.TOTAL, vigor, dedication, absorption, Engagement.TOTAL, FLOURISHING,
#   Boredom, WE, WC, Workaholism.TOTAL (BATC and the four totals equal
#   their item sums, asserted).
# id: row index. Code is a 1..418 study code (unique; replaced).
# Covariates: cov_age, cov_education (1 stager, 2 extern, 3 intern,
#   4 general practitioner, 5 resident, 6 specialist, 7 subspecialist
#   student, 8 subspecialist), cov_work_experience (years), work-setting
#   flags cov_government_centers, cov_private_centers, cov_health_centers,
#   cov_private_office, cov_charity_centers, cov_all_places (1 OK, 2 not
#   OK, as labelled), cov_training_course (1 not passed, 2 in progress,
#   3 passed, 4 exempt from medical plan).

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
URL = ("https://dataverse.harvard.edu/api/access/datafile/13419526"
       "?format=original")

BAT = [f"BATC{i}" for i in range(1, 24)] + [f"BATS{i}" for i in range(1, 11)]
UWES = [f"UWES{i}" for i in range(1, 10)]
FLOUR = [f"F{i}" for i in range(1, 9)]
DUBS = [f"DUBS{i}" for i in range(1, 9)]
DUWAS = [f"DUWAS{i}" for i in range(1, 11)]
TABLES = {
    "kalani_2026_bat": (BAT, range(1, 6)),
    "kalani_2026_uwes": (UWES, None),
    "kalani_2026_flourishing": (FLOUR, range(1, 8)),
    "kalani_2026_boredom": (DUBS, range(1, 6)),
    "kalani_2026_workaholism": (DUWAS, range(1, 6)),
}
COMPOSITES = {"BATC.Exhustion", "BATC.mentaldistance", "BATC.cognitive",
              "BATC.emotional", "BATS.psychological", "BATS.psychosomatic",
              "BATC", "BATS", "BAT.TOTAL", "vigor", "dedication",
              "absorption", "Engagement.TOTAL", "FLOURISHING", "Boredom",
              "WE", "WC", "Workaholism.TOTAL"}
COVS = {"Age": "cov_age", "Education": "cov_education",
        "workExperience": "cov_work_experience",
        "GovernmentCenters": "cov_government_centers",
        "PrivateCenters": "cov_private_centers",
        "HealthCenters": "cov_health_centers",
        "PrivateOffice": "cov_private_office",
        "CharityCenters": "cov_charity_centers",
        "AllPlaces": "cov_all_places",
        "PassingTrainingCourse": "cov_training_course"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (419, 97), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | COMPOSITES | set(COVS) | {"Code"}
    assert set(d.columns) == known, set(d.columns) ^ known

    # The uncoded stray row.
    stray = d["Code"].isna()
    assert stray.sum() == 1 and stray.iloc[-1]
    assert d.loc[stray, BAT + list(COVS)].isna().all(axis=None)
    d = d[~stray].reset_index(drop=True)
    assert sorted(d["Code"]) == list(range(1, 419))

    labels = {1.0: "هرگز", 2.0: "به ندرت", 3.0: "گاهی اوقات", 4.0: "اغلب",
              5.0: "همیشه"}
    for c in BAT + DUBS + DUWAS:
        assert meta.variable_value_labels[c] == labels, c
    for c in FLOUR:
        assert sorted(meta.variable_value_labels[c]) == list(
            map(float, range(1, 8))), c
    for c in UWES:
        assert c not in meta.variable_value_labels, c
    assert (d[BAT[:23]].sum(axis=1) == d["BATC"]).all()
    assert (d[UWES].sum(axis=1) == d["Engagement.TOTAL"]).all()
    assert (d[FLOUR].sum(axis=1) == d["FLOURISHING"]).all()
    assert (d[DUBS].sum(axis=1) == d["Boredom"]).all()
    assert (d[DUWAS].sum(axis=1) == d["Workaholism.TOTAL"]).all()

    frac_age = d["Age"] % 1 != 0
    assert set(d.loc[frac_age, "Age"]) == {33.39} and frac_age.sum() == 3
    d.loc[frac_age, "Age"] = pd.NA

    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        pv = None
        if allowed is not None:
            allowed = set(allowed)
            for it, g in long.groupby("item"):
                bad = set(g["resp"]) - allowed
                assert not bad, (table, it, bad)
            pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            if c != "cov_work_experience":
                long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv) if pv else run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        ctx = {"permitted_values": pv} if pv else None
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context=ctx)
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
