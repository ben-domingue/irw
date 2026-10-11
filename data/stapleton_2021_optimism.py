#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/5ZAFIF
# DOI: 10.1007/s11109-021-09717-7
#   Stapleton, C. E., Oliver, J., & Wolak, J. (2021). The Political Consequences of an
#   Optimistic Personality. Political Behavior. Data: Wolak, J., Stapleton, C., & Oliver, J.
#   (2021). Replication Data for: The Political Consequences of an Optimistic Personality.
#   Harvard Dataverse, V1.
# Data: "2008 CCAP optimism replication data.dta" (20,000 respondents of the 2008 Cooperative
#       Campaign Analysis Project, the authors' module) and "2018 CCES optimism replication
#       data.dta" (1,000 respondents of the authors' 2018 CCES team module). Every item is
#       stored rescaled to 0-1 (a 5-point item as 0, .25, .5, .75, 1; a 7-point item in
#       sixths); the script maps each back to its integer scale. Variable labels carry the
#       LOT-R stems and, for the TIPI, the adjective pair and the stored direction.
#       The deposit is the authors' own replication file of their own survey modules, not a
#       copy of a panel distributed by an institute; flagged for a ruling all the same.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped. The LOT-R stems are in the .dta variable labels but its five
#   anchors are not in the file (no value labels at either level); the TIPI labels are
#   "Extravert: 1-describes 0-does not describe" (a direction note, not the item), and the
#   knowledge items are described ("Office held by John Dingell"), not quoted.
#
# Tables:
#   stapleton_2021_lotr      opt1-opt3, pess1-pess3 (LOT-R, 6 scored items), 1-5. Both
#                            samples (cov_study = ccap2008 / cces2018); the pess items are
#                            stored in the pessimism direction, as deposited.
#   stapleton_2021_tipi      the ten TIPI items (2008 only), 1-7, stored in the trait
#                            direction: the five negatively keyed adjectives (reserved,
#                            disorganized, conventional, critical, calm) were reversed by
#                            the authors ("0-describes 1-does not describe").
#   stapleton_2021_polknow   know1-know14 (2008): 14 office-holder / fact questions, 0/1.
#   stapleton_2021_polknow18 eight 2018 partisan-control knowledge items, 0/1.
# Skipped: scale means and sums (opti, pessi, optimism, extro .. emostab, tknow, kpknow,
#   kpstate18, kpnat), emostab1/2 (neuroticism1/2 re-reversed), single attitude and
#   participation questions, weights.
# Covariates: cov_study, cov_female (1 female), cov_age, cov_pid7 (0 strong Democrat ..
#   6 strong Republican; September wave in 2008), cov_educ (1 no HS .. 6 post-grad, from the
#   deposit's 0-1 code).
# id: c08_<caseid> / c18_<caseid>.

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_5zafif"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DOI = "10.7910/DVN/5ZAFIF"
P = "stapleton_2021_"


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


def long(d: pd.DataFrame, items: list, covs: list, valid) -> pd.DataFrame:
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    bad = t[~t["resp"].isin(list(valid))]
    assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp"] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


def unscale(s: pd.Series, k: int) -> pd.Series:
    """A k-point item stored as 0 .. 1 in (k-1)ths -> 1 .. k."""
    v = (s * (k - 1)).round()
    ok = s.isna() | ((v - s * (k - 1)).abs() < 1e-4)
    assert ok.all(), f"not an evenly rescaled item: {s[~ok].unique()[:5]}"
    return (v + 1).astype("Int64")


LOTR = ["opt1", "opt2", "opt3", "pess1", "pess2", "pess3"]
TIPI = ["extrovert1", "extrovert2", "conscient1", "conscient2", "openness1", "openness2",
        "agreeable1", "agreeable2", "neuroticism1", "neuroticism2"]
KNOW08 = [f"know{k}" for k in range(1, 15)]
KNOW18 = ["kprep18", "kpsen18a", "kpsen18b", "kpgov18", "kphouse18", "kpsen18", "kpssen18",
          "kpshouse18"]
COVS = ["cov_study", "cov_female", "cov_age", "cov_pid7", "cov_educ"]


def prep(d: pd.DataFrame, study: str, pid: str, tag: str) -> pd.DataFrame:
    assert d["caseid"].is_unique
    d = d.copy()
    d["id"] = tag + d["caseid"].astype(int).astype(str)
    d["cov_study"] = study
    d["cov_female"] = d["female"].astype("Int64")
    d["cov_age"] = d["age"].astype("Int64")
    d["cov_pid7"] = d[pid].astype("Int64")
    d["cov_educ"] = unscale(d["educ"], 6)
    for c in LOTR:
        d[c] = unscale(d[c], 5)
    return d


def main() -> None:
    d08, m08 = pyreadstat.read_dta(str(dv_fetch(DOI, "2008 CCAP optimism replication data.dta", RAW_DIR)))
    d18, m18 = pyreadstat.read_dta(str(dv_fetch(DOI, "2018 CCES optimism replication data.dta", RAW_DIR)))
    assert len(d08) == 20000 and len(d18) == 1000
    for c in LOTR:
        assert m08.column_names_to_labels[c] == m18.column_names_to_labels[c], c
    d08 = prep(d08, "ccap2008", "pids", "c08_")
    d18 = prep(d18, "cces2018", "pid", "c18_")
    for c in TIPI:
        d08[c] = unscale(d08[c], 7)
    for c in KNOW08 + KNOW18:
        src = d08 if c in KNOW08 else d18
        assert set(src[c].dropna().unique()) <= {0.0, 1.0}, c
    both = pd.concat([d08[["id", *COVS, *LOTR]], d18[["id", *COVS, *LOTR]]], ignore_index=True)
    assert both["id"].is_unique
    out = {
        P + "lotr": (long(both, LOTR, COVS, range(1, 6)), {i: set(range(1, 6)) for i in LOTR}),
        P + "tipi": (long(d08, TIPI, COVS, range(1, 8)), {i: set(range(1, 8)) for i in TIPI}),
        P + "polknow": (long(d08, KNOW08, COVS, (0, 1)), {i: {0, 1} for i in KNOW08}),
        P + "polknow18": (long(d18, KNOW18, COVS, (0, 1)), {i: {0, 1} for i in KNOW18}),
    }
    emit(out)


if __name__ == "__main__":
    main()
