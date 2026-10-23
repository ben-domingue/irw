#!/usr/bin/env python3
# Energy Literacy and Citizenship in Canada -- a national survey of 3,000 Canadians, November 2014.
# Comeau, L., Beckley, T., Parkins, J., & Stedman, R. (2015). Energy Literacy Survey [Data set].
#   Borealis / University of Alberta Dataverse. https://doi.org/10.7939/DVN/10302 (version 3)
#   Report shipped with the deposit: PR-15-01.pdf. Questionnaire: "Energy Literacy and Citizenship
#   in Canada Questionnaire.pdf" (the full instrument, Sections A-H).
# Licence: the deposit carries NO licence -- its terms read "This dataset is made available without
#   information on how it can be used. You should communicate with the Contact(s) specified before
#   use." Included by written permission from John Parkins (the contact the Borealis record
#   designates; first author Comeau publishes no address), granted 2026-10-19 for the data and
#   2026-10-21 for the item wording, on the Dataverse Community Norms plus the data citation shown
#   on the dataset page. Recorded as Original License = Permission via Email. See
#   processing_notes/outreach/outreach_log.csv and itemtext/instrument_rights_register.csv.
# Data: "Energy Study Dataset (6).tab", downloaded with format=original (an SPSS .sav,
#   3,000 rows x 264 columns), md5 2626c66119f56a1270950f592df88826.
# Usage: python3 comeau_2015_energy_literacy.py <dir holding the .sav> <output dir>
#
# PII dropped, not carried into cov_: q37_0 and q37_1, the postal-code question -- q37_0 holds a
#   full six-character Canadian postal code for all 3,000 respondents. Per the PII tiering ruled
#   2026-10-20 a postal code is a dropped column, not a disqualified candidate. Also dropped: the
#   free-text boxes q11_0, q12_0, q16b_0, q42_other, nb5_text_a, nb5_text_b, nbff_0 and `comments`
#   (809 answers; exactly one volunteers an email address and a first name, which is why a free-text
#   column is never shipped). No IP, location, name or date-of-birth column exists in the file.
#
# THE DEPOSIT'S DERIVED COLUMNS ARE SHUFFLED -- do not use them, and do not trust them elsewhere.
#   The five "...Correct" knowledge dummies (HomeLightingCorrectQ29, BuildAMachineQ31,
#   RenewableContinuousQ33, OneHundred_35EfficientQ35, Q27HydroDummy) carry the right MARGINAL
#   totals and the wrong ROWS: each one's total equals exactly the number of respondents choosing
#   one raw option, but its agreement with (raw == that option) is 0.48-0.59, which is what
#   independent shuffling predicts for splits of that size (1 - 2p(1-p)). The same goes for
#   summed_perceived_barriers_q20, which correlates 0.06 with the row sum of its own nine items.
#   (summed_perceived_knowledge is fine -- it correlates 1.0000 with the q7 row sum, just rescaled.)
#   So the correctness of each knowledge item is rebuilt here from the raw response, with the key
#   read off those marginals and checked against the question wording:
#     q29 "requires the LEAST ENERGY"      -> 5 "Lighting the home"                      (n=1,356)
#     q31 "it is impossible to..."         -> 1 "Build a machine that produces more
#                                               energy than it uses"                      (n=858)
#     q33 "'renewable energy resources'"   -> 5 "in continuous supply or can be
#                                               replenished by nature"                  (n=2,005)
#     q35 "35% efficient"                  -> 4 "100 units in, 35 converted to
#                                               electrical energy"                      (n=1,561)
#   Each marginal matches its dummy's total exactly, so this reproduces what the authors intended.
#   "Don't know" (code 8) scores 0, as their totals imply. q27 (hydro's share of electrical supply)
#   is NOT shipped: Q27HydroDummy is 1 only within raw codes 1, 2 and 5 and not within any one of
#   them, so no key is recoverable and the question has no unambiguous answer in the file.
#
# Tables: one per scale, item names kept as the source's own column names so they match the
#   questionnaire PDF, with the response codes as administered (no reversal, no rescaling).
#   comeau_2015_energy_source_knowledge     q7_0-q7_10    11 items  1-5 Nothing..A lot
#   comeau_2015_energy_source_support       q8_0-q8_10    11 items  1-5 Strongly oppose..Strongly support
#   comeau_2015_home_energy_knowledge       q14_0-q14_4    5 items  1-5 Nothing..A lot
#   comeau_2015_home_energy_intentions      q15_0-q15_2    3 items  1-4 Definitely not..Definitely
#                                             (code 7 "Not applicable" is defined but never used)
#   comeau_2015_energy_participation        q18_0-q18_7    8 items  1-3 Have done it / Haven't but
#                                             willing / Haven't, unwilling
#   comeau_2015_information_trust           q19_0-q19_8    9 items  1-5 Strongly distrust..Strongly trust
#   comeau_2015_participation_barriers      q20_0-q20_8    9 items  1-3 Not a barrier..Very much a barrier
#   comeau_2015_provincial_process          q21_0-q21_5    6 items  1-5 Strongly disagree..Strongly agree
#   comeau_2015_decision_considerations     q22_0-q22_5    6 items  1-5 Not at all important..Very important
#   comeau_2015_environmental_values        q24_0-q24_7    8 items  1-5 Strongly disagree..Strongly agree
#   comeau_2015_climate_beliefs             q25_0-q25_4    5 items  1-5 Strongly disagree..Strongly agree
#   comeau_2015_energy_attitudes            q26a_0-5 + q26b_0-6  13 items  1-5 (one battery, two
#                                             screens; every respondent answered both)
#   comeau_2015_energy_literacy             q29/q31/q33/q35  4 items  0/1 correct (above)
#   comeau_2015_energy_literacy_sureness    q30/q32/q34/q36  4 items  1-3 Not at all sure..Sure,
#                                             the confidence item that follows each shipped quiz item
# Not shipped: q5, q6, q17, q23, q27, q38-q45 as items (q38/q39/q44/q45 become covariates);
#   q9_*/q10_* (importance of factors "in influencing your answer", where the answer referred to is
#   a source the respondent chose earlier, so the referent differs by respondent); q16_*new, the
#   see/hear/smell checklist (q16_11new and q16_12new carry 13 value labels against two for their
#   eleven siblings, so the block's coding is not trustworthy); q46a-k and q47a-k (one value label
#   each, 138 answers, follow-ups naming a source); the nb1-nb5 New Brunswick block (every value
#   missing in this file); every summed_*, *_recode, Dummy and scale column (see above); filter_$.
# Covariates on every table, mapped only from the file's own value labels: cov_gender,
#   cov_age_group, cov_province, cov_community_type, cov_education, cov_income_band,
#   cov_home_tenure, cov_first_language, cov_political_views_code (q43 runs 1-7 with NO value
#   labels in the file and no key in the questionnaire PDF, so the codes stay and take the _code
#   suffix). q1 offers only Male/Female, so cov_gender has no "other" value here.
# id: the file's own @_id, verified unique across the 3,000 rows.
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

