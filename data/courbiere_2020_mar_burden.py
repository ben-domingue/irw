#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0238945
# DOI: 10.1371/journal.pone.0238945
# Paper: Courbiere, B., Lacan, A., Grynberg, M., Grelat, A., Rio, V., Arbo,
#   E., & Solignac, C. (2020). Psychosocial
#   and professional burden of Medically Assisted Reproduction (MAR): Results
#   from a French survey. PLOS ONE 15(9): e0238945.
# Data: Mendeley Data 10.17632/6rmxbd56cf.1, "MAR dataset" (Courbiere),
#   file "MAR dataset.xlsx": sheet PARCOURS PMA (1,045 respondents x 258
#   columns), plus a VARIABLES sheet (French question wording per column)
#   and a LABELS sheet (numeric code -> French label per variable).
#   https://data.mendeley.com/datasets/6rmxbd56cf/1
# License: CC BY 4.0, verified on the DEPOSIT (Mendeley public API,
#   data_licence short_name "CC BY 4.0"); the article is also CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# An online survey (Ipsos-style panel) of 1,045 French women and men aged
# 18-50 who were in, or had been through, a MAR/ART pathway. The
# questionnaire is study-authored and organised as grid batteries; each
# battery is shipped as its own table, keyed by the deposit's own column
# names (Q17_0 .. Q17_8 etc.).
#
# RESPONSE CODES: the data cells are the French option LABELS. They are
# mapped to the deposit's OWN numeric codes from its LABELS sheet, so every
# resp value is the codebook's code, not one invented here. Two consequences
# to know before analysing:
#   * Direction differs by battery, as in the codebook: most run from the
#     strongest/most-positive option at 1 (e.g. Q17 1 "Tres satisfait(e)" ..
#     4 "Pas du tout satisfait(e)"; Q36 1 "Tres souvent" .. 5 "Jamais"),
#     while Q50 runs 1 "Jamais" .. 5 "Tres souvent". Each table's
#     description states its own direction.
#   * Q42 is the ONE exception: the codebook puts the midpoint "Ni plus, ni
#     moins" last (code 5). It is re-ordered here to the middle: 1 "Beaucoup
#     plus", 2 "Un plus" [sic, = un peu plus], 3 "Ni plus, ni moins",
#     4 "Un peu moins", 5 "Beaucoup moins".
#   * "Non concerne(e)" (Q21BIS, Q37, Q39) and "Je n'ai pas de contact avec
#     ce professionnel de sante" (Q53) are not-applicable answers and are
#     dropped, not scored. Q46's "Aucun impact" (code 5) is kept: it is the
#     bottom of the impact scale, below "pas du tout important".
#
# Tables shipped (14):
#   courbiere_2020_mar_satisfaction        Q17_0-8   satisfaction with MAR care, 1-4
#   courbiere_2020_mar_stimulation         Q21BIS_0-8 ovarian-stimulation treatment, agreement 1-4
#   courbiere_2020_mar_feelings            Q36_0-10  how often you feel ..., 1-5
#   courbiere_2020_mar_attitudes           Q37_0-9   attitudes in the MAR pathway, agreement 1-4
#   courbiere_2020_mar_physical            Q39_0-11  physical state, extent 1-4
#   courbiere_2020_mar_couple              Q41_0-9   couple life, extent 1-4
#   courbiere_2020_mar_relationship_change Q42_0-7   relationship became more/less ..., 1-5
#   courbiere_2020_mar_social              Q44_0-10  relations with others, extent 1-4
#   courbiere_2020_mar_work_impact         Q46_0-9   impact on working life, 1-5
#   courbiere_2020_mar_work_situations     Q48E_0-14 situations faced at work, 1 yes / 0 no
#   courbiere_2020_mar_financial           Q50_0-8   financial situations, 1 never .. 5 very often
#   courbiere_2020_mar_professionals       Q53_0-7   relations with health professionals, 1-4
#   courbiere_2020_mar_professional_conduct Q54_0-4  do professionals ..., 1-4
#   courbiere_2020_mar_information         Q55_0-6   have the information you need, 1-4
#
# NOT shipped: single questions and the 1-10 ratings (Q0, Q27, Q35, Q38,
# Q40, Q43, Q45, Q49, Q51 -- each one item on a different domain), the
# multiple-response lists (Q1, Q3, Q10, Q12, Q15, Q19, Q30 -- choice of
# labels, not graded responses), Q21E (yes/no adjective checklist), Q28
# (stage-satisfaction ratings, skip-gated to the stages each respondent
# went through), Q52E (nominal: anticipate/realise/delay/give up), and
# RESMAR.
#
# Covariates: gender, age, education (FR02EDU, French label), and MAR status
# (RS9, French label: in progress in France / abroad / finished / stopped /
# paused / waiting). Region (FRREGION3, REG5) and agglomeration size (AGGLO)
# are geographic codes and are dropped under the 2026-10-20 ruling.
# `id` is the row index (the sheet has no id column).
#
# Item text: NOT SHIPPED. Every stem is in the deposit's VARIABLES sheet and
#   every option label in its LABELS sheet, keyed by these same column names
#   (study-authored, CC BY). It is French, and the standard wants an English
#   translation in the *_translated columns -- ~140 IRW-generated
#   translations is content that owes its own provenance and issues-page
#   entry (the rosman_2022 obstacle). One pass over one workbook when done.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("COURBIERE_RAW", "MAR dataset.xlsx")
N_ROWS = 1045

