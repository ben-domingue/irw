#!/usr/bin/env python3
# Source: https://osf.io/gsr7j/  (Healthcare Experiences Among Adults with hEDS
#   and HSD in the US: Public Data)
#   Data_files/Hypermobility Survey OSF_data.csv  https://osf.io/download/xenyq/
#   Data_files/Hypermobility Survey OSF_key.csv   https://osf.io/download/2unea/
# Paper DOI: 10.1080/09638288.2023.2176554
#   Estrella, E., & Frazier, P. A. (2024). Healthcare experiences among adults
#   with hypermobile Ehlers-Danlos syndrome and hypermobility spectrum disorder
#   in the United States. Disability and Rehabilitation, 46(4), 731-740
#   (online 2023).
# Data DOI: 10.17605/OSF.IO/GSR7J
# License: CC BY 4.0 (OSF node gsr7j, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Sample: 2,125 U.S. adults with hEDS or HSD, online survey Feb-Mar 2022; the
#   deposit is the authors' cleaned analytic file (README: "Original N = 2,369.
#   Final analytic N = 2,125"). Blank cells (" ") are missing. 64 respondents
#   stopped early (Progress 43 or 57); their answered items are kept.
#
# Tables (item wording and codes from the deposit's key file):
#   estrella_2023_promis29: PROMIS-29 Profile v2.0, the 28 domain items:
#     physical function, anxiety, depression, fatigue, sleep disturbance, social
#     roles and pain interference, four items each, 1-5. Source
#     columns are renamed to domain_k (the source spells two fatigue columns
#     `promsi29_`; `fatig1_1, fatig1_2, fatig2_1, fatig2_2` -> fatigue_1..4,
#     `sleep1_1..3, sleep2_1` -> sleep_1..4). NOT shipped: the 29th item, pain
#     intensity (`promis29_pain_intens_1`, a single 0-10 rating; the key says
#     "1 to 10" but 0 occurs 8 times). It is a separate construct on a separate
#     scale, which irw-validate's construct check refuses to mix into this
#     table, and a one-item table of it is not worth having.
#   estrella_2023_promis_se: PROMIS Self-Efficacy for Managing Symptoms short
#     form 4a, 4 items, 1-5.
#   estrella_2023_psq18: Patient Satisfaction Questionnaire short form (PSQ-18),
#     18 items, 1 = strongly agree ... 5 = strongly disagree, numbered 1-18 in
#     the instrument's order (source psq18_1_1..psq18_3_6, three blocks of six;
#     the source's own reversed items 1_1, 1_2, 1_3, 1_5, 1_6, 2_2, 2_5, 3_3, 3_6
#     are exactly PSQ-18 items 1, 2, 3, 5, 6, 8, 11, 15, 18, the ones the scoring
#     manual reverses, which confirms the numbering).
#   estrella_2023_hakim5: the five-item hypermobility questionnaire (Hakim &
#     Grahame 2003), 0 = no, 1 = yes.
#
# Reverse keying: every item is shipped as RAW responses. The deposit's
#   `*_rev` columns (PROMIS sleep 1, social 1-4; PSQ-18 items listed above) are
#   the authors' reverse-scored copies and are not used. Domain sums and PSQ
#   subscale means are composites and are skipped.
#
# Item text: NOT extracted. PROMIS wording is withdrawn from IRW on rights
#   grounds (ruling 2026-09-05), and this script ships response data only.
#
# Covariates: age (values under 18 set missing: 18+ was an inclusion criterion),
#   hEDS diagnosis and HSD diagnosis (yes/no as asked), gender (the single option
#   chosen, "multiple" when more than one was checked), employment, income and
#   area (labels from the key). Education is left out: the key's codes do not
#   match the data (it assigns 6 twice and has no 8, which occurs 122 times).
#   Race, sexuality and free-text columns are not carried; ResponseId is dropped
#   and id is the row index.

import re
import sys
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL_DATA = "https://osf.io/download/xenyq/"
URL_KEY = "https://osf.io/download/2unea/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PROMIS29 = {}
for dom, cols in [
        ("phys", [f"promis29_phys_{i}" for i in range(1, 5)]),
        ("anx", [f"promis29_anx_{i}" for i in range(1, 5)]),
        ("dep", [f"promis29_depres_{i}" for i in range(1, 5)]),
        ("fatigue", ["promsi29_fatig1_1", "promsi29_fatig1_2",
                     "promis29_fatig2_1", "promis29_fatig2_2"]),
        ("sleep", ["promis29_sleep1_1", "promis29_sleep1_2",
                   "promis29_sleep1_3", "promis29_sleep2_1"]),
        ("social", [f"promis29_social_{i}" for i in range(1, 5)]),
        ("pain_interf", [f"promis29_pain_interf_{i}" for i in range(1, 5)])]:
    for k, c in enumerate(cols, 1):
        PROMIS29[c] = f"promis29_{dom}_{k}"
