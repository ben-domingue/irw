#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/32016954
# DOI: 10.6084/m9.figshare.32016954.v2
#   Sa'diyah, C., Windijarto, Widagdo, B., & Febrianto, Z. (2026). Survey Data
#   on Financial Knowledge, Financial Self-Efficacy, Financial Attitude, and
#   Financial Behavior among a Sample of Generation Z in Indonesia [Dataset].
#   figshare.
# Data: "Dataset.xlsx", sheet "Full Dataset 1516" -- 1,516 Indonesian
#   Generation Z respondents, 27 items on a 1-5 agreement scale, plus six
#   fully labelled demographics.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped, though the deposit carries it. "Codebook,
#   Questionnaire, and Variable Dictionary.xlsx" gives a full English stem for
#   all 27 items -- extraction is solved. It is held here because the four
#   scales are adapted published instruments (the FSE block is Lown's
#   Financial Self-Efficacy Scale) and none has a row in
#   itemtext/instrument_rights_register.csv; under the 2026-10-15 silence rule
#   that is a hold, not a ship. The file name above is where a ruling lands.
#
# THE 23 DUPLICATE RECORDS ARE DROPPED. The deposit audits its own data: a
#   trailing "Status" column marks 23 rows "Duplicate record" and a sibling
#   sheet ships the 1,493-row duplicate-free set. Those 23 are dropped here, so
#   the shipped N matches the deposit's own duplicate-free count exactly. The
#   deposit's further "outlier-free" 1,433 set is a modelling choice, not a
#   data-integrity one, and is NOT applied.
#
# OFFSET HEADER: row 1 holds the construct names spanning their blocks and row
#   2 the item codes; the data starts at row 3. Read with header=None and the
#   codes taken from row 2, so every item keeps the source's own code.
#
# FOUR tables, one per scale, 1,493 respondents x 1-5:
#   sadiyah_2026_financial_behavior       FB1-6
#   sadiyah_2026_financial_knowledge      FK1-7
#   sadiyah_2026_financial_self_efficacy  FSE1-8
#   sadiyah_2026_financial_attitude       FA1-6
# id: the deposit's own "No." serial (1-1516), kept so the four tables link.
# Covariates: cov_gender, cov_region, cov_age_band, cov_employment,
#   cov_income_band, cov_education -- all shipped as the source's own labels.
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
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "32016954" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME, SHEET = 32016954, "Dataset.xlsx", "Full Dataset 1516"
SCALE = set(range(1, 6))

BLOCKS = {
    "sadiyah_2026_financial_behavior": ("FB", 6),
    "sadiyah_2026_financial_knowledge": ("FK", 7),
    "sadiyah_2026_financial_self_efficacy": ("FSE", 8),
    "sadiyah_2026_financial_attitude": ("FA", 6),
}
COVS = {
    "Gender": "cov_gender",
    "Residence Region": "cov_region",
    "Age Range": "cov_age_band",
    "Employment Status": "cov_employment",
    "Monthly Income Range": "cov_income_band",
    "Highest Education": "cov_education",
}


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
    raw = pd.read_excel(fetch(), sheet_name=SHEET, header=None)
    codes = [str(v).strip() for v in raw.iloc[1].tolist()]
    df = raw.iloc[2:].copy()
    df.columns = ["No.", *codes[1:-1], "Status"]
    df = df[df["No."].notna()]

    dup = df["Status"].astype(str).str.strip().eq("Duplicate record")
    print(f"dropping {int(dup.sum())} rows the deposit itself marks "
          f"'Duplicate record'; {int((~dup).sum())} remain")
    assert int(dup.sum()) == 23, int(dup.sum())
    df = df[~dup].drop(columns=["Status"])
    assert len(df) == 1493, len(df)

    blocks = {name: [f"{pre}{i}" for i in range(1, n + 1)]
              for name, (pre, n) in BLOCKS.items()}
    items = [c for cols in blocks.values() for c in cols]
    for c in items + list(COVS):
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns
                   if c not in (["No."] + items + list(COVS))]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns={"No.": "id", **COVS})
    df["id"] = pd.to_numeric(df["id"]).astype(int)
    assert df["id"].is_unique

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in blocks.items():
        t = (df[["id", *COVS.values(), *cols]]
             .melt(id_vars=["id", *COVS.values()], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the documented 1-5 scale: {bad}"
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
