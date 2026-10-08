#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WABYKR
# DOI: 10.7910/DVN/WABYKR (dataset; paper "What predicts changes in perceived teacher work
#   ability?" -- no DOI on the record)
#   The record's author and depositor are anonymised ("A, A", Masaryk University); the
#   dataset contact is hlado@phil.muni.cz (Petr Hlado), so the tables are named hlado_2025.
# Data: Harvard Dataverse 10.7910/DVN/WABYKR (2025), "Dataset_What predicts changes in
#       PTWA.xlsx" (file 12139759): 613 Czech primary and lower-secondary teachers x 189
#       columns, two waves (V1 autumn 2023, V2 autumn 2024; 529 answered V2). No codebook.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: xlsx headers only (V1_PTWA_TO_1,
#   V1_Self_efficacy_01, V1_CPQ_06_Quantitative_demands ...), no labels, no codebook.
#   The Czech wording is not in the deposit.
#
# Tables (wave 1 = V1, 2 = V2; item codes = headers without the V1_/V2_ prefix):
#   hlado_2025_ptwa               PTWA_{TO,IM,N-TR,T-SI,NDS}_k (20 items)  1-7  perceived
#                                 teacher work ability (subscale prefixes as in the file)
#   hlado_2025_self_efficacy      Self_efficacy_01-12                     1-9
#   hlado_2025_burnout            Burnout_01-14                           1-7
#   hlado_2025_copsoq             CPQ_01-28 (influence, quantitative/cognitive/emotional
#                                 demands, sense of community, supervisor/colleague support,
#                                 work-life conflict; suffix names the subscale)  1-5
#   hlado_2025_work_engagement    Work_engagement_01-03                   1-5
#   hlado_2025_turnover           Turnover_01-03                          1-6
#   hlado_2025_locus_of_control   Locus_of_control_01-08 (wave 1 only)    1-6
#   hlado_2025_job_insecurity     Job_insecurity_01-02 (wave 1 only)      1-5
# Skipped: Health_total/physical/mental (three single-item self-ratings), free-text
#   V1_Comment, timestamps.
# Covariates: the source mixes Czech and English answer strings; mapped to English:
#   cov_gender (W/zena = female, M/muz = male, jine = other), cov_age, cov_years_practice,
#   cov_job_position, cov_class_teacher, cov_mentor_teacher, cov_caring (wave 1).
# id = row order.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "hlado_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/12139759?format=original"

BLOCKS = {  # table: (header stem regex, permitted range)
    "hlado_2025_ptwa": (r"PTWA_", range(1, 8)),
    "hlado_2025_self_efficacy": (r"Self_efficacy_", range(1, 10)),
    "hlado_2025_burnout": (r"Burnout_", range(1, 8)),
    "hlado_2025_copsoq": (r"CPQ_", range(1, 6)),
    "hlado_2025_work_engagement": (r"Work_engagement_", range(1, 6)),
    "hlado_2025_turnover": (r"Turnover_", range(1, 7)),
    "hlado_2025_locus_of_control": (r"Locus_of_control_", range(1, 7)),
    "hlado_2025_job_insecurity": (r"Job_insecurity_", range(1, 6)),
}
GENDER = {"W": "female", "žena": "female", "M": "male", "muž": "male",
          "jiné": "other"}
JOB = {"lower secondary teacher": "lower secondary teacher", "primary teacher": "primary teacher",
       "asistent/ka pedagoga": "teaching assistant",
       "učitel/ka nerozlišeno": "teacher (level not specified)",
       "vychovatel/ka": "after-school educator", "poradenský pracovník": "counsellor",
       "ředitel/ka": "head teacher", "zástupce/kyně ředitele": "deputy head",
       "učitel/ka MŠ": "kindergarten teacher", "jiné": "other"}
CARE = {"I care for a dependent child (up to the age of 26)": "child",
        "pečuji o nezaopatřené dítě (nejdéle do 26. roku věku)": "child",
        "I care for aging parents or other family members.": "parents/family",
        "pečuji o stárnoucí rodiče či jiné rodinné příslušníky": "parents/family",
        "I care for a dependent child as well as aging parents or other family members.": "child and parents/family",
        "pečuji o nezaopatřené dítě i o stárnoucí rodiče či jiné rodinné příslušníky": "child and parents/family",
        "None of the above.": "none", "žádná z uvedených možností": "none"}
COVS = ["cov_gender", "cov_age", "cov_years_practice", "cov_job_position",
        "cov_class_teacher", "cov_mentor_teacher", "cov_caring"]


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (613, 189), d.shape
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d["cov_gender"] = d["Gender"].map(GENDER)
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_years_practice"] = d["Years_of_practice"]
    d["cov_job_position"] = d["Job_position"].map(JOB)
    d["cov_class_teacher"] = d["Class_teacher"]
    d["cov_mentor_teacher"] = d["Mentor_teacher"]
    d["cov_caring"] = d["V1_Caring_for_close_person"].map(CARE)
    for c in ("cov_gender", "cov_job_position", "cov_caring"):
        assert d[c].notna().all(), c
    src_cov = {"Gender", "Age", "Years_of_practice", "Job_position", "Class_teacher",
               "Mentor_teacher", "V1_Caring_for_close_person"}
    skip = {"V2_Caring_for_close_person": "wave-2 repeat of a covariate",
            "V1_Comment": "free text", "V1_Timestamp": "timestamp", "V2_Timestamp": "timestamp"}
    skip.update({f"V{w}_Health_{h}": "single-item self-rating" for w in (1, 2)
                 for h in ("total", "physical", "mental")})
    item_cols = {}
    for name, (stem, _) in BLOCKS.items():
        item_cols[name] = [c for c in d.columns if c[:3] in ("V1_", "V2_") and c[3:].startswith(stem)]
    used = src_cov | set(skip) | {c for cs in item_cols.values() for c in cs} | {"id"} | set(COVS)
    assert used == set(d.columns), set(d.columns) ^ used
    for c, why in skip.items():
        print(f"  skip {c}: {why}")
    names = list(BLOCKS)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (stem, rng) in BLOCKS.items():
        t = d.melt(id_vars=["id"] + COVS, value_vars=item_cols[name], var_name="src",
                   value_name="resp").dropna(subset=["resp"])
        t["wave"] = t["src"].str[1].astype(int)
        t["item"] = t["src"].str[3:]
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "wave"] + COVS].sort_values(["id", "wave", "item"])
        t = t.reset_index(drop=True)
        assert not t.duplicated(["id", "item", "wave"]).any() and t["id"].nunique() >= 100
        assert t["item"].nunique() > 1
        pv = {i: set(rng) for i in t["item"].unique()}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn" and c.name != "dup_id_item":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()} "
              f"ids/wave={t.groupby('wave')['id'].nunique().to_dict()}")


if __name__ == "__main__":
    main()
