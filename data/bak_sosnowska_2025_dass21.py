#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/4FNIYH
# DOI: 10.7910/DVN/4FNIYH (dataset); paper: Bak-Sosnowska, M., Nowak-Zolty, E., &
#   Trusz, S. (2025). "How the Family of Origin Shapes Mental Health in Young Adults?
#   Unveiling the Connection Between Upbringing and Student Well-Being" (no paper DOI
#   on the Dataverse record).
# Data: Harvard Dataverse 10.7910/DVN/4FNIYH (Slawomir Trusz, 2025),
#       DANE_Lek_Stres_Depresja.xlsx (file 11595582): 473 Polish university students
#       x 120 columns (Lp row number, 17 coded background variables, PSAQ1-70, eight
#       parental-attitude subscale scores, DASS1-21, and the DASS Anx/Stress/Dep sums).
#       No codebook.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: xlsx headers only (no variable or value
#   labels, no codebook); "DASS1".."DASS21" are positional. The wording is the
#   published DASS-21 (Polish version), not in the deposit.
#
# Shipped: bak_sosnowska_2025_dass21 -- DASS1-21, 0-3 (DASS-21 standard 0 = did not
#   apply to me at all .. 3 = applied to me very much). The deposit's own sums confirm
#   the standard DASS-21 item order: Dep = DASS3+5+10+13+16+17+21, Anx =
#   DASS2+4+7+9+15+19+20, Stress = DASS1+6+8+11+12+14+18 on all 473 rows (asserted).
# Skipped: PSAQ1-70 (parental attitudes, mother/father): values include 1.5 on every
#   item and multi-digit entries (12, 23, 30, 32, ...) that look like two answers
#   typed into one cell; the scoring is undocumented in the deposit, so the block is
#   not shipped. The eight parental-attitude scores and the three DASS sums are
#   composites.
# Covariates: the deposit's codes (no codebook): gender, age, residence (childhood,
#   current), education, partnership, financial situation, siblings, family structure,
#   subtenant, parents' employment, family dysfunctions (alcohol/substances, mental
#   illness, mental abuse, physical violence), parents' religiousness, childhood
#   financial situation.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "bak_sosnowska_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/11595582?format=original"
NAME = "bak_sosnowska_2025_dass21"

ITEMS = [f"DASS{i}" for i in range(1, 22)]
SUMS = {"Dep": [3, 5, 10, 13, 16, 17, 21], "Anx": [2, 4, 7, 9, 15, 19, 20],
        "Stress": [1, 6, 8, 11, 12, 14, 18]}
PARENT_SCORES = [f"{a}_{p}" for p in ("Mother", "Father")
                 for a in ("Democratic", "Autocratic", "LibLoving", "LibUnloving")]
COVS = {"Gender": "cov_gender", "Age": "cov_age",
        "Place of residence - childhood": "cov_residence_childhood",
        "Place of residence – currently": "cov_residence_current",
        "EDU": "cov_education", "Partnership situation": "cov_partnership",
        "Financial situation": "cov_financial_situation", "Siblings": "cov_siblings",
        "Structre of family": "cov_family_structure", "Subtenant": "cov_subtenant",
        "Parents' professional situation": "cov_parents_employment",
        "Dysfunctions_Alcohol problem, substances": "cov_family_alcohol_substances",
        "Mental illness": "cov_family_mental_illness",
        "Mental abuse": "cov_family_mental_abuse",
        "Physical violence": "cov_family_physical_violence",
        "Parent’s religiousness": "cov_parents_religiousness",
        "Financial situation in childhood": "cov_financial_situation_childhood"}


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
    assert d.shape == (473, 120), d.shape
    psaq = [f"PSAQ{i}" for i in range(1, 71)]
    expected = {"Lp"} | set(COVS) | set(psaq) | set(PARENT_SCORES) | set(ITEMS) | set(SUMS)
    assert set(d.columns) == expected, set(d.columns) ^ expected
    print("  skip PSAQ1-70: undocumented scoring (1.5 on every item, multi-digit cells)")
    print("  skip parental-attitude scores and Dep/Anx/Stress: composites")
    for s, ix in SUMS.items():  # standard DASS-21 order
        assert (d[[f"DASS{i}" for i in ix]].sum(axis=1) == d[s]).all(), s
    assert d["Lp"].is_unique
    d = d.rename(columns={"Lp": "id", **COVS})
    covs = list(COVS.values())
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    assert t["resp"].isin(range(4)).all()
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
    pv = {i: set(range(4)) for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
