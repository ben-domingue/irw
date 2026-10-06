#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/SZQHAO
# DOI: 10.3352/jeehp.2026.23.26
#   Weber, Huber & Wiemschulte (2026). "Name-based instructor-student interaction
#   in medical teaching: development and psychometric evaluation of a pilot
#   questionnaire", Journal of Educational Evaluation for Health Professions 23:26.
# Data: Harvard Dataverse DVN/SZQHAO, "Dataset 1. Anonymized raw responses from the
#       pilot question.xlsx" (file 14203957): 270 German medical students x 139
#       columns (empty spacer columns between items). "Supplement 5. Item wording
#       table.xlsx" (14203958) gives the English wording of X1-X59;
#       "Supplement 4. Pilot questionnaire (English).pdf" gives the anchors.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: xlsx headers only (no labels in the data
#   file); the deposit's Supplement 5 ties every code X1-X59 to its English
#   wording, so the tie is clean -- but the questionnaire was administered in
#   German (Supplement 3, PDF only), and the item text standard wants the
#   administered wording with English as the translation. Cheap follow-up: German
#   stems from Supplement 3 + English from Supplement 5, codes X1-X59.
#
# Shipped: weber_2026_name_interaction -- X1-X59, perceived effects of being
#   addressed by name (sessions WITH vs WITHOUT name mention), 1 = strongly
#   disagree .. 5 = strongly agree. Items mix positive and negative effects; not
#   reversed.
# Not shipped: question 6 (how often five instructor roles used the name; 1-5
#   Never..Very often, but three roles carry an undocumented 0), question 7
#   (six format checkboxes), free-text "Sonstiges"/"Haeufigst".
# Covariates: semester, age, gender (m/w), number of courses this semester,
#   number of courses where an instructor knows the name (0,1,2,3,5 = ">4"
#   per the questionnaire's options), weekly study time band (1 <10h .. 5 >40h).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "weber_szqhao"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/14203957"
NAME = "weber_2026_name_interaction"
COVS = {"Semester": "cov_semester", "Alter": "cov_age", "Geschlecht": "cov_gender",
        "Anzahl der Kurse": "cov_n_courses", "Namenskenntnis": "cov_courses_name_known",
        "Zeit": "cov_study_time_band"}
SKIP = ["Professor", "Oberarzt", "Assistenzarzt", "Dozent", "Hilfskraft", "Vorlesung",
        "Seminar", "Praktikum", "Klinik", "Online", "1on1", "Sonstiges", "Häufigst"]


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
    assert d.shape == (270, 139), d.shape
    items = [f"X{i}" for i in range(1, 60)]
    empty = [c for c in d.columns if str(c).startswith("Unnamed") and d[c].isna().all()]
    accounted = set(items) | set(COVS) | set(SKIP) | set(empty) | {"Nr. "}
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    print(f"  [skip] {len(empty)} empty spacer columns; role/format/free-text columns: {SKIP}")
    assert d["Nr. "].is_unique
    d = d.rename(columns={"Nr. ": "id", **COVS})
    d["cov_gender"] = d["cov_gender"].map({"w": "female", "m": "male"})
    assert d["cov_gender"].notna().all()
    covs = list(COVS.values())
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    t["resp"] = pd.to_numeric(t["resp"])
    assert t["resp"].isin(range(1, 6)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert len(t) == 270 * 59 and not t.duplicated(["id", "item"]).any()
    pv = {i: {1, 2, 3, 4, 5} for i in items}
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
