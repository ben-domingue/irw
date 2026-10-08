#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Cognitive_Load_and_Error_patterns_as_predictors_of_Achievement_in_Algebraic_word_Problems/34032243
# DOI: 10.6084/m9.figshare.34032243.v1 (dataset; no paper DOI on the record)
#   Adebiyi, Akeem (2026). "Cognitive Load and Error patterns as predictors of
#   Achievement in Algebraic word Problems" [data set]. figshare.
# Data: Data_CognitiveLoadErrorPatternsAWPS.csv: 285 Junior Secondary School
#       students in Lagos State, Nigeria x Student_Code, Gender, AWPS_Score (test
#       total), Cognitive_Load (one Paas 1-9 rating), three error-type indicators,
#       ErrorPattern_Total, Fluency1-4 (the four Representational Fluency Task
#       items, scored 0/1), RF_Total, Reversed_RF_Total. Instruments_...AWPS.pdf
#       prints the test, the Paas scale and the four RFT problems.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped (instrument PDF in the deposit; the CSV header's number and
#   direction -- "Fluency1 (word->eq)" ... -- name the PDF's Problem 1-4 and its task).
#
# Shipped: adebiyi_2026_representational_fluency -- Fluency1-4, 0/1 (item codes are
#   the header up to the space: "Fluency1 (word→eq)" -> "Fluency1"). Two missing
#   cells (one each on Fluency1 and Fluency3) are dropped. RF_Total equals the sum
#   of the four items on every row.
# Not shipped: AWPS_Score (test total; the ten problem scores are not deposited),
#   Cognitive_Load (a single rating -- a one-item scale), the three error indicators
#   and ErrorPattern_Total (person-level coded error types across the whole test, not
#   item responses), RF_Total / Reversed_RF_Total (sums).
# Covariates: cov_gender (1/2 as deposited; coding not given).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "adebiyi_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"data.csv": "https://ndownloader.figshare.com/files/69495237",
         "instruments.pdf": "https://ndownloader.figshare.com/files/69495567"}
NAME = "adebiyi_2026_representational_fluency"
SKIP = {"AWPS_Score": "test total; problem scores not deposited",
        "Cognitive_Load": "single Paas rating (one-item scale)",
        "Translational_Error": "person-level error-type indicator, not an item",
        "Operational_Error": "person-level error-type indicator, not an item",
        "Reversal_Error": "person-level error-type indicator, not an item",
        "ErrorPattern_Total": "sum", "RF_Total": "sum of Fluency1-4",
        "Reversed_RF_Total": "reflected sum"}


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for f, u in FILES.items():
        p = RAW_DIR / f
        if not p.exists():
            r = requests.get(u, headers=UA, timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
    return RAW_DIR / "data.csv"


def main() -> None:
    d = pd.read_csv(fetch(), encoding="utf-8-sig")
    assert d.shape == (285, 14) and d["Student_Code"].is_unique
    flu = [c for c in d.columns if c.startswith("Fluency")]
    ren = {c: c.split(" ")[0] for c in flu}
    assert list(ren.values()) == ["Fluency1", "Fluency2", "Fluency3", "Fluency4"]
    assert set(d.columns) == {"Student_Code", "Gender"} | set(flu) | set(SKIP)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert (d[flu].sum(axis=1) == d["RF_Total"]).all()
    d = d.rename(columns={"Student_Code": "id", "Gender": "cov_gender", **ren})
    items = list(ren.values())
    t = d.melt(id_vars=["id", "cov_gender"], value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin([0, 1]).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "cov_gender"]].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
    pv = {i: {0, 1} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
