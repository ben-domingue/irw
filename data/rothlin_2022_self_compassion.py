#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.2547d7wsv (mirrored on Zenodo, record 6633659)
# DOI: 10.1080/1612197X.2021.2025134
#   Röthlin, P., Horvath, S., Messerli, T., Krieger, T., Berger, T., & Birrer, D. (2022).
#   Associations of self-compassion with shame, guilt, and training motivation after
#   sport-specific daily stress -- a smartphone study. International Journal of Sport and
#   Exercise Psychology. Data: Röthlin, P., et al. (2022). [Dataset]. Dryad.
# Data: "datafile_snf_diary.sav": 141 Swiss athletes (2019). The baseline Self-Compassion
#       Scale Short Form (scs1-scs12) carries the English stems as SPSS variable labels and
#       the five anchors as value labels; the rest of the file is a 60-day smartphone diary
#       (TrainWett_k, Datum/Beginn/Ende, and ten single daily ratings per day: ErwEnt,
#       Fehler, negFB, their *Stress twins, beschaemt, schuldig, Motivation), with -77 as
#       the missing code. README_file.txt.docx documents the diary, not the SCS-SF anchors.
#       Dryad's own download refuses scripts (Anubis); the Zenodo mirror of the same DOI
#       serves the file, so the script fetches from Zenodo.
# License: CC0 1.0 (Dryad / Zenodo record).
#
# Item text: shipped (stems from the .sav variable labels, anchors from its value labels;
#   the labels are English although the administration was in German-speaking Switzerland,
#   so language=German with empty _translated columns -- an English substitute; built by
#   automated_finding/itemtext_verification/make_itemtext_rothlin_2022.py).
#
# Tables (item = the .sav variable name):
#   rothlin_2022_scs_sf   scs1-scs12, Self-Compassion Scale Short Form, 1 very rarely ..
#                         5 very often, as stored (no reverse-coding applied).
# Skipped: the daily diary (ten different single-item ratings per day, no item battery),
#   dates and times, training/competition flags.
# Covariates: none in the file.
# id: the file's row number (1..141).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5061_dryad.2547d7wsv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/6633659/files/datafile_snf_diary.sav/content"
FNAME = "datafile_snf_diary.sav"
T = "rothlin_2022_scs_sf"
ITEMS = [f"scs{k}" for k in range(1, 13)]


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def raw() -> Path:
    return download(URL, RAW_DIR / FNAME)


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
    d, meta = pyreadstat.read_sav(str(raw()))
    assert len(d) == 141
    for c in ITEMS:
        assert meta.column_names_to_labels.get(c), c
        assert set(meta.variable_value_labels[c]) == {1.0, 2.0, 3.0, 4.0, 5.0}, c
    d["id"] = range(1, len(d) + 1)
    t = d.melt(id_vars=["id"], value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all(), t["resp"].unique()
    t = t[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)
    emit({T: (t, {i: set(range(1, 6)) for i in ITEMS})})


if __name__ == "__main__":
    main()
