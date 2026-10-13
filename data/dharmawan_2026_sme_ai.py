#!/usr/bin/env python3
# Source: https://zenodo.org/records/22146767
# DOI: 10.5281/zenodo.22146767 (dataset; the record names no paper)
#   Dharmawan, F., & Sumana, H. (2026). SME Research Questionnaire - AI Capability [Data
#   set]. Zenodo.
# Data: "SME Research Questionnaire - AI Capability.xlsx", sheet "Copy of Gabungan": 500
#       Indonesian SME respondents x 40 six-point items whose headers are construct codes
#       (HCL1-8, OA1-6, SP1-6, GHRM1-4, EP1-4, AC1-6, GPI1-6). No demographics, no codebook
#       and no description on the record; the codes are the only documentation, so each
#       prefix block ships as its own table under its code.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. The headers are codes, the sheet has no stems and the record
#   ships no questionnaire.
#
# Tables (item = the sheet header; 1-6 on every item):
#   dharmawan_2026_hcl    HCL1-HCL8      dharmawan_2026_oa    OA1-OA6
#   dharmawan_2026_sp     SP1-SP6        dharmawan_2026_ghrm  GHRM1-GHRM4
#   dharmawan_2026_ep     EP1-EP4        dharmawan_2026_ac    AC1-AC6
#   dharmawan_2026_gpi    GPI1-GPI6
#   (GHRM / EP / GPI read as green HRM, environmental performance, green product
#   innovation; AC as AI capability; HCL, OA, SP are undocumented.)
# Covariates: none in the file.
# id: the sheet's row number (1..500), shared across the seven tables.

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.22146767"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = "SME Research Questionnaire - AI Capability.xlsx"
URL = "https://zenodo.org/api/records/22146767/files/" + requests.utils.quote(FNAME) + "/content"
P = "dharmawan_2026_"
BLOCKS = {"HCL": 8, "OA": 6, "SP": 6, "GHRM": 4, "EP": 4, "AC": 6, "GPI": 6}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


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
    d = pd.read_excel(download(URL, RAW_DIR / FNAME), "Copy of Gabungan")
    d.columns = [str(c).strip() for c in d.columns]
    expected = [f"{b}{k}" for b, n in BLOCKS.items() for k in range(1, n + 1)]
    assert len(d) == 500 and list(d.columns) == expected, list(d.columns)
    d["id"] = range(1, len(d) + 1)
    out = {}
    for block, n in BLOCKS.items():
        items = [f"{block}{k}" for k in range(1, n + 1)]
        t = d.melt(id_vars=["id"], value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 6).all(), (block, t["resp"].unique())
        t = t[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + block.lower()] = (t, {i: set(range(1, 7)) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
