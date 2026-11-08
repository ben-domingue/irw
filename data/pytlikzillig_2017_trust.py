#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0175387
# DOI: 10.1371/journal.pone.0175387
# Paper: PytlikZillig LM, Kimbrough CD, Shockley E, Neal TMS, Herian MN,
#   Hamm JA, Bornstein BH, Tomkins AJ (2017). A longitudinal and experimental
#   study of the impact of knowledge on the bases of institutional trust.
#   PLoS ONE 12(4): e0175387.
# Data: PLOS Supporting Information S3 File "Longitudinal data"
#   (journal.pone.0175387.s003, .csv, wide, SAS "." = missing); S1 File
#   "Appendix of measures" gives the wording. 185 University of Nebraska
#   science students, six online surveys about 3 months apart (R1-R6).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 6.
#
# FOUR output tables, long over the six surveys (`wave` 1-6):
#   pytlikzillig_2017_institutional_trust  4 unspecified-confidence items
#     (USConf) and 40 trustworthiness items in 12 constructs (legitimacy,
#     respect, voice, distributive justice, loyalty, values, benevolence,
#     competence, integrity, obligation, bias, cynicism), each rated for
#     both water-regulatory institutions: the Nebraska Department of Natural
#     Resources (item prefix NDNR_) and the Natural Resources Districts
#     (NRD_). 88 items, 1-7 agreement. The paper combined the two targets.
#     The deposit's reversed copy of PfI4 is not used (see below).
#   pytlikzillig_2017_dispositional_trust  Dt1-Dt9, 1-7.
#   pytlikzillig_2017_government_trust  7 items, trust in the federal, state
#     and local government, the university administration, the Supreme
#     Court, the military and the President, 1-7. The two items about the
#     water institutions themselves are left out, as in the paper (S2 Note H).
#   pytlikzillig_2017_water_knowledge  objective knowledge quiz, scored 0/1
#     by the deposit (KNnRmCorrect). Surveys 1-2 used KN1-KN12; surveys 3-6
#     replaced five items (KN13-KN18), so items are keyed by their number.
#     KN14 is dropped: every one of its answers is scored correct.
#     Knowledge cells are kept only for surveys the person took (any 1-7
#     item of that survey answered): the deposit fills 0 for some absent
#     surveys, which would otherwise read as all wrong.
# Coding: every 1-7 item is DEPOSITED 1 = strongly agree ... 7 = strongly
#   disagree (the survey platform's order); the authors' SAS file builds
#   each scale as 8 minus the item mean. The paper codes 1 = strongly
#   disagree, 7 = strongly agree, so this script stores 8 - x for every 1-7
#   item: that is the answer in the paper's direction, with no reverse
#   keying (bias item PfI4 and the cynicism items stay as answered).
# Checks against Table 1 (survey 1): dispositional trust mean 5.232,
#   governmental trust mean 4.948, objective knowledge mean 3.692 (asserted).
# Dropped: DL1-DL5 (a 1-7 block not in the appendix of measures), the
#   subjective-knowledge items, all scale scores, gender and ethnicity
#   (unlabelled codes), the condition codes (ManipCond3 / ManipInfo: the
#   mapping to the paper's control vs experimental groups is not stated).
# `id` is the deposit's ResponseID (1-185, a row number). cov_age kept.
#
# Item text: NOT SHIPPED. The S1 File appendix carries the wording of
#   every response item ([institution] placeholder), CC BY 4.0. Cheap.

import io
import os
import re
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0175387.s003"
RAW = os.environ.get("PYTLIKZILLIG_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
GOV = ["Fed", "Stat", "Loc", "UNL", "USSC", "Mil", "Pres"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src, na_values=["."], keep_default_na=True)


def stack(df, pattern, rename):
    """pattern has one group for the item and one for the wave."""
    parts = []
    for c in df.columns:
        m = re.fullmatch(pattern, c)
        if m:
            p = df[["id", "cov_age", c]].rename(columns={c: "resp"})
            p["item"] = rename(m.group(1))
            p["wave"] = int(m.group(2))
            parts.append(p)
    long = pd.concat(parts, ignore_index=True)
    return long[long["resp"].notna()]


def save(long, name, values):
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(values), (name, set(long["resp"]))
    long = long[["id", "item", "resp", "wave", "cov_age"]].sort_values(["id", "wave", "item"])
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} waves={sorted(long['wave'].unique())}")


def convert():
    df = load().copy()
    assert df.shape == (185, 978), df.shape
    assert df["ResponseID"].is_unique
    df["id"] = df["ResponseID"].astype(int)
    df["cov_age"] = df["Age"]

    # Table 1 checks, survey 1.
    likert = [c for c in df.columns if re.fullmatch(r"(?:(?:NDNR|NRD)_[A-Za-z]+\d|Dt\d|Trus[A-Za-z]+)R[1-6]", c)]
    vals = pd.Series(df[likert].values.ravel()).dropna()
    assert set(vals) <= set(range(1, 8)), set(vals)
    rev = 8 - df[likert]
    df = pd.concat([df.drop(columns=likert), rev], axis=1)
    # The deposit's own reversed PfI4 copy equals 8 - PfI4: confirms the flip.
    assert (df["NDNR_PfI4R1"].dropna() == df["NDNR_PfI4R1rev"].dropna()).all()
    dt1 = df[[f"Dt{i}R1" for i in range(1, 10)]].mean(axis=1)
    gv1 = df[[f"Trus{g}R1" for g in GOV]].mean(axis=1)
    assert round(dt1.mean(), 2) == 5.23, dt1.mean()
    assert round(gv1.mean(), 2) == 4.95, gv1.mean()

    inst = stack(df, r"((?:NDNR|NRD)_[A-Za-z]+\d)R([1-6])", lambda s: s)
    assert inst["item"].nunique() == 88
    save(inst, "pytlikzillig_2017_institutional_trust", range(1, 8))

    save(stack(df, r"(Dt\d)R([1-6])", lambda s: s), "pytlikzillig_2017_dispositional_trust", range(1, 8))

    gov = stack(df, r"Trus(Fed|Stat|Loc|UNL|USSC|Mil|Pres)R([1-6])", lambda s: "Trus" + s)
    assert gov["item"].nunique() == 7
    save(gov, "pytlikzillig_2017_government_trust", range(1, 8))

    kn = stack(df, r"(KN\d+)R([1-6])Correct", lambda s: s)
    took = set()
    for w in range(1, 7):
        cols = [c for c in df.columns if re.fullmatch(rf"(?:(?:NDNR|NRD)_[A-Za-z]+\d|Dt\d|Trus[A-Za-z]+|DL\d)R{w}", c)]
        took |= {(i, w) for i in df.loc[df[cols].notna().any(axis=1), "id"]}
    kn = kn[[(i, w) in took for i, w in zip(kn["id"], kn["wave"])]]
    # KN14 (surveys 3-6) is scored correct for every one of its answers:
    # a scoring artifact or a give-away item, either way no information.
    assert set(kn.loc[kn["item"] == "KN14", "resp"]) == {1}
    kn = kn[kn["item"] != "KN14"]
    k1 = kn[kn["wave"] == 1].groupby("id")["resp"].sum()
    assert round(k1.mean(), 2) == 3.69, k1.mean()
    save(kn, "pytlikzillig_2017_water_knowledge", [0, 1])


if __name__ == "__main__":
    convert()
