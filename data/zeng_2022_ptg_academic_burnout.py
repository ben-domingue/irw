#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/Data_Sheet_1_Core_belief_challenge_moderated_the_relationship_between_posttraumatic_growth_and_adolescent_academic_burnout_in_Wenchuan_area_during_the_COVID-19_pandemic_xlsx/21219047
# DOI: 10.3389/fpsyg.2022.1005176
#   Zeng, Z., Wang, X., Chen, Q., Gou, Y., & Yuan, X. (2022). "Core belief challenge moderated
#   the relationship between posttraumatic growth and adolescent academic burnout in Wenchuan
#   area during the COVID-19 pandemic", Frontiers in Psychology 13, 1005176.
# Data: Frontiers figshare 10.3389/fpsyg.2022.1005176.s001 (file 37629161), sheet "data":
#       941 adolescents x 67 columns: id, four demographics, three item blocks, and
#       subscale/total means. No codebook.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Levels checked: xlsx headers only (T3Q1 ...), no labels, no
#   codebook; the paper (PMC9554300) names the instruments but prints no items.
#
# Tables (item codes = headers; the first header of each block carries the block name as a
#   prefix -- "PTGT3Q1", "AcademicBornoutT6Q1", "CoreBeliefChallengeT7Q1" -- which is
#   stripped so codes run T3Q1.., T6Q1.., T7Q1..):
#   zeng_2022_ptgi            T3Q1-22  0-5  Posttraumatic Growth Inventory (22-item Chinese
#                                           revision; the file's subscale means are
#                                           changes in self, relationships, philosophy of life)
#   zeng_2022_academic_burnout T6Q1-21 1-5  adolescent academic burnout (21 items; subscales
#                                           inefficiency, emotional exhaustion, teacher-student
#                                           alienation, physical exhaustion)
#   zeng_2022_core_beliefs    T7Q1-9   0-5  Core Beliefs Inventory (9 items)
# Skipped: all subscale and total means; ethnicity and age (their codes are undocumented
#   and include negative values).
# Covariates: cov_gender (1/2), cov_academic_stage (1/2), codes as in the file.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "zeng_2022"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/37629161"

TABLES = {"zeng_2022_ptgi": ("T3", 22, "PTG", range(0, 6)),
          "zeng_2022_academic_burnout": ("T6", 21, "AcademicBornout", range(1, 6)),
          "zeng_2022_core_beliefs": ("T7", 9, "CoreBeliefChallenge", range(0, 6))}
COVS = {"gender": "cov_gender", "AcademicStage": "cov_academic_stage"}
SKIP = ["ethnicity", "age", "CoreBeliefChallenge", "PTG", "PerceivedChangesInSelf",
        "AChangedSenseOfRelationshipWithOthers", "AChangedPhilosophyOfLife", "AcademicBornout",
        "AcademicInefficiency", "EmotionalExhaustion", "AlienationBetweenTeachersAndStudents",
        "PhysicalExhaustion"]


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="data")
    assert d.shape == (941, 67), d.shape
    cols = {}
    for t, (blk, k, pre, _) in TABLES.items():
        src = [f"{pre}{blk}Q1"] + [f"{blk}Q{i}" for i in range(2, k + 1)]
        cols[t] = {s: f"{blk}Q{i}" for i, s in enumerate(src, 1)}
    used = {"id"} | set(COVS) | set(SKIP) | {c for v in cols.values() for c in v}
    assert used == set(d.columns), set(d.columns) ^ used
    print(f"  skip {len(SKIP)} columns: ethnicity/age (undocumented codes), subscale/total means")
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (_, _, _, rng) in TABLES.items():
        cmap = cols[name]
        t = d[["id"] + covs + list(cmap)].rename(columns=cmap).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        assert t["resp"].isin(list(rng)).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in cmap.values()}
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
