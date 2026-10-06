#!/usr/bin/env python3
# Source: https://zenodo.org/records/5024411 (Dryad mirror)
# DOI: 10.1371/journal.pone.0207989
#   Bado, Rebustini, Jamieson, Cortellazzi & Mialhe (2018). "Evaluation of the
#   psychometric properties of the Brazilian version of the Oral Health Literacy
#   Assessment in Spanish and development of a shortened form of the instrument",
#   PLOS ONE 13(11): e0207989. Data: Dryad 10.5061/dryad.jc6dt.
# Data: Database_Brazilian_version_of_the_OLHA-S_literacy_instrument.xlsx, sheet
#       "Pronunciat and Compreh dat (24)": 250 adults aged 20-59 x 24 dental words
#       (header on the second row: Respondent, the 24 words, TOTAL); sheet "Codes "
#       gives the scoring.
# License: CC0 1.0 (Zenodo/Dryad record).
#
# Scoring (sheet "Codes "): 1 = both the pronunciation (word recognition) and the
#   association (comprehension) answers were correct, 0 = either was incorrect.
#   TOTAL (sum) dropped.
# Items: the OHLA word, lowercased, non-alphanumerics to "_" ("Floss (noun)" ->
#   floss_noun; "Bruxims" and "Maloclusion" kept as the deposit spells them).
#   "Sugar" is answered correctly by all 250 respondents; kept (it is a real item).
#
# Item text: not shipped. Levels checked: xlsx, no labels; the item code is the
#   word itself, but the comprehension alternatives (OHLA-S association words)
#   are in the paper/instrument, not the deposit.

import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "bado_2018"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/5024411/files/"
       "Database_Brazilian_version_of_the_OLHA-S_literacy_instrument.xlsx/content")
NAME = "bado_2018_ohla_b"


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Pronunciat and Compreh dat (24)", header=1)
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (250, 26) and d.columns[0] == "Respondent" and d.columns[-1] == "TOTAL"
    words = d.columns[1:-1].tolist()
    codes = {w: re.sub(r"[^a-z0-9]+", "_", w.lower()).strip("_") for w in words}
    assert len(set(codes.values())) == 24
    assert d["Respondent"].is_unique
    assert (d[words].sum(axis=1) == d["TOTAL"]).all()
    t = d.rename(columns={"Respondent": "id", **codes}).melt(
        id_vars=["id"], value_vars=list(codes.values()), var_name="item", value_name="resp")
    assert t["resp"].isin([0, 1]).all()
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    pv = {i: {0, 1} for i in codes.values()}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:200]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
