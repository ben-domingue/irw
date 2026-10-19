#!/usr/bin/env python3

# Source: https://zenodo.org/records/15314083
# DOI: 10.5281/zenodo.15314083
#   Cassandra, C., Megaryanti, N., Nayoan, C., et al. (2025). Factors Influencing
#   User Acceptance in Adopting Biometric/Facial Recognition [Dataset]. Zenodo.
# Data: "Raw Dataset.xlsx" -- 412 Indonesian respondents, 1-5 agreement.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. The item columns are bare construct codes (PU1, PEOU1,
#   ...) with no stems, and .xlsx has no label level. The screening and demographic
#   headers ARE full Indonesian questions, but they are covariates, not items.
#
# HEADER OFFSET. Row 0 is a title banner ("Dataset of \"Factors Influencing ...\"")
#   spanning the sheet, so a default read gives every column the name
#   "Unnamed: N" and the real header sits on row 1. Read with header=1. This is the
#   same banner shape that produced the duplicate-column reader fault fixed on
#   2026-10-18, so it is asserted rather than assumed.
#
# A SIX-POINT SCALE. All six categories are used across every item block, so
#   6 is a response and not a sentinel; checked over the whole item range
#   before shipping. (This deposit is one of two in the batch whose scale the
#   automated profiling could not read -- stem-bearing / banner-offset headers
#   defeat a prefix grouping -- and both turned out to be 1-6 rather than the
#   1-5 the rest of the family uses. The range assertion is what caught it.)
#
# EIGHT tables, all 1-6:
#   cassandra_2025_perceived_usefulness   4 (PU1-4)   cassandra_2025_trust        4 (TR1-4)
#   cassandra_2025_perceived_ease         5 (PEOU1-5) cassandra_2025_self_efficacy 5 (SE1-5)
#   cassandra_2025_perceived_value        4 (PV1-4)   cassandra_2025_perceived_risk 4 (PR1-4)
#   cassandra_2025_attitude               5 (ATU1-5)  cassandra_2025_intention     4 (BI1-4)
# Not shipped as items: the three screening questions (has the respondent used
#   facial recognition, what for, how often) and the six demographics, which become
#   covariates. The two geographic columns are province and city/regency -- an
#   administrative area, not a street address or coordinate, so not PII under the
#   pipeline's rule; the age column is a generational BAND, not a birthdate.
# id: the file carries no respondent id; the 0-based row index within the data
#   block is used.
# Covariates: cov_used_before, cov_purpose, cov_frequency, cov_gender,
#   cov_age_band, cov_education, cov_occupation, cov_province, cov_city.
# Rights: none of the eight is in the register. SE is "self-efficacy" and PR
#   "perceived risk" here, neither a register instrument; read off the deposit's
#   own construct naming rather than inferred from the code.
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "15314083"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 15314083, "Raw Dataset.xlsx"
SCALE = set(range(1, 7))

COV_NAMES = ["cov_used_before", "cov_purpose", "cov_frequency", "cov_gender",
             "cov_age_band", "cov_education", "cov_occupation",
             "cov_province", "cov_city"]
BLOCKS = {
    "cassandra_2025_perceived_usefulness": [f"PU{i}" for i in range(1, 5)],
    "cassandra_2025_perceived_ease": [f"PEOU{i}" for i in range(1, 6)],
    "cassandra_2025_perceived_value": [f"PV{i}" for i in range(1, 5)],
    "cassandra_2025_attitude": [f"ATU{i}" for i in range(1, 6)],
    "cassandra_2025_trust": [f"TR{i}" for i in range(1, 5)],
    "cassandra_2025_self_efficacy": [f"SE{i}" for i in range(1, 6)],
    "cassandra_2025_perceived_risk": [f"PR{i}" for i in range(1, 5)],
    "cassandra_2025_intention": [f"BI{i}" for i in range(1, 5)],
}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    p = fetch()
    banner = pd.read_excel(p, header=None, nrows=1)
    assert str(banner.iloc[0, 0]).startswith("Dataset of"), \
        "row 0 is not the expected title banner -- re-read the header offset note"
    df = pd.read_excel(p, header=1)
    assert not any(str(c).startswith("Unnamed") for c in df.columns), \
        f"header=1 still gives Unnamed columns: {list(df.columns)[:5]}"

    df.columns = COV_NAMES + [str(c).strip() for c in df.columns[len(COV_NAMES):]]
    df.insert(0, "id", range(len(df)))
    items = {c for cols in BLOCKS.values() for c in cols}
    for c in items:
        assert c in df.columns, f"expected item column {c} is absent"
    unaccounted = [c for c in df.columns
                   if c not in ({"id"} | items | set(COV_NAMES))]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *COV_NAMES, *cols]]
             .melt(id_vars=["id", *COV_NAMES], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-6 scale: {bad}"
        t = t[["id", "item", "resp", *COV_NAMES]]
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
