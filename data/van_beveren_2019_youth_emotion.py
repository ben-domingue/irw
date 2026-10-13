#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.nzs7h44mm (mirrored on Zenodo, record 4932285)
# DOI: 10.1371/journal.pone.0224126
#   Van Beveren, M.-L., Kuppens, S., Hankin, B., & Braet, C. (2019). Because you had a bad
#   day: General and daily relations between reactive temperament, emotion regulation, and
#   depressive symptoms in youth. PLOS ONE, 14(10), e0224126. Data: Van Beveren, M.-L., et
#   al. (2019). [Dataset]. Dryad.
# Data: "Datafile_Cross-sectional_analyses.sav": 495 Flemish youths aged 9-17, with the
#       FEEL-KJ (90 items), PANAS-C (30 items) and CDI (27 items) at the item level. Only
#       the first item of each block carries a variable label (the instrument name) and
#       Dutch value labels; the rest are unlabelled. A minority of cells are non-integer
#       (e.g. 5.57, 0.449, -0.062): regression-style imputations on an integer scale, so
#       the script drops every non-integer cell (counts printed) and ships observed
#       responses only. The daily-diary file holds composites only and is not used.
#       Dryad's own download refuses scripts (Anubis); the Zenodo mirror serves the file.
# License: CC0 1.0 (Dryad / Zenodo record).
#
# Item text: not shipped. Variable labels name the instrument on the first item only
#   (both label levels checked: stems absent on every item; Dutch value labels present on
#   the first item of each block only). The FEEL-KJ (Hogrefe) and CDI (MHS) are commercial
#   instruments in any case; the PANAS-C wording would need the published scale.
#
# Tables (item = the .sav variable name; Dutch administration):
#   van_beveren_2019_feelkj   FEELKJ1-FEELKJ90, Fragebogen zur Erhebung der
#                             Emotionsregulation bei Kindern und Jugendlichen (Dutch
#                             version), 1 almost never .. 5 almost always.
#   van_beveren_2019_panasc   PANAS1-PANAS30, PANAS for Children, 1-5.
#   van_beveren_2019_cdi      CDI1-CDI27, Children's Depression Inventory, 0-2.
# Skipped: the totals (NAff, PAff, RUM, POS, DEP).
# Covariates: cov_age, cov_gender (1 boy, 2 girl).
# id: the file's row number (1..495).

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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5061_dryad.nzs7h44mm"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/4932285/files/Datafile_Cross-sectional_analyses.sav/content"
FNAME = "Datafile_Cross-sectional_analyses.sav"
P = "van_beveren_2019_"
BLOCKS = {"feelkj": ([f"FEELKJ{k}" for k in range(1, 91)], range(1, 6)),
          "panasc": ([f"PANAS{k}" for k in range(1, 31)], range(1, 6)),
          "cdi": ([f"CDI{k}" for k in range(1, 28)], range(0, 3))}
COVS = ["cov_age", "cov_gender"]


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    d, meta = pyreadstat.read_sav(str(download(URL, RAW_DIR / FNAME)))
    assert len(d) == 495
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"Age": "cov_age", "Gender": "cov_gender"})
    for c in COVS:
        d[c] = d[c].astype("Int64")
    out = {}
    for block, (items, valid) in BLOCKS.items():
        t = d.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        frac = (t["resp"] % 1).abs() > 1e-9
        print(f"  [{block}] dropped {frac.sum()} non-integer (imputed) cells of {len(t)}")
        t = t[~frac].copy()
        t["resp"] = t["resp"].round().astype(int)
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, (block, bad["resp"].value_counts().to_dict())
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + block] = (t, {i: set(valid) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
