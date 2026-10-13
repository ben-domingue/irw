#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/24156723
# DOI: 10.1002/acp.70045
#   Frost, P., Simard, A., Iraci, M., & Stack, M. (2025). Cognitive Biases Associated With
#   Specific and Generalized Beliefs in Conspiracy Theory. Applied Cognitive Psychology.
#   Data: Frost, P. (2023). Cognitive Biases Associated with Conspiracy Theory Belief Item
#   [Data set]. figshare, 10.6084/m9.figshare.24156723.v1.
# Data: "Conspiracy Beliefs and Cognition Data 2023 Final Version.csv": 213 rows (200 with
#       responses) x 57 columns: the 30 items of the Cognitive Biases Questionnaire for
#       psychosis (Q1-Q30, 1-3), the 15-item Generic Conspiracist Beliefs scale
#       (Q1_1-Q1_15, 1-5), the seven bias subscale means, gender, education, a diagnosis
#       question. A handful of cells are 0 on these 1-based scales (one per item at most)
#       and are dropped as non-responses. No codebook or item wording in the deposit.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. The headers are positional (Q1 .. Q30, Q1_1 .. Q1_15) and the
#   deposit has no codebook; the CBQ and GCBS wording would come from the published
#   instruments.
#
# Tables (item = the deposit's header; the GCBS codes keep the Q1_ prefix):
#   frost_2023_cbq    Q1-Q30, Cognitive Biases Questionnaire for psychosis, 1-3.
#   frost_2023_gcbs   Q1_1-Q1_15, Generic Conspiracist Beliefs scale, 1-5.
# Skipped: the bias subscale means and Average Conspiracy Score (composites), the
#   diagnosis question.
# Covariates: cov_gender (the deposit's free text, trimmed), cov_education (1-5 as coded).
# id: the file's row number (1..213; rows with no responses vanish in the melt).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.6084_m9.figshare.24156723.v1"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = "Conspiracy Beliefs and Cognition Data 2023 Final Version.csv"
P = "frost_2023_"
CBQ = [f"Q{k}" for k in range(1, 31)]
GCBS = [f"Q1_{k}" for k in range(1, 16)]
BLOCKS = {"cbq": (CBQ, range(1, 4)), "gcbs": (GCBS, range(1, 6))}
COVS = ["cov_gender", "cov_education"]


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
        j = requests.get("https://api.figshare.com/v2/articles/24156723", headers=UA, timeout=120).json()
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


def main() -> None:
    d = pd.read_csv(fetch())
    assert len(d) == 213
    d["id"] = range(1, len(d) + 1)
    gcol = [c for c in d.columns if c.startswith("Q4What is your gender")][0]
    ecol = [c for c in d.columns if c.startswith("Q6Select your highest")][0]
    d["cov_gender"] = d[gcol].astype(str).str.strip().replace({"nan": pd.NA})
    d["cov_education"] = pd.to_numeric(d[ecol], errors="coerce").astype("Int64")
    out = {}
    for block, (items, valid) in BLOCKS.items():
        t = d.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        zero = t["resp"] == 0
        print(f"  [{block}] dropped {zero.sum()} zero cells (off-scale) of {len(t)}")
        t = t[~zero]
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, (block, bad["resp"].value_counts().to_dict())
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + block] = (t, {i: set(valid) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
