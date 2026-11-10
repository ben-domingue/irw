#!/usr/bin/env python3
# Source: https://zenodo.org/records/14903363
# DOI: 10.5281/zenodo.14903363 (no paper DOI on the record)
#   Rumangkit, S. (2025). "Dataset Questionnaire E-WOM Credibility, Brand
#   Image, Online Purchase Intention." Zenodo.
# Data: "PENGARUH E-WOM CREDIBILITY TERHADAP ONLINE PURCHASE INTENTION MELALUI
#   BRAND IMAGE PADA PRODUK KECANTIKAN (Responses).xlsx", sheet 'Form
#   Responses 1' (280 rows x 30 columns; Google Form export, Indonesian
#   social-media users on beauty-product reviews, October 2024).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# ITEM CODES: the headers are the full Indonesian item stems with no item
#   code. Codes are assigned BY STEM, not by position: STEMS below lists the
#   first words of each header in form order, and each header is matched to
#   exactly one entry (asserted), giving ewom_01 .. ewom_21. The record names
#   three constructs (e-WOM credibility, brand image, online purchase
#   intention) but does not say which item belongs to which, so the 21 items
#   ship as one table: one matrix block, one 1-5 format (the same handling as
#   rumangkit_2025_gamification). Read from the wording, 01-15 are e-WOM
#   source/content items, 16-18 brand image, 19-21 purchase intention; that
#   reading is NOT encoded in the codes.
#
# Item text: not shipped -- the stems are fully in hand (the headers), but the
#   administration is Indonesian and the authors ship no English, so it joins
#   the translation round the 2026-10 Rumangkit/Wiyono deposits are waiting
#   on. Study-written items; no register row matches.
#
# SCALE: plain 1-5 on every item.
#
# Dropped, with reasons:
#   Timestamp                               submission time
#   Jejaring Sosial Yang Aktif Digunakan    check-all list of platforms
#   Jenis Konten Yang Disukai               check-all list of content types
#   Column 29                               empty
# Covariates: cov_gender, cov_age_band, cov_education, cov_income_band,
#   cov_social_media_years (Indonesian labels as given).
# id: row index + 1 (the export carries no respondent identifier).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://zenodo.org/api/records/14903363/files/"
            "PENGARUH%20E-WOM%20CREDIBILITY%20TERHADAP%20ONLINE%20PURCHASE"
            "%20INTENTION%20MELALUI%20BRAND%20IMAGE%20PADA%20PRODUK%20"
            "KECANTIKAN%20(Responses).xlsx/content")
TABLE = "rumangkit_2025_ewom_purchase"
STEMS = [
    "Saya sering berinteraksi dengan pengguna media sosial",
    "Jika saya berpindah ke media sosial lain",
    "Saya sering termotivasi untuk berbagi pengalaman",
    "Saya percaya pada ulasan dan rekomendasi",
    "Dalam pandangan saya, pengguna media sosial memiliki rasa saling",
    "Pengguna media sosial merupakan orang yang kompeten",
    "Saya cenderung membeli produk kecantikan yang direkomendasikan",
    "Untuk tampil seperti seseorang yang saya kagumi",
    "Saya sering merasa terhubung dengan orang lain",
    "Konten ulasan produk kecantikan yang dapat membangkitkan emosi",
    "Saya menikmati konten ulasan produk kecantikan",
    "Konten tentang ulasan produk kecantikan yang menarik itu",
    "Saya sering membaca ulasan produk kecantikan",
    "Untuk memilih produk kecantikan yang tepat",
    "Saya selalu me-review produk kecantikan",
    "Kredibilitas ulasan produk kecantikan",
    "Persepsi saya tentang produk kecantikan",
    "Ulasan dari konsumen di media sosial dapat menciptakan brand image",
    "Saya ingin membeli produk kecantikan yang diperkenalkan",
    "Saya ingin membeli produk kecantikan berdasarkan informasi",
    "Ulasan konsumen di jejaring sosial dapat membuat saya",
]
COVS = {
    "Jenis Kelamin": "cov_gender",
    "Usia": "cov_age_band",
    "Pendidikan Terakhir": "cov_education",
    "Pendapatan Bulanan (Rupiah)": "cov_income_band",
    "Pengalaman Menggunakan Jejaring Sosial": "cov_social_media_years",
}
DROP = {"Timestamp", "Jejaring Sosial Yang Aktif Digunakan",
        "Jenis Konten Yang Disukai", "Column 29"}
ALLOWED = {1, 2, 3, 4, 5}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Form Responses 1")
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (280, 30), d.shape

    ren = {}
    for c in d.columns:
        hits = [i for i, s in enumerate(STEMS) if c.startswith(s)]
        if hits:
            assert len(hits) == 1, (c, hits)
            ren[c] = f"ewom_{hits[0] + 1:02d}"
    assert sorted(ren.values()) == [f"ewom_{i:02d}" for i in range(1, 22)]
    known = set(ren) | set(COVS) | DROP
    assert set(d.columns) == known, set(d.columns) ^ known
    print(f"[drop] {sorted(DROP)}")

    d = d.rename(columns={**ren, **COVS}).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    cov_cols = list(COVS.values())
    for c in cov_cols:
        d[c] = d[c].astype(str).str.strip()
    codes = sorted(ren.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=codes,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert not set(long["resp"]) - ALLOWED
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: ALLOWED for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
