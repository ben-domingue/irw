#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/HIT56P (Harvard Dataverse)
# DOI: 10.7910/DVN/HIT56P (dataset, 2024; Shan, Xiaoyue and Zoelitz, Ulf), "Replication data for: Peers Affect
#   Personality Development" (Review of Economics and Statistics, forthcoming). University students.
# Data: personality_raw.dta (2,212 rows, one per student, 46 columns). 25 Big Five items (BFI-S style: 5 traits x 5
#   items, 1-7 Likert; the Stata variable labels are the item wordings) measured at baseline, and the same 25 items
#   again at the end of the semester (suffix _edl, 21 of the 25 items: extr_energy, open_ideas, neur_moody and
#   cons_organized were not repeated; answered by 1,567 students). Variable names kept.
# Table: shan_2024_bfi_s  25 items, wave 0 = baseline, wave 1 = end of lecture period (_edl columns).
# Not shipped: analysis_data.dta and the other .dta files (composites, peer means, grades; no items).
# Reversal check: the deposit labels cons_lazy, extr_shy, agre_rude, agre_fault, neur_calm, neur_relaxed,
#   cons_organized ("tends to be disorganized") and extr_reserved with negatively worded text, yet in the data every
#   within-trait correlation is positive (lowest r = 0.08, agre_rude with its trait mates), i.e. these items are
#   already reverse-coded. Labels and data disagree, so nothing is flipped; codes are as deposited and the keying is
#   recorded in the dictionary notes.
# Covariates: none.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. personality_raw.dta carries no identifier at all; id is the 1..N row index of the source file (the
#   deposit's linking id exists only in analysis_data.dta and cannot be matched to these rows).
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_I_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
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
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


BASE = ["cons_thorough", "extr_talkative", "agre_rude", "open_original", "neur_worry", "cons_persevere",
        "extr_shy", "agre_cooperate", "open_inventive", "neur_calm", "agre_forgive", "cons_lazy", "extr_outgoing",
        "open_artistic", "neur_nervous", "agre_fault", "cons_efficient", "extr_energy", "open_ideas", "neur_moody",
        "cons_organized", "extr_reserved", "agre_kind", "open_imagine", "neur_relaxed"]


def main() -> None:
    p = dv_fetch("10.7910/DVN/HIT56P", "personality_raw.dta", RAW_ROOT / "hit56p")
    d = pd.read_stata(p).reset_index(drop=True)
    assert d.shape == (2212, 46)
    d["id"] = range(1, len(d) + 1)
    parts = []
    for wave, suffix in ((0, ""), (1, "_edl")):
        have = [c for c in BASE if c + suffix in d.columns]   # the end-of-lecture wave has 21 of the 25 items
        assert len(have) == (25 if wave == 0 else 21)
        w = d[["id"] + [c + suffix for c in have]].set_axis(["id"] + have, axis=1)
        w = w.melt(id_vars="id", value_vars=have, var_name="item", value_name="resp")
        w = w[w["resp"].notna()]
        w["wave"] = wave
        parts.append(w)
    t = pd.concat(parts, ignore_index=True)
    assert (t["resp"] % 1 == 0).all() and t["resp"].between(1, 7).all()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=BASE, ordered=True)
    t = t.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t = t[["id", "item", "resp", "wave"]]
    emit({"shan_2024_bfi_s": (t, {c: set(range(1, 8)) for c in BASE})})


if __name__ == "__main__":
    main()
