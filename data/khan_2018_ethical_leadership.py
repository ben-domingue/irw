#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/4IZYKK
# DOI: 10.7910/DVN/4IZYKK (dataset; no paper DOI -- PhD thesis data)
#   Khan, Shazia (2018). "Ethical Leadership, Moral Judgment and Moral Motivation"
#   [data set]. Harvard Dataverse.
# Data: DatafileThesisPhD.tab, downloaded as format=original (SPSS .sav, file id
#       3309855): 176 school teachers x 182 columns, with SPSS variable labels and
#       value labels.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: variable labels carry the full stem for
#   REL1-20/FEL1-20 (ethical leadership) and MID1-10 (moral identity), and value
#   labels carry every response option; SDE/IM variable labels are positional
#   ("Self Deception Enhancement Scale 1") and MM labels name the scenario
#   condition, not the question. So REL/FEL/MID text is cheap (data_labels); not
#   built in this batch (batch kept lean).
#
# Tables (codes kept as stored; several items are stored REVERSED by the source --
# their value labels run the other way, e.g. FEL20 1='Strongly Agree', IM1-19
# 1='Very True' while SDE 1='Not True' -- so resp direction varies across items):
#   khan_2018_ethical_leadership_real     REL1-20  1-6  rating of the respondent's own supervisor
#   khan_2018_ethical_leadership_vignette FEL1-20  1-6  same 20 items, rating the leader in the
#                                         assigned vignette (cov_condition); one FEL20=0 dropped
#                                         (outside the labelled 1-6 set)
#   khan_2018_moral_identity              MID1-10  1-7  (Aquino & Reed 2002 moral identity)
#   khan_2018_bidr_sde                    SDE1-20  1-5  (BIDR self-deceptive enhancement); one
#                                         SDE1=7 dropped (outside the labelled 1-5 set)
#   khan_2018_bidr_im                     IM1-19   1-5  (BIDR impression management; the deposit
#                                         has 19 IM columns, not 20)
#   khan_2018_moral_motivation            MM1-8    1-7  likelihood/motivation to act ethically
#                                         under eight reward/punishment scenarios
# Not shipped: DIT stage scores (Heinz*/Prisoner*/News*/Doc*/Webs*/Student*,
#   pre/post) are derived per-story stage scores, not item responses; Story1-4
#   are four yes/no story decisions with no documented question (labels name the
#   story only); every remaining column is a derived total, bin or residual.
# Sample: 176 teachers in 25 schools (Pakistan; English-language questionnaire).
# Covariates: cov_condition = vignette leader type (1 moral person, 2 moral
#   manager, 3 ethical leader, 4 indecisive); cluster_id = SchoolID.

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "khan_2018"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/3309855?format=original"

TABLES = {
    "khan_2018_ethical_leadership_real": ([f"REL{i}" for i in range(1, 21)], range(1, 7)),
    "khan_2018_ethical_leadership_vignette": ([f"FEL{i}" for i in range(1, 21)], range(1, 7)),
    "khan_2018_moral_identity": ([f"MID{i}" for i in range(1, 11)], range(1, 8)),
    "khan_2018_bidr_sde": ([f"SDE{i}" for i in range(1, 21)], range(1, 6)),
    "khan_2018_bidr_im": ([f"IM{i}" for i in range(1, 20)], range(1, 6)),
    "khan_2018_moral_motivation": ([f"MM{i}" for i in range(1, 9)], range(1, 8)),
}
COVS = {
    "Condition": "cov_condition",
    "SchoolCGT": "cov_school_category",
    "Gender": "cov_gender",
    "Age": "cov_age",
    "EduLevel": "cov_education",
    "JobStat": "cov_level_taught",
    "YearsJob": "cov_years_job",
    "YearsSupervisor": "cov_years_supervisor",
}


def fetch() -> Path:
    p = RAW_DIR / "orig"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, meta = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (176, 182), d.shape
    assert d["ID"].is_unique
    items = [c for its, _ in TABLES.values() for c in its]
    assert len(items) == len(set(items))
    skipped = [c for c in d.columns if c not in set(items) | set(COVS) | {"ID", "SchoolID"}]
    print(f"  [skip] {len(skipped)} columns: DIT stage scores, Story1-4, derived totals/bins, "
          f"identifiers (R.Code, SchoolGroup): {skipped}")

    d = d.rename(columns={"ID": "id", "SchoolID": "cluster_id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id", "cluster_id"] + covs, value_vars=its,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
        bad = ~t["resp"].isin(list(rng))
        if bad.any():
            print(f"  {name}: dropped {bad.sum()} out-of-set value(s): "
                  f"{t.loc[bad, ['item', 'resp']].values.tolist()}")
            assert bad.sum() <= 1
            t = t[~bad]
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "cluster_id"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
