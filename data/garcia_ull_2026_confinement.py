#!/usr/bin/env python3
# Source: https://zenodo.org/records/19183916
# DOI: 10.5281/zenodo.19183916 (dataset; the record names a 2023 book chapter and an article
#   under review, neither with a DOI in the record)
#   Garcia-Ull, Francisco Jose (2026). Dataset: Cuestionario sobre medidas de confinamiento,
#   vigilancia percibida y cumplimiento normativo en estudiantes universitarios espanoles
#   (2022) [Data set]. Zenodo.
# Data: "Jovenes universitarios y pandemia.csv" (semicolon-separated) -- 146 undergraduates
#       at four Spanish universities (Google Forms, February 2022) x timestamp, age and 26
#       questions. Per the record: block 2 = agreement with six categories of COVID-19
#       confinement measures, block 3 = perceived surveillance for the same six, block 4 =
#       declared compliance for the same six (all Likert 1-5), plus single questions.
#       The six category names are the column headers, repeated per block (pandas suffixes
#       the repeats .1 and .2).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Headers give only the six measure names in Spanish; the block
#   question stems and the 1-5 anchors are not in the deposit (the record paraphrases them).
#
# Tables (1-5; items = the six measure categories, coded from the header):
#   garcia_ull_2026_measure_agreement    block 2 (columns 2-7)
#   garcia_ull_2026_perceived_surveil    block 3 (columns 9-14)
#   garcia_ull_2026_compliance           block 4 (columns 16-21)
#   codes: circulacion (Libertad de circulacion), mascarillas (Uso de mascarillas), aforos
#   (Limitacion de aforos), horarios (Limitacion de horarios), distancia (Distancia de
#   seguridad), reuniones (Reuniones con familiares y amigos).
# Skipped: Marca temporal; the yes/no and categorical single questions (felt watched,
#   watching actors (multi-select free text; one copy empty), prospective compliance, whether
#   surveillance influenced compliance, unaware of rules, stress, confusion).
# Covariates: cov_age.
# id: row index (no identifier).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "z19183916"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/19183916/files/"
       "J%C3%B3venes%20universitarios%20y%20pandemia.csv/content")
P = "garcia_ull_2026_"
RANGE = range(1, 6)
CATS = {"Libertad de circulación": "circulacion", "Uso de mascarillas": "mascarillas",
        "Limitación de aforos": "aforos", "Limitación de horarios": "horarios",
        "Distancia de seguridad": "distancia", "Reuniones con familiares y amigos": "reuniones"}
BLOCKS = {"measure_agreement": "", "perceived_surveil": ".1", "compliance": ".2"}


def fetch() -> Path:
    p = RAW_DIR / "data.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch(), sep=";", encoding="utf-8-sig")
    assert d.shape == (146, 28)
    for suf in BLOCKS.values():
        assert {c + suf for c in CATS} <= set(d.columns), suf
    TABLES = {k: list(CATS.values()) for k in BLOCKS}
    print(f"  [skip] {d.shape[1] - 18 - 1} non-item columns (timestamp, single questions)")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={"Edad": "cov_age"})
    covs = ["cov_age"]
    frames = {}
    for k, suf in BLOCKS.items():
        f = d[["id"] + covs + [c + suf for c in CATS]].rename(
            columns={c + suf: v for c, v in CATS.items()})
        frames[k] = f
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for k, its in TABLES.items():
        name = P + k
        f = frames[k]
        t = f.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(RANGE).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100 and len(t) == int(f[its].notna().sum().sum())
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
            (name, [(fi.check, fi.message) for fi in report.errors])
        for fi in report.warnings:
            print(f"    [validate warn] {fi.check}: {fi.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
