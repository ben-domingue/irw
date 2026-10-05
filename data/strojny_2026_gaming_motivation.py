#!/usr/bin/env python3
# Source: https://osf.io/ay296/
# DOI: 10.1038/s41598-026-49533-9
#   "Introjected regulation is the primary predictor of gaming disorder symptoms
#   across WHO and APA criteria in a representative sample of Polish adolescents"
#   (Strojny, Zajas, Kiszka, Starzec, Demetrovics & Király, 2026),
#   Scientific Reports 16:23135. PMC13396395.
# Data: osf.io/ay296 "GMI-PL validation data.sav" (930 x 151, SPSS;
#       https://osf.io/download/tpfa8/). The article's only SI file
#       (41598_2026_49533_MOESM1_ESM.docx) prints the Polish GMI (88 items) and
#       descriptive tables; it holds no item-level data.
# License: CC BY 4.0 on the OSF node (public; licence id 563c1cf88c5e4a3877f9e96a
#          resolves via api.osf.io/v2/licenses/ to "CC-By Attribution 4.0
#          International"); the article is also CC BY 4.0 (Europe PMC).
#
# Item text: shipped for strojny_2026_gmi only. Both label levels are populated
#   for every GMI, IGD and GDT item: SPSS variable labels carry the Polish stem
#   (e.g. GMI1 "D_GMI_1_Rozwój_Dlaczego grasz w gry wideo? Gram w gry wideo… -
#   ponieważ lubię uczucie ciągłego awansowania.", GDT1 "D_GDT1_Miałem
#   trudności z kontrolowaniem ...") and value labels carry the anchors
#   (1 zdecydowanie się nie odnosi .. 7 zdecydowanie się odnosi, midpoints bare
#   numbers; 1 Nigdy .. 5 Bardzo często; 99 = "uzasadniony brak danych" never
#   occurs). GMI built by
#   automated_finding/itemtext_verification/make_itemtext_strojny_2026.py
#   (Polish + IRW's own English in *_translated).
#   Not shipped for strojny_2026_igds9sf or strojny_2026_gdt on RIGHTS, not
#   availability: both are Dr. Halley Pontes's instruments;
#   itemtext/instrument_rights_register.csv blocks IGDS9-SF (CC BY-NC-ND footer
#   + "if you wish to further develop and validate the IGDS9-SF in another
#   language, please do get in touch", ruled 2026-09-09), and the GDT page
#   (halleypontes.com/tests/gaming-disorder-test/) carries the same footer and
#   the site's same translation clause. The Polish wording is in the .sav.
#   Not shipped for strojny_2026_gis: its variable labels are English glosses
#   ("1. Playing video games - one weekday") with copy errors (IGI4wrk, IGI4wee),
#   value labels only carry 9999 = justified missing, and the Polish wording is
#   not in the deposit or the SI.
#
# Sample: 930 Polish adolescents aged 13-17 from the 'Ariadna' national panel
# who answered 'yes' to "Do you play video games" (Gamer = 1 for all rows; the
# 130 non-gamers of the 1,060 recruited are not in the file). CAWI, March 2023.
#
# Tables:
#   strojny_2026_gmi      Gaming Motivation Inventory, Polish version, 88 items,
#                         1-7 (GMI1..GMI88; 1-66 "Why do you play video games?",
#                         67-88 "What kinds of games do you prefer?")
#   strojny_2026_igds9sf  Internet Gaming Disorder Scale-Short Form, 9 items, 1-5
#   strojny_2026_gdt      Gaming Disorder Test, 4 items, 1-5
#   strojny_2026_gis      Gaming Involvement Scale: minutes spent on 6 gaming
#                         activities on one weekday (*wrk) and one weekend day
#                         (*wee); continuous, 12 items
#
# Duplicate respondents: 15 pairs of rows are identical on all 150 non-ID
# columns (88 GMI items, 13 disorder items, 12 time estimates, demographics),
# and 4 further pairs share an identical, non-constant 88-item GMI vector
# (2 of them also identical on all 13 IGDS9-SF/GDT items, differing only in
# minutes). Not chance at that length: treated as double submissions. The
# first row (lowest ID) of each group is kept and the later copy dropped from
# every table -- 19 rows, leaving 911 respondents. Straight-lined GMI rows (25,
# every item the same value) are left alone: identical vectors there are not
# evidence of duplication.
#
# No imputation (every item cell is an integer), no PII (ID is a row number
# 1-1060 with gaps).

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW = REPO_ROOT / "automated_finding" / "runs" / "raw" / "strojny_2026"
URL = "https://osf.io/download/tpfa8/"

GMI = [f"GMI{i}" for i in range(1, 89)]
IGD = [f"IGD{i}" for i in range(1, 10)]
GDT = [f"GDT{i}" for i in range(1, 5)]
GIS = ["DGIwrk", "IGI1wrk", "IGI2wrk", "IGI3wrk", "IGI4wrk", "IGI5wrk",
       "DGIwee", "IGI1wee", "IGI2wee", "IGI3wee", "IGI4wee", "IGI5wee"]
