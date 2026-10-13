#!/usr/bin/env python3
# Source: https://zenodo.org/records/8406719
# DOI: 10.5281/zenodo.8406719 (dataset; the record names no paper)
#   Makkiyah, F. A. (2023). Not just motivation, but also self-regulated learning affected
#   the academic achievement of Indonesian medical students [Data set]. Zenodo.
# Data: "20082023 data responden - 2.xlsx", sheet "TOTAL": 211 Indonesian medical students
#       (18-23) x four questionnaires whose column headers are the Indonesian item
#       statements: a 50-item self-regulated learning scale (MSLQ learning-strategies
#       items, 1-5), an 18-item learning-motivation scale (MSLQ motivation items, 1-5), the
#       10-item General Self-Efficacy Scale (1-4) and a 16-item emotional-intelligence scale
#       (WLEIS wording, 1-5). The header row is the second row of the sheet. The per-scale
#       detail sheets carry empty "Nama" / "NIM" columns (no names or student numbers are
#       filled in). No codebook; the headers are the documentation.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (Indonesian stems from the column headers; IRW's own English
#   translation in the _translated columns; the anchors are not in the file, so option_text
#   is blank; built by automated_finding/itemtext_verification/make_itemtext_makkiyah_2023.py).
#
# Tables (item codes are <block>_<k> in header order; stems() returns the header text for
#   each code, which the item text builder imports):
#   makkiyah_2023_srl          srl_1-srl_50, 1-5
#   makkiyah_2023_motivation   mot_1-mot_18, 1-5
#   makkiyah_2023_gse          gse_1-gse_10, 1-4
#   makkiyah_2023_eq           eq_1-eq_16, 1-5
# Skipped: the TOTAL / Kategori columns per scale, IPK (GPA; kept as a covariate).
# Covariates: cov_sex (1 laki-laki/male, 2 perempuan/female, the deposit's code),
#   cov_age, cov_semester (semester completed), cov_gpa (IPK, 0-4 scale).
# id: the sheet's row number (1..211).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.8406719"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = "20082023 data responden - 2.xlsx"
URL = "https://zenodo.org/api/records/8406719/files/" + requests.utils.quote(FNAME) + "/content"
P = "makkiyah_2023_"
# block -> (column positions in the TOTAL sheet, valid range)
BLOCKS = {"srl": (range(5, 55), range(1, 6)), "mot": (range(57, 75), range(1, 6)),
          "gse": (range(77, 87), range(1, 5)), "eq": (range(89, 105), range(1, 6))}
NAMES = {"srl": "srl", "mot": "motivation", "gse": "gse", "eq": "eq"}
COVS = ["cov_sex", "cov_age", "cov_semester", "cov_gpa"]


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


def load() -> pd.DataFrame:
    d = pd.read_excel(download(URL, RAW_DIR / FNAME), "TOTAL", header=1)
    assert len(d) == 211, len(d)
    return d


def stems(block: str) -> list:
    """[(item code, header text)] for a block, in questionnaire order; the header's leading
    'k.' number is kept as written (one item reads '16,')."""
    cols = list(load().columns)
    pos, _ = BLOCKS[block]
    out = []
    for k, i in enumerate(pos, 1):
        h = " ".join(str(cols[i]).split())
        assert h[:2].rstrip(".,") == str(k) or h.split(".")[0].split(",")[0] == str(k), (block, k, h)
        out.append((f"{block}_{k}", h))
    return out


def main() -> None:
    d = load()
    cols = list(d.columns)
    assert cols[0] == "Jenis Kelamin" and cols[107] == "IPK", (cols[0], cols[107])
    base = pd.DataFrame({"id": range(1, len(d) + 1),
                         "cov_sex": pd.to_numeric(d[cols[1]], errors="coerce").astype("Int64"),
                         "cov_age": pd.to_numeric(d[cols[2]], errors="coerce").astype("Int64"),
                         "cov_semester": pd.to_numeric(d[cols[3]], errors="coerce").astype("Int64"),
                         "cov_gpa": pd.to_numeric(d[cols[107]], errors="coerce")})
    out = {}
    for block, (pos, valid) in BLOCKS.items():
        codes = stems(block)
        w = base.copy()
        for (code, _), i in zip(codes, pos):
            w[code] = pd.to_numeric(d[cols[i]], errors="coerce")
        items = [c for c, _ in codes]
        t = w.melt(id_vars=["id"] + COVS, value_vars=items, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, (block, bad["resp"].value_counts().to_dict())
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        out[P + NAMES[block]] = (t, {i: set(valid) for i in items})
    emit(out)


if __name__ == "__main__":
    main()
