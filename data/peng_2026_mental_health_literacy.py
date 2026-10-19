#!/usr/bin/env python3

# Source: https://zenodo.org/records/22104999
# DOI: 10.5281/zenodo.22104999
#   PENG, Shenli (2026). Associations between Adolescents' Mental Health Literacy
#   and Subjective Well-Being [Dataset]. Zenodo.
# Data: "IJMHP_Association bewteen MHL & SWB.sav" -- 457 Chinese adolescents.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. Both label levels checked: 0 of 83 variables carry a
#   variable label (so there are no stems in the file at all), while 60 of 83 carry
#   value labels (the anchors). Shipping option_text without any stem is exactly
#   what irw#1770 forbids. The stems are in the published IJMHP article's
#   instrument section, one hop away.
#
# THREE instruments ship; TWO are withheld on rights:
#   peng_2026_mhl_knowledge   9 items, 1-3  (MHL_K_item1-9, knowledge subscale)
#   peng_2026_mhl_attitude    8 items, 1-5  (MHL_A_item1-8, attitude subscale)
#   peng_2026_pyd            16 items, 1-5  (PYD_item1-16, positive youth development)
# WITHHELD, both `block` in itemtext/instrument_rights_register.csv:
#   SWLS_item1-5    Satisfaction With Life Scale (Diener) -- register row "Satisfaction
#                   With Life Scale (SWLS)", verdict block. Its code matcher is ^swls,
#                   which DOES match these codes; caught by matcher and by stem.
#   PANAS_item1-20  Positive and Negative Affect Schedule -- register row "Positive and
#                   Negative Affect Schedule (PANAS)", verdict block. Its matcher is
#                   ^pan[_ ]?[0-9]|panas, which matches PANAS_item*.
#   Ben ruled 2026-09-29 (irw#2401) that a block row covers the instrument in every
#   language, so the Chinese administration is covered too.
# Not shipped besides those: the derived subscale/total columns and the demographics
#   that become covariates.
# id: the deposit's ID column is unique over the 457 rows and is used directly.
# Covariates: cov_age, cov_gender, cov_hukou (urban/rural registration).
import os
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "22104999"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 22104999
FNAME = "IJMHP_Association bewteen MHL & SWB.sav"

BLOCKS = {
    "peng_2026_mhl_knowledge": ([f"MHL_K_item{i}" for i in range(1, 10)], range(1, 4)),
    "peng_2026_mhl_attitude": ([f"MHL_A_item{i}" for i in range(1, 9)], range(1, 6)),
    "peng_2026_pyd": ([f"PYD_item{i}" for i in range(1, 17)], range(1, 6)),
}
WITHHELD = ([f"SWLS_item{i}" for i in range(1, 6)]
            + [f"PANAS_item{i}" for i in range(1, 21)])
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Hukou": "cov_hukou"}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df = df.rename(columns={"ID": "id"})
    df["id"] = df["id"].astype(int)
    assert df["id"].is_unique, "ID does not identify a respondent"

    items = {c for cols, _ in BLOCKS.values() for c in cols}
    accounted = {"id"} | set(COVS) | items | set(WITHHELD)
    other = [c for c in df.columns if c not in accounted]
    for c in WITHHELD:
        assert c in df.columns, f"expected withheld column {c} is absent"
    print(f"  withheld {len(WITHHELD)} columns on rights (SWLS 5, PANAS 20)")
    for c in other:
        print(f"  skipped {c}: derived score or unused column, not an item")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, (cols, scale) in BLOCKS.items():
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - set(scale))
        assert not bad, f"{name}: resp outside the value-labelled scale: {bad}"
        for c in COVS.values():
            t[c] = t[c].astype("Int64")
        t = t[["id", "item", "resp", *COVS.values()]]

        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        pv = set(scale)
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:180]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