SCALES = {
    "energy_source_knowledge": [f"q7_{i}" for i in range(11)],
    "energy_source_support": [f"q8_{i}" for i in range(11)],
    "home_energy_knowledge": [f"q14_{i}" for i in range(5)],
    "home_energy_intentions": [f"q15_{i}" for i in range(3)],
    "energy_participation": [f"q18_{i}" for i in range(8)],
    "information_trust": [f"q19_{i}" for i in range(9)],
    "participation_barriers": [f"q20_{i}" for i in range(9)],
    "provincial_process": [f"q21_{i}" for i in range(6)],
    "decision_considerations": [f"q22_{i}" for i in range(6)],
    "environmental_values": [f"q24_{i}" for i in range(8)],
    "climate_beliefs": [f"q25_{i}" for i in range(5)],
    "energy_attitudes": [f"q26a_{i}" for i in range(6)] + [f"q26b_{i}" for i in range(7)],
    "energy_literacy_sureness": ["q30", "q32", "q34", "q36"],
}
# raw knowledge item -> correct code, and the dummy whose marginal total confirms it
KEY = {"q29": (5, "HomeLightingCorrectQ29"), "q31": (1, "BuildAMachineQ31"),
       "q33": (5, "RenewableContinuousQ33"), "q35": (4, "OneHundred_35EfficientQ35")}
