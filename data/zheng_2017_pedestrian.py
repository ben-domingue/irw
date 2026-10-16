#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/The_joint_effect_of_personality_traits_and_perceived_stress_on_pedestrian_behavior_in_a_Chinese_sample/5652049
# DOI: 10.1371/journal.pone.0188153 (Zheng, T., Qu, W., Ge, Y., Sun, X., & Zhang, K. (2017). The joint effect of
#   personality traits and perceived stress on pedestrian behavior in a Chinese sample. PLOS ONE 12(11): e0188153.)
#   Data: S6 Appendix (figshare 5652049), a 311-respondent paper survey of residents of Anshun, Guizhou.
# Data: S6 Appendix.xlsx, Sheet1 (311 x 459; Sheet2 is the bare variable list, no labels). The workbook is a larger
#       survey than the paper uses, coded q<block>_<item> with no codebook; 0 = not answered throughout. Blocks
#       were tied to instruments through the score columns the depositor left in the file: q16_1-10 (1-5) is the
#       PSS-10 (r = .76 with the PSS total; the paper reports PSS-10 on a 0-4 scale, the file stores 1-5),
#       q17_1-40 (1-4) is the Zung SDS (items 1-20; the file's reverse-coded copies q17_<k>r sit exactly on SDS
#       reversals 2,5,6,11,12,14,16,17,18,20) followed by the Zung SAS (items 21-40; reversed copies on SAS
#       reversals 5,9,13,17,19), q18_1-12 (1-7) is the PSSS (sum equals the PSSS total where complete),
#       q19_1-5 (1-7) is the SWLS (sum equals SWB), q22_1-40 (1-5) is the 40-item personality block (BFI
#       Extraversion 8 + Openness 10 + Neuroticism 8 + normlessness 4 + IPIP altruism 10 = 40; the per-trait
#       score ranges Per_1..Per_5 match those lengths, but the file's reverse-coded copies do not reproduce the
#       BFI key, so the item-to-trait assignment is NOT established -- shipped as an opaque 40-item block). The
#       CPBS block could not be located with confidence (no block sums to PBS_1-4) and is not shipped; nor are
#       the remaining q-blocks, demographics (s*, lx: undocumented codes) or any score.
# License: CC BY 4.0 (PLOS / figshare).
#
# Item text: not shipped -- the S1-S5 appendices give the English instruments (BFI-44, normlessness, altruism,
#   CPBS, PSS-10) but the q-codes are not keyed to them and the administration was Chinese; the SDS/SAS/PSSS/SWLS
#   wording is not in the deposit.
#
# Tables: zheng_2017_pss10 (10), zheng_2017_sds_sas (40; q17_1-20 SDS, q17_21-40 SAS), zheng_2017_psss (12),
#   zheng_2017_swls (5), zheng_2017_personality (40, opaque).
# Covariates: none (the demographic codes are undocumented).
# id: the deposit's qumn questionnaire number.
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

RAW_DIR = RAW_ROOT / "figshare_5652049"


def main() -> None:
    d = pd.read_excel(figshare_fetch(5652049, "S6 Appendix.xlsx", RAW_DIR), sheet_name="Sheet1")
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 311 and d["qumn"].is_unique
    d["id"] = d["qumn"].astype(int)
    blocks = {"zheng_2017_pss10": ([f"q16_{i}" for i in range(1, 11)], range(1, 6)),
              "zheng_2017_sds_sas": ([f"q17_{i}" for i in range(1, 41)], range(1, 5)),
              "zheng_2017_psss": ([f"q18_{i}" for i in range(1, 13)], range(1, 8)),
              "zheng_2017_swls": ([f"q19_{i}" for i in range(1, 6)], range(1, 8)),
              "zheng_2017_personality": ([f"q22_{i}" for i in range(1, 41)], range(1, 6))}
    tabs = {}
    for name, (cols, valid) in blocks.items():
        v = d[cols].apply(pd.to_numeric, errors="coerce")
        v = v.mask(v == 0)  # 0 = not answered
        frac = v.notna() & (v % 1 != 0)
        if frac.values.sum():
            print(f"    [{name}] {int(frac.values.sum())} fractional (mean-replaced) cell(s) dropped")
        v = v.mask(frac)
        bad = v.notna() & ~v.isin(list(valid))
        if bad.values.sum():
            print(f"    [{name}] {int(bad.values.sum())} out-of-range cell(s) dropped: {sorted(set(v.values[bad.values].tolist()))}")
        d[cols] = v.mask(bad)
        tabs[name] = (long(d, cols, [], valid=valid), pv_for(cols, valid))
    emit(tabs)


if __name__ == "__main__":
    main()
