#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ED8ZOO (Harvard Dataverse)
# Eichmeier, A. (2019). Replication Data for: Differences that don't make much difference: Party asymmetry in open-minded
#   cognitive styles has little relationship to information processing behavior [Data set]. Harvard Dataverse.
#   Paper: Eichmeier, A. & Stenhouse, N. (2019), Research & Politics.
# Data: rp_dataset_042019_2.tab (SPSS file as deposited, 1,129 rows x 468 columns; US online survey, fracking
#   message experiment). Syntax rp_cleaning_syntax_042019.sps documents which raw column became which scale item.
# Tables (raw, non-imputed Qualtrics columns Q3.1-Q3.4, Q6.2, Q6.3; item names follow the authors' renamed variables):
#   eichmeier_2019_aot                    Actively open-minded thinking, 11 items, 1-6 (disagree strongly .. agree strongly)
#   eichmeier_2019_nfc                    Need for cognition, 16 items, 1-5 (extremely uncharacteristic .. characteristic)
#   eichmeier_2019_need_for_affect        Need for affect, 26 items, 1-5 (strongly disagree .. strongly agree)
#   eichmeier_2019_need_for_closure       Need for cognitive closure, 15 items, 1-6 (completely disagree .. agree)
#   eichmeier_2019_moralized_rationality  Moralized rationality, 9 items, 1-7 (completely disagree .. completely agree)
#   eichmeier_2019_epistemic_beliefs      Faith in intuition (4), need for evidence (4), truth is political (4); 1-5
# Not shipped: the HD columns (hot-deck IMPUTED copies of the raw columns; the raw columns have ~0.5% missing and are
#   used instead), composites (AOTDog, NFC, ...), the 6-item importance-of-rationality block (<8 items), religious
#   fundamentalism (6), science knowledge (mixed knowledge items and recodes), CRT (strings), single-item blocks, the
#   fracking-message experiment variables, birth year (Q16.5.0 is hand-recoded in the syntax), party/ideology (no value
#   labels in the file).
# Recode check: for every shipped item the authors' renamed variable (hot-decked, so only compared where the raw cell is
#   observed) must equal the raw column after the syntax's reverse recode; asserted below. Items the authors reverse-key
#   in their composites are flagged REV and NOT flipped here: the table keeps the administered direction. Labels and
#   data agree (e.g. AOTFac_4/5 correlate ~0 or negatively with the other nine AOT items in the raw direction).
# Q6.2 is stored with irregular codes (1, 14, 11, 4, 5, 6, 12 for 1-7; value labels mark 1 = completely disagree and
#   12 = completely agree, 14 = 2, 11 = 3); mapped to 1-7 as the syntax does, without reversing.
# Covariate: cov_gender (Q16.2: 1 male, 2 female, 3 other; 4 prefer not to say -> blank).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none (no free text, IP, location or names in the shipped file); id is the 1..N row index.
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_K_2026-10-16"
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


