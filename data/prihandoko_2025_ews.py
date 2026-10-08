#!/usr/bin/env python3
# Source: https://zenodo.org/records/18056003
# DOI: 10.5281/zenodo.18056003 (dataset; no paper DOI on the record)
#   Prihandoko, Danang, Rafsanjani, Brian & Mathius, Ramos (2025). "More Than Salary:
#   The Reletionship Between a Healthy Work Culture (Well-Being) and Company
#   Profitability" [data set]. Zenodo.
# Data: "INSTRUMEN SURVEI EMPLOYEE WELL-BEING SCORE (EWS)   (Jawaban) 2.xlsx" (Google
#       Forms export): 121 professional employees in Greater Jakarta x Timestamp,
#       gender, age band, free-text job ("Pekerjaan Anda"), and the 13 EWS statements
#       as column headers (Indonesian), all 1-5. No codebook, no option labels.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (the column headers ARE the administered Indonesian statements;
#   built by automated_finding/itemtext_verification/make_itemtext_prihandoko_2025.py).
#   English item_text_translated is IRW's own translation; no option labels exist.
#
# Shipped: prihandoko_2025_ews -- ews1-ews13, codes assigned to the statement headers
#   in column order (stems() returns the exact (code, header) pairs). Two missing
#   cells (ews7) dropped. The record calls the instrument the Employee Well-Being
#   Score (EWS), built on the JD-R model; item 1 ("I do not often experience burnout
#   ...") and item 13 ("I rarely take sick leave ...") are worded so that higher =
#   better, like the rest.
# Not shipped: Timestamp (form metadata), "Pekerjaan Anda" (free-text job title).
# Covariates: cov_gender (Laki-Laki / Perempuan), cov_age_band ("18-25", "26-35",
#   "35>", "<17" as recorded).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "prihandoko_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/18056003/files/INSTRUMEN%20SURVEI%20EMPLOYEE"
       "%20WELL-BEING%20SCORE%20(EWS)%20%20%20(Jawaban)%202.xlsx/content")
NAME = "prihandoko_2025_ews"


def fetch() -> Path:
    p = RAW_DIR / "ews.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def stems() -> list:
    d = pd.read_excel(fetch())
    assert d.shape == (121, 17)
    assert d.columns[:4].tolist() == ["Timestamp", "Jenis Kelamin", "Usia Anda", "Pekerjaan Anda"]
    return [(f"ews{i + 1}", h) for i, h in enumerate(d.columns[4:])]


def main() -> None:
    d = pd.read_excel(fetch())
    pairs = stems()
    print("  [skip] Timestamp (form metadata), Pekerjaan Anda (free-text job title)")
    d.insert(0, "id", range(1, len(d) + 1))     # no id column in the deposit
    d = d.rename(columns={"Jenis Kelamin": "cov_gender", "Usia Anda": "cov_age_band",
                          **{h: c for c, h in pairs}})
    items = [c for c, _ in pairs]
    covs = ["cov_gender", "cov_age_band"]
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin(range(1, 6)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(items) and not t.duplicated(["id", "item"]).any()
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
