#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/32576487
# DOI: 10.6084/m9.figshare.32576487.v1 (dataset; the record names no paper)
#   Zhang, Z. (2026). DATA BASE Emotional Companion AI User Experience and Behavior Survey
#   Questionnaire [Data set]. figshare.
# Data: "DATA BASE Emotional Companion AI User Experience and Behavior Survey
#       Questionnaire.xlsx.xlsx", one sheet: 615 users of a conversational AI (surveyed
#       July 2025) x 40 columns. Headers 10-36 are the 27 Likert statements (1-5) in
#       English; headers 1-9 are usage and demographic questions. The numbering uses the
#       Chinese enumeration comma ("10、") and one stem ends with a Chinese full stop, so the
#       administration was most likely in Chinese; the Chinese wording is not in the
#       deposit. No codebook; the record has no description.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped (the English column headers as an English substitute for a Chinese
#   administration -- language=Chinese with empty _translated columns; the anchors are not
#   in the file, so option_text is blank; built by
#   automated_finding/itemtext_verification/make_itemtext_zhang_2026.py).
#
# Tables (item = q<k> for header "<k>、...", k = 10..36; stems() returns the header text):
#   zhang_2026_ai_companion   27 statements on attachment, satisfaction, loyalty, emotional
#                             benefit, trust, AI anxiety, privacy and algorithm awareness,
#                             1-5 (q18 is marked reverse-coded in its header; stored as
#                             deposited).
# Skipped: the AI product used, interaction frequency / duration, modality checkboxes,
#   submission time.
# Covariates: cov_gender (1-2), cov_age_group (2-6), cov_education (1-5), cov_field (1-6),
#   cov_region (1-4), cov_ai_product (1-4), all as coded in the deposit (no labels).
# id: the deposit's "No" (its response number).

import os
import re
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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.6084_m9.figshare.32576487.v1"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = "DATA BASE Emotional Companion AI User Experience and Behavior Survey Questionnaire.xlsx.xlsx"
T = "zhang_2026_ai_companion"
COVMAP = {2: "cov_gender", 3: "cov_age_group", 4: "cov_education", 5: "cov_field",
          6: "cov_region", 1: "cov_ai_product"}
COVS = ["cov_gender", "cov_age_group", "cov_education", "cov_field", "cov_region", "cov_ai_product"]


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        j = requests.get("https://api.figshare.com/v2/articles/32576487", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        download(url, p)
    return p


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any()
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


def numbered() -> dict:
    """question number -> (column header, stem without its number)."""
    out = {}
    for c in pd.read_excel(fetch(), nrows=0).columns:
        m = re.match(r"^(\d+)[、.]\s*(.*)$", str(c).strip(), re.S)
        if m and int(m.group(1)) not in out:
            out[int(m.group(1))] = (c, " ".join(m.group(2).split()))
    return out


def stems() -> list:
    """[(item code, stem)] for the 27 Likert statements, header order."""
    n = numbered()
    return [(f"q{k}", n[k][1]) for k in range(10, 37)]


def main() -> None:
    d = pd.read_excel(fetch())
    n = numbered()
    assert len(d) == 615 and d["No"].is_unique
    w = pd.DataFrame({"id": d["No"].astype(int)})
    for k, cov in COVMAP.items():
        w[cov] = pd.to_numeric(d[n[k][0]], errors="coerce").astype("Int64")
    items = []
    for k in range(10, 37):
        w[f"q{k}"] = d[n[k][0]]
        items.append(f"q{k}")
    t = w.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
    emit({T: (t, {i: set(range(1, 6)) for i in items})})


if __name__ == "__main__":
    main()
