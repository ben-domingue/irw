#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.32626206.v2
# DOI: 10.6084/m9.figshare.32626206.v2 (dataset; the record names no paper)
#   Montaña-Blasco, Mireia; Jiménez-Morales, Mònika (2026). Dataset on Adolescent Digital
#   Engagement and Well-being Patterns Among Spanish Youth (SMARS, 2024). figshare.
# Data: SMARS_Adolescent_Social_Media_Spain_2024 (1).csv: 1,043 Spanish adolescents aged
#       12-18, online survey 24 Apr - 6 May 2024 (ODEC fieldwork). Codebook_SMARS_2024 (1).csv
#       gives every variable's Spanish label and value labels; the Spanish questionnaire is
#       in the record. Shipped blocks (native codes kept, 1 = the first anchor):
#         P2101-P2209 digital skills, 18 items: 1 can do and could teach .. 5 don't know
#           what it is (6 no sabe / 7 no contesta dropped)
#         P2401-P2406 AI literacy, 6: 1 totalmente de acuerdo .. 5 totalmente en desacuerdo
#         P3101-P3109 perceived impact of social media on ... , 9: 1 muy positivamente .. 5
#         P5101-P5109 mental-illness attitudes, 9: agreement 1-5
#         P5201-P5212 mental-health statements, 12: 1 verdadera, 2 falsa (no key applied)
#         P7101-P7120 content viewing frequency, 20: 1 siempre .. 5 nunca
#         P8101-P8113 digital well-being on TikTok, 13: agreement 1-5, TikTok users only
#           (B1107 = 1, as the codebook directs)
#         P9101-P9125 coping with negative feelings, 25: agreement 1-5
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped for the study-authored blocks (digital skills, social-media impact,
#   content frequency, TikTok well-being) from the codebook's Spanish labels, IRW English
#   translation; built by automated_finding/itemtext_verification/make_itemtext_montana_blasco_2026.py.
#   Not shipped for AI literacy, mental-illness attitudes, mental-health statements and
#   coping: adapted published scales whose rights were not checked (text is in the codebook).
#
# Tables (item = the deposit's variable name): montana_blasco_2026_digital_skills,
#   _ai_literacy, _sm_impact, _mi_attitudes, _mh_statements, _content_freq,
#   _tiktok_wellbeing, _coping.
# Covariates: cov_gender (1 hombre, 2 mujer), cov_age (years, P002 code + 10),
#   cov_municipality_size (1-5), cov_education (P005 code), cov_region (P004 code 1-17).
# id: row index of the csv.

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

RAW_DIR = RAW_ROOT / "10_6084_m9_figshare_32626206_v2"
FNAME = "SMARS_Adolescent_Social_Media_Spain_2024 (1).csv"
P = "montana_blasco_2026_"
BLOCKS = {  # table -> (variables, valid codes, tiktok-only)
    P + "digital_skills": ([f"P21{k:02d}" for k in range(1, 10)] + [f"P22{k:02d}" for k in range(1, 10)], range(1, 6), False),
    P + "ai_literacy": ([f"P24{k:02d}" for k in range(1, 7)], range(1, 6), False),
    P + "sm_impact": ([f"P31{k:02d}" for k in range(1, 10)], range(1, 6), False),
    P + "mi_attitudes": ([f"P51{k:02d}" for k in range(1, 10)], range(1, 6), False),
    P + "mh_statements": ([f"P52{k:02d}" for k in range(1, 13)], (1, 2), False),
    P + "content_freq": ([f"P71{k:02d}" for k in range(1, 21)], range(1, 6), False),
    P + "tiktok_wellbeing": ([f"P81{k:02d}" for k in range(1, 14)], range(1, 6), True),
    P + "coping": ([f"P91{k:02d}" for k in range(1, 26)], range(1, 6), False),
}


def main() -> None:
    d = pd.read_csv(figshare_fetch(32626206, FNAME, RAW_DIR))
    assert len(d) == 1043
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["P002"] + 10
    d = d.rename(columns={"P001": "cov_gender", "P003": "cov_municipality_size", "P005": "cov_education", "P004": "cov_region"})
    covs = ["cov_gender", "cov_age", "cov_municipality_size", "cov_education", "cov_region"]
    out = {}
    for name, (items, valid, tiktok) in BLOCKS.items():
        x = d[d["B1107"] == 1] if tiktok else d
        drop = x[items].notna() & ~x[items].isin(list(valid))
        if drop.values.any():
            print(f"  {name}: dropped {int(drop.values.sum())} no-sabe/no-contesta (6/7) responses")
        x = x.copy()
        x[items] = x[items].mask(drop)
        out[name] = (long(x, items, covs, valid=valid), pv_for(items, valid))
    emit(out)


if __name__ == "__main__":
    main()
