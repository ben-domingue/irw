#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/GTJZQA
# DOI: 10.7910/DVN/GTJZQA (dataset); paper: Trusz, S., & Demeshkant, N. (2025).
#   "Teachers' Technological, Pedagogical, and Content Knowledge related to Artificial
#   Intelligence as a Protective Factor Against Technostress and Techno-anxiety" (no
#   paper DOI on the Dataverse record).
# Data: Harvard Dataverse 10.7910/DVN/GTJZQA (Slawomir Trusz, 2025),
#       "Trusz & Demeshkant2025_Techno-anxiety, Technostress & AI-TPACK_Data_160425-2.xlsx"
#       (file 11196869): 419 Polish pre-service and in-service teachers x 69 columns.
#       No codebook.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: xlsx headers only (no variable or value
#   labels, no codebook); headers are positional ("AI-TK1", "ATAS3", "PEFST5_NST1").
#
# Tables:
#   trusz_2025_ai_tpack         AI-TK1-5, AI-TPK1-7, AI-TCK1-4, AI-TPACK1-7, Ethics1-4
#                               (27 items, 1-7): intelligent-TPACK (AI-related
#                               technological, pedagogical and content knowledge, plus
#                               ethics)
#   trusz_2025_techno_anxiety   ATAS1-11 (1-5); ATAS_Average = their mean (asserted)
#   trusz_2025_technostress     PEFST1-8 (0-4): ADT1-4 and NST1-4 subscales (header
#                               suffixes); Technostress_Total = their mean (asserted)
# Skipped: TimSignature (submission timestamp), free-text Major, SubjectTaught and
#   AI_Tool_Example, and the ten subscale/total means.
# Covariates: cov_group (1 = pre-service, 2 = in-service, from the header
#   "Group1PST2IST"), cov_gender (0 male, 1 female, 2 other, from the header), age,
#   residence (1 village, 2 town up to 50k, 3 50-100k, 4 above 100k, from the header),
#   college level (Polish label), year of study, seniority (years), AI use (0 no, 1 yes,
#   2 yes/no, from the header).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "trusz_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/11196869?format=original"

TPACK = ([f"AI-TK{i}" for i in range(1, 6)] + [f"AI-TPK{i}" for i in range(1, 8)]
         + [f"AI-TCK{i}" for i in range(1, 5)] + [f"AI-TPACK{i}" for i in range(1, 8)]
         + [f"Ethics{i}" for i in range(1, 5)])
ATAS = [f"ATAS{i}" for i in range(1, 12)]
PEFST = [f"PEFST{i}_ADT{i}" for i in range(1, 5)] + [f"PEFST{i}_NST{i-4}" for i in range(5, 9)]
TABLES = {"trusz_2025_ai_tpack": (TPACK, range(1, 8)),
          "trusz_2025_techno_anxiety": (ATAS, range(1, 6)),
          "trusz_2025_technostress": (PEFST, range(0, 5))}
COVS = {"Group1PST2IST": "cov_group", "Gender0M1F2Other": "cov_gender", "Age": "cov_age",
        "Residence_1V2_To50_3From50do100_4Above100000 ": "cov_residence",
        "CollegeLevel": "cov_college_level", "YearOfStudy": "cov_year_of_study",
        "Seniority": "cov_seniority_years", "UsingAI_0No1Yes2Yes/No": "cov_uses_ai"}
SKIP = {"TimSignature": "timestamp", "Major": "free text", "SubjectTaught": "free text",
        "AI_Tool_Example": "free text"}
COMPOSITES = ["ATAS_Average", "Technostress_Total", "Technostress_ADT", "TechnostressNST",
              "AI-TPACK_Totl", "AI-TK", "AI-TPK", "AI-TCK", "AI-TPACK", "Ethics"]


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
    assert d.shape == (419, 69), d.shape
    expected = {"id"} | set(COVS) | set(SKIP) | set(COMPOSITES) | set(TPACK) | set(ATAS) | set(PEFST)
    assert set(d.columns) == expected, set(d.columns) ^ expected
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    print(f"  skip {len(COMPOSITES)} subscale/total means")
    assert (d[ATAS].mean(axis=1) - d["ATAS_Average"]).abs().max() < 1e-9
    assert (d[PEFST].mean(axis=1) - d["Technostress_Total"]).abs().max() < 1e-9
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    d["cov_college_level"] = d["cov_college_level"].str.strip()
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        assert t["resp"].isin(list(rng)).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
