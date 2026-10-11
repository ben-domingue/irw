#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WXOYVM
# DOI: 10.1007/s11109-022-09787-1
#   Lee, A. H.-Y. (2022). Social Trust in Polarized Times: How Perceptions of Political
#   Polarization Affect Americans' Trust in Each Other. Political Behavior. Data: Lee, A. H.-Y.
#   (2022). Replication Data for: Social Trust in Polarized Times. Harvard Dataverse, V1.
# Data: "PerPolarization_SocialTrust_Experiment.dta": 1,006 US adults (an online survey
#       experiment, April-May 2020) randomised to a less-polarization / more-polarization /
#       control article (condition) and a baseline / double donation condition. Variable
#       labels carry the stems (cut at 80 characters); there are no value labels on the
#       items. The deposit's panel-survey file is not used.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped. The .dta variable labels hold the stems but Stata truncated
#   several at 80 characters (perpol_3, stranger_1, gstrust1/2), and there are no value
#   labels for any item, so the anchors of the 1-5, 1-4 and 1-2 scales are not in the deposit.
#
# Tables (item = the .dta variable name; `treat` = 1 for either polarization article,
#   0 for the control article, and cov_condition names the arm (less-polarization /
#   more-polarization / control); every block was asked after the manipulation):
#   lee_2022_ameritrust    ameritrust_1-8: how many Americans would do each civic thing
#                          (accept election results, cast informed votes, ...), 1-5.
#   lee_2022_perpol        perpol_1-5: perceived political polarization, 1-4.
#   lee_2022_stranger      stranger_1-3: willingness to trust a stranger in three
#                          situations, 1-4.
#   lee_2022_gen_trust     gstrust1-3: the three generalized-trust questions, 1/2.
# Skipped: the indexes (perpolindx, gstrustindx, ameritrustindx, strangertrindx), the
#   gstrust2r recode, the charity allocations, sharevalues/shareinterests (two single
#   questions), and the ethnicity dummies.
# Covariates: cov_age, cov_gender (1 male, 2 female), cov_income (1-11 bands),
#   cov_education (1-9), cov_ideology (1-7), cov_race (1-4, the deposit's recode),
#   cov_donation_condition (1 baseline, 2 double), cov_condition (the experimental arm).
# id: the Qualtrics response id's row index (1..1006).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_wxoyvm"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DOI = "10.7910/DVN/WXOYVM"
FNAME = "PerPolarization_SocialTrust_Experiment.dta"
P = "lee_2022_"
BLOCKS = {"ameritrust": ([f"ameritrust_{k}" for k in range(1, 9)], range(1, 6)),
          "perpol": ([f"perpol_{k}" for k in range(1, 6)], range(1, 5)),
          "stranger": ([f"stranger_{k}" for k in range(1, 4)], range(1, 5)),
          "gen_trust": ([f"gstrust{k}" for k in range(1, 4)], (1, 2))}
COVS = ["cov_condition", "cov_age", "cov_gender", "cov_income", "cov_education", "cov_ideology",
        "cov_race", "cov_donation_condition"]
ARMS = {1: "less-polarization", 2: "more-polarization", 3: "control"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


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
    d, meta = pyreadstat.read_dta(str(dv_fetch(DOI, FNAME, RAW_DIR)))
    assert len(d) == 1006 and d["responseid"].is_unique
    d["id"] = range(1, len(d) + 1)
    assert set(d["condition"].unique()) == set(ARMS)
    d["treat"] = (d["condition"] != 3).astype(int)
    d["cov_condition"] = d["condition"].map(ARMS)
    ren = {"qage": "cov_age", "qgender": "cov_gender", "qincome": "cov_income",
           "qeducation": "cov_education", "qpolitical_ideology": "cov_ideology",
           "race": "cov_race", "donation": "cov_donation_condition"}
    d = d.rename(columns=ren)
    for c in COVS[1:]:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
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
