#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC4906282
# DOI: 10.1038/srep27824
#   "Moral Bargain Hunters Purchase Moral Righteousness When it is Cheap:
#   Within-Individual Effect of Stake Size in Economic Games" (Yamagishi, Li,
#   Matsumoto & Kiyonari, 2016), Scientific Reports 6:27824.
# Data: Scientific Reports supplementary files from the Europe PMC
#       supplementaryFiles zip: srep27824-s1.csv (Study 1 + Study 3, 479 x 17)
#       and srep27824-s2.csv (Study 2, 162 x 62).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data are
#          the article's own supplementary files.
#
# Item text: not shipped. These are game decisions, not questionnaire items; the
#   paper's Methods describe the games (binary prisoner's dilemma, keep or give
#   an endowment of JPY 300 / 800 / 1,500 that is doubled for the partner) but
#   there is no per-decision wording, and the CSVs carry no labels.
#
# Sample (Study 1): 479 non-student residents of a Tokyo suburb, aged 20-59
#   (paper; the file's minimum age is 19). `ID` is the study's participant
#   number (unique), used as id.
#
# Tables:
#   yamagishi_2016_pd  Study 1: 12 binary prisoner's-dilemma decisions, 1 =
#                      give (cooperate), 0 = keep. Played in this fixed order:
#                      simultaneous game at JPY 300/800/1500 (sim300..sim1500),
#                      first mover in the sequential game (first300..first1500),
#                      second mover by the strategy method after the partner gave
#                      (secC300..) and after the partner kept (secD300..).
#
# Skipped: OBS (row number); Study3 (Study 3's single one-shot PD giving, as a
# share of JPY 1,000, '.' for the 45 Study 1 participants who did not take part
# -- one decision, no single-item tables); srep27824-s2.csv (Study 2: 162
# students x 30 simultaneous PD trials whose stake was randomised per trial, so
# trial k is not the same probe across people -- not a fixed item set).
# No missing cells; no exact-duplicate rows.

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4906282/supplementaryFiles"

ITEMS = [f"{g}{s}" for g in ("sim", "first", "secC", "secD") for s in (300, 800, 1500)]
COV = {"Male": "cov_male", "Age": "cov_age"}
SKIP = {"OBS": "row number",
        "Study3": "Study 3 single one-shot PD decision (share given); no single-item tables"}


def load() -> pd.DataFrame:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return pd.read_csv(io.BytesIO(z.read("srep27824-s1.csv")))


def main() -> None:
    d = load()
    assert d.shape == (479, 17), d.shape
    assert set(d.columns) == {"ID"} | set(ITEMS) | set(COV) | set(SKIP)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    print("  [skip] srep27824-s2.csv: Study 2, randomised stake per trial (no fixed items)")
    assert d["ID"].is_unique and not d.duplicated().any()
    assert not d[ITEMS + list(COV)].isna().any().any()

    d = d.rename(columns={"ID": "id", **COV})
    covs = list(COV.values())
    name = "yamagishi_2016_pd"
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() == 479
    pv = {i: {0, 1} for i in ITEMS}
    for i in ITEMS:
        assert set(t.loc[t["item"] == i, "resp"]) <= {0, 1}, i
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
