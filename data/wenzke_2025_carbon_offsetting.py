#!/usr/bin/env python3
# Source: https://doi.org/10.5281/zenodo.17802433
# DOI: 10.5281/zenodo.17802433 (dataset; the record names no paper)
#   Wenzke, Malin Anna (2025). Closing the Attitude-Behaviour Gap: Acceptance of Mandatory
#   Carbon Offsetting in Tourism [Data set]. Zenodo.
# Data: Klimakompensiert.sav: 379 customers of a Swiss travel company (online survey,
#       German; `language` is constant 1 = Deutsch) x 41 columns. The record says the
#       questionnaire is built on the Theory of Planned Behaviour; the variable labels
#       carry the German statements, the value labels the anchors.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Cheap at both levels for the statement items (German stems in
#   the variable labels; value labels give the end anchors, 1 "trifft/stimme ueberhaupt
#   nicht zu" .. 5 "trifft/stimme voll und ganz zu", 2-4 unlabelled), but the English
#   would be IRW's, and the semantic-differential items (ATT_5-ATT_12, KNOW_4-5) carry
#   only their adjective pairs: the object being rated is not in the deposit.
#
# Tables (1-5 as stored; item = the deposit's variable name):
#   wenzke_2025_knowledge      KNOW_1-KNOW_3  feeling well informed (travel's
#                              environmental impact, CO2 savings, the operator's climate
#                              engagement)
#   wenzke_2025_attitude       ATT_1-ATT_4    agreement statements on tourism's CO2
#                              contribution and on operators' investment in climate
#                              projects
#   wenzke_2025_att_sd_a       ATT_5-ATT_8    semantic differential (schlecht-gut,
#                              unnoetig-notwendig, unerfreulich-erfreulich,
#                              unglaubwuerdig-glaubwuerdig); object not given in the deposit
#   wenzke_2025_att_sd_b       ATT_9-ATT_12   semantic differential (schlecht-gut,
#                              nicht nuetzlich-nuetzlich, nicht wuenschenswert-
#                              wuenschenswert, unpassend-passend); object not given
#   wenzke_2025_info_quality   KNOW_4-KNOW_5  how visible / how understandable the
#                              operator's climate information was
#   wenzke_2025_pbc            PBC_1-PBC_2    perceived behavioural control
#   wenzke_2025_personal_norm  PEN_1-PEN_2    personal norm
#   wenzke_2025_social_norm    SON_1-SON_2    subjective norm
#   wenzke_2025_intention      INT_1-INT_2    intention for the next holiday
# Skipped: quality and duration (survey-platform quality index and completion time),
#   KNOW_6-KNOW_12 and KNOW_10a (where the respondent saw climate information: a
#   multi-select checklist and its free text), ATT_17 (who should choose the climate
#   project: nominal), language (constant).
# Covariates: cov_age_group (DEM_1, 1 18-25 .. 7 over 75), cov_travel_party (SEG_1:
#   1 alone, 2 two, 3 group, 4 does not remember), cov_transport (SEG_2: 1 plane, 2 rail,
#   3 bus, 4 car, 5 does not remember), cov_destination (SEG_3: 1 Switzerland, 2 Europe,
#   3 long-haul, 4 does not remember).
# id: row index (no id column).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


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
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path
import pyreadstat

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.17802433"
URL = "https://zenodo.org/api/records/17802433/files/Klimakompensiert.sav/content"
P = "wenzke_2025_"
TABLES = {"knowledge": ["KNOW_1", "KNOW_2", "KNOW_3"],
          "attitude": ["ATT_1", "ATT_2", "ATT_3", "ATT_4"],
          "att_sd_a": ["ATT_5", "ATT_6", "ATT_7", "ATT_8"],
          "att_sd_b": ["ATT_9", "ATT_10", "ATT_11", "ATT_12"],
          "info_quality": ["KNOW_4", "KNOW_5"],
          "pbc": ["PBC_1", "PBC_2"], "personal_norm": ["PEN_1", "PEN_2"],
          "social_norm": ["SON_1", "SON_2"], "intention": ["INT_1", "INT_2"]}
COVS = {"DEM_1": "cov_age_group", "SEG_1": "cov_travel_party", "SEG_2": "cov_transport",
        "SEG_3": "cov_destination"}
SKIP = ["quality", "duration", "ATT_17", "language", "KNOW_10a"] + \
    [f"KNOW_{i}" for i in range(6, 13)]


def main() -> None:
    d, meta = pyreadstat.read_sav(str(download(URL, RAW_DIR / "Klimakompensiert.sav")))
    assert d.shape == (379, 41) and (d["language"] == 1).all()
    items = [c for its in TABLES.values() for c in its]
    assert set(items) | set(COVS) | set(SKIP) == set(d.columns)
    for c in items:
        assert set(meta.variable_value_labels[c]) == {1, 2, 3, 4, 5}, c
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}
    for suf, its in TABLES.items():
        out[P + suf] = (long(d, its, covs, valid=range(1, 6)), {i: set(range(1, 6)) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
