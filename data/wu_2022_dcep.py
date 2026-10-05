#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9046427
# DOI: 10.1038/s41598-022-10927-0
#   "Extending UTAUT with national identity and fairness to understand user
#   adoption of DCEP in China" (Wu, An, Wang & Shin, 2022), Scientific
#   Reports 12:6856.
# Data: the article's supplementary files from the Europe PMC supplementaryFiles
#       zip: 41598_2022_10927_MOESM2_ESM.csv (295 x 25: a respondent number `No`,
#       the 18 item columns, six empty trailing columns) and MOESM1_ESM.docx (the
#       questionnaire, item wording grouped under construct headings).
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Item text: not shipped. Levels checked: the CSV has no variable or value
#   labels (plain headers such as perceivedrisk1). The English wording is in
#   MOESM1_ESM.docx, three statements under each construct heading, but the
#   data codes tie to them only by position within a construct (the k-th
#   statement under "Perceived risk" = perceivedrisk<k>), so the mapping would
#   be paper_order, not data_labels. Anchors: "1-strongly disagree;
#   7-strongly agree" (docx), points 2-6 unlabelled.
#
# Sample: 295 users of China's digital currency (DCEP) recruited in the lobbies
# of city banks piloting DCEP (paper Methods: 438 distributed, 295 valid). The
# deposit carries no demographics.
#
# Tables (all 1-7 agreement, three items each; one table per construct, as in
# the paper's Table 3 measurement model):
#   wu_2022_dcep_risk               perceivedrisk1-3       (paper R1-R3)
#   wu_2022_dcep_habit              habit1-3               (H1-H3)
#   wu_2022_dcep_social_influence   socialinfuence1, socialinfluence2-3 (SI1-SI3;
#                                   the first header is misspelled in the source
#                                   and kept as spelled)
#   wu_2022_dcep_national_identity  natioanlidentity1-3    (NI1-NI3; source spelling)
#   wu_2022_dcep_fairness           perceivedfairness1-3   (PF1-PF3)
#   wu_2022_dcep_usage              usage1-3               (U1-U3)
#
# Checks: every item cell is an integer 1-7, none missing; no straight-liners.
# Eleven groups of respondents share an identical 18-item vector (24 rows), but
# they are almost all near-constant 5/6 patterns and mostly non-adjacent, and
# the agreement histogram decays smoothly to them (pairs agreeing on 16/17/18
# items: 114/29/15), so they are kept as plausible low-entropy responses rather
# than dropped as duplicates.

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "wu_2022_dcep"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9046427/supplementaryFiles"
FILE = "41598_2022_10927_MOESM2_ESM.csv"


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(zipfile.ZipFile(io.BytesIO(r.content)).read(FILE))
    return p


TABLES = {
    "wu_2022_dcep_risk": ["perceivedrisk1", "perceivedrisk2", "perceivedrisk3"],
    "wu_2022_dcep_habit": ["habit1", "habit2", "habit3"],
    "wu_2022_dcep_social_influence": ["socialinfuence1", "socialinfluence2", "socialinfluence3"],
    "wu_2022_dcep_national_identity": ["natioanlidentity1", "natioanlidentity2", "natioanlidentity3"],
    "wu_2022_dcep_fairness": ["perceivedfairness1", "perceivedfairness2", "perceivedfairness3"],
    "wu_2022_dcep_usage": ["usage1", "usage2", "usage3"],
}


def main() -> None:
    d = pd.read_csv(fetch())
    assert d.shape == (295, 25), d.shape
    items = [c for v in TABLES.values() for c in v]
    assert len(items) == len(set(items)) == 18
    empty = [c for c in d.columns if c.startswith("Unnamed")]
    assert d[empty].isna().all().all() and len(empty) == 6
    # balance the books: every source column is an item, the id, or an empty column
    assert set(d.columns) == set(items) | {"No"} | set(empty), \
        set(d.columns) ^ (set(items) | {"No"} | set(empty))
    print(f"  [skip] {len(empty)} empty trailing columns (all NaN)")
    assert d["No"].is_unique and d["No"].tolist() == list(range(1, 296))
    assert d[items].notna().all().all()
    assert (d[items] % 1 == 0).all().all() and d[items].isin(range(1, 8)).all().all()
    assert (d[items].nunique(axis=1) > 1).all()

    d = d.rename(columns={"No": "id"})
    assert len(TABLES) == len(set(TABLES))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"], value_vars=its, var_name="item", value_name="resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(1, 8)) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
