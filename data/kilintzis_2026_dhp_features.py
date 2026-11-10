#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13032310
# DOI: 10.1186/s12889-026-26412-6
#   "Key factors in developing effective digital health promotion tools for
#   cancer prevention and health behavior change in adolescence through a
#   multi-country survey" (Kilintzis, Kondylakis, Petrakis, Koutra, Micheli et
#   al., 2026), BMC Public Health 26:1023. SUNRISE project (Horizon Europe).
# Data: the article's supplementary file 12889_2026_26412_MOESM1_ESM.xlsx
#   (Europe PMC supplementaryFiles zip), "Sheet 1": 511 LimeSurvey submissions
#   x 47 columns from seven countries (Cyprus, Greece, Belgium, Spain, Slovenia,
#   Switzerland, Italy). Ratings are stored as "4: Important" text; the code is
#   the leading digit.
# License: CC BY 4.0 (article licence; Data availability: "All data analysed
#   during this study are included in this published article and its
#   supplementary information files").
#
# Sample: the paper analyses "493 completed surveys ..., each reflecting at least
#   80% of the proposed features rated". Keeping submissions with >= 23 of the
#   28 features rated reproduces that exactly: 493 respondents, 381 female /
#   111 male / 1 non-binary, and the paper's Table 2 counts for Ft1-Ft3
#   (asserted below). Respondents are parents, educators and high-school
#   students (cov_role). id = row index; the per-country LimeSurvey Response ID
#   repeats across countries and the random `Seed` is not carried.
#
# Table:
#   kilintzis_2026_dhp_features  ft1..ft28  1-5  importance of 28 proposed
#     features of a digital health-promotion tool for adolescents (paper Table 2,
#     Ft1..Ft28 in sheet order): 1 Not important at all, 2 Not that important,
#     3 Not sure, 4 Important, 5 Very important. The paper treats this as one
#     five-point Likert scale (3 "Not sure" is its midpoint), so it is kept.
#
# Covariates: age, gender identity, role, survey start language, country, born
#   in country, parents born in same country, the five education-completed flags.
#
# Item text: not shipped. Levels checked: no SPSS-style labels (xlsx); the
#   column headers are full English feature descriptions, but the survey was
#   administered in seven languages (Start language: sl, nl, en, it, ...), so
#   the English header is not the wording most respondents saw.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "kilintzis_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13032310/supplementaryFiles"
FILE = "12889_2026_26412_MOESM1_ESM.xlsx"
NAME = "kilintzis_2026_dhp_features"
PAPER_COUNTS = {"ft1": [9, 15, 54, 209, 191], "ft2": [4, 13, 32, 178, 259],
                "ft3": [3, 9, 23, 186, 266]}


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        p.write_bytes(z.read([n for n in z.namelist() if n.endswith(FILE)][0]))
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name=0)
    assert d.shape == (511, 47), d.shape
    feat = list(d.columns[18:46])
    assert feat[0].startswith("Tailored personalised content")
    assert feat[-1].startswith("Accessible via laptop PC")
    assert str(d.columns[17]).startswith("In the following section")
    codes = {}
    for i, c in enumerate(feat, 1):
        raw = d[c].astype("string").str.strip()
        code = raw.str.extract(r"^([1-5]):")[0]
        assert not (raw.notna() & code.isna()).any(), c
        codes[f"ft{i}"] = pd.to_numeric(code)
    r = pd.DataFrame(codes)
    keep = r.notna().sum(axis=1) >= 23
    assert keep.sum() == 493
    d, r = d[keep].reset_index(drop=True), r[keep].reset_index(drop=True)
    g = d["Gender Identity"].value_counts().to_dict()
    assert g == {"Female": 381, "Male": 111, "Non-Binary": 1}, g
    for k, v in PAPER_COUNTS.items():
        assert r[k].value_counts().sort_index().tolist() == v, (k, r[k].value_counts())

    cov = pd.DataFrame({
        "id": range(1, len(d) + 1),
        "cov_age": d["Age"],
        "cov_gender": d["Gender Identity"].str.lower(),
        "cov_role": d["You will answer as "].str.strip().str.lower(),
        "cov_language": d["Start language"],
        "cov_country": d["Country"],
        "cov_born_in_country": d["Were you born in the country you currently live in "],
        "cov_parents_born_same_country": d["Were both of your parents born in the same country as you "],
        "cov_edu_primary": d["Education levels completed Primary "],
        "cov_edu_highschool": d["Education levels completed Highschool "],
        "cov_edu_bachelor": d["Education levels completed Bachelor "],
        "cov_edu_postgraduate": d["Education levels completed Postgraduate education "],
        "cov_edu_vocational": d["Education levels completed Vocational non academic diploma "],
    })
    r.insert(0, "id", cov["id"])
    items = [f"ft{i}" for i in range(1, 29)]
    t = r.melt(id_vars="id", value_vars=items, var_name="item", value_name="resp").dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    t = t.merge(cov, on="id", how="left")
    t["_o"] = t["item"].str[2:].astype(int)
    t = t.sort_values(["id", "_o"]).drop(columns="_o").reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() == 493

    pv = {i: {1, 2, 3, 4, 5} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:160]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
