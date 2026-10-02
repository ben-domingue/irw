#!/usr/bin/env python3
# Source: https://zenodo.org/records/7153436
# DOI: 10.3389/fpsyg.2021.702648
#   Bauwens, R., Denissen, M., Van Beurden, J., & Coun, M. (2021). Can
#   leaders prevent technology from backfiring? Empowering leadership as a
#   double-edged sword for technostress in care. Frontiers in Psychology, 12,
#   702648. (PMC8260968; not linked from the deposit, found by Crossref
#   search. Same sample: 339 Dutch childcare workers, Qualtrics, Sept-Oct
#   2020, age 19-64, mean 40.66 -- all reproduced by the file.)
#   Dataset: Bauwens, R. (2022). Leadership, technology and well-being in
#   childcare. Zenodo. https://doi.org/10.5281/zenodo.7153436
# Data: Data_TechnologyChildcare_Nienke.sav (339 rows x 417 columns).
# License: CC BY 4.0 (Zenodo API).
#
# Response format: the paper states "All measures were derived from
# prior-validated scales and administered in Dutch ... Answers were scored on
# a 7-point scale (1 = not at all; 7 = to a very large extent)". Every
# shipped item is asserted to lie in 1-7 after the two recodes below, and
# every block carries a 7-label value-label set.
#   - OVL1-5 and INVA1-4 are stored with Qualtrics codes 1, 4, 5, 6, 7, 8, 9,
#     and their value labels attach the 7-point agreement scale to exactly
#     those codes (1 Helemaal oneens, 4 Oneens .. 9 Helemaal eens). They are
#     recoded by label order to 1-7 (asserted: observed codes are a subset of
#     the labelled ones). The deposit's own composites (overload, invasion,
#     techno, *_short) average the RAW codes, and the paper's Table 2
#     overload mean (4.854) equals the raw-code OV_short mean, so the
#     published analysis used the miscoded scale; the shipped table does not.
#   - ENG1-3, EME1-5 and Turnoverintent carry stale value labels (1, 8-13)
#     while the data are 1-7: the labels' 7 categories match the data's 7
#     codes in order. The data are shipped as stored (1-7); the stale labels
#     are not used.
#
# Item text: shipped for 7 tables (autonomy, work_pressure, red_tape,
#   empowering_leadership, supervisory_support, lmx,
#   technostress_inhibitors): both label levels checked -- every item's
#   variable label is "<English construct name> - <full Dutch stem>" and the
#   value labels give all 7 Dutch anchors. The English construct prefix is
#   stripped; the Dutch stem is item_text. No English item wording in the
#   source, so the _translated fields are empty.
#   Not shipped:
#   - technostress_creators: the OVL/INVA stems are elliptical ("... word ik
#     gedwongen veel sneller te werken.") with the shared lead-in missing.
#   - safety_of_care, quality_of_care: same ("...zou ik me veilig voelen").
#   - engagement: UWES-3 wording, a rights-register block.
#   - exhaustion: the Dutch MBI/UBOS exhaustion items (Schaufeli et al.
#     1996), a commercially published instrument.
#
# Tables (item codes are the source column names):
#   bauwens_2022_autonomy               AUT1-3
#   bauwens_2022_work_pressure          WOP1-3
#   bauwens_2022_red_tape               RT1-6
#   bauwens_2022_empowering_leadership  EMPL1-6 (Pearce & Sims 2002, per
#                                       the paper; empleader = mean, asserted)
#   bauwens_2022_supervisory_support    PSS1-4 (PSS4 negatively worded, kept
#                                       as stored; PSS4R = 8 - PSS4 dropped)
#   bauwens_2022_lmx                    LMX1-7
#   bauwens_2022_technostress_creators  OVL1-5, INVA1-4, COM1-5, INS1-5,
#                                       UNC1-4 (23 items: the five
#                                       technostress-creator dimensions; the
#                                       paper analyses an 11-item subset)
#   bauwens_2022_technostress_inhibitors  SPORT1-4, LIT1-4, INVO1-5 (13
#                                       items: technical support, literacy
#                                       facilitation, involvement
#                                       facilitation; INVO1's label says
#                                       "Literacy facilitation" but the
#                                       deposit's literate composite is the
#                                       mean of LIT1-4 only, asserted)
#   bauwens_2022_engagement             ENG1-3
#   bauwens_2022_exhaustion             EME1-5 (Schaufeli et al. 1996, per
#                                       the paper)
#   bauwens_2022_safety_of_care         SAFE1-6 (SAFE5 negatively worded,
#                                       kept as stored; SAFE5R = 8 - SAFE5
#                                       dropped)
#   bauwens_2022_quality_of_care        QOC1-3 (Aiken et al. 2002, per the
#                                       paper)
#
# Dropped:
#   - PD, Turnoverintent: single-item measures (no table of one item).
#   - ICT_parents .. ICT_other, ICT_other_txt: a multi-select checklist of
#     what ICT is used for (not a scale); the free text names work tasks only
#     (checked: no names or contact details).
#   - PSS4R, SAFE5R: reversed copies (asserted).
#   - Every composite, centred score, interaction and dummy the authors
#     computed (lmx .. I_em_co_lit, cOVL1 .., L1xT1 .., *_short, edu_*,
#     D_*): 300+ derived columns, listed in DERIVED below by exclusion.
# id: row index. cluster_id: KDV, the childcare facility identifier (156
#   facilities; 18 respondents have none), a grouping only.
# Note: the supervisory-support codes PSS1-4 collide with the rights
#   register's Perceived Stress Scale code pattern. They are the deposit's
#   column names for Perceived Supervisory Support, not PSS wording; the
#   item text shipped for them is this deposit's own Dutch wording.
# Covariates: cov_gender (1 man, 2 woman, 4 other; value-labelled),
#   cov_age (years), cov_education (1 Basisschool .. 7 Universiteit),
#   cov_tenure (years in the current organisation; decimal commas parsed,
#   one "2/3" set to NA), cov_fulltime (1 full-time, 2 part-time),
#   cov_temporary (1 permanent, 2 temporary contract), cov_children (1 yes,
#   2 no), cov_n_children (numeric text), cov_parent_app (digital parent
#   environment in use: 1 yes, 2 no, 3 don't know).

