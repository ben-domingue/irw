#!/usr/bin/env python3
# Source: https://zenodo.org/records/20494091
# DOI: 10.5281/zenodo.20494091 (dataset; the record names no paper)
#   Wunn, N., Fitting, N., & Seibert, J.-N. (2026). Research competence, intrinsic
#   motivation, and cognitive load of high school students after their participation in a
#   student laboratory using the IBL or GBIL approach [Data set]. Zenodo.
# Data: "DataSheet_ResearchCompetence_ IntrinsicMotivation_ CognitiveLoad.xlsx": sheet
#       "Datenpunkte" with 170 German upper-secondary students (14-20) in an experimental
#       (EG, inquiry-based) or control (KG, guided inquiry) student-lab group; a 27-item
#       research-competence self-assessment before (RKV/MKV/RFV/KKV/FWV, 1-4) and after
#       (RKN/...) the lab, matched on the pseudonymous Code; a 12-item Intrinsic Motivation
#       Inventory short form (IV, WK, WW, DA; 1-5) and an 8-item cognitive-load scale
#       (ICL, GCL, ECL; 1-5) after the lab. Sheet "Items" gives every item's English and
#       German wording; the response anchors are documented in the deposit's
#       Documentation PDF, not in the sheet. Trailing summary rows ("N = 170") are dropped.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (German stems and their English rendering from the deposit's "Items"
#   sheet; anchors not in the sheet, so option_text is left blank; built by
#   automated_finding/itemtext_verification/make_itemtext_wunn_2026.py).
#
# Tables (item = the sheet's code with the pre/post letter removed and brackets dropped,
#   e.g. "RKV[RK01]" / "RKN[RK01]" -> RK01; treat = 1 EG, 0 KG):
#   wunn_2026_research_competence   27 items (RK01-04, MK01-10, RF01-04, KK1-5, FW1-4), 1-4,
#                                   wave 1 = before the lab, 2 = after.
#   wunn_2026_imi                   IV01-03, WK01-03, WW01-03, DA01-03 (interest/enjoyment,
#                                   perceived competence, perceived choice, pressure), 1-5.
#   wunn_2026_cognitive_load        ICL1-2, GCL1-3, ECL1-3, 1-5.
# Skipped: the subscale means (FK_Pre .. FW_Post, Vergnügen, Kompetenz, Wahlfreiheit, Druck,
#   ICL, GCL, ECL).
# Covariates: cov_age, cov_sex (männlich / weiblich / divers / k.A. as deposited).
# id: the deposit's pseudonymous Code, case-normalised (the post-test block spells one code
#   "S1AiA25" against "S1AIA25"). The two blocks sit side by side in different row orders
#   and are joined on the code; post-test codes with no pre-test row are dropped (printed).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.20494091"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = "DataSheet_ResearchCompetence_ IntrinsicMotivation_ CognitiveLoad.xlsx"
URL = "https://zenodo.org/api/records/20494091/files/" + requests.utils.quote(FNAME) + "/content"
P = "wunn_2026_"
RC = ([f"RK0{k}" for k in range(1, 5)] + [f"MK{k:02d}" for k in range(1, 11)]
      + [f"RF0{k}" for k in range(1, 5)] + [f"KK{k}" for k in range(1, 6)] + [f"FW{k}" for k in range(1, 5)])
IMI = [f"{b}0{k}" for b in ("IV", "WK", "WW", "DA") for k in range(1, 4)]
CL = ["ICL1", "ICL2", "GCL1", "GCL2", "GCL3", "ECL1", "ECL2", "ECL3"]
COVS = ["cov_age", "cov_sex"]


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def raw() -> Path:
    return download(URL, RAW_DIR / FNAME)


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def code(col: str) -> str:
    """'RKV[RK01]' -> 'RK01', 'IV[IV01]' -> 'IV01', 'CL[ICL1]' -> 'ICL1'."""
    return col.split("[")[1].rstrip("]")


