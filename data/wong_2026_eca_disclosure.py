#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/bng8pktfn7
# DOI: 10.17632/bng8pktfn7.1 (dataset, 2026; Wong, Kenji). "Disclosure Governance in Repeated Interactions with an
#   Embodied Conversational Agent" -- 252 Chinese-speaking adults who each held two scripted sessions (R1, R2)
#   with an embodied conversational agent and rated the session afterwards.
# Data: Submission_Dataset.xlsx, sheet Table1_Questionnaire (the Lang_Acoustic and Interview sheets are
#       speech-analytic and coded-interview variables, not shipped). M1_R1..M15_R1 and M1_R2..M15_R2 = the 15
#       post-session questionnaire items (1-7), shipped with wave = round. The deposit does not say which items
#       form the six scored constructs (disclosure breadth/depth, social mask lowering, privacy interpretive
#       authority delegation, felt epistemic recognition, reflective reappraisal), so the block ships as one
#       table with a data note. The single pre/post readiness, boundary-control and evaluation-concern items,
#       durations and the AI-literacy composites are not shipped.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: not shipped -- codes M1-M15 only; no codebook in the deposit.
#
# Tables: wong_2026_eca_disclosure (15 items x 2 waves, N = 252).
# Covariates: cov_gender (1/2/3), cov_age, cov_education (1-6), cov_role (1-7), cov_ai_literacy (deposit's total
#   mean), cov_script_version (V1-V4, per wave), cov_topic (1-6, per wave).
# id: row index (the deposit's QDIR-### codes are not shipped).
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


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p

RAW_DIR = RAW_ROOT / "mendeley_bng8pktfn7"


def main() -> None:
    d = pd.read_excel(mendeley_fetch("bng8pktfn7", "Submission_Dataset.xlsx", RAW_DIR), sheet_name="Table1_Questionnaire")
    assert len(d) == 252 and d["participant_id"].is_unique
    d["id"] = range(1, len(d) + 1)
    for k, v in {"cov_gender": "gender", "cov_age": "actual_age", "cov_education": "education", "cov_role": "role",
                 "cov_ai_literacy": "AI_Literacy_Total"}.items():
        d[k] = d[v]
    base = ["cov_gender", "cov_age", "cov_education", "cov_role", "cov_ai_literacy"]
    items = [f"M{i}" for i in range(1, 16)]
    parts = []
    for r in (1, 2):
        p = d[["id", *base]].copy()
        p["wave"] = r
        p["cov_script_version"] = d[f"script_version_R{r}"]
        p["cov_topic"] = d[f"topic_code_R{r}"]
        for i in items:
            p[i] = d[f"{i}_R{r}"]
        parts.append(p)
    both = pd.concat(parts, ignore_index=True)
    covs = base + ["cov_script_version", "cov_topic"]
    emit({"wong_2026_eca_disclosure": (long(both, items, covs, valid=range(1, 8), extra=["wave"]), pv_for(items, range(1, 8)))})


if __name__ == "__main__":
    main()
