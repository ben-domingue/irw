#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC12296581
# DOI: 10.7717/peerj.19707
#   "Psychological distress and problematic internet use among language
#   teachers: a latent profile analysis" (Shen, Liu & Chen, 2025), PeerJ 13:e19707.
# Data: PeerJ supplementary files from the Europe PMC supplementaryFiles zip:
#       peerj-13-19707-s002.sav (1,259 x 48 raw data, one row per teacher) and
#       peerj-13-19707-s003.doc ("Data Code": demographic codes, every item's
#       English wording and the response anchors of each scale).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data are
#          the article's own supplementary file.
#
# Item text: shipped for dass21, bsmas and sabas; NOT shipped for igds9sf, which
#   is `block` in itemtext/instrument_rights_register.csv (2026-09-09 ruling).
#   Variable labels: present on every item
#   (the English stem, e.g. S1 "I found it hard to wind down"). Value labels:
#   present on the five demographics only, none on any item; the anchors come
#   from the s003 codebook (DASS 0 not at all .. 3 most of the time; BSMAS
#   very rarely .. very often; SABAS strongly disagree .. strongly agree;
#   IGDS9-SF never .. very often). The survey used the Chinese versions of all
#   four scales (paper, Instruments); no Chinese wording is in the deposit, so
#   the English is a translated substitute (language = Chinese).
#
# Sample: 1,259 primary and junior-high school language teachers in China
# (paper: 1,848 collected, 589 deleted for missing data or < 3 min completion).
# `code` is the source's respondent number (unique), used as id.
#
# Tables (item codes are the source column names):
#   shen_2025_dass21    DASS-21, S1-S7 / A1-A7 / D1-D7, 0-3
#   shen_2025_bsmas     Bergen Social Media Addiction Scale, SD1-SD6, 1-5
#   shen_2025_sabas     Smartphone Application-Based Addiction Scale, PD1-PD6, 1-6
#   shen_2025_igds9sf   Internet Gaming Disorder Scale-Short Form, GD1-GD9, 1-5
#
# No missing cells, no fractional values. 25 rows share all 47 non-id columns with
# another row; 23 are straight-line floor responders (0 on all DASS items, 1 on
# all others) and 2 are one step off the floor, each in one of only 32 possible
# demographic cells. Chance coincidence at the floor, not a duplicate network:
# kept as genuine respondents.

import io
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12296581/supplementaryFiles"

DASS = ["S1", "A1", "D1", "A2", "D2", "S2", "A3", "S3", "A4", "D3", "S4", "S5", "D4",
        "S6", "A5", "D5", "D6", "S7", "A6", "A7", "D7"]
TABLES = {
    "shen_2025_dass21": (DASS, {0, 1, 2, 3}),
    "shen_2025_bsmas": ([f"SD{i}" for i in range(1, 7)], {1, 2, 3, 4, 5}),
    "shen_2025_sabas": ([f"PD{i}" for i in range(1, 7)], {1, 2, 3, 4, 5, 6}),
    "shen_2025_igds9sf": ([f"GD{i}" for i in range(1, 10)], {1, 2, 3, 4, 5}),
}
COV = {
    "gender": "cov_gender",                  # 1 male, 2 female
    "schooltype": "cov_school_type",         # 1 public, 2 private
    "schoolstage": "cov_school_stage",       # 1 junior, 2 primary (value labels)
    "headteacher": "cov_homeroom_teacher",   # 1 yes, 2 no
    "teachingexperience": "cov_teaching_experience",  # 1 <=5 years, 2 >5 years
}


def load():
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    blob = zipfile.ZipFile(io.BytesIO(r.content)).read("peerj-13-19707-s002.sav")
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(blob)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    return d, meta


def main() -> None:
    d, _ = load()
    assert d.shape == (1259, 48), d.shape
    assert d["code"].is_unique and d["code"].notna().all()
    assert not d.isna().any().any()

    item_cols = [c for items, _ in TABLES.values() for c in items]
    assert len(item_cols) == len(set(item_cols))
    accounted = {"code"} | set(COV) | set(item_cols)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    assert len(TABLES) == len(set(TABLES))

    # duplicates: only straight-line minimum responders (see header)
    dup = d.drop(columns="code").duplicated(keep=False)
    floor = d[DASS].sum(axis=1) + (d[[c for c in item_cols if c not in DASS]] - 1).sum(axis=1)
    assert int(dup.sum()) == 25 and (floor[dup] <= 1).all()

    d = d.rename(columns={"code": "id", **COV})
    d["id"] = d["id"].astype(int)
    covs = list(COV.values())
    for c in covs:
        d[c] = d[c].astype(int)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (items, pvset) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(items)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(pvset) for i in items}
        for i in items:
            assert set(t.loc[t["item"] == i, "resp"]) <= pvset, (name, i)
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
