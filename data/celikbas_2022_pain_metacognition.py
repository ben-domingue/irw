#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Pain_Metacognition_Questionnaire/19750066
# DOI: 10.6084/m9.figshare.19750066 (dataset; the record's description names the paper
#   "Beliefs About Pain Rumination: Psychometric Properties of the Turkish Version of the Pain
#   Metacognitions Questionnaire" without a DOI)
#   Çelikbaş, Z. (2022). Pain Metacognition Questionnaire. figshare.
# Data: Agriyailiskinüstbilisölcegi.sav (the record lists the file twice): 210 Turkish adults,
#       105 chronic-pain patients and 105 controls, with the 21-item Pain Metacognitions
#       Questionnaire (0-3), the 30-item Metacognitions Questionnaire MCQ-30 (ÜBÖ1-30, 1-4), the
#       Pain Catastrophizing Scale (13 items, 0-4; the file carries a 14th column under the same
#       prefix that is not part of the deposited subscale sums and is not shipped) and the Brief
#       Pain Inventory's 4 intensity and 7 interference ratings (0-10). The subscale/total
#       columns (positive/negative metacognitions, ÜBÖ_toplam, AFÖ_*, mindfulness, HADS) are
#       composites and are not shipped.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Checked both label levels: no variable labels on any column; value
#   labels on the PMQ (anchors, mojibake'd) and PCS items only. No Turkish stems in the deposit.
#
# Tables: celikbas_2022_pmq (210 x 21, 0-3), celikbas_2022_mcq30 (210 x 30, 1-4),
#   celikbas_2022_pcs (210 x 13, 0-4), celikbas_2022_bpi (210 x 11, 0-10). Item codes PMQ_k,
#   MCQ30_k, PCS_k are the deposit's Agriya_iliskin_üstbilisler_ölcegi_k, ÜBÖk and
#   Agriyi_felaketlestirme_ölcegi_k by position; BPI_intensity_k and BPI_interf_<facet> are the
#   deposit's Kisa_agri_envanteri_* columns (facets: genel_aktivite, ruh_durumu, yürüme,
#   egzersiz, iliskiler, uyku, yasamdan_zevk).
# Covariates: cov_group (1 kontrol / 2 agri), cov_age, cov_gender, cov_marital,
#   cov_education_years, cov_employment, cov_ses, cov_comorbidity, cov_substance_use, cov_vas_pain.
# id: the deposit's katilimcino.
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


def figshare_fetch(article: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.figshare.com/v2/articles/{article}", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == fname][0]
        download(url, p)
    return p


def mendeley_fetch(dataset: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://data.mendeley.com/public-api/datasets/{dataset}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"] if f["filename"] == fname][0]
        download(url, p)
    return p


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
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
    """Melt `items` to long, drop missing, check integer codes inside `valid`, order columns.
    `rename` maps a source column to the `item` code it ships under (default: the column name)."""
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


import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "figshare_19750066"
FNAME = "Agriyailiskinüstbilisölcegi.sav"
COVS = {"gruplar": "cov_group", "yas": "cov_age", "cinsiyet": "cov_gender", "medenidurum": "cov_marital",
        "ögrenimsüresi": "cov_education_years", "calisma_durumu": "cov_employment",
        "sosyoekonomik_düzey": "cov_ses", "ek_hastalik": "cov_comorbidity", "Madde_kullanimi": "cov_substance_use",
        "Görsel_agri_skalasi": "cov_vas_pain"}
PMQ = {f"Agriya_iliskin_üstbilisler_ölcegi_{i}": f"PMQ_{i}" for i in range(1, 22)}
MCQ = {f"ÜBÖ{i}": f"MCQ30_{i}" for i in range(1, 31)}
PCS = {f"Agriyi_felaketlestirme_ölcegi_{i}": f"PCS_{i}" for i in range(1, 14)}
BPI = {f"Kisa_agri_envanteri_agri_yogunlugu_alt_ölcegi_{i}.soru": f"BPI_intensity_{i}" for i in range(1, 5)}
BPI.update({"Kisa_agri_envanteri_yeti_yetimi__alt_ölcegi_genel_aktivite": "BPI_interf_genel_aktivite",
            "Kisa_agri_envanteri_yeti_yetimi__alt_ölcegi_ruh_durumu": "BPI_interf_ruh_durumu",
            "Kisa_agri_envanteri_yeti_yetimi__alt_ölcegi_yürüme_yetenegi": "BPI_interf_yurume",
            "Kisa_agri_envanteri_yeti_yetimi__alt_ölcegi_egzersiz": "BPI_interf_egzersiz",
            "Kisa_agri_envanteri_yeti_yetimi__alt_ölcegi_dig_ins_ilsk": "BPI_interf_iliskiler",
            "Kisa_agri_envanteri_yeti_yetimi__alt_ölcegi_uyku": "BPI_interf_uyku",
            "Kisa_agri_envanteri_yeti_yetimi__alt_ölcegi_yasamdan_zevk_alma": "BPI_interf_yasamdan_zevk"})


def main() -> None:
    d, m = pyreadstat.read_sav(figshare_fetch(19750066, FNAME, RAW_DIR))
    assert len(d) == 210 and d["katilimcino"].is_unique
    d["id"] = d["katilimcino"].astype(int)
    assert (d[list(PMQ)].sum(axis=1) == d["Positive_metacognitions_subscale"] + d["Negative_metacognitions_subscale"]).all()
    assert (d[list(MCQ)].sum(axis=1) == d["ÜBÖ_toplam"]).all()
    assert (d[list(PCS)].sum(axis=1) == d[["AFÖ_ruminasyon", "AFÖ_büyütme", "AFÖ_çaresizlik"]].sum(axis=1)).all()
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")

    def tab(mp, valid):
        return (long(d, list(mp), covs, valid=valid, rename=mp), pv_for(list(mp.values()), valid))
    emit({"celikbas_2022_pmq": tab(PMQ, range(0, 4)), "celikbas_2022_mcq30": tab(MCQ, range(1, 5)),
          "celikbas_2022_pcs": tab(PCS, range(0, 5)), "celikbas_2022_bpi": tab(BPI, range(0, 11))})


if __name__ == "__main__":
    main()
