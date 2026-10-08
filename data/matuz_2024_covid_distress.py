#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/msxv59kwcx
# DOI: 10.17632/msxv59kwcx (dataset; no paper DOI on the record)
#   Matuz, Andras (2024). "Reframing prolonged negative mental health effects of COVID-19:
#   Cognitive restructuring promotes posttraumatic growth" [data set], Mendeley Data, V1.
# Data: Reframing_database_2024.xlsx (sheet "Reframing_database_2022"): 1426 Hungarian
#       university students and staff from three cross-sectional online surveys (three
#       pandemic waves) x 157 columns. Headers are scale_item_1; no codebook.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: not shipped. Levels checked: xlsx headers only (CPDI_3_1, WOC_7_1 ...), no
#   labels, no codebook. Hungarian wording not in the deposit; STAI and IES-R are blocked
#   in the rights register anyway.
#
# Tables (item code = header without the trailing "_1"; ranges as observed and standard
#   for each instrument):
#   matuz_2024_cpdi     CPDI_1-24     0-4  COVID-19 Peritraumatic Distress Index
#   matuz_2024_bdi9     BDI_1-9       0-3  9-item Beck Depression Inventory short form
#   matuz_2024_stai_t   STAI_T_1-20   0-3  STAI trait, coded 0-3
#   matuz_2024_stai_s   STAI_S_1-20   0-3  STAI state, coded 0-3
#   matuz_2024_woc      WOC_1-16      0-3  Ways of Coping (16-item short form; the file's
#                                          subscale sums are PA, SR, CR, PC)
#   matuz_2024_iesr     IES_1-22      0-4  Impact of Event Scale-Revised (third wave only)
#   matuz_2024_ptgi     PTG_1-21      0-5  Posttraumatic Growth Inventory (third wave only)
#   The three surveys sampled different people, so the survey wave is a covariate
#   (cov_survey_wave), not `wave`.
# Dropped cells: fractional values on otherwise-integer items (IES_15 = 0.5, PTG_21 = 1.5;
#   counts printed at run time) -- imputation or entry errors.
# The file's FILTER_IES_PTG marks 4 third-wave respondents the authors excluded from the
#   IES/PTG analyses; kept, flagged as cov_excluded_ies_ptg (1/0) on those two tables.
# Skipped: wave dummies, the EFA/CFA subsample split, and every sum/mean/subscale score.
# Covariates: cov_sex (0 female, 1 male, from the header), cov_age, cov_survey_wave (1-3).
# id = row order.

import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "matuz_2024"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/msxv59kwcx/files/"
       "a88b95d8-da85-4537-aa9c-c6a7ad097477/file_downloaded")

TABLES = {"matuz_2024_cpdi": ("CPDI", 24, range(0, 5)), "matuz_2024_bdi9": ("BDI", 9, range(0, 4)),
          "matuz_2024_stai_t": ("STAI_T", 20, range(0, 4)), "matuz_2024_stai_s": ("STAI_S", 20, range(0, 4)),
          "matuz_2024_woc": ("WOC", 16, range(0, 4)), "matuz_2024_iesr": ("IES", 22, range(0, 5)),
          "matuz_2024_ptgi": ("PTG", 21, range(0, 6))}
COVS = {"Sex (0-female, 1-male)": "cov_sex", "Age": "cov_age", "Wave": "cov_survey_wave"}


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
    assert d.shape == (1426, 157), d.shape
    cols = {t: [f"{p}_{i}_1" for i in range(1, k + 1)] for t, (p, k, _) in TABLES.items()}
    items = {c for v in cols.values() for c in v}
    assert items <= set(d.columns)
    rest = [c for c in d.columns if c not in items | set(COVS)]
    print(f"  skip {len(rest)} columns: {rest}")
    assert all(re.search(r"(DUMMY|Subsample|sum|WOC_[A-Z]{2}$|IES_[A-Z]|PTG_[A-Z]|total|Total|CPDI_[A-Za-z]|mean|Mean)", c)
               for c in rest), rest
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    f = "FILTER_IES_PTG (1 - excluded from IES and PTG analyses)"
    d["cov_excluded_ies_ptg"] = d[f].eq(1).astype(int)
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (pre, _, rng) in TABLES.items():
        cmap = {c: c[:-2] for c in cols[name]}
        tc = covs + (["cov_excluded_ies_ptg"] if pre in ("IES", "PTG") else [])
        t = d[["id"] + tc + cols[name]].rename(columns=cmap).melt(
            id_vars=["id"] + tc, var_name="item", value_name="resp").dropna(subset=["resp"])
        bad = ~t["resp"].isin(list(rng))
        for (it, v), n in t[bad].groupby(["item", "resp"]).size().items():
            print(f"    {name}: drop {it}={v:g} x{n}")
        assert bad.sum() <= 10, name
        t = t[~bad].copy()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + tc].sort_values(["id", "item"]).reset_index(drop=True)
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
