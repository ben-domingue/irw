#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/wkmm4t7bwh
# DOI: 10.17632/wkmm4t7bwh (Mendeley Data, 2026; Niu, Di). "Anonymized Data for 'When Should AI
#   Recommendations Be Assertive? Matching ...'"; no linked article.
# Data: Study3.sav, the largest of the deposit's eleven experiment files: 655 online consumers in a
#       2 (analytical vs empathetic recommendation content) x 2 (assertive vs non-assertive message) x 2
#       (system- vs user-initiated) between-subjects design about an AI product recommendation for
#       carry-on luggage. After the stimulus, 28 seven-point items: RA1-3 recommendation acceptance,
#       PI1-3 purchase intention, Diag1-3 diagnosticity, Comfort1-4 psychological comfort, Analytical1-3
#       / Empathetic1-3 / Assertiveness1-3 / Certainty1-2 perceived message properties, Involvement1-4
#       product involvement. Means (*_M), the forced choice, PerceivedInitiation and the screening
#       flags are not shipped. Pretests, Studies 1-2 and the control files use different item sets and
#       are left out.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: shipped (the .sav variable labels are the English stems for all 28 items; no value labels
#   on the items, so option_text is blank; Certainty1-2 labels name their semantic-differential poles).
#   Built by automated_finding/itemtext_verification/make_itemtext_niu_2026.py from stems().
#
# Table: niu_2026_ai_recommendation (28 items, 1-7); all items are post-stimulus ratings, so one
#   table with the design as covariates.
# Covariates: cov_condition (1-8, the eight cells), cov_content (0 analytical, 1 empathetic),
#   cov_assertive (0 assertive, 1 non-assertive), cov_initiation (0 system, 1 user), cov_ai_frequency
#   (1-4), cov_gender (1 male, 2 female), cov_age_group (1 18-29 .. 5 60+).
# id: row index (no identifier in the file).
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
import re

RAW_DIR = RAW_ROOT / "mdl_wkmm4t7bwh"
ITEM = re.compile(r"(RA|PI|Diag|Comfort|Analytical|Empathetic|Assertiveness|Certainty|Involvement)\d")


def load():
    import pyreadstat
    return pyreadstat.read_sav(str(mendeley_fetch("wkmm4t7bwh", "Study3.sav", RAW_DIR)))


def stems():
    d, meta = load()
    for c in d.columns:
        if ITEM.fullmatch(c):
            assert c not in meta.variable_value_labels
            yield c, meta.column_names_to_labels[c].strip()


def main() -> None:
    d, meta = load()
    assert len(d) == 655
    d["id"] = range(1, len(d) + 1)
    cov = {"cov_condition": "Condition", "cov_content": "Content", "cov_assertive": "Assert",
           "cov_initiation": "Initiation", "cov_ai_frequency": "AIFrequency", "cov_gender": "Gender",
           "cov_age_group": "Age"}
    for k, v in cov.items():
        d[k] = d[v].astype(int)
    items = [c for c in d.columns if ITEM.fullmatch(c)]
    assert len(items) == 28
    emit({"niu_2026_ai_recommendation": (long(d, items, list(cov), valid=range(1, 8)), pv_for(items, range(1, 8)))})


if __name__ == "__main__":
    main()
