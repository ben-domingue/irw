#!/usr/bin/env python3

# Source: https://zenodo.org/records/14054426
# DOI: 10.5281/zenodo.14054426
#   Yang, Yeing (2024). Examining Local Acceptance of Online Film Festivals: The
#   Role of ... [Dataset]. Zenodo.
# Data: the deposit's single .sav -- 442 Chinese respondents, 1-5 agreement.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. BOTH label levels checked, and this is the awkward case
#   where labels exist but say nothing: 30 of 31 variables carry a variable label,
#   but for every ITEM the label is the code echoed back ("CE1" -> "CE1"). Real
#   stems appear only for the demographics. Value labels (28 of 31) are likewise
#   demographic. So the file holds no item wording at any level; it is in the paper.
# Naming: yang_2024_phone_addiction_burnout and yang_2024_teacher_wellbeing are
#   already shipped (different authors, same surname and year), so this deposit
#   takes yang_2024c_*.
#
# SIX tables, all 1-5:
#   yang_2024c_content_engagement    4 items (CE1-4)
#   yang_2024c_social_engagement     6 items (SE1-6)
#   yang_2024c_effort_expectancy     3 items (EE1-3)
#   yang_2024c_technology_anxiety    4 items (TA1-4)
#   yang_2024c_intention             3 items (IT1-3)
#   yang_2024c_satisfaction          4 items (SAT1-4)
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: cov_gender, cov_age, cov_education, cov_identity, cov_city,
#   cov_city_original, cov_frequency.
# Rights: none of the six is in the register. TA here is "technology anxiety" --
#   NOT the Toronto Alexithymia Scale or the CD-RISC codes a bare code-prefix
#   matcher would collide with. Resolved by reading the deposit's own construct
#   names, which is the only safe route when 154 of the register's 243 block rows
#   carry no matcher at all.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "14054426"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 14054426
SCALE = set(range(1, 6))

COVS = {"Gender": "cov_gender", "Age": "cov_age", "Education": "cov_education",
        "Identity": "cov_identity", "CITY": "cov_city",
        "City_original": "cov_city_original", "Frequency": "cov_frequency"}
BLOCKS = {
    "yang_2024c_content_engagement": [f"CE{i}" for i in range(1, 5)],
    "yang_2024c_social_engagement": [f"SE{i}" for i in range(1, 7)],
    "yang_2024c_effort_expectancy": [f"EE{i}" for i in range(1, 4)],
    "yang_2024c_technology_anxiety": [f"TA{i}" for i in range(1, 5)],
    "yang_2024c_intention": [f"IT{i}" for i in range(1, 4)],
    "yang_2024c_satisfaction": [f"SAT{i}" for i in range(1, 5)],
}


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    hits = [p for p in RAW_DIR.iterdir() if p.name != "_record.json"]
    if hits:
        return hits[0]
    j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                     headers=UA, timeout=120).json()
    f = j["files"][0]
    p = RAW_DIR / f["key"]
    r = requests.get(f["links"]["self"], headers=UA, timeout=300)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df.insert(0, "id", range(len(df)))
    items = {c for cols in BLOCKS.values() for c in cols}
    accounted = {"id"} | set(COVS) | items
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-5 scale: {bad}"
        for c in COVS.values():
            v = pd.to_numeric(t[c], errors="coerce")
            t[c] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v
        t = t[["id", "item", "resp", *COVS.values()]]
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
