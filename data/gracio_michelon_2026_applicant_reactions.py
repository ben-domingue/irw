#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/wjw7b6ghc8
# DOI: 10.17632/wjw7b6ghc8 (data; no paper DOI on the record)
#   Gracio Michelon, V. (2026). "Counterfactual explanations and algorithm
#   aversion." Mendeley Data, V1.
# Data: Study_1_data.sav (125 respondents; rejection by a human, AI or hybrid
#   evaluator, between subjects) and Study_2_data.sav (384 respondents;
#   3 evaluator x 3 rejection-message design). Both Qualtrics exports with
#   full SPSS variable and value labels; Study_*_syntax.sps define the scales.
# License: CC BY 4.0 (Mendeley Data record).
# Codebook: none beyond the labelled .sav files and the .sps syntax.
#
# Item text: not shipped -- the wording is in the SPSS variable labels, but no
#   rights-register rows exist yet for these instruments (Bauer et al. 2001
#   SPJS subscales, PANAS short form, org-attraction items); left for an
#   itemtext pass.
#
# PII: none. Free-text "_TEXT" self-describe fields (ethnicity, gender,
#   education, employment) and RecordedDate are not carried.
#
# Items are kept as deposited (no reverse-scoring; Study 2 syntax reverses
#   Oatt_2 and Pqua_2 for its sums). Every observed value is checked against
#   the item's SPSS value labels. All respondents passed the deposit's
#   attention checks, and every Study 2 row passes the .sps manipulation-check
#   filter (asserted), so nothing is filtered here.
#
# Same-instrument merge (memory: collapse same-instrument samples): nine
#   blocks were given in both studies with identical item wording (the
#   variable label after its lead-in) and identical value labels (asserted below), so they ship as one table with cov_study.
#   Item codes are Study 2's (CREe_1 ...); the Study 1 header each one comes
#   from is in MERGED below. Study 2 ids are offset by 1000.
# evaluator_trust: TBB (benevolence, 3), TBI (integrity, 4), TBC (competence,
#   4) ship as one 11-item table because the Study 2 .sps scores them as one
#   TRUST mean.
# Two-item blocks (Transparency/Ptra, JR_P, JR_C, Recommendation/Orec,
#   Realism checks) are not shipped (datastandard: 2 items is not a scale).
#
# Covariates: cov_study (merged tables), cov_evaluator (human/hybrid/ai, from
#   the FL_33 block randomizer columns, as the .sps derive EVA), cov_message
#   (Study 2: none/outcome/counterfactual, as the .sps derive MSG),
#   cov_age (Study 2 only: Study 1's Age value labels
#   (code 8 = '18') contradict its values, so it is not carried), cov_gender.

import sys
from pathlib import Path

import pandas as pd
import pyreadstat

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

RAW = Path.home() / "irw-wt" / "hour-1110-c-raw" / "wjw7b6ghc8"
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
P = "gracio_michelon_2026_"


def rng(prefix, n):
    return [f"{prefix}_{i}" for i in range(1, n + 1)]


# table suffix -> (study 1 prefix, study 2 prefix, n items)
MERGED = {
    "emotional_reaction": ("Emotional", "CREe", 5),
    "ambiguity_reaction": ("Ambiguity", "CREa", 5),
    "eval_intelligence": ("Intelligence", "EVint", 5),
    "org_trust": ("Org_trust", "Otru", 6),
    "org_attractiveness": ("Org_attractiveness", "Oatt", 5),
    "org_prestige": ("Org_prestige", "Opre", 5),
    "reapplication": ("Reapplication", "Orea", 4),
    "job_pursuit": ("Pursuit", "Opur", 5),
    "litigation": ("Litigation", "Olit", 4),
}
STUDY1 = {
    "xai_satisfaction_s1": rng("XAI_satisfaction", 8),
    "xai_trust_s1": rng("XAI_trust", 6),
    "reductionism_quant": rng("Reductionism___Qu_Qa", 3),
    "reductionism_qual": [f"Reductionism___Qu_Qa_{i}" for i in (4, 5, 6)],
    "panas_pa": rng("PANAS___Positive", 5),
    "panas_na": rng("PANAS___Negative", 5),
    "spjs_job_info": rng("IK", 3),
    "spjs_chance_perform": rng("CP", 4),
    "spjs_reconsider": rng("RO", 5),
    "spjs_feedback": rng("Feedback", 3),
    "spjs_consistency": rng("Consistency", 3),
    "spjs_openness": rng("Openness", 4),
    "spjs_treatment": rng("Treatment", 5),
    "spjs_two_way_comm": rng("TW_C", 5),
    "spjs_propriety": rng("PQ", 3),
}
STUDY2 = {
    "eval_likeability": rng("EVlik", 5),
    "xai_satisfaction_s2": rng("XAI_S", 8),
    "decontextualization": rng("Pdec", 3),
    "quantification": rng("Pqua", 3),
    "fairness": rng("FAIR", 4),
    "evaluator_trust": rng("TBB", 3) + rng("TBI", 4) + rng("TBC", 4),
}