COVS = {
    "cov_gender": ("q1", {1: "male", 2: "female"}),
    "cov_age_group": ("q2", None),
    "cov_province": ("q3", None),
    "cov_community_type": ("q38", None),
    "cov_education": ("q39", None),
    "cov_income_band": ("q44", None),
    "cov_home_tenure": ("q45", None),
    "cov_first_language": ("q42", None),
    "cov_political_views_code": ("q43", "keep_codes"),
}


def main() -> None:
    import pyreadstat
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    sav = next(p for p in raw.iterdir() if p.suffix.lower() == ".sav")
    d, m = pyreadstat.read_sav(str(sav))
    assert d.shape == (3000, 264), d.shape
    labels = m.variable_value_labels

    assert d["@_id"].is_unique
    d["id"] = d["@_id"].astype(int)

    cov = pd.DataFrame({"id": d["id"]})
    for name, (col, mapping) in COVS.items():
        if mapping == "keep_codes":
            assert col not in labels, f"{col} now has value labels -- map them instead"
            cov[name] = d[col].astype("Int64")
        else:
            lab = mapping or {int(k): v for k, v in labels[col].items()}
            vals = d[col].dropna().unique()
            assert set(int(v) for v in vals) <= set(lab), (col, sorted(vals))
            cov[name] = d[col].map(lambda v: lab.get(int(v)) if pd.notna(v) else None)

    tables, permitted = {}, {}
    for name, cols in SCALES.items():
        lv = {k for c in cols for k in labels[c]}
        for c in cols:
            assert set(labels[c]) == lv, (name, c)   # one shared response scale per table
        t = d.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
        t = t[t["resp"].notna()].copy()
        assert set(t["resp"].unique()) <= lv, (name, sorted(set(t["resp"]) - lv))
        t["resp"] = t["resp"].astype(int)
        t["item"] = pd.Categorical(t["item"], categories=cols, ordered=True)
        tables[f"comeau_2015_{name}"] = t
        permitted[f"comeau_2015_{name}"] = sorted(int(v) for v in lv)

    # the knowledge quiz, rebuilt from the raw responses (see the header)
    frames = []
    for col, (correct, dummy) in KEY.items():
        assert int((d[col] == correct).sum()) == int(d[dummy].sum()), (col, dummy)
        frames.append(pd.DataFrame({"id": d["id"], "item": col,
                                    "resp": (d[col] == correct).astype(int)})[d[col].notna()])
    quiz = pd.concat(frames, ignore_index=True)
    quiz["item"] = pd.Categorical(quiz["item"], categories=list(KEY), ordered=True)
    tables["comeau_2015_energy_literacy"] = quiz
    permitted["comeau_2015_energy_literacy"] = [0, 1]

    out.mkdir(parents=True, exist_ok=True)
    for name, t in tables.items():
        t = t.merge(cov, on="id", how="left").sort_values(["id", "item"])
        t = t[["id", "item", "resp"] + [c for c in cov.columns if c != "id"]]
        assert not t[["id", "item"]].duplicated().any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3, name
        # the validator gates the write; permitted_values are the file's own
        # value-label codes, not the observed range
        pv = permitted[name]
        fails = [(c.name, c.detail) for c in run_qc(t, permitted_values=pv)
                 if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"  [{f.severity}] {f.check}: {f.message}")
        t.to_csv(out / f"{name}.csv", index=False)
        print(f"{name}.csv rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
