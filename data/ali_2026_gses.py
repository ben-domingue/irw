#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/f86brhwxpj/1
# DOI: 10.17632/f86brhwxpj.1 (dataset; no paper DOI on the record)
#   Ali, Amira (2026). "Psychometric evaluation of the General Self-Efficacy Scale and
#   Six Shortened Versions Among Adults with and without Acquired
#   Movement Disability" [data set]. Mendeley Data, V1.
# Data: "Psychometric evaluation of the General Self-Efficacy Scale and Six
#       Shortened.sav": 120 adults with and without acquired movement disability x
#       Number, demographics, Group, GSES1-10 (Schwarzer & Jerusalem General
#       Self-Efficacy Scale, 1-4), and derived totals, short-form totals, health
#       locus of control and SWLS totals, and cluster memberships. SPSS value labels
#       on some covariates only; no variable labels on the items.
#   The sister deposit 10.17632/brs8d6dvzd.1 ("Construct Validity of Short-Form
#   General Self-Efficacy Scales ...", same author, same 120 people: identical
#   Number/demographic columns) holds only the totals and clusters -- no item
#   responses -- so it adds nothing and is not read.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: not shipped. Levels checked: .sav variable labels absent on GSES1-10 and
#   no value labels on them; the wording used (language not stated) is not in the
#   deposit.
#
# Shipped: ali_2026_gses -- GSES1-10, 1-4 (the GSES's 4-point format; the file's
#   GSES total equals the item sum on every row).
# Not shipped: GSES, GSES_Sten, GSETotal and the short-form totals (GSE*Tot, GSEF*,
#   GSES*Swedish, GSEaction, GSEcoping) -- sums of the shipped items; IHLC/PHLC/CHLC,
#   SWLS3, Congruence, Achievement_Acceptance, Past/Present_atisfaction -- scale
#   totals whose items are not deposited; Age2Cat32, Edu2Cat -- recodes; TSC_*,
#   Cluster_*, GSECluster_6533 -- model output.
# Covariates: cov_male (Sex 0 female, 1 male), cov_age, cov_education (0-3, unlabelled),
#   cov_marital (0 single, 2 in relation; others unlabelled), cov_urban (0 rural,
#   1 urban), cov_disability_years, cov_disabled (Group 0 no, 1 acquired movement
#   disability). id = Number.

import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "ali_2026"
UA = {"User-Agent": "Mozilla/5.0 (IRW-Finder/1.0; ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/f86brhwxpj"
NAME = "ali_2026_gses"
ITEMS = [f"GSES{i}" for i in range(1, 11)]
COVS = {"Sex": "cov_male", "Age": "cov_age", "Educationn": "cov_education",
        "Marital_status": "cov_marital", "Place_residence": "cov_urban",
        "Disability_Duration": "cov_disability_years", "Group": "cov_disabled"}


def fetch() -> Path:
    p = RAW_DIR / "gses.sav"
    if not p.exists():
        meta = requests.get(API, headers=UA, timeout=120).json()
        assert meta["data_licence"]["short_name"] == "CC BY 4.0"
        (f,) = meta["files"]
        r = requests.get(f["content_details"]["download_url"], headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (120, 52)
    assert (d[ITEMS].sum(axis=1) == d["GSES"]).all()
    skipped = [c for c in d.columns if c not in ITEMS + list(COVS) + ["Number"]]
    print(f"  [skip] {len(skipped)} columns (totals, recodes, cluster output): {skipped}")
    d["id"] = d["Number"].astype(int)
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    assert t["resp"].notna().all() and t["resp"].isin(range(1, 5)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    pv = {i: {1, 2, 3, 4} for i in ITEMS}
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
