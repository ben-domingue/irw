#!/usr/bin/env python3
# Source: https://zenodo.org/records/14928790
# DOI: 10.1080/02770903.2025.2519100
#   Al-Qerem, W., Jarab, A., Al Bawab, A. Q., Eberhardt, J., Al-Zayadneh, E.,
#   Al-Iede, M., Khdour, M., Al-sa'di, L., & Sawaftah, L. (2025). "Parental
#   numeracy skills and asthma control: a cross-sectional study." Journal of
#   Asthma, 62(10), 1768-1775. (Matched by sample: 400 parents of children
#   with asthma at the University of Jordan Hospital, February-May 2024 --
#   the deposit's own timestamps run Feb-May 2024. Not linked from the
#   deposit. CC BY-NC-ND but bot-walled at both T&F and the Teesside
#   repository, so not read.) The same 400 parents' ANQ is analysed in
#   Al-Qerem et al. (2025) J Asthma Allergy 18, "Validation of the Arabic
#   Version of Asthma Numeracy Questionnaire (ANQ) Among Parents of
#   Asthmatic Children" (PMC11724629, read), whose data statement points to
#   a separate, smaller ANQ-only deposit (Zenodo 11670017, not in the IRW);
#   and the PedsQL block in a 2026 J Asthma paper (10.1080/02770903.2026.
#   2712840, not read).
#   Deposit: Al-Qerem, W. (2025). Health literacy and asthma control. Zenodo.
# Data: control data.sav (400 rows x 155 columns). Each row is a parent
#   answering about one child with asthma, recruited at an outpatient
#   respiratory clinic in Amman. The questionnaire was administered in
#   Arabic: the Arabic answers are kept as string columns beside the English
#   value-labelled numeric recodes.
# License: CC BY 4.0 (Zenodo API).
#
# Item text: both label levels checked. Every item has an ENGLISH
#   variable label on its numeric column (two PedsQL treatment items carry
#   the Arabic stem instead) and English value labels; the ARABIC stems, as
#   administered, are the variable labels of the string answer columns, with
#   the Arabic options as their values.
#   - alqerem_2025_gina_control: SHIPPED (itemtext_output/
#     alqerem_2025_gina_control__items.csv, data_labels + study_materials).
#     item_text = the Arabic string-column label verbatim (it carries the
#     "in the past four weeks" frame), item_text_translated = the deposit's
#     own English variable label verbatim; options from the Arabic answer
#     values / English value labels, tied to resp by the asserted mapping.
#   - not shipped: PedsQL Asthma Module (Mapi-licensed) and MARS-5 (licensed;
#     neither cleared in the rights register); knowledge and ANQ ship as
#     scored correctness, so their administered options are not the resp
#     categories. Their wording is at both label levels as above.
#
# Tables (item codes are the source numeric column names):
#   alqerem_2025_pedsql_asthma  Qol_1 .. Qol_c_3 (28 items)  PedsQL 3.0
#       Asthma Module, parent report: asthma symptoms (11), treatment
#       problems (11), worry (3), communication (3). The numeric columns hold
#       the PedsQL 0-100 transform; the Arabic answer columns hold the raw
#       5-point response (Never .. Almost always, the value labels). The
#       transform is asserted to equal 100 - 25 x raw for every cell, and
#       resp is the RAW 0-4 (0 = never .. 4 = almost always).
#       Permitted {0..4}.
#   alqerem_2025_gina_control   symptom_control_1 .. 4  GINA asthma symptom
#       control screen (daytime symptoms > 2/week, night waking, reliever
#       > 2/week, activity limitation), 0 = no, 1 = yes (value labels;
#       asserted against the Arabic answers). control_sum = their sum.
#   alqerem_2025_mars5          adherance_1 .. adherance_5  Medication
#       Adherence Report Scale (MARS-5), parent version, 1 = always ..
#       5 = never (value labels; asserted against the Arabic answers).
#       adherance_sum = their sum.
#   alqerem_2025_asthma_knowledge  k_1 .. k_7  seven asthma-knowledge items
#       (JAA paper: "composed of 7 items"), shipped as the deposit's scored
#       correctness k_k_c (1 = correct). Each k_k_c is asserted to be a
#       deterministic function of the raw multiple-choice answer k_k, and
#       k_sum = their sum.
#   alqerem_2025_anq            anq_1 .. anq_4  Arabic Asthma Numeracy
#       Questionnaire; "each correctly answered item is worth one point"
#       (JAA paper). Scored here from the RAW answers with the key the items
#       themselves imply: anq_1 (30 mg/day from 5 mg tablets) = 6 pills;
#       anq_2 (1% risk) = "Out of 100 patients, one" (code 2); anq_3 (Red
#       Zone = 50% of a 400 L/min best) = 200 L/min; anq_4 (Yellow Zone between
#       50% and 80% of 400) = "Between 200 and 320 L/min" (code 2). The
#       deposit's own anq_k_c scored columns follow the same key in all but
#       30 of 1,600 cells (8/6/6/10 per item, asserted), where they disagree
#       with the raw answer recorded in BOTH the numeric and the Arabic
#       column, so the raw answer is taken as authoritative.
#
# Dropped:
#   - The Arabic answer string columns (used only for the assertions above),
#     the medication multi-select (a checklist of drug classes, not free
#     text; checked) and every medication flag (Ventolin .. Inhaled_c,
#     medications, montilukast, antihistamin_s, VAR00001/2, C1, C2).
#   - Composites and scorings: control_sum, control_sum_status, control_di,
#     NEW_control_status, k_sum, the k_k_c and anq_k_c columns (see above),
#     sum_anq, adherance_sum, adherance_status, asthma_sore, treatment_sore,
#     worry_sore, communication_sore, total_mean_qol, sum_medication,
#     medication_no.
#   - The submission timestamp (date only, Feb-May 2024) and ID (a record
#     number 1-400).
# id: row index.
# Covariates: cov_age (parent's age, years), cov_parent_gender (1 female,
#   2 male), cov_parent_education (1 high school or less, 2 college degree,
#   3 bachelor's or postgraduate), cov_income (1 < 500 JOD, 2 500-1000,
#   3 > 1000), cov_child_age (years), cov_child_gender (1 female, 2 male).

