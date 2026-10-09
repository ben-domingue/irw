#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/JU6K33
# DOI: 10.7910/DVN/JU6K33 (dataset; the paper it replicates, "The Relationship between
#   Stress-is-enhancing Mindset and Academic Achievement: Evidence from Variable-centered
#   and Person-centered Analyses", was not found in Crossref)
#   Zhang, Siman (2025). Replication Data for: The Relationship between Stress-is-enhancing
#   Mindset and Academic Achievement. Harvard Dataverse. (The record lists the author as
#   "Siman, Zhang"; the family name is taken to be Zhang.)
# Data: "raw data.xlsx" (format=original): 347 Chinese university students x 59 columns:
#       gender (2、您的性别), age (3、年龄), major (6、专业) and 56 five-point items numbered
#       7-62 by the questionnaire. Non-reversed items' headers are "<n>、<Chinese stem>";
#       reverse-keyed items' headers are just "反<n>" ("reversed n") with no stem, and
#       their values are already reverse-scored: every 反 item correlates positively with
#       the rest of its scale (item-rest r .07-.51). The deposit's other files are SPSS
#       output (.spv) and Mplus latent-profile runs.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The xlsx headers carry the Chinese stem for the 37
#   non-reversed items only; the 19 reversed items have no wording in the deposit, there
#   are no value labels (xlsx), and no questionnaire is deposited. The 12-item Grit Scale
#   is a `block` row in itemtext/instrument_rights_register.csv, as is the UWES.
#
# Item codes: q<n> from the questionnaire number at the start of each header, with "_r"
#   for the reversed 反 items (反7 -> q7_r); reversible.
# Tables (1-5 as stored; constructs by the questionnaire's numbering):
#   zhang_2025_stress_mindset     q7-q14   stress mindset (q8 "experiencing stress
#                                          benefits my learning and growth" ...; 4 reversed)
#   zhang_2025_learning_engagement q15-q31 17 items, the three UWES-S engagement facets
#                                          (vigour 15-20, dedication 21-25, absorption 26-31)
#   zhang_2025_study_performance  q32-q46  self-rated study performance (task completion,
#                                          relations with classmates, initiative)
#   zhang_2025_relative_grades    q47-q50  own scores compared with the class average
#                                          (overall, academic, moral, sports/arts)
#   zhang_2025_grit               q51-q62  12-item Grit Scale (6 reversed)
# Covariates as stored, no labels in the file: cov_gender (1/2), cov_age, cov_major (1/2).
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
import re

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_ju6k33"
P = "zhang_2025_"
TABLES = {"stress_mindset": (7, 14), "learning_engagement": (15, 31),
          "study_performance": (32, 46), "relative_grades": (47, 50), "grit": (51, 62)}
COVS = {"2、您的性别：": "cov_gender", "3、年龄：": "cov_age", "6、专业：": "cov_major"}


def main() -> None:
    d = pd.read_excel(dv_fetch("10.7910/DVN/JU6K33", "raw data.xlsx", RAW_DIR))
    assert d.shape == (347, 59)
    code, num = {}, {}
    for c in d.columns:
        if c in COVS:
            continue
        m = re.match(r"(反)?(\d+)", c)
        n = int(m.group(2))
        code[c] = f"q{n}" + ("_r" if m.group(1) else "")
        num[code[c]] = n
    assert sorted(num.values()) == list(range(7, 63))
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns={**COVS, **code})
    covs = list(COVS.values())
    out = {}
    for suf, (lo, hi) in TABLES.items():
        its = sorted((k for k, n in num.items() if lo <= n <= hi), key=num.get)
        t = long(d, its, covs, valid=range(1, 6))
        # reversed items are stored reversed: each correlates positively with the rest
        w = d[its]
        for i in its:
            assert w[i].corr(w.drop(columns=i).sum(axis=1)) > 0, (suf, i)
        out[P + suf] = (t, {i: set(range(1, 6)) for i in its})
    assert sum(len(set(t["item"])) for t, _ in out.values()) == 56
    emit(out)


if __name__ == "__main__":
    main()
