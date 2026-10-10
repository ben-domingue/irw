#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/HPJFSD
# DOI: 10.1371/journal.pone.0337603
#   Kim, H., Kim, G., Lee, T., & Lee, J.-H. (2025). "Unraveling participant
#   motivation dynamics in local-centric secondhand digital sharing platforms",
#   PLOS ONE. Data Availability points to this deposit.
# Data: Harvard Dataverse 10.7910/DVN/HPJFSD, "Karrot market user's motivation,
#       attitudes and behavior" (kim, gyuhwan; deposited 2025-08-05).
#       Karrot_Dataset.xlsx (file 11850859, one sheet): 450 Seoul adults who had
#       bought on Karrot (Macromill Embrain online panel, Aug-Sep 2022) x num + 26
#       columns named q<k>. No codebook in the deposit; the paper's S1 File
#       (pone.0337603.s009) is the questionnaire, Table 1 the retained items.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The xlsx has only q<k> headers (no labels at either
#   level). The English wording is in the paper's Table 1 and S1 File, but the
#   data's q-numbers do NOT follow S1 File's numbering (S1 numbers the Likert
#   block 31-53; the data has q31-41, 43, 44, 45, 47, 48, 50, 52, 53, 54), so the
#   item-to-wording tie within each block is positional and would need a Step 5b
#   verification.
#
# Constructs (inferred -- data note): the 20 Likert columns are the paper's 20
#   retained Table 1 indicators, in Table 1's order: eco1-3, env1-5, int1-3,
#   rep1-2, att1-4, beh1-3. Evidence: block sizes 3/5/3/2/4/3 match Table 1, and
#   each eco/env/int/rep item correlates more with its own block than with any
#   other (asserted below). The attitude/behaviour boundary is NOT pinned by the
#   data: q45 and q50 correlate slightly more with the behaviour block than with
#   the attitude block, so that split rests on Table 1's order and 4/3 sizes
#   alone. The S1 File's extra items (two economic, one reputation) are not in
#   the deposit.
# Tables (all 1-7 agreement ratings, as stored; the paper says "Likert-scale" and
#   gives no anchors):
#   kim_2025_karrot_econ_motiv     q31-q33  economic motivations
#   kim_2025_karrot_env_motiv      q34-q38  environmental motivations
#   kim_2025_karrot_interact_motiv q39-q41  interaction motivations
#   kim_2025_karrot_reput_motiv    q43-q44  reputation ("manner temperature")
#   kim_2025_karrot_attitude       q45, q47, q48, q50  attitude
#   kim_2025_karrot_behav_intent   q52-q54  behavioural intention
# Covariates, written as labels; the codes were matched to the paper's reported
#   counts (asserted): q1 -> cov_gender (1 male 210, 2 female 240), q3 ->
#   cov_age_group (1 20-29, 2 30-39, 3 40-49; codes 4 and 5 are both written
#   "50+", the paper's own band, since the 4/5 split is not documented), q8 ->
#   cov_income (monthly household, <1M KRW ... >5M KRW), q57 -> cov_education,
#   q23 -> cov_other_dsp (used sharing platforms other than Karrot: yes/no).
# Skipped: q55 (binary, 235/215; matches no reported characteristic).
# id: num (1..450, unique). All 450 rows kept; the paper drops one z-score
#   outlier for its SEM, which is an analysis choice.

import os
import sys
from itertools import combinations
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw" / "kim_2025_karrot"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/11850859"

TABLES = {
    "kim_2025_karrot_econ_motiv": ["q31", "q32", "q33"],
    "kim_2025_karrot_env_motiv": ["q34", "q35", "q36", "q37", "q38"],
    "kim_2025_karrot_interact_motiv": ["q39", "q40", "q41"],
    "kim_2025_karrot_reput_motiv": ["q43", "q44"],
    "kim_2025_karrot_attitude": ["q45", "q47", "q48", "q50"],
    "kim_2025_karrot_behav_intent": ["q52", "q53", "q54"],
}
COVS = {"q1": "cov_gender", "q3": "cov_age_group", "q8": "cov_income",
        "q57": "cov_education", "q23": "cov_other_dsp"}
LABELS = {"q1": {1: "male", 2: "female"},
          "q3": {1: "20-29", 2: "30-39", 3: "40-49", 4: "50+", 5: "50+"},
          "q8": {1: "<1M KRW", 2: "1-2M KRW", 3: "2-3M KRW", 4: "3-4M KRW",
                 5: "4-5M KRW", 6: ">5M KRW"},
          "q57": {1: "less than high school", 2: "high school", 3: "college",
                  4: "master's or higher"},
          "q23": {1: "yes", 2: "no"}}
SKIP = {"q55": "binary with no documented meaning (235/215 matches nothing the paper reports)"}


def fetch() -> Path:
    p = RAW_DIR / "Karrot_Dataset.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (450, 27) and d["num"].is_unique
    items = [c for its in TABLES.values() for c in its]
    assert set(d.columns) == {"num"} | set(items) | set(COVS) | set(SKIP)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    # covariate codes reproduce the paper's reported counts
    assert d["q1"].value_counts().to_dict() == {2: 240, 1: 210}
    assert d["q8"].value_counts().sort_index().tolist() == [29, 36, 56, 68, 65, 196]
    assert d["q57"].value_counts().sort_index().tolist() == [5, 45, 340, 60]
    assert d["q23"].value_counts().sort_index().tolist() == [141, 309]
    # the construct blocks are the correlation blocks
    r = d[items].corr()
    blocks = list(TABLES.values())
    def mean_r(x, b):
        vals = [r.loc[x, y] for y in b if y != x]
        return sum(vals) / len(vals)
    for name, b in TABLES.items():
        for x in b:
            own = mean_r(x, b)
            other = {n: mean_r(x, b2) for n, b2 in TABLES.items() if n != name}
            top = max(other, key=other.get)
            print(f"    {x}: own-block r={own:.2f}; highest other {top[16:]} r={other[top]:.2f}")
            # eco/env/int/rep are pinned by the correlations; the attitude/behaviour
            # boundary is not (both load on one cluster) and rests on Table 1's 4/3 order
            if not name.endswith(("attitude", "behav_intent")):
                assert own > max(other.values()), (x, own, other)

    for src, labels in LABELS.items():
        assert set(d[src]) <= set(labels), src
        d[src] = d[src].map(labels)
    d = d.rename(columns={"num": "id", **COVS})
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 8)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        checks = run_qc(t)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload")
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