# battery prefix -> (table suffix, n items, codes treated as not-applicable, recode)
BATTERIES = {
    "Q17": ("satisfaction", 9, (), None),
    "Q21BIS": ("stimulation", 9, (5,), None),
    "Q36": ("feelings", 11, (), None),
    "Q37": ("attitudes", 10, (5,), None),
    "Q39": ("physical", 12, (5,), None),
    "Q41": ("couple", 10, (), None),
    "Q42": ("relationship_change", 8, (), {1: 1, 2: 2, 5: 3, 3: 4, 4: 5}),
    "Q44": ("social", 11, (), None),
    "Q46": ("work_impact", 10, (), None),
    "Q48E": ("work_situations", 15, (), {1: 1, 2: 0}),
    "Q50": ("financial", 9, (), None),
    "Q53": ("professionals", 8, (5,), None),
    "Q54": ("professional_conduct", 5, (), None),
    "Q55": ("information", 7, (), None),
}
COV_SRC = ["GENDER", "AGE", "FR02EDU", "RS9"]
GEO_DROPPED = ["FRREGION3", "REG5", "AGGLO"]


def labels_sheet():
    lab = pd.read_excel(RAW, sheet_name="LABELS", header=None).iloc[2:]
    lab[0] = lab[0].ffill()
    out = {}
    for var, g in lab.groupby(0):
        out[var] = {str(t).strip(): int(c) for c, t in zip(g[1], g[2]) if pd.notna(c)}
    return out


def convert():
    df = pd.read_excel(RAW, sheet_name="PARCOURS PMA")
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined")
    assert len(txt) > 100
    lab = labels_sheet()
    # every text column must be a closed codebook category -- no free text anywhere
    free = [c for c in txt if c in lab and not set(df[c].dropna().astype(str).str.strip()) <= set(lab[c])]
    unlabelled = [c for c in txt if c not in lab]
    print(f"  text columns outside their LABELS codebook: {free}; text columns with no codebook entry: {unlabelled}")
    assert not free

    df["id"] = range(1, N_ROWS + 1)
    df["cov_gender"] = df["GENDER"].map({"Un homme": "male", "Une femme": "female"})
    df["cov_age"] = df["AGE"]
    df["cov_education"] = df["FR02EDU"]
    df["cov_mar_status"] = df["RS9"]
    cov_cols = ["cov_gender", "cov_age", "cov_education", "cov_mar_status"]
    assert df[cov_cols].notna().all().all()

    used = set(COV_SRC) | set(GEO_DROPPED)
    names, total = [], 0
    for pfx, (suffix, k, na_codes, recode) in BATTERIES.items():
        items = [f"{pfx}_{i}" for i in range(k)]
        assert all(c in df.columns for c in items), pfx
        used |= set(items)
        wide = df[["id"] + cov_cols].copy()
        for c in items:
            m = lab[c]
            codes = df[c].astype("string").str.strip().map(m)
            assert codes.notna().sum() == df[c].notna().sum(), c  # every label resolved
            codes = codes.where(~codes.isin(na_codes))
            if recode:
                codes = codes.map(recode)
            wide[c] = codes
        long = wide.melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        scale = sorted(set(recode.values()) if recode else
                       {v for c in items for v in lab[c].values()} - set(na_codes))
        assert set(long["resp"]) <= set(scale), (pfx, set(long["resp"]), scale)
        checks = run_qc(long, permitted_values={c: scale for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {suffix} {c.name}: {c.detail[:150]}")
        name = f"courbiere_2020_mar_{suffix}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} resp={scale}")
    assert len(set(names)) == len(names) == 14
    not_shipped = [c for c in df.columns if c not in used and c not in ["id"] + cov_cols]
    print(f"total responses {total}; {len(not_shipped)} source columns not shipped (see header): "
          f"{sorted({c.split('_')[0] for c in not_shipped})}")


if __name__ == "__main__":
    convert()