SUBSCALE_MEANS = ["GMI_Advancement", "GMI_Amotivation", "GMI_Autonomy",
                  "GMI_Boredom", "GMI_Competence", "GMI_Competition",
                  "GMI_Completion", "GMI_Coping", "GMI_Escape",
                  "GMI_ExplMechanics", "GMI_Fantasy", "GMI_Financial",
                  "GMI_GameSkills", "GMI_Identity", "GMI_IntrojRegulation",
                  "GMI_Recreation", "GMI_SkillDevelopment", "GMI_Social",
                  "GMI_Status", "GMI_ArousalAction", "GMI_Cooperation",
                  "GMI_Customization", "GMI_Destruction", "GMI_Graphics",
                  "GMI_Story", "GMI_Strategy"]
SKIP = {
    "Gamer": "screening question, constant (1 = Yes) for every row",
    "GDT": "sum of GDT1-GDT4 (composite)",
    "IGD": "sum of IGD1-IGD9 (composite)",
    "GDT_endorsed": "derived screening flag",
    "IGD_36_cut": "derived cut-off flag",
    "IGD_32_cut": "derived cut-off flag",
    "DGI": "weekly composite: DGIwrk*5 + DGIwee*2",
    "IGI": "weekly composite of the five IGI activities",
    "GI": "DGI + IGI (composite)",
    **{c: "GMI subscale mean (composite)" for c in SUBSCALE_MEANS},
}


def load():
    RAW.mkdir(parents=True, exist_ok=True)
    f = RAW / "GMI-PL_validation_data.sav"
    if not f.exists():
        r = requests.get(URL, timeout=120)
        r.raise_for_status()
        f.write_bytes(r.content)
    d, meta = pyreadstat.read_sav(str(f))
    return d, meta


def duplicate_drops(d):
    """IDs of later copies in groups sharing a non-constant 88-item GMI vector."""
    g = d[GMI]
    straight = g.nunique(axis=1) == 1
    cand = d[~straight].copy()
    cand["_key"] = cand[GMI].astype(int).astype(str).agg("".join, axis=1)
    drops = []
    for _, grp in cand.groupby("_key"):
        if len(grp) > 1:
            drops += sorted(int(x) for x in grp["ID"])[1:]
    return drops


def main():
    d, meta = load()
    assert d.shape == (930, 151), d.shape
    assert d["ID"].is_unique
    # composites really are composites
    assert (d[GDT].sum(axis=1) == d["GDT"]).all()
    assert (d[IGD].sum(axis=1) == d["IGD"]).all()
    assert (d["DGIwrk"] * 5 + d["DGIwee"] * 2 == d["DGI"]).all()
    assert (d["Gamer"] == 1).all()

    # books
    accounted = {"ID", "Gender", "Age"} | set(GMI) | set(IGD) | set(GDT) \
        | set(GIS) | set(SKIP)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    assert len(d.columns) == len(accounted)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")

    non_id = [c for c in d.columns if c != "ID"]
    n_exact = int(d.duplicated(subset=non_id).sum())
    drops = duplicate_drops(d)
    assert n_exact == 15 and len(drops) == 19, (n_exact, len(drops))
    print(f"  dropping {len(drops)} later copies of duplicated respondents "
          f"({n_exact} exact on all 150 columns): IDs {drops}")
    d = d[~d["ID"].isin(drops)].copy()

    d["id"] = d["ID"].astype(int)
    d["cov_gender"] = d["Gender"].map({1: "female", 2: "male", 3: "other"})
    d["cov_age"] = d["Age"].astype(int)
    assert d["cov_gender"].notna().all()
    covs = ["cov_gender", "cov_age"]

    tables = {
        "strojny_2026_gmi": (GMI, set(range(1, 8))),
        "strojny_2026_igds9sf": (IGD, set(range(1, 6))),
        "strojny_2026_gdt": (GDT, set(range(1, 6))),
        "strojny_2026_gis": (GIS, None),
    }
    assert len(tables) == len(set(tables))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (items, allowed) in tables.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=items,
                   var_name="item", value_name="resp")
        if allowed is None:
            n_miss = int((t["resp"] == 9999).sum())
            t = t[t["resp"] != 9999]
            print(f"  {name}: {n_miss} '9999 = justified missing' cells dropped")
        t = t.dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        if allowed is not None:
            assert set(t["resp"]) <= allowed, (name, set(t["resp"]) - allowed)
        else:
            assert t["resp"].between(0, 1440).all(), name  # minutes in a day
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        assert set(t["item"]) == set(items)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100

        pv = {i: allowed for i in items} if allowed is not None else None
        checks = run_qc(t, permitted_values=pv) if pv else run_qc(t)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        ctx = {"permitted_values": pv} if pv else {}
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context=ctx)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
