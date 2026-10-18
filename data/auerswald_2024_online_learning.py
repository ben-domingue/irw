#!/usr/bin/env python3

# Source: https://zenodo.org/records/10731829
# DOI: 10.5281/zenodo.10731829 (dataset)
#   Auerswald, S., Koddebusch, C., & Hermann, C. (2024). Elevated perceived stress in
#   university students due to COVID-19 pandemic: Potential contributing factors in a
#   propensity-score matched sample [Dataset]. Zenodo.
# Data: "Auerswald_et_al_SJOP.sav": 1,918 German university students across three
#       cohorts (2016, 2017, 2021). The deposit also carries its own codebook PDF
#       ("Auerswald_et_al_SJOP_OpenDataMaterials_CodeBook.pdf") and an SPSS syntax
#       file; the codebook is what is recorded at ingest.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: SHIPPED (German as administered, with the authors' own English). The four
#   Corona_* variable labels carry the English wording followed by the administered
#   German in typographic quotes, so BOTH languages come from the deposit and neither
#   is IRW's. The value labels give each item's five anchors. These are items the
#   authors wrote for this study about the switch to online-only teaching, not a named
#   third-party instrument, so the CC BY deposit is the originator's own grant.
#
# ONE table only, because almost nothing else in this deposit is item-level: PSS, PHQ,
# GAD, GSE and SEB are deposited as SUM SCORES and APSI_P/APSI_F/APSI_A/PSRD/SRR as
# MEAN SCORES. Those are aggregates, not responses, and are not shipped.
#   auerswald_2024_online_learning  4 items, 0-4.
#
# The anchors are REVERSED on two of the four items, which is a property of the
# deposit and is preserved deliberately: on Corona_1 and Corona_3 (negatively worded)
# 0 = "Trifft nicht zu" and 4 = "Trifft zu", while on Corona_2 and Corona_4
# (positively worded) 0 = "Trifft zu" and 4 = "Trifft nicht zu". The depositor flipped
# the positively worded items so that a HIGH code always means a worse experience of
# online teaching, so the construct direction is consistent across all four and the
# numeric scale is comparable. What differs is the wording attached to each code, and
# the item text table carries each item's own option_text accordingly rather than one
# shared set.
#
# Covariates: cov_phase (the deposit's `treat`, pre-COVID vs COVID), cov_cohort,
#   cov_age, cov_gender, cov_semester, cov_distress_housing, cov_distress_funding,
#   cov_written_exams, cov_oral_exams, cov_written_coursework,
#   cov_oral_presentations. The exam/coursework counts and the two distress ratings
#   are single items on their own scales, so they are covariates, not a scale.
# Not shipped: the two section-header columns Section_1.1_SAMPLE_CHARACTERISTICS and
#   Section_1.2_SUBJECTIVE_RATINGS, which hold no data.
# id: the deposit's "ID" (1,918 distinct over 1,918 rows).
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
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def zenodo_fetch(record: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://zenodo.org/api/records/{record}", headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == fname][0]
        download(url, p)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values or None). QC, validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=(),
         rename: dict | None = None) -> pd.DataFrame:
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", *extra, "item"]).reset_index(drop=True)


def pv_for(items, valid) -> dict:
    return {i: set(valid) for i in items}


def books(all_cols, used: dict) -> None:
    """Every source column is either shipped or skipped for a printed reason."""
    seen = {}
    for reason, cols in used.items():
        for c in cols:
            assert c not in seen, (c, reason, seen[c])
            seen[c] = reason
    missing = [c for c in all_cols if c not in seen]
    assert not missing, f"unaccounted source columns: {missing}"
    extra = [c for c in seen if c not in all_cols]
    assert not extra, f"named columns not in the source: {extra}"
    for reason, cols in used.items():
        if reason != "shipped" and cols:
            print(f"    [skipped: {reason}] {len(cols)}: {', '.join(map(str, cols))[:300]}")


RAW_DIR = RAW_ROOT / "10_5281_zenodo_10731829"
ITEMS = [f"Corona_{i}" for i in range(1, 5)]
SUMS = ["PSS", "PHQ", "GAD", "GSE", "SEB"]
MEANS = ["APSI_P", "APSI_F", "APSI_A", "PSRD", "SRR"]
COVS = {"treat": "cov_phase", "cohort": "cov_cohort", "Age": "cov_age",
        "Gender": "cov_gender", "Semester": "cov_semester",
        "distress_housing": "cov_distress_housing",
        "distress_funding": "cov_distress_funding",
        "written_exams": "cov_written_exams", "oral_exams": "cov_oral_exams",
        "written_coursework": "cov_written_coursework",
        "oral_presentations": "cov_oral_presentations"}
SECTIONS = ["Section_1.1_SAMPLE_CHARACTERISTIC_DATA_next_columns",
            "Section_1.2_SUBJECTIVE_RATINGS_next_columns"]


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(
        zenodo_fetch(10731829, "Auerswald_et_al_SJOP.sav", RAW_DIR),
        apply_value_formats=False)
    assert len(d) == 1918, len(d)
    sec = [c for c in d.columns if str(c).startswith("Section_")]
    assert sorted(sec) == sorted(SECTIONS), sec
    books(list(d.columns), {
        "shipped": ITEMS,
        "covariate": list(COVS),
        "respondent id": ["ID"],
        "sum score computed by the depositor": SUMS,
        "mean score computed by the depositor": MEANS,
        "section header, no data": SECTIONS,
    })
    # The anchors run in opposite directions on 1/3 vs 2/4; assert that rather than
    # leaving the header comment as the only record of it.
    vl = meta.variable_value_labels
    assert vl["Corona_1"][0.0] == "Trifft nicht zu", vl["Corona_1"]
    assert vl["Corona_2"][0.0] == "Trifft zu", vl["Corona_2"]
    d = d.rename(columns={"ID": "id", **COVS})
    assert d["id"].nunique() == len(d), d["id"].nunique()
    covs = list(COVS.values())
    v = range(0, 5)
    emit({"auerswald_2024_online_learning":
          (long(d, ITEMS, covs, valid=v), pv_for(ITEMS, v))})


if __name__ == "__main__":
    main()
