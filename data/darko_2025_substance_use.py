#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/MDDYTI
# DOI: 10.1186/s13104-025-07307-y
#   Darko, R. A., & Glozah, F. N. (2025). Psychosocial factors driving common substances
#   used among Ghanaian senior high school students. BMC Research Notes. Data: Darko, R. A.,
#   & Glozah, F. (2025). Self-esteem, peer influence and associated factors driving common
#   substances used among Ghanaian adolescents. Harvard Dataverse, V1.
# Data: "Copy of Correlates of substance use cleaned data..xlsx", one sheet: 425 senior high
#       school students (ages 14-22, two schools) x 171 columns. The column headers are the
#       questionnaire's own wording; the Likert blocks are stored as the option labels
#       ("Strongly Disagree" .. "Strongly Agree"), which the script maps to integers. No
#       separate codebook; the headers are the only documentation.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: shipped (the column headers are the statements and the cells hold the option
#   labels; English administration; built by
#   automated_finding/itemtext_verification/make_itemtext_darko_2025.py).
#
# Tables (item codes are <block>_<k> in header order; the header text for each code is
#   returned by stems(), which the item text builder imports, so the tie is by construction):
#   darko_2025_rses           the 10 Rosenberg Self-Esteem Scale statements, 1 strongly
#                             disagree .. 4 strongly agree (as written; no neutral point).
#   darko_2025_reasons        17 "reasons for substance use" statements (to relax .. use of
#                             substance by a family member), 1 strongly disagree .. 5.
#   darko_2025_perceptions    12 perception-of-substance-use statements, 1-5.
#   darko_2025_interventions  10 school-intervention statements, 1-5.
# Skipped: the substance checklists and frequency questions (Alcohol*, Cigarette*,
#   Shisha*, Marijuana*: ever used, ease of access, where/when used, dependence counts),
#   the derived scores (esteem2, perception, access, their z/t-scores and RECODEs) and the
#   free-text "specify" columns.
# Covariates: cov_age, cov_sex (Female/Male), cov_form (SHS 1 / SHS 2), cov_religion.
# id: the deposit's "No." (its questionnaire number).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_mddyti"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DOI = "10.7910/DVN/MDDYTI"
FNAME = "Copy of Correlates of substance use cleaned data..xlsx"
P = "darko_2025_"
FIVE = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
FOUR = {"Strongly disagree": 1, "Disagree": 2, "Agree": 3, "Strongly agree": 4}
# table -> (first header, last header, option map): a block is the contiguous run of columns
BLOCKS = {
    "reasons": ("To relax", "Use of substance by a family member", FIVE),
    "perceptions": ("When people use substances they feel tired",
                    "Substance use does not affect a person's ability to learn", FIVE),
    "rses": ("On the whole, I am satisfied with myself.",
             "I take a positive attitude toward myself.", FOUR),
    "interventions": ("Awareness talks on substance abuse",
                      "A core unit on drugs and substance abuse in first year", FIVE),
}
COVS = ["cov_age", "cov_sex", "cov_form", "cov_religion"]


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


def load() -> pd.DataFrame:
    d = pd.read_excel(dv_fetch(DOI, FNAME, RAW_DIR))
    assert len(d) == 425 and d["No."].is_unique
    return d


def stems(block: str) -> list:
    """[(item code, header text)] for a block, in questionnaire order."""
    cols = list(load().columns)
    a, b, _ = BLOCKS[block]
    run = cols[cols.index(a): cols.index(b) + 1]
    return [(f"{block}_{k}", c.strip()) for k, c in enumerate(run, 1)]


def main() -> None:
    d = load()
    base = pd.DataFrame({"id": d["No."].astype(int), "cov_age": d["Age"].astype("Int64"),
                         "cov_sex": d["Sex"], "cov_form": d["Form"],
                         "cov_religion": d["Religious affiliation"]})
    out = {}
    for block, (_, _, opts) in BLOCKS.items():
        codes = stems(block)
        w = base.copy()
        for code, header in codes:
            s = d[header]
            bad = s.dropna()[~s.dropna().isin(opts)]
            assert bad.empty, (block, header, bad.unique())
            w[code] = s.map(opts).astype("Int64")
        items = [c for c, _ in codes]
        t = w.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + block] = (t, {i: set(opts.values()) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
