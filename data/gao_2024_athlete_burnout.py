#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/Data_Sheet_1_A_study_on_the_relationship_and_path_between_mental_health_and_burnout_of_Chinese_athletes_CSV/26336833
# DOI: 10.3389/fpsyg.2024.1422207
#   Gao, Y., & Wang, L. (2024). "A study on the relationship and path between mental health
#   and burnout of Chinese athletes", Frontiers in Psychology 15, 1422207.
# Data: Frontiers figshare 10.3389/fpsyg.2024.1422207.s001 (file 47804209),
#       Data_Sheet_1 (...).CSV: 501 elite Chinese athletes x 164 columns: questionnaire items
#       Q1-Q91 (numbered as administered; not all numbers present), recoded "Q<k>score"
#       copies, and scale/subscale scores. No codebook.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Levels checked: CSV headers only (Q61 ...), no labels, no codebook;
#   the paper (PMC11295933) names the instruments but prints no items.
#
# Blocks -> instruments (paper: GAD-7, PHQ-9, APSQ, ABQ; each block's location is pinned by
#   the file's own scores, asserted below):
#   gao_2024_gad7  Q61-67  1-4  GAD-7 as stored (Anxietyscore = sum of Q61score..Q67score,
#                               and Q<k>score = Q<k> - 1, i.e. the usual 0-3)
#   gao_2024_phq9  Q68-76  1-4  PHQ-9 as stored (Deprscore likewise)
#   gao_2024_apsq  Q51-60  1-5  Athlete Psychological Strain Questionnaire (APSQscore = sum
#                               of Q51..Q60)
#   gao_2024_abq   Q77-91  1-5  Athlete Burnout Questionnaire (ABQscore = sum of the score
#                               copies, which reverse Q77 and Q90 -- ABQ items 1 and 14 --
#                               and subtract 1 from the rest). Raw answers shipped, not
#                               reversed.
# Skipped: index (kept as id); Q3 and Q12-Q50 (diet, media use, sleep and chronotype
#   questions of mixed formats, not the four instruments); all Q<k>score copies; every
#   score, subscale and range column.
# Covariates: cov_age (Q1), cov_gender (Q2, 1/2 code).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "gao_2024"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/47804209"

TABLES = {"gao_2024_gad7": (61, 67, range(1, 5)), "gao_2024_phq9": (68, 76, range(1, 5)),
          "gao_2024_apsq": (51, 60, range(1, 6)), "gao_2024_abq": (77, 91, range(1, 6))}
COVS = {"Q1": "cov_age", "Q2": "cov_gender"}


def fetch() -> Path:
    p = RAW_DIR / "data.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def q(a, b, suf=""):
    return [f"Q{i}{suf}" for i in range(a, b + 1)]


def main() -> None:
    d = pd.read_csv(fetch(), encoding="utf-8-sig")
    assert d.shape == (501, 164), d.shape
    # block locations pinned by the file's own scores
    assert (d[q(61, 67, "score")].sum(axis=1) == d["Anxietyscore"]).all()
    assert (d[q(68, 76, "score")].sum(axis=1) == d["Deprscore"]).all()
    assert (d[q(51, 60)].sum(axis=1) == d["APSQscore"]).all()
    assert (d[q(77, 91, "score")].sum(axis=1) == d["ABQscore"]).all()
    for i in range(61, 77):
        assert (d[f"Q{i}"] - 1 == d[f"Q{i}score"]).all()
    items = {c for a, b, _ in TABLES.values() for c in q(a, b)}
    skipped = [c for c in d.columns if c not in items | set(COVS) | {"index"}]
    print(f"  skip {len(skipped)} columns: other questionnaire sections (Q3, Q12-Q50), "
          "recoded score copies, scores and ranges")
    assert d["index"].is_unique
    d = d.rename(columns={"index": "id", **COVS})
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (a, b, rng) in TABLES.items():
        its = q(a, b)
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
