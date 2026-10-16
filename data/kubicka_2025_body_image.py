#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WZWS6Q
# DOI: 10.7910/DVN/WZWS6Q (dataset, 2025; Kubicka, Karolina). "Parent-Child Relationship Quality, Media Ideal
#   Internalization in Shaping Positive Body Image and Self-Esteem in Children": 421 Polish children aged 7-13
#   rating their relationship with their mother (_M) and father (_O) and their own body appreciation and media
#   internalization.
# Data: one SPSS file deposited without an extension (Dataverse datafile 11882635, application/x-spss-sav).
#       CSQ1-20_M/_O = Coping Strategies Questionnaire, child form (0-2; a handful of CSQ20 cells are 3/4, out of
#       range, dropped), SS21-35_M/_O = Security Scale (1-4; two 0 cells dropped), KBF1-6_M_REK/_O_REK = Physical
#       Closeness Scale stored recoded by the depositor (1-4, shipped as stored, codes keep the _REK suffix),
#       BAS1-10 = Body Appreciation Scale-2 for children (1 never - 5 always), M1-6 = media ideal
#       internalization (1-4). Items answered about the mother and the father ship as separate items (suffix _M /
#       _O) in one table per instrument. The Self-Perception Scale (3 recoded items + text) and all totals are not
#       shipped. Variable labels name the instruments only; value labels exist for BAS and the covariates.
# License: CC0 1.0 (Harvard Dataverse).
#
# Item text: not shipped -- the .sav labels name the instrument on the first item of each block only
#   (variable-label level) and only BAS and the demographics carry value labels; no Polish item wording in the
#   deposit.
#
# Tables: kubicka_2025_csq (40), kubicka_2025_security_scale (30), kubicka_2025_physical_closeness (12),
#   kubicka_2025_bas2c (10), kubicka_2025_media_internalization (6).
# Covariates: cov_child_age_years, cov_child_sex (1 boy, 2 girl), cov_bmi, cov_weight_group (-2..2),
#   cov_nationality (1 Polish ...), cov_internet_hours (1-6 bands), cov_raised_by (1 both, 2 mother, 3 father ...),
#   cov_siblings (1 yes, 2 no), cov_mother_education, cov_father_education (1-5), cov_material_situation (1-6).
# id: row index.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

import warnings

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

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


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p

def drop_frac(d: pd.DataFrame, cols: list, label: str) -> pd.DataFrame:
    """Blank non-integer cells (the lab's person-mean imputation of missing answers) and say how many."""
    v = d[cols].apply(pd.to_numeric, errors="coerce")
    frac = (v.notna() & (v % 1 != 0))
    n = int(frac.values.sum())
    if n:
        print(f"    [{label}] {n} fractional (imputed) cell(s) of {int(v.notna().values.sum())} dropped")
    d[cols] = v.mask(frac)
    return d


def stack_waves(d: pd.DataFrame, prefixes: dict, items: list, covs: list, valid, label: str,
                extra_cov_by_wave: dict | None = None) -> pd.DataFrame:
    """prefixes: wave number -> column prefix; items: bare item codes (prefix + code = source column).
    Returns long with a `wave` column; waves with no answers for a respondent drop out."""
    parts = []
    for w, pre in prefixes.items():
        cols = [pre + i for i in items]
        missing = [c for c in cols if c not in d.columns]
        assert not missing, (label, w, missing)
        sub = d[["id", *covs] + cols].copy()
        if extra_cov_by_wave:
            for k, v in extra_cov_by_wave.items():
                sub[k] = d[v[w]] if v.get(w) in d.columns else pd.NA
        sub = drop_frac(sub, cols, f"{label} wave {w}")
        sub = sub.rename(columns={pre + i: i for i in items})
        sub["wave"] = w
        ex = list(extra_cov_by_wave) if extra_cov_by_wave else []
        t = long(sub, items, covs + ex, valid=valid, extra=["wave"])
        parts.append(t)
    t = pd.concat(parts, ignore_index=True)
    return t.sort_values(["id", "wave", "item"]).reset_index(drop=True)

RAW_DIR = RAW_ROOT / "dvn_WZWS6Q"


def main() -> None:
    import pyreadstat
    p = download("https://dataverse.harvard.edu/api/access/datafile/11882635?format=original", RAW_DIR / "kubicka.sav")
    d, meta = pyreadstat.read_sav(str(p))
    assert len(d) == 421
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_child_age_years": "Wiek_lata_M", "cov_child_sex": "Plec_dziecko_M", "cov_bmi": "BMI", "cov_weight_group": "Grupa_waga",
           "cov_nationality": "Narodowosc_M", "cov_internet_hours": "Internet_M", "cov_raised_by": "Wych_dziecko_M",
           "cov_siblings": "Rodzenstwo_M", "cov_mother_education": "Wyksz_M_M", "cov_father_education": "Wyksz_O_M",
           "cov_material_situation": "Syt_materialna_M"}
    for k, v in cov.items():
        d[k] = d[v]
    covs = list(cov)
    csq = [f"CSQ{i}_{s}" for s in ("M", "O") for i in range(1, 21)]
    ss = [f"SS{i}_{s}" for s in ("M", "O") for i in range(21, 36)]
    kbf = [f"KBF{i}_{s}_REK" for s in ("M", "O") for i in range(1, 7)]
    bas = [f"BAS{i}" for i in range(1, 11)]
    med = [f"M{i}" for i in range(1, 7)]
    for cols, valid, lab in ((csq, range(0, 3), "csq"), (ss, range(1, 5), "ss")):
        v = d[cols].apply(pd.to_numeric, errors="coerce")
        bad = v.notna() & ~v.isin(list(valid))
        print(f"    [{lab}] {int(bad.values.sum())} out-of-range cell(s) dropped: {sorted(set(v.values[bad.values].tolist()))}")
        d[cols] = v.mask(bad)
    emit({"kubicka_2025_csq": (long(d, csq, covs, valid=range(0, 3)), pv_for(csq, range(0, 3))),
          "kubicka_2025_security_scale": (long(d, ss, covs, valid=range(1, 5)), pv_for(ss, range(1, 5))),
          "kubicka_2025_physical_closeness": (long(d, kbf, covs, valid=range(1, 5)), pv_for(kbf, range(1, 5))),
          "kubicka_2025_bas2c": (long(d, bas, covs, valid=range(1, 6)), pv_for(bas, range(1, 6))),
          "kubicka_2025_media_internalization": (long(d, med, covs, valid=range(1, 5)), pv_for(med, range(1, 5)))})


if __name__ == "__main__":
    main()
