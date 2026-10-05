#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.23537073
# DOI: 10.1016/j.heliyon.2024.e36260
#   "The Eye of the Beholder: Attitudes toward divorced parents and perception of
#   children's happiness in Peru and Spain" (Clemente, Espinosa, Aguilar-Valera &
#   Guevara-Cordero, 2024), Heliyon 10(16):e36260. PMC11378926.
# Data: figshare 23537073 "Repository Data.sav" (414 x 80, SPSS;
#       https://ndownloader.figshare.com/files/41280237). The article's own SI
#       (mmc1.pdf, Europe PMC supplementaryFiles zip) prints the questionnaire:
#       the authors' English translation of the attitude block, then the full
#       Spanish original including the SD4 and PMD items.
# License: CC BY 4.0 on the figshare record (api.figshare.com/v2/articles/23537073
#          license "CC BY 4.0"); the article is also CC BY 4.0.
#
# Item text: shipped for all four tables from mmc1.pdf. Variable labels: present
#   on FATHER1-10, MOTHER1-10 and CHILD_not_happy only, as short English glosses
#   (e.g. "Child does not love him (father)"); no variable labels on SD4_*, the
#   PMD columns (named by mechanism) or the covariates. Value labels: present on
#   the categorical covariates only, none on any item. Administered in Spanish in
#   both countries; the Spanish wording ships as item_text, the authors' English
#   translation as item_text_translated for the parent items (the SI has no
#   English for SD4/PMD).
#
# Sample: 414 divorced parents and members of children's extended families,
#   Spain (259) and Peru (155). The deposit has no respondent id: row index.
#
# Tables:
#   clemente_2024_attitude_father  10 items FATHER1-10 about the children's father, 1-5
#   clemente_2024_attitude_mother  10 items MOTHER1-10 about the children's mother, 1-5
#   clemente_2024_sd4              Short Dark Tetrad, SD4_1-SD4_28, 1-5
#   clemente_2024_pmd              Propensity to Morally Disengage, 8 items named by
#                                  mechanism (Moore et al. 2012 order), 1-7
#
# The source's composites are skipped: Negative_Attitude_vs_Father/Mother and the
# four SD4 subscale scores equal the item means exactly (asserted); SD4_global
# and Moral_Disengagement are also composites (the latter is the mean of the
# first seven PMD items, without Attribution_of_blame -- asserted).
# FATHER9/MOTHER9 carry the variable label "Does not see child", but item 9 of
# the printed questionnaire is "Creo que no quiere a sus hijos"; the other nine
# labels match the questionnaire item at the same position. The table ships the
# column as deposited; the mismatch is recorded in the item text provenance.
# No missing item cells, no fractional item values, no exact-duplicate rows.
# The SI questionnaire asks for the last four digits of the respondent's DNI as
# an identifier; no such column is in the deposit.

import sys
import tempfile
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
URL = "https://ndownloader.figshare.com/files/41280237"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FATHER = [f"FATHER{i}" for i in range(1, 11)]
MOTHER = [f"MOTHER{i}" for i in range(1, 11)]
SD4 = [f"SD4_{i}" for i in range(1, 29)]
PMD = ["Moral_justification", "Euphemistic_labelling", "Advantageous_comparison",
       "Displacement_of_responsability", "Difussion_of_responsability",
       "Distortion_of_consequences", "Dehumanization", "Attribution_of_blame"]
TABLES = {
    "clemente_2024_attitude_father": (FATHER, {1, 2, 3, 4, 5}),
    "clemente_2024_attitude_mother": (MOTHER, {1, 2, 3, 4, 5}),
    "clemente_2024_sd4": (SD4, {1, 2, 3, 4, 5}),
    "clemente_2024_pmd": (PMD, {1, 2, 3, 4, 5, 6, 7}),
}
COV = {
    "SAMPLE": "cov_country",                 # 1 Spain, 2 Peru
    "Gender": "cov_gender",                  # 1 male, 2 female
    "Age": "cov_age",
    "Education": "cov_education",            # value labels in the .sav
    "Religion": "cov_religion",
    "Nationality": "cov_nationality",
    "Child_age": "cov_child_age",
    "Lives_with_father": "cov_child_lives_with_father",     # 1 yes, 2 no
    "Lives_with_mother": "cov_child_lives_with_mother",     # 1 yes, 2 no
    "Lives_with_mother_or_both": "cov_child_lives_mother_or_both",
    "Lives_with_father_or_both": "cov_child_lives_father_or_both",
    "Relation_to_child": "cov_relation_to_child",           # 1 parent, 2 other
    "Relación_by_gender": "cov_relation_by_gender",         # 1 father 2 mother 3 other male 4 other female
}
SKIP = {
    "control4": "attention-check column not in the printed questionnaire (413 x 4, 1 x 5)",
    "control2": "PMD attention check ('circle Bastante en desacuerdo' = 2), constant 2",
    "Moral_Disengagement": "composite: mean of the first seven PMD items",
    "SD4_Machiavellianism": "composite: mean of SD4_1-7",
    "SD4_Narcissism": "composite: mean of SD4_8-14",
    "SD4_Psychopathy": "composite: mean of SD4_15-21",
    "SD4_Sadism": "composite: mean of SD4_22-28",
    "SD4_global": "composite of the SD4 subscales",
    "Negative_Attitude_vs_Father": "composite: mean of FATHER1-10",
    "Negative_Attitude_vs_Mother": "composite: mean of MOTHER1-10",
    "CHILD_not_happy": "single item ('I believe the child is not happy'); no single-item tables",
}


def load() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    return d


def main() -> None:
    d = load()
    assert d.shape == (414, 80), d.shape
    assert not d.duplicated().any()

    # composites (see header)
    def same(a, b):
        return bool(np.allclose(a, b, atol=1e-6))
    assert same(d[FATHER].mean(axis=1), d["Negative_Attitude_vs_Father"])
    assert same(d[MOTHER].mean(axis=1), d["Negative_Attitude_vs_Mother"])
    for k, nm in enumerate(["Machiavellianism", "Narcissism", "Psychopathy", "Sadism"]):
        assert same(d[SD4[7 * k:7 * k + 7]].mean(axis=1), d[f"SD4_{nm}"]), nm
    assert same(d[PMD[:7]].mean(axis=1), d["Moral_Disengagement"])
    assert (d["control2"] == 2).all()

    item_cols = [c for items, _ in TABLES.values() for c in items]
    assert len(item_cols) == len(set(item_cols)) and len(TABLES) == len(set(TABLES))
    accounted = set(item_cols) | set(COV) | set(SKIP)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert not d[item_cols].isna().any().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COV)
    covs = list(COV.values())
    for c in covs:
        if c != "cov_child_age":
            d[c] = d[c].astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (items, pvset) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(items)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(pvset) for i in items}
        for i in items:
            assert set(t.loc[t["item"] == i, "resp"]) <= pvset, (name, i)
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
