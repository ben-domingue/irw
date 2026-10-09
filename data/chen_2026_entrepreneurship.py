#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/N56YBG
# DOI: 10.4018/IJABIM.396958
#   Chen, C., Zhou, W., Lu, Y., & Cai, Z. (2026). The Study of the Relationship Between
#   College Students' Entrepreneurial Motivation and Entrepreneurial Intention.
#   International Journal of Asian Business and Information Management, 16(1), 1-22.
# Data: Harvard Dataverse 10.7910/DVN/N56YBG (Chen, Chiwei; 2024-01-10),
#       dataset1ESatisfactionEN.sav (format=original): 330 Chinese college students x 51
#       columns -- V1-V37 five-point items whose variable labels name the construct and
#       item number ("SelfPursuitQ1", "EntreprenurialIntentionQ2" [sic]), TotalScore and
#       ten construct means, Gender, Grade, ProfessionalMajor.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Variable labels are construct names with a number, not stems;
#   no value labels on any item; no questionnaire in the deposit.
#
# Item codes: the deposit's variable names V1-V37 (the labels are construct-plus-number
#   and carry typos, so they are reported here instead: V1-V2 SelfPursuit, V3-V4
#   ReputationPursuit, V5-V6 SocialContribution, V7-V9 EconomicPursuit, V10-V17
#   EntrepreneurialIntention, V18-V24 CurriculumManagement, V25-V27 TeachingStaff,
#   V28-V30 TeachingContent, V31-V33 AssessmentEvaluation, V34-V37 OverallCourseEvaluation).
# Tables (1-5 as stored):
#   chen_2026_entre_motivation   V1-V9    entrepreneurial motivation (four dimensions)
#   chen_2026_entre_intention    V10-V17  entrepreneurial intention
#   chen_2026_course_satisfaction V18-V37 satisfaction with innovation and
#                                         entrepreneurship courses (five dimensions)
#   The dimension tables hold one construct each with several facets, so run_qc may flag
#   nothing (V-codes share one prefix); the facet map is above.
# Skipped: TotalScore and the ten construct means.
# Covariates: cov_gender (1 male, 2 female), cov_grade (1 freshman .. 4 senior),
#   cov_major (ProfessionalMajor: 1 economics and management, 2 science and engineering,
#   3 arts and history, 4 politics and law, 5 agriculture, 6 education, 7 medical, 8 other).
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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_n56ybg"
P = "chen_2026_"
TABLES = {"entre_motivation": (1, 9), "entre_intention": (10, 17),
          "course_satisfaction": (18, 37)}
COVS = {"Gender": "cov_gender", "Grade": "cov_grade", "ProfessionalMajor": "cov_major"}
LABEL_PREFIX = {1: "SelfPursuit", 10: "EntrepneurialIntention", 18: "CurriculumManagement",
                37: "OverallCourseEvaluation"}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/N56YBG", "dataset1ESatisfactionEN.sav", RAW_DIR)))
    assert d.shape == (330, 51)
    lab = meta.column_names_to_labels
    for n, pre in LABEL_PREFIX.items():
        assert lab[f"V{n}"].startswith(pre), (n, lab[f"V{n}"])
    items = [f"V{i}" for i in range(1, 38)]
    means = [c for c in d.columns if c not in items and c not in COVS]
    assert len(means) == 11, means
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}
    for suf, (lo, hi) in TABLES.items():
        its = [f"V{i}" for i in range(lo, hi + 1)]
        out[P + suf] = (long(d, its, covs, valid=range(1, 6)), {i: set(range(1, 6)) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
