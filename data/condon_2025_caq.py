#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/2IBBMG
# DOI: 10.7910/DVN/2IBBMG (deposit; no linked paper on the record)
#   Condon, D., Zabelina, D., & Revelle, W. (2025). Reproducibility Data for: Creative
#   Achievement and Individual Differences. Harvard Dataverse, V5.
# Data: CAQ.tab (format=original -> CAQ.csv): 5,650 SAPA respondents (RID) x 140 columns of a
#       revised Creative Achievement Questionnaire. Ten domains (inv, music, ttvf, sci, cw,
#       dance, cook, art, humor, ad), each a check-all-that-apply list of 7-10 achievement
#       statements coded 1 = checked / 999 = not checked (every row carries 1 or 999, and the
#       CAFreq* follow-up is answered exactly when the matching box is checked, so 999 is an
#       unchecked box, not a refusal). CAFreq* columns are "how many times" follow-ups,
#       1-7, present only for the checked statement.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: not shipped. The file has no variable labels (CSV export) and the deposit has
#   no codebook; the statements are Carson et al.'s (2005) CAQ as revised for SAPA, which
#   would need the published instrument (and the SAPA revision) to transcribe.
#
# Tables:
#   condon_2025_caq       81 checkbox items, 1 checked / 0 not checked (source 999 -> 0)
#   condon_2025_caq_freq  59 frequency follow-ups, 1-6 observed (1-7 permitted), only where the box was checked
# id: the deposit's RID. No covariates in this file (the SAPA personality file is separate).

RAW_KEY = "10.7910_dvn_2ibbmg"
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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / RAW_KEY
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def dv_fetch(doi: str, fname: str, raw_dir: Path = None,
             host: str = "dataverse.harvard.edu") -> Path:
    """Fetch a Harvard Dataverse file by its ORIGINAL name, as format=original
    (never the lossy .tab conversion)."""
    raw_dir = raw_dir or RAW_DIR
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def to_long(d: pd.DataFrame, items, id_col="id", extra=(), rename=None) -> pd.DataFrame:
    """Melt `items` (wide columns) to id/item/resp, carrying `extra` columns."""
    keep = [id_col] + list(extra)
    t = d[keep + list(items)].melt(id_vars=keep, value_vars=list(items),
                                   var_name="item", value_name="resp")
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t = t.dropna(subset=["resp"])
    if id_col != "id":
        t = t.rename(columns={id_col: "id"})
    lead = ["id", "item", "resp"] + [c for c in ("wave", "treat", "rt", "date") if c in t.columns]
    cov = [c for c in t.columns if c.startswith("cov_")]
    tail = [c for c in ("rater", "item_family") if c in t.columns]
    return t[lead + cov + tail].reset_index(drop=True)


def emit(tables: dict) -> None:
    """tables: name -> (long df, permitted_values or None). QC + validate + write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in names:
        assert not (OUT_DIR / f"{name}.csv").exists() or os.environ.get("IRW_OVERWRITE"), \
            f"{name}.csv already staged; set IRW_OVERWRITE=1 to rebuild"
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + [c for c in ("wave", "rater") if c in t]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, (name, t["id"].nunique())
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


DOI = "10.7910/DVN/2IBBMG"


def load() -> pd.DataFrame:
    d = pd.read_csv(dv_fetch(DOI, "CAQ.csv"))
    assert d["RID"].is_unique and len(d) == 5651
    d = d.rename(columns={"RID": "id"})
    d = d.dropna(subset=[c for c in d.columns if c != "id"], how="all")
    return d


def main() -> None:
    d = load()
    box = [c for c in d.columns if c.startswith("CA") and not c.startswith("CAFreq")]
    freq = [c for c in d.columns if c.startswith("CAFreq")]
    assert len(box) + len(freq) + 1 == d.shape[1], (len(box), len(freq))
    b = d[["id"] + box].copy()
    for c in box:
        assert set(b[c].dropna().unique()) <= {1.0, 999.0}, c
        b[c] = b[c].map({1.0: 1, 999.0: 0})
    f = d[["id"] + freq].replace(999.0, float("nan"))
    for c in freq:
        assert f[c].dropna().between(1, 7).all(), c
    lower = {c: c[2:].lower() for c in box}            # CAinv1 -> inv1
    lowerf = {c: "freq_" + c[6:].lower() for c in freq}  # CAFreqinv4 -> freq_inv4
    emit({
        "condon_2025_caq": (to_long(b, box, rename=lower), [0, 1]),
        "condon_2025_caq_freq": (to_long(f, freq, rename=lowerf), list(range(1, 8))),
    })


if __name__ == "__main__":
    main()
