#!/usr/bin/env python3
# Source: https://zenodo.org/records/14526147
# DOI: 10.5281/zenodo.14526147 (dataset; the record names no paper)
#   Deryahanoğlu, G., Bal, E., & Yağar, G. (2024). Personality-Motivation [Data set]. Zenodo.
# Data: "KİŞİLİK-VERİ.sav": 358 Turkish exercisers (ages 10-65) with an exercise-motivation
#       scale (E1-E19, 0-4; the Turkish BREQ-2 has 19 items on 0-4) and a ten-item
#       personality scale (K1-K10, 1-5), plus the subscale means (İÇSEL, İÇATIM, DIŞSAL,
#       GÜDÜSÜZ = intrinsic, introjected, external, amotivation; DIŞADÖN .. NÖROTİK = the five
#       traits), gender, age, exercise history and Mahalanobis distances. The record has no
#       description and no codebook; the item variables carry no labels at either level.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. No variable labels and no value labels on any item (both levels
#   checked); the record ships no codebook, so even the instrument names are inferred from
#   the subscale variable names.
#
# Tables (item = the .sav variable name; Turkish administration):
#   deryahanoglu_2024_exercise_motivation   E1-E19, 0-4 (19 items, the subscale means
#                                           name BREQ-2's four regulations).
#   deryahanoglu_2024_big5_10               K1-K10, 1-5 (a ten-item Big Five measure; the
#                                           five trait means are sums of two items each,
#                                           2-10).
# Skipped: the subscale means, EDDÖ, Mahalanobis distances, exercise-duration fields.
# Covariates: cov_sex (1 kadın/female, 2 erkek/male), cov_age.
# id: VAR00001, the deposit's case number.

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.14526147"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/14526147/files/K%C4%B0%C5%9E%C4%B0L%C4%B0K-VER%C4%B0.sav/content"
FNAME = "KİŞİLİK-VERİ.sav"
P = "deryahanoglu_2024_"
BLOCKS = {"exercise_motivation": ([f"E{k}" for k in range(1, 20)], range(0, 5)),
          "big5_10": ([f"K{k}" for k in range(1, 11)], range(1, 6))}
COVS = ["cov_sex", "cov_age"]


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
    assert len(d) == 358 and d["VAR00001"].is_unique
    d["id"] = d["VAR00001"].astype(int)
    d["cov_sex"] = d["Cinsiyet"].astype("Int64")
    d["cov_age"] = pd.to_numeric(d["Yaş"], errors="coerce").astype("Int64")
    out = {}
    for block, (items, valid) in BLOCKS.items():
        t = d.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, (block, bad["resp"].value_counts().to_dict())
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + block] = (t, {i: set(valid) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
