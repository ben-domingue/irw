#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/DataSheet_1_Childhood_trauma_psychache_and_depression_among_university_students_a_moderated_mediation_model_xlsx/26087080
# DOI: 10.3389/fpsyt.2024.1414105
#   Chen, S., Fu, T., Wang, Y., & Sun, G. (2024). "Childhood trauma, psychache, and
#   depression among university students: a moderated mediation model", Frontiers in
#   Psychiatry 15, 1414105.
# Data: Frontiers figshare 10.3389/fpsyt.2024.1414105.s001 (file 47207716), DataSheet_1
#       (...).xlsx: 623 Chinese university students x 135 columns: demographics, item
#       blocks TY1-3, CS1-28, CT1-23, XW1-20, TK1-13, YY1-20, and subscale/total sums.
#       The paper reports analysing 476 of them; all 623 rows are kept.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Levels checked: xlsx headers only (pinyin initials + number, no
#   labels, no codebook). Wording is in the cited Chinese versions.
#
# Blocks -> instruments (paper's Measures section; the abbreviations are pinyin initials):
#   chen_2024_ctq_sf    CS1-28   1-5  Childhood Trauma Questionnaire - Short Form (1 never ..
#                                     5 almost always)
#   chen_2024_aeq       CT1-23   1-7  Ambivalence over Emotional Expression Questionnaire
#                                     (Feng et al.'s 23-item, five-dimension version;
#                                     1 totally disagree .. 7 absolutely agree)
#   chen_2024_bisbas    XW1-20   1-4  BIS/BAS scales (not described in the paper; the file's
#                                     own sums are named "BIS all", "BAS all"; XW1-20 sum to
#                                     "3XW all" on every row)
#   chen_2024_psychache TK1-13   1-5  Psychache Scale (Holden; 1 never .. 5 always); TK1-13
#                                     sum to "4TK all" on every row
#   chen_2024_cesd      YY1-20   1-4  CES-D. The paper scores 0-3; the file stores 1-4 (its
#                                     "5YY all" equals the item sum minus 20 on every row).
#                                     Shipped as stored. Positive items not reversed.
# Skipped: number (kept as id), the PARS-3 physical-activity items TY1-3 (three
#   differently-scaled questions multiplied into a score), and all sums.
# Covariates: cov_gender (1/2), cov_age, cov_bmi, cov_grade (1-5), cov_major (1/2),
#   cov_only_child (1/2), cov_residence (city, 1/2) -- codes (two implausible ages, e.g. 222, set missing) as in the file; the paper
#   names the categories but not the codes.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "chen_2024"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/47207716"

TABLES = {"chen_2024_ctq_sf": ("CS", 28, range(1, 6)), "chen_2024_aeq": ("CT", 23, range(1, 8)),
          "chen_2024_bisbas": ("XW", 20, range(1, 5)), "chen_2024_psychache": ("TK", 13, range(1, 6)),
          "chen_2024_cesd": ("YY", 20, range(1, 5))}
COVS = {"gender": "cov_gender", "age": "cov_age", "BMI": "cov_bmi", "grade": "cov_grade",
        "major": "cov_major", "only child": "cov_only_child", "city": "cov_residence"}
SKIP = ["TY1", "TY2", "TY3", "TY all", "CS V1QN", "CS V2QN", "CS V3XN", "CS V4QH", "CS V5QTH",
        "1CS all", "2CT all", "CTV1HH", "CTV2KW", "CTV3YZZ", "CTV4QX", "CTV5YZF", "BIS all",
        "BAS all", "BAS1JS", "BAS2QL", "3XW all", "4TK all", "5YY all"]


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (623, 135), d.shape
    cols = {t: [f"{p}{i}" for i in range(1, k + 1)] for t, (p, k, _) in TABLES.items()}
    used = {"number"} | set(COVS) | set(SKIP) | {c for v in cols.values() for c in v}
    assert used == set(d.columns), set(d.columns) ^ used
    print(f"  skip {len(SKIP)} columns: PARS-3 items and score, subscale and total sums")
    assert (d[cols["chen_2024_cesd"]].sum(axis=1) - 20 == d["5YY all"]).all()
    assert (d[cols["chen_2024_psychache"]].sum(axis=1) == d["4TK all"]).all()
    assert d["number"].is_unique
    d = d.rename(columns={"number": "id", **COVS})
    d["cov_bmi"] = d["cov_bmi"].round(2)
    bad_age = d["cov_age"] > 100  # e.g. 222: typos
    print(f"  cov_age: {int(bad_age.sum())} implausible value(s) set missing")
    d["cov_age"] = d["cov_age"].where(~bad_age).astype("Int64")
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (_, _, rng) in TABLES.items():
        its = cols[name]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        assert t["resp"].isin(list(rng)).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
