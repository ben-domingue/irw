#!/usr/bin/env python3
# Source: https://zenodo.org/records/17023586
# DOI: 10.5281/zenodo.17023586 (dataset; the record names no paper)
#   Karsen, M. (2025). MOOC Motivation [Data set]. Zenodo.
# Data: "Final-Questionnaire-MOOC Motivation (Responses)_Lengkap_Pernah ikut MOOC_396_
#       bersihin pertanyaan.xlsx", one sheet of 396 Indonesian respondents who had taken a
#       MOOC x 61 Likert items (1-5) whose headers are construct codes: SE1-5, SJ1-5, SD1-5,
#       SI1-7, MC1-5, GA1-5, GS1-5, CC1-5, IM1-9, EM1-5, MCO1-5. No demographics, no
#       codebook, no description on the record; the codes are the only documentation, so
#       the blocks are shipped together as one table rather than split under guessed names.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. The headers are codes (SE1 ...), the sheet has no stems and the
#   record ships no questionnaire.
#
# Tables (item = the sheet header):
#   karsen_2025_mooc_motivation   61 items in eleven prefix blocks (SE, SJ, SD, SI, MC, GA,
#                                 GS, CC, IM, EM, MCO), 1-5. IM/EM read as intrinsic /
#                                 extrinsic motivation; the other codes are undocumented.
# Covariates: none in the file.
# id: the sheet's row number (1..396).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.17023586"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = ("Final-Questionnaire-MOOC Motivation (Responses)_Lengkap_Pernah ikut MOOC_396_"
         "bersihin pertanyaan.xlsx")
URL = "https://zenodo.org/api/records/17023586/files/" + requests.utils.quote(FNAME) + "/content"
T = "karsen_2025_mooc_motivation"
BLOCKS = {"SE": 5, "SJ": 5, "SD": 5, "SI": 7, "MC": 5, "GA": 5, "GS": 5, "CC": 5, "IM": 9,
          "EM": 5, "MCO": 5}
ITEMS = [f"{b}{k}" for b, n in BLOCKS.items() for k in range(1, n + 1)]


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
    d = pd.read_excel(download(URL, RAW_DIR / FNAME))
    d.columns = [str(c).strip() for c in d.columns]   # "SD1 " and "SI4   ..." carry stray spaces
    assert len(d) == 396 and list(d.columns) == ITEMS, list(d.columns)
    d["id"] = range(1, len(d) + 1)
    t = d.melt(id_vars=["id"], value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    t = t[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)
    emit({T: (t, {i: set(range(1, 6)) for i in ITEMS})})


if __name__ == "__main__":
    main()
