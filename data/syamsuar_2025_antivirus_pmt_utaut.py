#!/usr/bin/env python3
# Source: https://zenodo.org/records/15671603
# DOI: 10.5281/zenodo.15671603 (dataset; no paper DOI on the record)
#   Syamsuar, Dedy & Putra, Ryan Rajendra (2025). "Evolution of Cyber Threats: The
#   Critical Role of Antivirus in Overcoming Current Digital Security Challenges"
#   [data set]. Zenodo.
# Data: "Data mentah after UG1.xlsx" (one sheet): 277 Indonesian internet users x ID
#       (1-316, unique; the gaps are respondents removed before deposit) and 64 items
#       in 13 five-item blocks (MV has 4), all 1-5, no missing cells. No codebook.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Levels checked: xlsx headers are codes only (no labels, no
#   codebook); the questionnaire is not in the deposit.
#
# Constructs: the record's abstract names a PMT + UTAUT model of antivirus adoption
#   with response efficacy, performance expectancy, social influence, facilitating
#   conditions, effort expectancy, perceived vulnerability, threat severity,
#   behavioural intention, protective behaviour and usage. Block prefixes are the
#   standard abbreviations of those constructs (PS perceived severity, PV perceived
#   vulnerability, RE response efficacy, SE self-efficacy, RC response cost -- the
#   five PMT appraisals; PE, EE, SI, FC -- UTAUT; BI, PB, UB) -- an inference from the
#   abstract, recorded in data_notes.
# Tables: syamsuar_2025_<suffix> for each block below, items as stored (PS1-5 ...).
# Not shipped: MV1-4 -- the abstract names no construct that "MV" can stand for, so
#   what it measures is unknown.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "syamsuar_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/15671603/files/Data%20mentah%20after%20UG1.xlsx/content"
BLOCKS = {"PS": "perceived_severity", "PV": "perceived_vulnerability",
          "RE": "response_efficacy", "SE": "self_efficacy", "RC": "response_cost",
          "PE": "performance_expectancy", "EE": "effort_expectancy",
          "SI": "social_influence", "FC": "facilitating_conditions",
          "BI": "behavioral_intention", "PB": "protective_behavior", "UB": "usage_behavior"}


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
    assert d.shape == (277, 65) and d["ID"].is_unique
    want = {f"{p}{i}" for p in BLOCKS for i in range(1, 6)}
    mv = [f"MV{i}" for i in range(1, 5)]
    assert set(d.columns) == {"ID"} | want | set(mv)
    print(f"  [skip] {mv}: construct undocumented")
    d = d.rename(columns={"ID": "id"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    names = []
    for pre, suf in BLOCKS.items():
        name = f"syamsuar_2025_{suf}"
        names.append(name)
        its = [f"{pre}{i}" for i in range(1, 6)]
        t = d.melt(id_vars=["id"], value_vars=its, var_name="item", value_name="resp")
        assert t["resp"].isin(range(1, 6)).all(), name
        t = t[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: {1, 2, 3, 4, 5} for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert len(set(names)) == len(names) and all(len(n) <= 40 for n in names)


if __name__ == "__main__":
    main()