import os
import re
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
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/7153436/files/"
       "Data_TechnologyChildcare_Nienke.sav/content")


def r(prefix, n, start=1):
    return [f"{prefix}{i}" for i in range(start, n + 1)]


TABLES = {
    "bauwens_2022_autonomy": r("AUT", 3),
    "bauwens_2022_work_pressure": r("WOP", 3),
    "bauwens_2022_red_tape": r("RT", 6),
    "bauwens_2022_empowering_leadership": r("EMPL", 6),
    "bauwens_2022_supervisory_support": r("PSS", 4),
    "bauwens_2022_lmx": r("LMX", 7),
    "bauwens_2022_technostress_creators": (r("OVL", 5) + r("INVA", 4)
                                           + r("COM", 5) + r("INS", 5)
                                           + r("UNC", 4)),
    "bauwens_2022_technostress_inhibitors": (r("SPORT", 4) + r("LIT", 4)
                                             + r("INVO", 5)),
    "bauwens_2022_engagement": r("ENG", 3),
    "bauwens_2022_exhaustion": r("EME", 5),
    "bauwens_2022_safety_of_care": r("SAFE", 6),
    "bauwens_2022_quality_of_care": r("QOC", 3),
}
TEXT_TABLES = {
    "bauwens_2022_autonomy": "Autonomy (Dutch)",
    "bauwens_2022_work_pressure": "Work pressure (Dutch)",
    "bauwens_2022_red_tape": "Red tape (Dutch)",
    "bauwens_2022_empowering_leadership":
        "Empowering leadership (Pearce & Sims 2002), Dutch",
    "bauwens_2022_supervisory_support":
        "Perceived supervisory support (Dutch)",
    "bauwens_2022_lmx": "Leader-member exchange, LMX-7 (Dutch)",
    "bauwens_2022_technostress_inhibitors":
        "Technostress inhibitors: technical support, literacy facilitation, "
        "involvement facilitation (Dutch)",
}
RECODE = r("OVL", 5) + r("INVA", 4)
STALE = r("ENG", 3) + r("EME", 5) + ["Turnoverintent"]
REVERSED = {"PSS4R": "PSS4", "SAFE5R": "SAFE5"}
SINGLE = {"PD", "Turnoverintent"}
ICT = {"ICT_parents", "ICT_colleagues", "ICT_supervisor",
       "ICT_administration", "ICT_absences", "ICT_orders", "ICT_other",
       "ICT_other_txt"}
