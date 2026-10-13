#!/usr/bin/env python3
# Source: https://zenodo.org/records/12732523
# DOI: 10.1111/puar.13844
#   Vogel, R., Vogel, D., Liegat, M. C., & Hensel, D. (2024). From social categorization to
#   implicit citizenship theories: Advancing the socio-cognitive foundations of state-citizen
#   interactions. Public Administration Review. Data: Zenodo 10.5281/zenodo.12732523.
# Data: Study2.sav (611 German public employees) and Study3.sav (860): for a list of adjectives
#       describing citizens, whether the adjective "fits" (1) or "does not fit" (0) the
#       respondent's image of citizens (PA2_IM_*), each with the response time in ms (RT_*);
#       Study 3 also rates each adjective's emotional valence (Val_*, -2 very negative .. +2 very
#       positive). Study 1b (free-text attributes) is not shipped. The fit columns carry
#       mean-imputed cells (a third, fractional value equal to the item mean): those cells are
#       dropped, not shipped. The *_rvrs copies, duration and the admin_level dummies are not
#       shipped. Study 2 lists 34 adjectives, Study 3 a 17-adjective subset (with "assertive"
#       where Study 2 says "asserting"); administered in German, the codes are the authors'
#       English adjective keys.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- the .sav variable labels are the English adjective keys ("burdened";
#   value labels "does not fit" / "fits"), not the German wording respondents saw; the
#   codebooks repeat the keys. The administered German list is in the paper's appendix.
#
# Tables: vogel_2024_citizen_attributes_s2 (611 x 34, 0/1 + rt in s),
#   vogel_2024_citizen_attributes_s3 (860 x 17, 0/1 + rt), vogel_2024_attribute_valence_s3
#   (860 x 17, -2..2); item = the adjective key.
# Covariates: cov_age, cov_gender (1 male, 2 female, 3 non-binary), cov_academic_degree
#   (Study 2/3: 1 yes, 2 no), cov_part_time (0/1), cov_tenure_years, cov_paygroup (1-5),
#   cov_admin_level (1 federal .. 5 other), cov_admin_subfield (1-11).
# id: the deposit's id (distinct per study; the two studies are separate tables).
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

RAW_DIR = RAW_ROOT / "10_5281_zenodo_12732523"
COVS = {"age": "cov_age", "gender": "cov_gender", "academic_degree": "cov_academic_degree",
        "part_time": "cov_part_time", "tenure": "cov_tenure_years", "paygroup": "cov_paygroup",
        "admin_level": "cov_admin_level", "admin_subfield": "cov_admin_subfield"}


def fits(study: int) -> tuple:
    """(frame, meta) for Study 2 or 3, with the adjective fit items and their response times."""
    d, meta = pyreadstat.read_sav(str(zenodo_fetch(12732523, f"Study{study}.sav", RAW_DIR)))
    return d, meta


def adjectives(d: pd.DataFrame) -> list:
    return [c[len("PA2_IM_"):] for c in d.columns if c.startswith("PA2_IM_") and not c.endswith("_rvrs")]


def build(study: int) -> dict:
    d, meta = fits(study)
    assert d["id"].is_unique
    d["id"] = d["id"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        if c != "cov_tenure_years":
            d[c] = d[c].astype("Int64")
    adj = adjectives(d)
    rows = []
    n_imputed = 0
    for a in adj:
        resp = d[f"PA2_IM_{a}"]
        frac = resp.notna() & (resp % 1 != 0)
        n_imputed += int(frac.sum())
        keep = resp.notna() & ~frac
        part = d.loc[keep, ["id"] + covs].copy()
        part["item"] = a
        part["resp"] = resp[keep].astype(int)
        part["rt"] = d.loc[keep, f"RT_{a}"] / 1000.0  # ms -> s
        rows.append(part)
    t = pd.concat(rows, ignore_index=True)
    print(f"    study {study}: dropped {n_imputed} fractional (mean-imputed) fit cells over {len(adj)} adjectives")
    t = t[["id", "item", "resp", "rt"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    out = {f"vogel_2024_citizen_attributes_s{study}": (t, pv_for(adj, (0, 1)))}
    if study == 3:  # emotional valence rating of the same 17 adjectives, -2 .. +2
        val = [c for c in d.columns if c.startswith("Val_")]
        v = long(d, val, covs, valid=range(-2, 3), rename={c: c[len("Val_"):] for c in val})
        out["vogel_2024_attribute_valence_s3"] = (v, pv_for([c[4:] for c in val], range(-2, 3)))
    return out


def main() -> None:
    out = {}
    out.update(build(2))
    out.update(build(3))
    emit(out)


if __name__ == "__main__":
    main()
