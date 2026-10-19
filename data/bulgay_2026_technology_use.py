#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/33227889
# DOI: 10.6084/m9.figshare.33227889.v1
#   Bulgay, C. (2026). The relationship between technology use and academic
#   achievement among sports sciences students: The mediating role of academic
#   self-efficacy [Dataset]. figshare.
# Data: "DATA.sav" -- 417 Turkish sports-sciences undergraduates, two item
#   blocks on 1-5 agreement scales.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. Both label levels were checked: the two item blocks
#   carry NEITHER a variable label nor value labels (only the covariates do),
#   so the file documents nothing but the codes AÖ1-7 and TK1-13. The wording
#   is in the paper behind the deposit title -- a Turkish academic
#   self-efficacy scale and a technology-use scale, neither identified in the
#   deposit itself.
#
# ITEM CODES are the source's own, including the Turkish "Ö" in AÖ1-AÖ7; they
#   are not transliterated, so the codes still match the deposit.
#
# TWO tables, 417 respondents, both 1-5:
#   bulgay_2026_academic_self_efficacy   AÖ1-AÖ7    (7 items)
#   bulgay_2026_technology_use           TK1-TK13  (13 items)
# id: the deposit's own V1 serial, kept so the two tables link.
# Covariates: cov_age, cov_gender, cov_monthly_income, cov_residence,
#   cov_department, cov_year_of_study, cov_gpa, cov_follows_technology,
#   cov_daily_use_hours, cov_device. The last two were read as item columns by
#   the triage; their variable labels ("Ne sıklıkla kull.", "Hangi Cihaz") and
#   value labels (hour bands, device type) make them technology-use
#   covariates, not scale items. .sav value labels are harvested into
#   metadata/covariate_labels/.
# Dropped: AKAD_M and TEK_M, the two block means.
# ONE COVARIATE CELL IS BLANKED: a single cov_age of 120 in a sample otherwise
#   aged 18-40, which is a data-entry error rather than a response.
import os
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "33227889" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 33227889, "DATA.sav"
SCALE = set(range(1, 6))

BLOCKS = {
    "bulgay_2026_academic_self_efficacy": [f"AÖ{i}" for i in range(1, 8)],
    "bulgay_2026_technology_use": [f"TK{i}" for i in range(1, 14)],
}
COVS = {
    "Yaş": "cov_age",
    "Cinsiyet": "cov_gender",
    "AGelir": "cov_monthly_income",
    "Yyer": "cov_residence",
    "Bölüm": "cov_department",
    "Sınıf": "cov_year_of_study",
    "NotOrt": "cov_gpa",
    "Ttakip": "cov_follows_technology",
    "Nsıkkul": "cov_daily_use_hours",
    "HCihaz": "cov_device",
}
DROPPED = ["AKAD_M", "TEK_M"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, _meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    items = [c for cols in BLOCKS.values() for c in cols]
    for c in items + list(COVS) + DROPPED + ["V1"]:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns
                   if c not in set(items + list(COVS) + DROPPED + ["V1"])]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"dropped, block means: {DROPPED}")

    df = df.rename(columns={"V1": "id", **COVS})
    df["id"] = pd.to_numeric(df["id"]).astype(int)
    assert df["id"].is_unique
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        df[cov] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v

    # One respondent's age is 120 in a sample otherwise aged 18-40: a
    # data-entry error in a covariate, blanked rather than shipped.
    bad_age = df["cov_age"] > 100
    print(f"cov_age: blanking {int(bad_age.sum())} value(s) over 100 "
          f"(observed {sorted(df.loc[bad_age, 'cov_age'].unique())}) in a "
          f"sample otherwise aged {int(df.loc[~bad_age, 'cov_age'].min())}-"
          f"{int(df.loc[~bad_age, 'cov_age'].max())}")
    assert int(bad_age.sum()) == 1
    df.loc[bad_age, "cov_age"] = pd.NA

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the documented 1-5 scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