SE = {f"promis_sx_{i}": f"promis_se_{i}" for i in range(1, 5)}
PSQ = {f"psq18_{b}_{k}": f"psq18_{(b - 1) * 6 + k}" for b in (1, 2, 3) for k in range(1, 7)}
HAKIM = {f"inclusion_hakim5_{i}": f"hakim5_{i}" for i in range(1, 6)}
PSQ_REV_SRC = {"psq18_1_1", "psq18_1_2", "psq18_1_3", "psq18_1_5", "psq18_1_6",
               "psq18_2_2", "psq18_2_5", "psq18_3_3", "psq18_3_6"}
PSQ_REV_MANUAL = {1, 2, 3, 5, 6, 8, 11, 15, 18}
PSQ_SUB = {"general_satisfaction": (3, 17), "technical_quality": (2, 4, 6, 14),
           "interpersonal_manner": (10, 11), "communication": (1, 13),
           "financial": (5, 7), "time_with_doctor": (12, 15),
           "accessibility": (8, 9, 16, 18)}


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def codes(values: str) -> dict:
    parts = re.split(r",\s*(?=\d+=)", values.strip())
    return {int(k): v.strip() for k, v in (p.split("=", 1) for p in parts)}


def finish(t, name, pv, cl):
    t = t.copy()
    assert (t["resp"] == t["resp"].round()).all()
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    checks = run_qc(t, permitted_values=pv, item_constructs=cl)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=name, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(BytesIO(fetch(URL_DATA)), dtype=str, keep_default_na=False)
    key = pd.read_csv(BytesIO(fetch(URL_KEY)), encoding="latin1").set_index("Name")
    assert d.shape == (2125, 135), d.shape
    d = d.apply(lambda s: s.str.strip()).replace("", pd.NA)

    # PSQ-18 numbering check: the source's reversed items are the manual's
    rev = {c[:-4] for c in d.columns if c.startswith("psq18_") and c.endswith("_rev")}
    assert rev == PSQ_REV_SRC
    assert {int(PSQ[c].split("_")[1]) for c in rev} == PSQ_REV_MANUAL
    # PSQ key wording spot checks
    assert "explaining the reason for medical tests" in key.Label["psq18_1_1"]
    assert "whenever I need it" in key.Label["psq18_3_6"]
    assert "dissatisfied" in key.Label["psq18_3_5"]

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    age = pd.to_numeric(d["demo_age"])
    d["cov_age"] = age.where(age >= 18)
    print(f"  cov_age: {int(((age < 18)).sum())} value(s) under 18 set missing")
    yn = {"1": "yes", "2": "no"}
    d["cov_heds_dx"] = d["inclusion_eds"].map(yn)
    d["cov_hsd_dx"] = d["inclusion_hsd"].map(yn)
    glab = {i: key.Label[f"demo_gender_{i}"].split("Selected Choice")[-1].strip()
            for i in range(1, 10)}
    glab[8] = "Gender not listed"
    g = d[[f"demo_gender_{i}" for i in range(1, 10)]].apply(pd.to_numeric).fillna(0)
    n = g.sum(axis=1)
    one = g.idxmax(axis=1).str.rsplit("_", n=1).str[1].astype(int).map(glab)
    d["cov_gender"] = one.where(n == 1, "multiple").where(n > 0)
    for src, dst in (("demo_employment", "cov_employment"),
                     ("demo_income", "cov_income"), ("demo_area", "cov_area")):
        m = codes(key.Values[src])
        vals = set(pd.to_numeric(d[src]).dropna().astype(int))
        assert vals <= set(m), (src, vals - set(m))
        d[dst] = pd.to_numeric(d[src]).map(m)
    covs = ["cov_age", "cov_gender", "cov_heds_dx", "cov_hsd_dx",
            "cov_employment", "cov_income", "cov_area"]

    def long(cmap):
        x = d[["id"] + list(cmap) + covs].rename(columns=cmap)
        x = x.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        x["resp"] = pd.to_numeric(x["resp"])
        x = x.dropna(subset=["resp"])
        return x[["id", "item", "resp"] + covs]

    pv = {v: set(range(1, 6)) for v in PROMIS29.values()}
    cl = {v: v.rsplit("_", 1)[0] for v in PROMIS29.values()}
    finish(long(PROMIS29), "estrella_2023_promis29", pv, cl)

    finish(long(SE), "estrella_2023_promis_se",
           {v: set(range(1, 6)) for v in SE.values()},
           {v: "self_efficacy_managing_symptoms" for v in SE.values()})

    cl = {f"psq18_{i}": sub for sub, idx in PSQ_SUB.items() for i in idx}
    assert len(cl) == 18
    finish(long(PSQ), "estrella_2023_psq18",
           {v: set(range(1, 6)) for v in PSQ.values()}, cl)

    finish(long(HAKIM), "estrella_2023_hakim5",
           {v: {0, 1} for v in HAKIM.values()},
           {v: "joint_hypermobility" for v in HAKIM.values()})


if __name__ == "__main__":
    convert()