import os
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
IT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/14928790/files/"
       "control%20data.sav/content")

PEDSQL = (["Qol_" + str(i) for i in range(1, 12)]
          + ["Qol_t_" + str(i) for i in range(1, 11)]
          + ["Qol_treatment_11", "Qol_worry_1", "Qol_w_2", "Qol_w_3",
             "Qol_c_1", "Qol_c_2", "Qol_c_3"])
GINA = [f"symptom_control_{i}" for i in range(1, 5)]
MARS = [f"adherance_{i}" for i in range(1, 6)]
KNOW = [f"k_{i}" for i in range(1, 8)]
ANQ = [f"anq_{i}" for i in range(1, 5)]
ANQ_KEY = {"anq_1": 6, "anq_2": 2, "anq_3": 200, "anq_4": 2}
ANQ_DISAGREE = {"anq_1": 8, "anq_2": 6, "anq_3": 6, "anq_4": 10}
TABLES = {
    "alqerem_2025_pedsql_asthma": (PEDSQL, set(range(0, 5))),
    "alqerem_2025_gina_control": (GINA, {0, 1}),
    "alqerem_2025_mars5": (MARS, set(range(1, 6))),
    "alqerem_2025_asthma_knowledge": (KNOW, {0, 1}),
    "alqerem_2025_anq": (ANQ, {0, 1}),
}
# Arabic raw answer -> PedsQL raw 0-4 (spacing varies between blocks).
PEDSQL_AR = {"لا يوجد": 0, "لايوجد": 0, "لايوجد الى حد كبير": 1,
             "لا يوجد الى حد كبير": 1, "يوجد أحيانًا": 2, "يوجد غالبًا": 3,
             "يوجد باستمرار": 4}
YESNO_AR = {"نعم": 1, "لا": 0}
MARS_AR = {"دائمًا": 1, "غالبًا": 2, "أحيانًا": 3, "نادرًا": 4, "أبدًا": 5}
SCORINGS = {"control_sum", "control_sum_status", "control_di",
            "NEW_control_status", "k_sum", "sum_anq", "adherance_sum",
            "adherance_status", "asthma_sore", "treatment_sore",
            "worry_sore", "communication_sore", "total_mean_qol",
            "sum_medication", "medication_no"}
SCORED_COPIES = {f"{c}_c" for c in KNOW + ANQ}
MEDS = {"Ventolin", "Montelukast", "Antihistamines", "Tiotropium_bromide",
        "ICS_pulmicort", "ventolin_n", "ICS", "montilukast", "Montilukast_N",
        "antihistamin_s", "antihistamin_N", "cough_syrup",
        "oral_corticosteroids", "ipratrppromide_n", "Antibiotics_n",
        "tiotropium_bromide_n", "VAR00001", "VAR00002", "C1", "C2",
        "Inhaled_c", "medications"}
COVS = {"education_parents": "cov_parent_education", "income": "cov_income",
        "gender_parents": "cov_parent_gender",
        "gender_child": "cov_child_gender"}
