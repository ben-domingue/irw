#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10432410
# DOI: 10.1038/s41598-023-40048-1
#   "Development and validation of a sleep questionnaire, SNoRE 3.0, to evaluate
#   sleep in companion dogs" (Mondino, Ludwig, Menchaca, Russell, Simon,
#   Griffith, Kis, Lascelles et al., 2023), Scientific Reports 13:13340.
# Data: the article's supplementary file 41598_2023_40048_MOESM3_ESM.xlsx (Europe
#   PMC supplementaryFiles zip), "Confirmatory Analysis Data file. Scores for each
#   SNoRE question along with ID and age": 194 dogs x (Name, age, Q1, Q2, Q3, Q5,
#   Q6, Q7, Q8). MOESM1_ESM.pdf is the questionnaire: every question is answered
#   on a 1-10 scale between two anchors (e.g. Q1 "Falls asleep easily at bedtime"
#   .. "Takes much longer than usual to fall asleep").
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Sample: the paper's phase-2 (confirmatory factor analysis) sample: "194 owners
#   completed the questionnaire, the median age of the dogs was 6.90 years
#   (range 0.43-17.02)". `id` = the dog (the deposit's Name code T1..T194, the
#   number kept). Owners rate their dog: an animal table (the 100-id floor does
#   not apply to animal data, but this one clears it anyway).
#
# Table:
#   mondino_2023_snore  Q1, Q2, Q3, Q5, Q6, Q7, Q8  1-10 (higher = more sleep
#     disturbance). Items keep the questionnaire numbers; Q4 (dreaming) and Q9
#     (daytime naps) were not carried into this file.
#   Not shipped: MOESM4 (test-retest, 96 dogs). Its "time1" answers match the
#   confirmatory file for only 42-72% of the same-named dogs per item, so the
#   two files cannot be tied together as waves; MOESM2 (phase 1, 69 dogs, EEG
#   plus totals).
#
# Covariates: dog age in years (missing for some dogs, as the paper says).
#
# Item text: not shipped (cheap later). The SI PDF prints the full original
#   SNoRE wording with both anchors per question; the SNoRE comes from the same
#   lab (Knazovicky et al. 2015) and has no register row yet.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "mondino_2023"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10432410/supplementaryFiles"
FILE = "41598_2023_40048_MOESM3_ESM.xlsx"
NAME = "mondino_2023_snore"
ITEMS = ["Q1", "Q2", "Q3", "Q5", "Q6", "Q7", "Q8"]


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        p.write_bytes(z.read([n for n in z.namelist() if n.endswith(FILE)][0]))
    return p


def main() -> None:
    d = pd.read_excel(fetch(), header=1)
    assert list(d.columns) == ["Name", "Age (years)"] + ITEMS, list(d.columns)
    assert len(d) == 194 and d["Name"].is_unique
    assert d["Name"].str.fullmatch(r"T\d+").all()
    d["id"] = d["Name"].str[1:].astype(int)
    d = d.rename(columns={"Age (years)": "cov_age"})
    t = d.melt(id_vars=["id", "cov_age"], value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "cov_age"]].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()

    pv = {i: set(range(1, 11)) for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:150]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