GENDER = {1: "female", 2: "male", 3: "non-binary", 4: "self-described"}


def load(n):
    df, meta = pyreadstat.read_sav(str(RAW / f"Study_{n}_data.sav"))
    return df, meta


def evaluator(df, keys):
    fl = [c for c in df.columns if c.startswith("FL_33_DO_")]
    assert df[fl].notna().sum(axis=1).eq(1).all()
    out = pd.Series(pd.NA, index=df.index, dtype="object")
    for c in fl:
        for k, v in keys.items():
            if c.endswith(k):
                out[df[c].notna()] = v
    assert out.notna().all()
    return out


def check_values(df, meta, cols):
    for c in cols:
        vl = set(meta.variable_value_labels[c])
        obs = set(df[c].dropna())
        assert obs <= vl, (c, obs - vl)


def prep():
    a, ma = load(1)
    b, mb = load(2)
    assert a.shape == (125, 144) and b.shape == (384, 110)
    assert (a["Consent_form"] == 1).all() and (b["CONSENT"] == 1).all()
    a["id"] = range(1, len(a) + 1)
    b["id"] = range(1001, 1001 + len(b))
    a["cov_study"] = 1
    b["cov_study"] = 2
    a["cov_evaluator"] = evaluator(a, {"Human": "human", "_AI": "ai",
                                       "Hybrid": "hybrid"})
    b["cov_evaluator"] = evaluator(b, {"Human": "human", "_AI": "ai",
                                       "Hybrid": "hybrid"})
    msg = pd.Series(pd.NA, index=b.index, dtype="object")
    for k, v in {"NO_message": "none", "Outcome": "outcome",
                 "Counterfactual": "counterfactual"}.items():
        hit = b[[c for c in b.columns if c.startswith(f"FL_33_DO_Vignette_{k}")]]
        msg[hit.notna().any(axis=1)] = v
    assert msg.notna().all()
    a["cov_message"] = pd.NA
    b["cov_message"] = msg
    # .sps: filter_$ = (MC1 = EVA) AND (MC2 = MSG)
    eva = b["cov_evaluator"].map({"human": 1, "hybrid": 2, "ai": 3})
    msg_code = msg.map({"none": 1, "outcome": 2, "counterfactual": 3})
    # every deposited Study 2 row passes both (the deposit is post-filter)
    assert ((b["MC1"] == eva) & (b["MC2"] == msg_code)).all()
    b["cov_age"] = b["Age"].where(b["Age"] >= 18)
    a["cov_age"] = pd.NA
    a["cov_gender"] = a["Gender_identity"].map(GENDER)
    b["cov_gender"] = b["Gender"].map(GENDER)
    return a, ma, b, mb


def melt(df, cols, covs, rename=None):
    d = df[["id"] + covs + cols]
    if rename:
        d = d.rename(columns=rename)
        cols = [rename[c] for c in cols]
    long = d.melt(id_vars=["id"] + covs, value_vars=cols, var_name="item",
                  value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    return long


def write(table, long, permitted):
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    long = long.dropna(axis=1, how="all")
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {table} {c.name}: {c.detail[:120]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {table}: {len(long)} responses, {long['id'].nunique()} "
          f"ids x {long['item'].nunique()} items")


def main():
    a, ma, b, mb = prep()
    la = dict(zip(ma.column_names, ma.column_labels))
    lb = dict(zip(mb.column_names, mb.column_labels))
    covs = ["cov_study", "cov_evaluator", "cov_message",
            "cov_age", "cov_gender"]
    for suf, (p1, p2, n) in MERGED.items():
        c1, c2 = rng(p1, n), rng(p2, n)
        for x, y in zip(c1, c2):
            # the item part after " - " (the lead-in differs: "decision-maker"
            # in Study 1, "evaluator that reviewed your application" in 2)
            assert (la[x].split(" - ")[-1].strip().lower()
                    == lb[y].split(" - ")[-1].strip().lower()), (x, y)
            assert ma.variable_value_labels[x] == mb.variable_value_labels[y]
        check_values(a, ma, c1)
        check_values(b, mb, c2)
        long = pd.concat([melt(a, c1, covs, dict(zip(c1, c2))),
                          melt(b, c2, covs)], ignore_index=True)
        write(P + suf, long[["id", "item", "resp"] + covs],
              {c: set(mb.variable_value_labels[c]) for c in c2})
    c_one = ["cov_evaluator", "cov_gender"]
    for suf, cols in STUDY1.items():
        check_values(a, ma, cols)
        write(P + suf, melt(a, cols, c_one)[["id", "item", "resp"] + c_one],
              {c: set(ma.variable_value_labels[c]) for c in cols})
    c_two = ["cov_evaluator", "cov_message", "cov_age", "cov_gender"]
    for suf, cols in STUDY2.items():
        check_values(b, mb, cols)
        write(P + suf, melt(b, cols, c_two)[["id", "item", "resp"] + c_two],
              {c: set(mb.variable_value_labels[c]) for c in cols})


if __name__ == "__main__":
    main()
