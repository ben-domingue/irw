#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XRMB5G
# DOI: 10.7910/DVN/XRMB5G (dataset, 2026; Lavigne, Mathieu). Replication data for "The politicization of
#   attitudes towards misinformation: how ideology shapes epistemic beliefs, normative judgments, and policy
#   support" (Journal of Elections, Public Opinion and Parties). Study 2 = the Quebec Election Misinformation
#   Project (QEMP) 2022 panel, post-election survey (N = 3,707).
# Data: qemp.csv (Study 1's cemp.csv holds single 0-10 vignette ratings, one condition per respondent, and is not
#       item-response data). misinfo_exp1_1-5_post = five agree/disagree statements on misinformation (public
#       discourse biased against the right / the left; no impartial way to settle factual debates; politicians
#       should be free to say what is considered false; my party's leader should always tell the truth) and
#       misinfo_attitudes2_1-3_post = three statements on content moderation and anti-misinformation measures,
#       all 1 strongly disagree - 5 strongly agree, 6 = don't know (set to missing). The codebook ("QEMP - PES.pdf")
#       numbers the sub-items 9/14/10/12/13 and 9/10/12 while the data columns are _1.._5 and _1.._3, so the
#       column-to-statement assignment is positional and not established. The misinfo_exp1 block follows a
#       randomised prompt (control / left / right), kept as cov_prompt.
# License: CC0 1.0 (Harvard Dataverse).
#
# Item text: not shipped -- the codebook gives the eight statements, but the data columns' suffixes do not
#   match the codebook's sub-item numbers, so the mapping cannot be established from the deposit.
#
# Tables: lavigne_2026_misinfo_attitudes (8 items).
# Covariates: cov_prompt (control / left / right prompt shown before the block), cov_age, cov_gender (1-4),
#   cov_education (1-11), cov_ideology (0-10), cov_news_frequency (1-5), cov_social_media_frequency (1-6),
#   cov_language (EN / FR-CA).
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

RAW_DIR = RAW_ROOT / "dvn_XRMB5G"


def main() -> None:
    d = pd.read_csv(dv_fetch("10.7910/DVN/XRMB5G", "qemp.csv", RAW_DIR))
    assert len(d) == 3707
    d["id"] = range(1, len(d) + 1)
    pr = {"control": "Experiment_DO_prompt_control_post", "left": "Experiment_DO_prompt_left_post", "right": "Experiment_DO_prompt_right_post"}
    d["cov_prompt"] = pd.NA
    for k, c in pr.items():
        d.loc[d[c].notna(), "cov_prompt"] = k
    d = d.rename(columns={"age_pre": "cov_age", "gender_pre": "cov_gender", "education_pre": "cov_education", "ideology_1_post": "cov_ideology",
                          "freq_news_pre": "cov_news_frequency", "freq_socmed_pre": "cov_social_media_frequency", "UserLanguage_pre": "cov_language"})
    covs = ["cov_prompt", "cov_age", "cov_gender", "cov_education", "cov_ideology", "cov_news_frequency", "cov_social_media_frequency", "cov_language"]
    items = [f"misinfo_exp1_{i}_post" for i in range(1, 6)] + [f"misinfo_attitudes2_{i}_post" for i in range(1, 4)]
    v = d[items].apply(pd.to_numeric, errors="coerce")
    print(f"    [dk] {int((v == 6).values.sum())} don't-know (6) cells set to missing")
    d[items] = v.mask(v == 6)
    ren = {c: c.replace("_post", "") for c in items}
    t = long(d, items, covs, valid=range(1, 6), rename=ren)
    emit({"lavigne_2026_misinfo_attitudes": (t, pv_for(list(ren.values()), range(1, 6)))})


if __name__ == "__main__":
    main()
