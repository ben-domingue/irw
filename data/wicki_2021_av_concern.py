#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/IZKSL7 (Harvard Dataverse)
# "Replication Data for: How do Familiarity and Fatal Accidents Affect Acceptance of Self-Driving Vehicles?" [Data set],
#   Wicki, M. (ETH Zurich), deposited 2021-10-27. Year = deposit year (the deposit lists only Wicki 2020, an ETH
#   dissertation, as its publication; the journal paper year cannot be confirmed from the deposit).
# Data: DiffInDiff_replication.RData (object df, 819 rows x 347 cols): a three-wave panel of Swiss residents of three
#   municipalities (self-driving shuttle trial); unprefixed columns = wave 1, w2* = wave 2, w3* = wave 3.
# Tables:
#   wicki_2021_av_concern   8 concerns about self-driving vehicles (privacy, software misuse/hacking, liability, system
#                           safety, system reliability, loss of driving pleasure, loss of driver control, job loss), 1-5,
#                           waves 1-3. Direction is documented by the deposit's own script (DiffInDiff_replication.R, plot
#                           title "Concerns regarding self-driving vehicles; 1=do not agree at all, 5=fully agree") and by the
#                           questionnaire PDF ("Stimme ueberhaupt nicht zu 1 ... Stimme voll und ganz zu 5"); higher = more
#                           concern. No recoding.
# Not shipped: the five situational-concern items (avcCar/Ped/Sit/DrAb/Weath; anchor 1 = "besorgt mich sehr", only 5 items),
#   attitude/benefit/judgement items (mixed formats, German strings, "Weiss nicht"), municipality (city), education text,
#   party, income, timestamps, the panel id.
# id: the file's panel id is a platform (panel-provider) code, and 17 codes occur on two rows whose wave-2 answers differ
#   (a merge artefact), so those 34 rows are dropped as ambiguous; id is the row index of the remaining 785 rows.
# Covariates: cov_age (years), cov_male (0/1).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-17).
# PII: none shipped (platform id, municipality and text columns removed).
# Item text: German wording is in the deposit's questionnaire PDFs (Questionnaire_PanelWave_*.pdf).
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_W_2026-10-17"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, saveas: str, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset by its label or original name, in original format."""
    p = raw_dir / saveas
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if fname in (f["label"], f["dataFile"].get("originalFileName"))][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", params={"format": "original"}, headers=UA, timeout=600)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        time.sleep(4)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert len(name) <= 40, name
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any(), name
        assert t["id"].nunique() >= 100 and 8 <= t["item"].nunique() <= 700, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False, float_format="%.10g")
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


ITEMS = {"Priv": "avc_privacy", "Hack": "avc_hack", "Acci": "avc_liability", "SysSc": "avc_system_safety",
         "SysRl": "avc_system_reliability", "DrPl": "avc_driving_pleasure", "DrCtr": "avc_driver_control",
         "Joblos": "avc_job_loss"}


def main() -> None:
    import pyreadr
    p = dv_fetch("10.7910/DVN/IZKSL7", "DiffInDiff_replication.RData", RAW_ROOT, "izksl7.RData")
    d = pyreadr.read_r(str(p))["df"]
    assert d.shape == (819, 347), d.shape
    dup = d["id"].duplicated(keep=False)
    assert dup.sum() == 34, dup.sum()
    d = d[~dup].reset_index(drop=True)
    d["rid"] = np.arange(1, len(d) + 1)
    assert d["male"].dropna().isin([0, 1]).all() and d["age"].dropna().min() >= 18, d["age"].min()
    frames = []
    for wave, pre in ((1, ""), (2, "w2"), (3, "w3")):
        for k, name in ITEMS.items():
            x = pd.to_numeric(d[f"{pre}avc{k}"], errors="raise")
            assert x.dropna().isin([1, 2, 3, 4, 5]).all(), (pre, k)
            frames.append(pd.DataFrame({"id": d["rid"], "item": name, "resp": x, "wave": wave,
                                        "cov_age": d["age"], "cov_male": d["male"]}))
    t = pd.concat(frames)
    t = t[t["resp"].notna()].copy()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=list(ITEMS.values()), ordered=True)
    t = t.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t["cov_male"] = t["cov_male"].astype("Int64")
    t["cov_age"] = t["cov_age"].astype("Int64")
    t = t[["id", "item", "resp", "wave", "cov_age", "cov_male"]]
    c = t.pivot_table(index=["id", "wave"], columns="item", values="resp").corr().values
    print(f"    [note] inter-item r: min {c.min():.2f} mean {c.mean():.2f}")
    assert c.min() > 0
    emit({"wicki_2021_av_concern": (t, {n: {1, 2, 3, 4, 5} for n in ITEMS.values()})})


if __name__ == "__main__":
    main()
