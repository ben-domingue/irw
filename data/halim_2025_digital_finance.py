#!/usr/bin/env python3
# Source: https://zenodo.org/records/14718556
# DOI: 10.5281/zenodo.14718556 (dataset; the record links no paper)
#   Halim, E., Edita, F., & Tosin, A. D. P. (2025). User Perception of the Digital
#   Financial Services and Its Impact on Financial Well-Being [Data set]. Zenodo.
# Data: "DATA KELOMPOK 7.csv" -- 370 users of digital financial services (Indonesia;
#       purposive sample via Google Forms) x 35 items in seven five-item blocks (1-5) and
#       STDDEV.P (each respondent's response SD, a straight-lining screen).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Plain CSV with positional codes; no labels, no questionnaire.
#
# Constructs: the record names financial literacy, financial skills, digital finance,
#   financial stress, financial self-efficacy, financial behaviour and financial
#   well-being; the block prefixes map onto them as FLC (literacy), FSK (skills), DFC
#   (digital finance), FSS (stress), FSE (self-efficacy), FBR (behaviour), FWB (well-being).
#   This mapping is read from the abbreviations (the record has no codebook) and is
#   recorded as a data note.
# Tables (1-5): halim_2025_fin_literacy (FLC1-5), halim_2025_fin_skills (FSK1-5),
#   halim_2025_digital_finance (DFC1-5), halim_2025_fin_stress (FSS1-5),
#   halim_2025_fin_self_efficacy (FSE1-5), halim_2025_fin_behavior (FBR1-5),
#   halim_2025_fin_wellbeing (FWB1-5).
# Skipped: STDDEV.P (derived).
# id: row index (no identifier). No covariates.

import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "z14718556"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/14718556/files/DATA%20KELOMPOK%207.csv/content"
P = "halim_2025_"
RANGE = range(1, 6)
TABLES = {"fin_literacy": "FLC", "fin_skills": "FSK", "digital_finance": "DFC",
          "fin_stress": "FSS", "fin_self_efficacy": "FSE", "fin_behavior": "FBR",
          "fin_wellbeing": "FWB"}
TABLES = {k: [f"{p}{i}" for i in range(1, 6)] for k, p in TABLES.items()}


def fetch() -> Path:
    p = RAW_DIR / "data.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    items = [c for v in TABLES.values() for c in v]
    assert d.shape == (370, 36) and set(d.columns) == set(items) | {"STDDEV.P"}
    assert (d[items].std(axis=1, ddof=0) - d["STDDEV.P"]).abs().max() < 1e-4
    print("  [skip] STDDEV.P: per-respondent SD of the 35 items (checked)")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    covs = []
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(RANGE).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(RANGE) for i in its}
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
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
