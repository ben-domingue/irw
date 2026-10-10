#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/TKXWRF
# DOI: 10.7910/DVN/TKXWRF (dataset; the article, "Tungiasis reduces children's quality of
#   life which is moderated by their caregiver's mental health and parenting style", was
#   submitted to Quality of Life Research per the deposit's codebook and readme)
#   Elson, L., Otieno, B., Matharu, A. K., Rithi, N., Chongwo, E., Mutebi, F.,
#   Feldmeier, H., Kruecken, J., Fillinger, U., & Abubakar, A. (2024). Replication Data
#   for: Assessing the impact of tungiasis on children's quality of life in two rural
#   communities in Kenya. Harvard Dataverse.
# Data: "Elson_Tungiasis QoL dataset_anon.csv" (format=original): 397 school pupils aged
#       8-14 in Kwale and Siaya counties, Kenya, interviewed Feb 2020-Apr 2021 x 115
#       columns. "Elson Tungiasis QoL dataset Codebook.pdf" (S10 Supporting Information)
#       documents every variable; the readme gives the licence.
# License: CC BY 4.0 (Dataverse record and readme).
#
# Item text: not shipped. The codebook gives a short description per item ("the jiggers
#   make the pupil feel embarrassed", "KIDSCREEN52 physical wellbeing Q1") and the anchor
#   range, not the administered wording, and the CSV has no labels. KIDSCREEN is a
#   `block` row in itemtext/instrument_rights_register.csv in any case.
#
# Tables (item = the deposit's column name):
#   elson_2024_kidscreen52  childs_health .. child_been_bullied: the 52 KIDSCREEN-52 items
#                           (codebook: physical wellbeing Q1-5, psychological wellbeing,
#                           moods and emotions, self-perception, autonomy, parent relations
#                           and home life, financial resources, social support and peers,
#                           school environment, bullying), 1-5 as stored. The codebook
#                           anchors run "extremely good - bad" for childs_health and "not
#                           at all - very much" (or the dimension's frequency scale) for
#                           the rest; negatively worded items are stored as worded.
#   elson_2024_tmdlqi       embarrassed .. itch_feel: the 10-item Tungiasis-modified
#                           Dermatology Life Quality Index, 0 not at all .. 3 a lot; asked
#                           of the 196 infected pupils only.
# Skipped: tmdlqi and tmdlqi_gps (total and its quintile groups), the ten KIDSCREEN
#   dimension totals (*p_total, *p_totals) and their T-values (kp52*_t, total_tvalues),
#   intensityscore (flea count), rfs_date (interview date), and the household and
#   caregiver variables (adultslivewith .. hugchild_0no_1yes, ses, parent_stress_tot,
#   depress_class), which describe the caregiver or household rather than the pupil and
#   are left to the source.
# Covariates: cov_tungiasis (tungiasis_status: 0 uninfected, 1 infected),
#   cov_severity (intensity_group_fleacounts: 0 uninfected, 1 mild, 2 severe),
#   cov_county (region_code_1kw_2si: 1 Kwale, 2 Siaya), cov_sex (0 female, 1 male),
#   cov_age (pupil_age).
# cluster_id = schoolid. id = pupil_id_anon (the deposit's anonymised pupil code).

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
import re

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_tkxwrf"
FNAME = "Elson_Tungiasis QoL dataset_anon.csv"
TMDLQI = ["embarrassed", "diff_walk_run", "conc_itch", "aff_sleep", "aff_friendship",
          "cruel_unkind", "feel_sad", "anger", "pain_feel", "itch_feel"]
COVS = {"tungiasis_status": "cov_tungiasis", "intensity_group_fleacounts": "cov_severity",
        "region_code_1kw_2si": "cov_county", "sex": "cov_sex", "pupil_age": "cov_age"}
SKIP_RE = re.compile(r"^(tmdlqi|tmdlqi_gps|\w+p_totals?|kp52\w+_t|total_tvalues|intensityscore|"
                     r"rfs_date|ses|adultslivewith|who_cares|unwell_goes|mother_ed|father_ed|"
                     r"father_away|mother_away|parent_schmeet|family_illmonths|"
                     r"family_disability|parent_stress_tot|depress_class|hhh_sex|hhhage|"
                     r"caregiver_sex|caregiver_age|ophanhood|time_spend|"
                     r"family_fear_0no_1yes|hugchild_0no_1yes)$")


def main() -> None:
    d = pd.read_csv(dv_fetch("10.7910/DVN/TKXWRF", FNAME, RAW_DIR)).copy()
    assert d.shape == (397, 115) and d["pupil_id_anon"].is_unique
    cols = list(d.columns)
    ks = cols[cols.index("childs_health"):cols.index("child_been_bullied") + 1]
    assert len(ks) == 52
    used = set(ks) | set(TMDLQI) | set(COVS) | {"pupil_id_anon", "schoolid"}
    rest = [c for c in cols if c not in used and not SKIP_RE.match(c)]
    assert not rest, rest
    d["id"] = d["pupil_id_anon"]
    d["cluster_id"] = d["schoolid"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {
        "elson_2024_kidscreen52": (long(d, ks, covs, valid=range(1, 6), extra=("cluster_id",)),
                                   {i: set(range(1, 6)) for i in ks}),
        "elson_2024_tmdlqi": (long(d, TMDLQI, covs, valid=range(0, 4), extra=("cluster_id",)),
                              {i: set(range(4)) for i in TMDLQI}),
    }
    assert set(out["elson_2024_tmdlqi"][0]["cov_tungiasis"]) == {1}
    emit(out)


if __name__ == "__main__":
    main()
