#!/usr/bin/env python3
# Source: https://zenodo.org/records/10050394
# DOI: 10.24425/ppb.2023.148847
#   Cwalina, W., & Koniak, P. (2024). The role of conspiracy mentality, reactance, and
#   anxiety in the effectiveness of gain- vs. loss-framed promotion of COVID-19 protective
#   measures: Is vaccination different? Polish Psychological Bulletin. Data: Cwalina, W., &
#   Koniak, P. (2023). [Data set and materials]. Zenodo.
# Data: "Data.sav": 159 Polish students (17-35) randomised to a gain- or loss-framed
#       message (Frame), then rating six COVID-19 protective measures on seven 7-point
#       semantic-differential scales each, eight affect items (reactance / anxiety) and the
#       15-item Generic Conspiracist Beliefs scale. SPSS variable labels carry the English
#       pole pairs for the attitude items ("wearing masks - dangerous/safe") and the affect
#       names; GCB1 is labelled with the scale name only; no value labels on any item.
#       "Excl" flags 8 cases the authors excluded from analysis; they are kept, with
#       cov_excluded_by_authors marking them.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. The attitude labels are pole pairs ("dangerous/safe") without the
#   Polish wording respondents saw, the affect labels are single English words, and the
#   GCB items carry no stems (both label levels checked: variable labels on the attitude
#   and affect items only, value labels on none). The Polish wording is in the Stimulus
#   material.pdf of the deposit.
#
# Tables (item = the .sav variable name; treat = 1 gain frame, 0 loss frame):
#   cwalina_2023_covid_attitudes   42 items: six measures (Mask, Hand, Dist, Nose, Vacc,
#                                  Test) x seven scales (Dang, ScJu, HThr, Effe, Risk, Do,
#                                  Will), 1-7 (negative pole = 1).
#   cwalina_2023_affect            Threat, Irritat, Restlessness, Annoy, Fear, Aggrav,
#                                  Anger, Anxiety, 1-7.
#   cwalina_2023_gcbs              GCB1-GCB15, 1-5.
# Skipped: the indexes (IndAnxi, IndReact, Att*, GCBIndx).
# Covariates: cov_sex (1 female, 2 male), cov_age, cov_excluded_by_authors (0/1).
# id: the file's row number (1..159).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.10050394"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/10050394/files/Data.sav/content"
P = "cwalina_2023_"
MEASURES = ["Mask", "Hand", "Dist", "Nose", "Vacc", "Test"]
SCALES = ["Dang", "ScJu", "HThr", "Effe", "Risk", "Do", "Will"]
ATT = [m + s for m in MEASURES for s in SCALES]
ATT = ["MskWill" if a == "MaskWill" else a for a in ATT]   # the deposit's spelling
AFFECT = ["Threat", "Irritat", "Restlessness", "Annoy", "Fear", "Aggrav", "Anger", "Anxiety"]
GCB = [f"GCB{k}" for k in range(1, 16)]
BLOCKS = {"covid_attitudes": (ATT, range(1, 8)), "affect": (AFFECT, range(1, 8)),
          "gcbs": (GCB, range(1, 6))}
COVS = ["cov_sex", "cov_age", "cov_excluded_by_authors"]


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
    d, meta = pyreadstat.read_sav(str(download(URL, RAW_DIR / "Data.sav")))
    assert len(d) == 159
    missing = [c for c in ATT + AFFECT + GCB if c not in d.columns]
    assert not missing, missing
    d["id"] = range(1, len(d) + 1)
    assert set(d["Frame"].unique()) == {-1.0, 1.0}
    d["treat"] = (d["Frame"] == 1).astype(int)
    d["cov_sex"] = d["Sex"].astype("Int64")
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_excluded_by_authors"] = d["Excl"].astype("Int64")
    out = {}
    for block, (items, valid) in BLOCKS.items():
        t = d.melt(id_vars=["id", "treat"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, (block, bad["resp"].value_counts().to_dict())
        t = t[["id", "item", "resp", "treat"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + block] = (t, {i: set(valid) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
