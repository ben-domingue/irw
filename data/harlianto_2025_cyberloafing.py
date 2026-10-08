#!/usr/bin/env python3
# Source: https://zenodo.org/records/16890070
# DOI: 10.5281/zenodo.16890070 (dataset; no paper DOI on the record)
#   Harlianto, Jefta & Kiolol, Nadya Gwynni Pankrasius (2025). "Job Stress,
#   Cyberloafing, and Burnout" [data set; "Exploring the Mediating Role of
#   Cyberloafing in Jakarta's Workforce"]. Zenodo.
# Data: "Data_JS_CL_ JB_for Zenodo rev.xlsx", sheet "Zenodo": 185 Jakarta workers x
#       No., eight Indonesian demographic/work questions, then three item blocks
#       labelled in the banner row above the header: CL (cyberloafing: BA1-9, EM1-3),
#       JS (job stress: PA1, H1, KK1, B1, O1, PP1, LF1, BK1, HK1), JB (job burnout:
#       KE1-3, MPP1-4, D1-3). All items 1-5. No codebook in the deposit.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Levels checked: xlsx headers are codes only (no labels,
#   no codebook); the questionnaire is not in the deposit.
#
# Tables (block membership from the deposit's own CL/JS/JB banner; codes as stored):
#   harlianto_2025_cyberloafing  BA1-9, EM1-3 (12)
#   harlianto_2025_job_stress    PA1 ... HK1 (9)
#   harlianto_2025_burnout       KE1-3, MPP1-4, D1-3 (10)
# Covariates (Indonesian strings as recorded): cov_gender (Jenis Kelamin), cov_age_band
#   (Umur), cov_tenure (Lama Bekerja), cov_education (Pendidikan terakhir),
#   cov_job_level (Tingkat jabatan), cov_job_field (Bidang Pekerjaan), cov_industry
#   (Jenis industri), cov_cyberloafing_time (daily cyberloafing time band).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "harlianto_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/16890070/files/"
       "Data_JS_CL_%20JB_for%20Zenodo%20rev.xlsx/content")
BLOCKS = {"CL": "harlianto_2025_cyberloafing", "JS": "harlianto_2025_job_stress",
          "JB": "harlianto_2025_burnout"}
COVS = {"Jenis Kelamin": "cov_gender", "Umur": "cov_age_band",
        "Lama Bekerja": "cov_tenure", "Pendidikan terakhir": "cov_education",
        "Tingkat jabatan (setara dengan jabatan)": "cov_job_level",
        "Bidang Pekerjaan": "cov_job_field",
        "Jenis industri dari tempat bekerja Anda saat ini": "cov_industry",
        "Berapa total waktu Anda melakukan Cyberloafing selama jam kerja":
            "cov_cyberloafing_time"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    raw = pd.read_excel(fetch(), header=None)
    banner = raw.iloc[0].tolist()
    hdr = [str(c).strip() for c in raw.iloc[1].tolist()]
    d = raw.iloc[2:].reset_index(drop=True)
    d.columns = hdr
    assert d.shape == (185, 40) and hdr[0] == "No." and d["No."].is_unique
    assert hdr[1:9] == list(COVS)
    tables, cur = {}, None
    for b, h in zip(banner[9:], hdr[9:]):
        if isinstance(b, str):
            cur = b.strip()
        tables.setdefault(BLOCKS[cur], []).append(h)
    assert [len(v) for v in tables.values()] == [12, 9, 10], tables
    d = d.rename(columns={"No.": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in tables.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: {1, 2, 3, 4, 5} for i in its}
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
