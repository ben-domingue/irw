#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/sjyrmwbcbx
# DOI: 10.17632/sjyrmwbcbx (dataset; the record names no published paper)
#   Li (2026). Compensatory Online Aggressive Behavior Is Associated With Psychological Distress
#   Through Emotional Venting and Negative Affect Duration, Moderated by Empathy. Mendeley
#   Data, V1.
# Data: data.xlsx, sheet "data": 442 adult social-media users who comment on athlete-influencer
#       videos; Q1-Q12 demographics / usage, Q13-Q57 the five study scales on a 1-7 agreement
#       scale, Q58-Q67 the authors' scale means (not shipped). The second sheet ("Variable,
#       Dimension, Item Name") gives each item's English statement and the covariate codings.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: shipped for all five tables (the deposit's item sheet gives the English statement
#   per Q-code and the anchors "{1, Strongly disagree} ... {7, Strongly agree}"; the sheet is in
#   English and the deposit does not state the administered language; built by
#   automated_finding/itemtext_verification/make_itemtext_li_2026.py, which imports stems()).
#
# Tables (item = Q-code, resp 1-7): li_2026_coab (Q13-Q21, compensatory online aggressive
#   behavior), li_2026_pev (Q22-Q29, perceived emotional venting), li_2026_nad (Q30-Q39,
#   negative affect duration), li_2026_pd (Q40-Q47, psychological distress), li_2026_empathy
#   (Q48-Q57).
# Covariates (codes as in the item sheet): cov_gender (1 male, 2 female), cov_age_group (1-4),
#   cov_education (1-2), cov_employment (1-4), cov_social_media_hours (1-3),
#   cov_video_frequency (1-3), cov_comment_engagement (1-3), cov_comment_target (1-2),
#   cov_sports_participation (1-3), cov_aggressive_posting (1-3), cov_extraversion (1
#   introverted, 2 extraverted), cov_negative_treatment (1-3).
# id: row index.
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
RAW_DIR = RAW_ROOT / "mendeley_sjyrmwbcbx"
COVS = {"Q1": "cov_gender", "Q2": "cov_age_group", "Q3": "cov_education", "Q4": "cov_employment",
        "Q5": "cov_social_media_hours", "Q6": "cov_video_frequency", "Q7": "cov_comment_engagement",
        "Q8": "cov_comment_target", "Q9": "cov_sports_participation", "Q10": "cov_aggressive_posting",
        "Q11": "cov_extraversion", "Q12": "cov_negative_treatment"}
BLOCKS = {  # suffix -> (item numbers, instrument)
    "coab": (range(13, 22), "Compensatory online aggressive behavior (COAB)"),
    "pev": (range(22, 30), "Perceived emotional venting (PEV)"),
    "nad": (range(30, 40), "Negative affect duration (NAD)"),
    "pd": (range(40, 48), "Psychological distress (PD)"),
    "empathy": (range(48, 58), "Empathy toward athletes (EP)"),
}


def stems() -> dict:
    """Q-code -> statement, from the deposit's item sheet."""
    s = pd.read_excel(mendeley_fetch("sjyrmwbcbx", "data.xlsx", RAW_DIR), sheet_name=1, header=None)
    return {str(r[0]).strip(): str(r[1]).strip() for _, r in s.iterrows() if str(r[0]).startswith("Q")}


def main() -> None:
    d = pd.read_excel(mendeley_fetch("sjyrmwbcbx", "data.xlsx", RAW_DIR), sheet_name="data")
    assert len(d) == 442 and list(d.columns) == [f"Q{k}" for k in range(1, 68)]
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {}
    for suffix, (nums, _) in BLOCKS.items():
        items = [f"Q{k}" for k in nums]
        out[f"li_2026_{suffix}"] = (long(d, items, covs, valid=range(1, 8)), pv_for(items, range(1, 8)))
    assert sum(len(list(n)) for n, _ in BLOCKS.values()) == 45  # Q13..Q57; Q58-Q67 are means
    emit(out)


if __name__ == "__main__":
    main()