COVS = {"gender": "cov_gender", "age": "cov_age",
        "education": "cov_education", "tenure": "cov_tenure",
        "fulltime": "cov_fulltime", "temporary": "cov_temporary",
        "children": "cov_children", "children_nof": "cov_n_children",
        "parent_environment": "cov_parent_app"}
FIRST_DERIVED = "lmx"  # every column from here to the end is derived


def load():
    resp = requests.get(URL, headers=UA, timeout=120)
    resp.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(resp.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def stem(label):
    return re.sub(r"\s+", " ", label.split(" - ", 1)[1]).strip()


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (339, 417), d.shape
    vl = meta.variable_value_labels

    # Balance the books.
    cols = list(d.columns)
    derived = set(cols[cols.index(FIRST_DERIVED):])
    items = {c for its in TABLES.values() for c in its}
    known = (items | derived | set(REVERSED) | SINGLE | ICT | set(COVS)
             | {"KDV"})
    assert set(cols) == known, set(cols) ^ known
    assert not items & derived and not set(COVS) & derived
    assert not d.duplicated().any()
    assert not d[sorted(items)].duplicated().any()

    # Derived columns and copies.
    for c, src in REVERSED.items():
        assert ((d[c] == 8 - d[src]) | d[src].isna()).all(), c
    for comp, its in {"empleader": r("EMPL", 6), "literate": r("LIT", 4),
                      "sport": r("SPORT", 4), "overload": r("OVL", 5),
                      "invasion": r("INVA", 4),
                      "techno": TABLES["bauwens_2022_technostress_creators"]
                      }.items():
        assert np.allclose(d[its].mean(axis=1), d[comp], equal_nan=True), \
            comp

    # Response codes.
    agree9 = {1.0: "Helemaal oneens", 4.0: "Oneens", 5.0: "Eerder oneens",
              6.0: "Neutraal", 7.0: "Eerder eens", 8.0: "Eens",
              9.0: "Helemaal eens"}
    for c in RECODE:
        assert vl[c] == agree9, c
        assert set(d[c].dropna()) <= set(agree9), c
        d[c] = d[c].map({k: i + 1 for i, k in enumerate(sorted(agree9))})
    for c in STALE:
        assert sorted(vl[c]) == [1.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0], c
    for c in items:
        v = d[c].dropna()
        assert (v % 1 == 0).all() and set(v) <= set(range(1, 8)), c
        if c not in RECODE and c not in STALE:
            assert sorted(vl[c]) == [float(k) for k in range(1, 8)], c

    # Covariates.
    ten = d["tenure"].replace("", np.nan).str.replace(",", ".", regex=False)
    assert set(ten[pd.to_numeric(ten, errors="coerce").isna()].dropna()) \
        == {"2/3"}
    d["tenure"] = pd.to_numeric(ten, errors="coerce")
    d["children_nof"] = pd.to_numeric(d["children_nof"].replace("", np.nan))
    assert d["age"].dropna().between(19, 64).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d["cluster_id"] = d["KDV"].astype("Int64")  # 18 rows have no facility code
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id", "cluster_id"] + cov_cols,
                      value_vars=its, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "cluster_id"] + cov_cols]
        for c in cov_cols:
            if c not in ("cov_tenure",):
                long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        pv = {i: set(range(1, 8)) for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

        if table in TEXT_TABLES:
            text = []
            for it in its:
                lab = meta.column_names_to_labels[it]
                assert " - " in lab and "..." not in lab and "…" not in lab
                for k in range(1, 8):
                    text.append({
                        "table": table, "section_id": f"{table}_1",
                        "item": it, "instrument": TEXT_TABLES[table],
                        "language": "Dutch", "instructions": "",
                        "section_prompt": "", "item_text": stem(lab),
                        "item_text_translated": "", "correct_response": "",
                        "option_text": vl[it][float(k)],
                        "option_text_translated": "", "resp": k})
            tx = pd.DataFrame(text)
            assert set(tx["item"]) == set(long["item"])
            assert set(tx["resp"]) == set(range(1, 8))
            assert tx.groupby("item")["item_text"].first().is_unique
            tx.to_csv(TEXT_DIR / f"{table}__items.csv", index=False)
            print(f"{table}__items.csv: rows={len(tx)}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
