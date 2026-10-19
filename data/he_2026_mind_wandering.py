#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/21070342
# DOI: 10.6084/m9.figshare.21070342.v8
#   He, H. (2026). mind wandering and depression [Dataset]. figshare.
# Data: "Rawdata_Study1.xlsx" (262 participants) and "Rawdata_Study2.xlsx"
#   (134) -- thought-probe responses collected during a sustained-attention
#   (SART) task: exactly 10 probes per participant, each probe answered on a
#   1-6 scale.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. The .xlsx headers are the probe abbreviations
#   (MW, FBE, Intention, Awareeness) and the deposit ships no codebook, so the
#   probe wording is only in the author's paper. The deposit's other files are
#   the fitted HLM model frames, which carry no wording either.
#
# TWO SAMPLES, ONE FILE. Both studies administered the same probes on the same
#   1-6 scale, with the same 10-probes-per-person design, so they merge under
#   cov_study rather than splitting into two tables. Study 2 asked only the MW
#   and FBE probes; long format carries that without padding. The two id
#   ranges OVERLAP (119 ids appear in both files and are different people), so
#   id is prefixed with the study -- study1_12, study2_12 -- rather than
#   offset.
#
# REPEATED MEASURES: wave is the SART trial the probe interrupted (10-250 in
#   study 1, 11-276 in study 2), which is the source's own numeric order and
#   keeps the spacing between probes. (id, item, wave) is unique.
#
# NOT SHIPPED: ACC, whether the SART response at that trial was correct. It is
#   a 0/1 task outcome rather than a probe response, so it belongs neither in
#   a 1-6 probe table (mixed scales) nor in a table of its own (one item).
#   The deposit's Model*.csv / SModel*.csv files are z-scored copies of these
#   same frames for the paper's HLM fits, and are not a second source.
#
# ONE table, 396 respondents, 3,960 probe occasions:
#   he_2026_mind_wandering   4 items, 1-6
#     MW          mind wandering
#     FBE         (the deposit's own code; the paper is the only source)
#     Intention   intentionality of the mind wandering   (study 1 only)
#     Awareeness  awareness of it -- the source's spelling, kept as given
#                                                         (study 1 only)
# Covariates: cov_study (study1/study2) and cov_bdi_total, the participant's
#   Beck Depression Inventory sum, which is constant within every id in both
#   files.
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "21070342" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE = 21070342
FILES = {"study1": "Rawdata_Study1.xlsx", "study2": "Rawdata_Study2.xlsx"}
NAME = "he_2026_mind_wandering"
SCALE = set(range(1, 7))
ITEMS = {"study1": ["MW", "FBE", "Intention", "Awareeness"],
         "study2": ["MW", "FBE"]}


def fetch(fname: str) -> Path:
    p = RAW_DIR / fname
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == fname][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    parts = []
    for study, fname in FILES.items():
        d = pd.read_excel(fetch(fname))
        cols = ITEMS[study]
        known = set(cols) | {"ID", "Trial", "ACC", "BDI"}
        unaccounted = [c for c in d.columns if c not in known]
        assert not unaccounted, (study, unaccounted)
        for c in known:
            assert c in d.columns, (study, c)
        assert (d.groupby("ID")["BDI"].nunique() == 1).all(), study
        assert set(d.groupby("ID").size().unique()) == {10}, study
        print(f"{study}: {d['ID'].nunique()} participants x 10 probes; "
              f"ACC dropped (0/1 SART accuracy, not a probe response)")
        d = d.assign(id=study + "_" + d["ID"].astype(int).astype(str),
                     cov_study=study,
                     cov_bdi_total=d["BDI"].astype(int),
                     wave=d["Trial"].astype(int))
        parts.append(d.melt(id_vars=["id", "wave", "cov_study",
                                     "cov_bdi_total"],
                            value_vars=cols, var_name="item",
                            value_name="resp"))

    t = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 1-6 scale: {bad}"
    t = t[["id", "item", "resp", "wave", "cov_study", "cov_bdi_total"]]
    assert not t.duplicated(["id", "item", "wave"]).any()
    assert t["id"].nunique() == 396, t["id"].nunique()
    assert t["item"].nunique() == 4

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} waves={t['wave'].nunique()} "
          f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