# (item name, raw column, authors reverse-key it in their composite)
SCALES = {
    "aot": (range(1, 7), [
        ("AOTDog_1", "Q3.1_1", False), ("AOTDog_2", "Q3.1_4", False), ("AOTDog_3", "Q3.1_5", False), ("AOTDog_4", "Q3.1_7", False), ("AOTDog_5", "Q3.1_8", False), ("AOTDog_6", "Q3.1_10", False), ("AOTFac_1", "Q3.1_9", False), ("AOTFac_2", "Q3.1_11", False), ("AOTFac_3", "Q3.1_12", False), ("AOTFac_4", "Q3.1_13", True), ("AOTFac_5", "Q3.1_14", True)]),
    "nfc": (range(1, 6), [
        ("NFC_1", "Q3.2_1", True), ("NFC_2", "Q3.2_2", False), ("NFC_3", "Q3.2_3", True), ("NFC_4", "Q3.2_4", True), ("NFC_5", "Q3.2_5", True), ("NFC_6", "Q3.2_6", False), ("NFC_7", "Q3.2_7", True), ("NFC_8", "Q3.2_8", True), ("NFC_9", "Q3.2_9", True), ("NFC_10", "Q3.2_10", False), ("NFC_11", "Q3.2_11", False), ("NFC_12", "Q3.2_12", True), ("NFC_13", "Q3.2_13", False), ("NFC_14", "Q3.2_14", True), ("NFC_15", "Q3.2_15", True), ("NFC_16", "Q3.2_16", False)]),
    "need_for_affect": (range(1, 6), [
        ("NAff_1", "Q3.3_1", True), ("NAff_2", "Q3.3_2", True), ("NAff_3", "Q3.3_26", False), ("NAff_4", "Q3.3_3", False), ("NAff_5", "Q3.3_4", False), ("NAff_6", "Q3.3_5", False), ("NAff_7", "Q3.3_6", False), ("NAff_8", "Q3.3_7", True), ("NAff_9", "Q3.3_9", True), ("NAff_10", "Q3.3_10", True), ("NAff_11", "Q3.3_8", True), ("NAff_12", "Q3.3_11", True), ("NAff_13", "Q3.3_12", False), ("NAff_14", "Q3.3_13", True), ("NAff_15", "Q3.3_14", False), ("NAff_16", "Q3.3_15", True), ("NAff_17", "Q3.3_16", False), ("NAff_18", "Q3.3_17", False), ("NAff_19", "Q3.3_18", False), ("NAff_20", "Q3.3_19", False), ("NAff_21", "Q3.3_20", True), ("NAff_22", "Q3.3_21", True), ("NAff_23", "Q3.3_22", True), ("NAff_24", "Q3.3_23", False), ("NAff_25", "Q3.3_24", True), ("NAff_26", "Q3.3_25", False)]),
    "need_for_closure": (range(1, 7), [
        ("NFClo_1", "Q3.4_1", False), ("NFClo_2", "Q3.4_2", False), ("NFClo_3", "Q3.4_3", False), ("NFClo_4", "Q3.4_4", False), ("NFClo_5", "Q3.4_5", False), ("NFClo_6", "Q3.4_6", False), ("NFClo_7", "Q3.4_7", False), ("NFClo_8", "Q3.4_8", False), ("NFClo_9", "Q3.4_9", False), ("NFClo_10", "Q3.4_10", False), ("NFClo_11", "Q3.4_11", False), ("NFClo_12", "Q3.4_12", False), ("NFClo_13", "Q3.4_13", False), ("NFClo_14", "Q3.4_14", False), ("NFClo_15", "Q3.4_15", False)]),
    "moralized_rationality": (range(1, 8), [
        ("MoRat_1", "Q6.2_1", False), ("MoRat_2", "Q6.2_2", False), ("MoRat_3", "Q6.2_3", False), ("MoRat_4", "Q6.2_4", False), ("MoRat_5", "Q6.2_5", False), ("MoRat_6", "Q6.2_6", False), ("MoRat_7", "Q6.2_7", False), ("MoRat_8", "Q6.2_8", True), ("MoRat_9", "Q6.2_9", True)]),
    "epistemic_beliefs": (range(1, 6), [
        ("FaInt_1", "Q6.3_1", False), ("FaInt_2", "Q6.3_2", False), ("FaInt_3", "Q6.3_3", False), ("FaInt_4", "Q6.3_4", False), ("NFEv_1", "Q6.3_5", False), ("NFEv_2", "Q6.3_6", False), ("NFEv_3", "Q6.3_7", False), ("NFEv_4", "Q6.3_8", False), ("TruPol_1", "Q6.3_9", False), ("TruPol_2", "Q6.3_10", False), ("TruPol_3", "Q6.3_11", False), ("TruPol_4", "Q6.3_12", False)]),
}
Q62_MAP = {1: 1, 14: 2, 11: 3, 4: 4, 5: 5, 6: 6, 12: 7}


def main() -> None:
    import pyreadstat
    p = dv_fetch("10.7910/DVN/ED8ZOO", "rp_dataset_042019_2.tab", RAW_ROOT / "ed8zoo")
    d, _ = pyreadstat.read_sav(str(p))
    d = d.reset_index(drop=True)
    assert d.shape == (1129, 468)
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Q16.2"].where(d["Q16.2"].isin([1, 2, 3])).astype("Int64")
    out = {}
    for key, (levels, items) in SCALES.items():
        frames = []
        for name, col, rev in items:
            raw = d[col].astype(float)
            if col.startswith("Q6.2"):
                assert raw.dropna().isin(Q62_MAP).all(), col
                raw = raw.map(Q62_MAP)
            assert raw.dropna().isin(list(levels)).all(), (col, raw.dropna().unique())
            # authors' renamed (hot-decked, reverse-recoded where flagged) variable must agree where raw is observed
            ref = d[name].astype(float)
            top = max(levels) + 1
            exp = (top - raw) if rev else raw
            ok = raw.notna()
            assert (exp[ok] == ref[ok]).all(), (name, col)
            frames.append(pd.DataFrame({"id": d["id"], "item": name, "resp": raw, "cov_gender": d["cov_gender"]}))
        t = pd.concat(frames, ignore_index=True)
        t = t[t["resp"].notna()].copy()
        t["resp"] = t["resp"].astype(int)
        order = {n: i for i, (n, _, _) in enumerate(items)}
        t = t.sort_values(["id", "item"], key=lambda s: s.map(order) if s.name == "item" else s).reset_index(drop=True)
        pv = {n: set(levels) for n, _, _ in items}
        out[f"eichmeier_2019_{key}"] = (t, pv)
    emit(out)


if __name__ == "__main__":
    main()
