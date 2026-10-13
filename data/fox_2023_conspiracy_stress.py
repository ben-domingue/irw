#!/usr/bin/env python3
# Source: https://osf.io/sfuz9/
# DOI: 10.12688/routledgeopenres.17925.2
#   Fox, N., & Williams, M. N. (2023/2024). Do stress and anxiety lead to belief in
#   conspiracy theories? Routledge Open Research, 2:30. Data: Fox, N., & Williams, M.
#   (2021). Stress, anxiety and belief in conspiracy theories. OSF, doi:10.17605/OSF.IO/SFUZ9.
# Data: "Study 1 Deidentified Data.csv" (529 rows; Australia / New Zealand, 2021) and
#       "Study 2 Deidentified Data.csv" (1,063 rows; Australia, 2021), Qualtrics exports with
#       the item codes as headers, plus "Study 1 Data Dictionary.csv" / "Study 2 Data
#       Dictionary.csv" giving every variable's question text and response levels. The same
#       three instruments with the same codes and levels in both studies, so each ships as
#       one table with cov_study.
# License: CC BY 4.0 (OSF node licence, resolved from the API).
#
# Item text: shipped for fox_2023_bct and fox_2023_gad7 (stems and levels from the data
#   dictionaries; English administration; built by
#   automated_finding/itemtext_verification/make_itemtext_fox_2023.py). fox_2023_pss10 not
#   shipped: the PSS is a `block` row in itemtext/instrument_rights_register.csv.
#
# Tables (item = the deposit's variable name; cov_study 1 / 2; id = study-prefixed row):
#   fox_2023_bct    BCT_1_NWO .. BCT_15_Fluor, the authors' 15 specific conspiracy beliefs,
#                   1 strongly disagree .. 5 strongly agree.
#   fox_2023_pss10  PSS_1-PSS_10 (Perceived Stress Scale), 0 never .. 4 very often.
#   fox_2023_gad7   GAD_1-GAD_7, 0 not at all .. 3 nearly every day.
# Skipped: att_check (the attention item), SSocial_1 (single ladder item), Summary, SC0
#   (Qualtrics sum), Status/Consent/Duration. Rows with Consent 0 or Status != 0 are dropped
#   (counts printed); respondents who answered no item vanish in the melt.
# Covariates: cov_study, cov_age (as typed; Study 2 has a few implausible values, kept as
#   deposited), cov_gender (1 male, 2 female, 3 non-binary, 4 prefer not to say),
#   cov_education (1 doctoral .. 7 no high school), cov_political (1 strongly left .. 5
#   strongly right), cov_country (Study 1: 1 Australia, 2 New Zealand, 3 other; Study 2 all 1).
# id: s1_<row> / s2_<row>, the row's position in its deposited file.

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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "sfuz9"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"Study 1 Deidentified Data.csv": "https://osf.io/download/esujw/",
         "Study 2 Deidentified Data.csv": "https://osf.io/download/exm5z/",
         "Study 1 Data Dictionary.csv": "https://osf.io/download/dkc9w/",
         "Study 2 Data Dictionary.csv": "https://osf.io/download/rtn7p/"}
P = "fox_2023_"
BCT = ["BCT_1_NWO", "BCT_2_COVID", "BCT_3_Sim", "BCT_4_Pharm", "BCT_5_MLK", "BCT_6_Moon",
       "BCT_7_Area51", "BCT_8_911", "BCT_9_JFK", "BCT_10_Alien", "BCT_11_Dianna", "BCT_12_5G",
       "BCT_13_Vac", "BCT_14_Climate", "BCT_15_Fluor"]
PSS = [f"PSS_{k}" for k in range(1, 11)]
GAD = [f"GAD_{k}" for k in range(1, 8)]
BLOCKS = {"bct": (BCT, range(1, 6)), "pss10": (PSS, range(0, 5)), "gad7": (GAD, range(0, 4))}
COVS = ["cov_study", "cov_age", "cov_gender", "cov_education", "cov_political", "cov_country"]


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def fetch(name: str) -> Path:
    return download(FILES[name], RAW_DIR / name)


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


def dictionary(study: int) -> pd.DataFrame:
    return pd.read_csv(fetch(f"Study {study} Data Dictionary.csv")).set_index("variable")


def main() -> None:
    frames = []
    for study in (1, 2):
        d = pd.read_csv(fetch(f"Study {study} Deidentified Data.csv"))
        drop = (d["Status"] != 0) | (d["Consent"] != 1)
        print(f"  [study {study}] {len(d)} rows, dropping {drop.sum()} incomplete / no-consent")
        d = d[~drop].copy()
        d["id"] = [f"s{study}_{i + 1}" for i in d.index]
        d["cov_study"] = study
        d = d.rename(columns={"Age": "cov_age", "Gender": "cov_gender", "Educat": "cov_education",
                              "Political": "cov_political", "Country": "cov_country"})
        for c in COVS[1:]:
            d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
        frames.append(d[["id", *COVS, *BCT, *PSS, *GAD]])
    d = pd.concat(frames, ignore_index=True)
    assert d["id"].is_unique
    out = {}
    for block, (items, valid) in BLOCKS.items():
        t = d.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, (block, bad["resp"].value_counts().to_dict())
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + block] = (t, {i: set(valid) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