def items_sheet() -> dict:
    """code -> (English, German) from the deposit's Items sheet."""
    s = pd.read_excel(raw(), "Items", header=None)
    out = {}
    for _, r in s.iterrows():
        if isinstance(r[0], str) and "[" in r[0]:
            out[code(r[0])] = (" ".join(str(r[1]).split()), " ".join(str(r[2]).split()))
    return out


def main() -> None:
    d = pd.read_excel(raw(), "Datenpunkte")
    d.columns = [str(c).strip() for c in d.columns]   # "Alter " carries a trailing space
    pre_cols = [c for c in d.columns if c[:3] in ("RKV", "MKV", "RFV", "KKV", "FWV")]
    post_cols = [c for c in d.columns if c[:3] in ("RKN", "MKN", "RFN", "KKN", "FWN")]
    imi_cols = {c: code(c) for c in d.columns if c[:3] in ("IV[", "WK[", "WW[", "DA[")}
    cl_cols = {c: code(c) for c in d.columns if c.startswith("CL[")}
    assert sorted(code(c) for c in pre_cols) == sorted(code(c) for c in post_cols) == sorted(RC)
    assert sorted(imi_cols.values()) == sorted(IMI) and sorted(cl_cols.values()) == sorted(CL)
    # The sheet is two side-by-side blocks in different row orders: the pre-test block
    # (Gruppe, Code, Alter, Geschlecht, *V items) and the post-test block (Code.1, *N items,
    # IMI, cognitive load). They are joined on the pseudonymous code, not by row.
    pre = d[d["Gruppe"].isin(["EG", "KG"])].copy()
    assert len(pre) == 170, len(pre)
    pre["id"] = pre["Code"].str.upper().str.strip()
    assert pre["id"].is_unique
    pre["treat"] = (pre["Gruppe"] == "EG").astype(int)
    pre["cov_age"] = pd.to_numeric(pre["Alter"], errors="coerce").astype("Int64")
    pre["cov_sex"] = pre["Geschlecht"]
    base = pre[["id", "treat", *COVS]]
    post = d[d["Code.1"].notna() & ~d["Code.1"].astype(str).str.startswith("N =")].copy()
    post["id"] = post["Code.1"].astype(str).str.upper().str.strip()
    assert post["id"].is_unique, post["id"][post["id"].duplicated()]
    unmatched = set(post["id"]) - set(base["id"])
    print(f"  pre-test rows {len(pre)}, post-test rows {len(post)}, post codes without a pre row: {sorted(unmatched)}")
    post = post[post["id"].isin(base["id"])]
    pre_w = pre[["id", *pre_cols]].rename(columns={c: code(c) for c in pre_cols})
    post_w = post[["id", *post_cols]].rename(columns={c: code(c) for c in post_cols})
    parts = []
    for wave, w in ((1, pre_w), (2, post_w)):
        m = w.melt(id_vars=["id"], var_name="item", value_name="resp")
        m["wave"] = wave
        parts.append(m)
    rc = pd.concat(parts).merge(base, on="id")
    imi = post[["id", *imi_cols]].rename(columns=imi_cols).melt(id_vars=["id"], var_name="item", value_name="resp").merge(base, on="id")
    cl = post[["id", *cl_cols]].rename(columns=cl_cols).melt(id_vars=["id"], var_name="item", value_name="resp").merge(base, on="id")
    out = {}
    for name, t, items, valid in ((P + "research_competence", rc, RC, range(1, 5)),
                                  (P + "imi", imi, IMI, range(1, 6)),
                                  (P + "cognitive_load", cl, CL, range(1, 6))):
        t = t.dropna(subset=["resp"]).copy()
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, (name, bad["resp"].value_counts().to_dict())
        extra = ["wave", "treat"] if "wave" in t else ["treat"]
        t = t[["id", "item", "resp", *extra, *COVS]].sort_values(["id", *extra[:1], "item"]).reset_index(drop=True)
        out[name] = (t, {i: set(valid) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
