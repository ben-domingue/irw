#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZL47OH
# DOI: 10.1016/j.paid.2016.10.008
#   Hatemi, P. K., Crabtree, C., & McDermott, R. (2017). The relationship between sexual
#   preferences and political orientations: Do positions in the bedroom affect positions in
#   the ballot box? Personality and Individual Differences, 105, 318-325. Data: Hatemi, P.
#   (2019). Replication Data for: The relationship between sexual preferences and political
#   orientations. Harvard Dataverse, V1.
# Data: "hcm.csv", 1,058 US adults (an online survey) x 46 variables, with "codebook.txt"
#       describing each variable ("Ordinal indicator for how often participants engaged in
#       oral sex during the preceding 12 months") but not quoting the question or the
#       anchors of the 1-5 frequency scale.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped. codebook.txt paraphrases each item ("Ordinal indicator for how
#   often ...") and gives no anchors; the questionnaire itself is not in the deposit.
#
# Tables (item = the deposit's variable name):
#   hatemi_2017_sex_freq   18 sexual-behaviour frequency items (given_oral_sex ..
#                          filmed_self_having_sex), 1-5 (how often in the preceding 12
#                          months; higher = more often per the codebook).
# Skipped: the 10 risky-behaviour yes/no indicators and their sum (lifetime-ever events,
#   not a frequency scale), the ideology sub-scale means (econ_libertarian,
#   national_security, out_group_punishment, social_conservatism: composites), vote choice,
#   single-item satisfaction, partner counts and ages at first sex.
# Covariates: cov_sex (biological_sex, 1-3 as deposited), cov_age, cov_education (1-5),
#   cov_pid7 (self_reported_pid, 1 strong Democrat .. 7 strong Republican),
#   cov_ideology7 (self_reported_ideology, 1 extremely liberal .. 7 extremely conservative).
# id: the file's row number (its unnamed first column).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_zl47oh"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DOI = "10.7910/DVN/ZL47OH"
T = "hatemi_2017_sex_freq"
ITEMS = ["given_oral_sex", "sex_w_female_on_top", "doggy_style", "masturbation", "sex_toys",
         "mouth_contact_w_breast", "s_m", "feel_breasts", "missionary_male_on_top",
         "kissing_on_mouth", "som_touching_your_genitalia", "rubbing_genitalia",
         "touching_som_genitalia", "received_oral_sex", "face_to_face_sex", "anal_sex",
         "public_sex", "filmed_self_having_sex"]
COVS = ["cov_sex", "cov_age", "cov_education", "cov_pid7", "cov_ideology7"]


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
    d = pd.read_csv(dv_fetch(DOI, "hcm.csv", RAW_DIR))
    assert len(d) == 1058
    d = d.rename(columns={d.columns[0]: "id", "biological_sex": "cov_sex", "age": "cov_age",
                          "education": "cov_education", "self_reported_pid": "cov_pid7",
                          "self_reported_ideology": "cov_ideology7"})
    assert d["id"].is_unique
    for c in COVS:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
    t = d.melt(id_vars=["id"] + COVS, value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
    emit({T: (t, {i: set(range(1, 6)) for i in ITEMS})})


if __name__ == "__main__":
    main()