# Arabic-named columns, by position in the file.
AR_PARENT_AGE, AR_CHILD_AGE = 1, 5
AR_PEDSQL = range(12, 40)
AR_GINA = range(40, 44)
AR_MARS = range(44, 49)
AR_KNOW = range(49, 56)
AR_OTHER = [0, 2, 3, 4, 6, 7, 9, 11]


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
    assert d.shape == (400, 155), d.shape
    cols = list(d.columns)
    ar = {i: cols[i] for i in range(56)}

    # Balance the books.
    items = set(PEDSQL + GINA + MARS + KNOW + ANQ)
    known = (items | SCORINGS | SCORED_COPIES | MEDS | set(COVS)
             | set(ar.values()) | {"ID"})
    assert set(cols) == known, set(cols) ^ known
    assert d["ID"].is_unique
    assert not d.drop(columns=["ID"]).duplicated().any()

    # PedsQL: numeric is the 0-100 transform of the Arabic raw answer.
    ped = pd.DataFrame(index=d.index)
    for i, c in zip(AR_PEDSQL, PEDSQL):
        raw = d[ar[i]].str.strip().map(PEDSQL_AR)
        assert raw.notna().all(), c
        assert (d[c] == 100 - 25 * raw).all(), c
        ped[c] = raw
    for i, c in zip(AR_GINA, GINA):
        assert (d[ar[i]].str.strip().map(YESNO_AR) == d[c]).all(), c
    for i, c in zip(AR_MARS, MARS):
        assert (d[ar[i]].str.strip().map(MARS_AR) == d[c]).all(), c
    assert (d[GINA].sum(axis=1) == d["control_sum"]).all()
    assert (d[MARS].sum(axis=1) == d["adherance_sum"]).all()

    # Knowledge: scored copy is a deterministic function of the raw answer.
    know = pd.DataFrame(index=d.index)
    for c in KNOW:
        g = d.groupby(c)[f"{c}_c"].nunique()
        assert (g == 1).all(), c
        know[c] = d[f"{c}_c"]
    assert (know.sum(axis=1) == d["k_sum"]).all()

    # ANQ: score from the raw answers with the item key.
    anq = pd.DataFrame(index=d.index)
    for c, key in ANQ_KEY.items():
        anq[c] = (d[c] == key).astype(int)
        assert (anq[c] != d[f"{c}_c"]).sum() == ANQ_DISAGREE[c], c
    # The medication column is a fixed checklist, not narrative.
    assert d[ar[7]].str.len().max() < 200

    d = d.reset_index(drop=True)
    out = pd.DataFrame({"id": d.index + 1})
    out["cov_age"] = d[ar[AR_PARENT_AGE]]
    out["cov_child_age"] = d[ar[AR_CHILD_AGE]]
    for src, dst in COVS.items():
        out[dst] = d[src]
    cov_cols = ["cov_age", "cov_parent_gender", "cov_parent_education",
                "cov_income", "cov_child_age", "cov_child_gender"]
    blocks = {"alqerem_2025_pedsql_asthma": ped.reset_index(drop=True),
              "alqerem_2025_gina_control": d[GINA],
              "alqerem_2025_mars5": d[MARS],
              "alqerem_2025_asthma_knowledge": know.reset_index(drop=True),
              "alqerem_2025_anq": anq.reset_index(drop=True)}

    names = []
    for table, (its, allowed) in TABLES.items():
        wide = pd.concat([out[["id"] + cov_cols], blocks[table][its]], axis=1)
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=its,
                         var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        path = OUT_DIR / f"{table}.csv"
        long.to_csv(path, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(path), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))
    write_gina_itemtext(meta, cols, ar)


def write_gina_itemtext(meta, cols, ar):
    table = "alqerem_2025_gina_control"
    opts_ar = {0: "لا", 1: "نعم"}
    rows = []
    for i, c in zip(AR_GINA, GINA):
        vl = meta.variable_value_labels[c]
        assert vl == {0.0: "No", 1.0: "Yes"}, c
        for resp in (0, 1):
            rows.append({
                "table": table, "section_id": f"{table}_1", "item": c,
                "instrument": "GINA asthma symptom control assessment "
                              "(Global Initiative for Asthma), parent report",
                "language": "Arabic", "instructions": None,
                "section_prompt": None,
                "item_text": meta.column_names_to_labels[ar[i]].strip(),
                "item_text_translated": meta.column_names_to_labels[c].strip(),
                "correct_response": None, "option_text": opts_ar[resp],
                "option_text_translated": vl[float(resp)], "resp": resp})
    IT_DIR.mkdir(parents=True, exist_ok=True)
    it = pd.DataFrame(rows)
    path = IT_DIR / f"{table}__items.csv"
    it.to_csv(path, index=False, quoting=1)
    print(f"{path.name}: rows={len(it)} (run normalize_nulls.R after)")


if __name__ == "__main__":
    convert()
