#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/GROWTH_MINDSET_MALE-POWER_STEREOTYPE_AND_STEM_SELF-EFFICACY_AMONG_CHILDREN_A_MULTI-GROUP_ANALYSIS/34075200
# DOI: 10.6084/m9.figshare.34075200.v1 (data; no paper DOI on the record)
#   Binti Mokhtar NS (2026). Growth Mindset, Male-Power Stereotype, and STEM
#   Self-Efficacy among Children: A Multi-Group Analysis. figshare.
# Data: "DATA OF STEM SELF-EFFICACY_MGA.sav" (600 x 30), Malaysian children
#   aged 8-9, urban and rural schools.
# License: CC BY 4.0 (figshare record).
# Codebook: none; SPSS value labels (items 1 = disagree, 2 = neutral,
#   3 = agree; age 1 = 8, 2 = 9 years) and the record's description.
#
# Counts: 600 rows, 301 boys / 299 girls = the description's figures
#   (asserted).
# Tables (1-3, codes as deposited):
#   mokhtar_2026_growth_mindset      GM1-GM7, GM8_r (GM8 is deposited only in
#                                    its reverse-coded form)
#   mokhtar_2026_stem_self_efficacy  SE1-SE8
#   A code 4 appears 1-2 times on seven items (GM3, GM4, GM7, SE3, SE4, SE6,
#   SE7), never more, against 600 responses on a labelled 1-3 scale: isolated
#   entry errors, dropped (datastandard "Data entry errors at known values").
# Not shipped: SE_TotalScore, GM_TotalScore, the Male/Female/Urban/Rural
#   dummies (folded into covariates), Version (1-8, undocumented),
#   Dominant_gender and Scale_dominance/Scale_subordinate (undocumented
#   stereotype-task scores).
# id = row index: Pupil repeats on two pairs of different children.
# Covariates: school (code), age (8/9), gender, urban.
# Item text: not shipped -- no variable labels on the items.

import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/69671775"
SPEC = {
    "mokhtar_2026_growth_mindset": [f"GM{i}" for i in range(1, 8)] + ["GM8_r"],
    "mokhtar_2026_stem_self_efficacy": [f"SE{i}" for i in range(1, 9)],
}
COVS = {"School": "cov_school", "Age": "cov_age", "Gender": "cov_gender",
        "Urban": "cov_urban"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    assert d.shape == (600, 30), d.shape
    assert d["Gender"].value_counts().to_dict() == {1.0: 301, 2.0: 299}
    assert ((d["Urban"] + d["Rural"]) == 1).all()
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    allowed = {1, 2, 3}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, cols in SPEC.items():
        long = d[["id"] + cols + covs].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp"
        ).dropna(subset=["resp"])
        errs = long[long["resp"] == 4]
        assert errs.groupby("item").size().max() <= 2, table
        print(f"[drop] {table}: {len(errs)} isolated code-4 cells")
        long = long[long["resp"] != 4]
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
