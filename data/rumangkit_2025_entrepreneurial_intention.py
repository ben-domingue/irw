#!/usr/bin/env python3

# Source: https://zenodo.org/records/15511693
# DOI: 10.5281/zenodo.15511693
#   Rumangkit, Stefanus (2025). Dataset Questionnaire: The determinants of
#   Indonesian students' intention and commitment to entrepreneurship [Dataset].
#   Zenodo.
# Data: the deposit's single workbook -- 344 Indonesian students, 1-5 agreement.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. The workbook has one header row of bare construct codes
#   (ATT1, SN1, ...) and no label level; .xlsx carries none. The stems are in the
#   paper behind the deposit title.
#
# SEVEN tables, all 1-5, one per construct of a theory-of-planned-behaviour battery:
#   rumangkit_2025_attitude                4 items (ATT1-4)
#   rumangkit_2025_subjective_norm         4 items (SN1-4)
#   rumangkit_2025_perceived_control       5 items (PBC1-5)
#   rumangkit_2025_self_efficacy           5 items (ESI1-5)
#   rumangkit_2025_intention               8 items (EI1-EI7, EI9)
#   rumangkit_2025_passion                 4 items (EPE1-4)
#   rumangkit_2025_commitment              2 items (ECO1-2)
# EI8 IS ABSENT from the deposit. The gap is the source's -- the file jumps EI7 to
#   EI9 -- so the item codes keep the author's numbering rather than being
#   renumbered 1..8, which would silently move every item after the gap.
# Not shipped: MAH_1 (Mahalanobis distance), Outlier (a flag), and the 48
#   "<item>.ESI<k>" columns, which are interaction PRODUCTS of two item columns
#   computed for the moderation analysis, not responses.
# id: the deposit's ID column is unique over the 344 rows and is used directly.
# Covariates: none -- the deposit ships no demographics.
# Rights: none of the seven is in the instrument rights register. These are
#   standard TPB entrepreneurial-intention items; checked against the register's
#   block list by hand rather than relying on its code matchers.
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "15511693"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 15511693
SCALE = set(range(1, 6))

BLOCKS = {
    "rumangkit_2025_attitude": [f"ATT{i}" for i in range(1, 5)],
    "rumangkit_2025_subjective_norm": [f"SN{i}" for i in range(1, 5)],
    "rumangkit_2025_perceived_control": [f"PBC{i}" for i in range(1, 6)],
    "rumangkit_2025_self_efficacy": [f"ESI{i}" for i in range(1, 6)],
    "rumangkit_2025_intention": [f"EI{i}" for i in [1, 2, 3, 4, 5, 6, 7, 9]],
    "rumangkit_2025_passion": [f"EPE{i}" for i in range(1, 5)],
    "rumangkit_2025_commitment": [f"ECO{i}" for i in range(1, 3)],
}


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    hits = [p for p in RAW_DIR.iterdir() if p.suffix.lower() in (".xlsx", ".xls", ".csv")]
    if hits:
        return hits[0]
    j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                     headers=UA, timeout=120).json()
    f = j["files"][0]
    p = RAW_DIR / f["key"]
    r = requests.get(f["links"]["self"], headers=UA, timeout=300)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p


def main():
    p = fetch()
    df = pd.read_excel(p) if p.suffix.lower() in (".xlsx", ".xls") else pd.read_csv(p)
    df = df.rename(columns={"ID": "id"})
    df["id"] = df["id"].astype(int)
    assert df["id"].is_unique, "ID does not identify a respondent"
    assert "EI8" not in df.columns, "EI8 is present after all -- re-read the header"

    items = {c for cols in BLOCKS.values() for c in cols}
    for c in items:
        assert c in df.columns, f"expected item column {c} is absent"
    products = [c for c in df.columns if "." in str(c)]
    flags = ["MAH_1", "Outlier"]
    accounted = {"id"} | items | set(products) | set(flags)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"  skipped {len(products)} <item>.ESI<k> columns: interaction products "
          f"of two item columns, not responses")
    for c in flags:
        print(f"  skipped {c}: outlier diagnostic, not an item")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-5 scale: {bad}"
        t = t[["id", "item", "resp"]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
