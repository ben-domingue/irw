"""Covariance family (irw_cov, source = "cov"): Wang (2026) AI use, dependency, critical thinking MASEM.

Source: Zenodo record 23688987 (https://doi.org/10.5281/zenodo.23688987),
"MASEM data" (Wang, 2026), CC BY 4.0: the coding table of a two-stage MASEM
whose manuscript is not named in the deposit (no paper found, 2026-11-17), so the
dataset is cited.

MASEM_Coding_Table_Final.xlsx:
- "Effect-Size Coding": one row per study and pair of U (AI use), D (AI
  dependency), CT (critical thinking) and LM (learning motivation), with
  r_original (as reported in the primary study), r_analyzed (after the
  meta-analyst reversed the sign of three D-CT rows) and Sample_n. r_original is
  used, so values are as published.
- "Study-Level Coding": region, object type (school level) per study.
- "Data Notes": abbreviations and exclusions.

Coverage is sparse (81 correlations over 31 studies). A study is built when it
reports every pair among the constructs it measured; a study with a missing
pair is not built and is printed. Values are kept as the stored text.

Modification (2026-11-17): pivoted from pairwise rows to the long lower-triangle
layout in data/covariance/README.md, one group per study (the deposit's Study_ID).

Usage: python3 data/covariance/zenodo_wang2026_aidependence.py <out dir>
"""
import csv
import io
import json
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

import openpyxl

URL = "https://zenodo.org/api/records/23688987/files/MASEM_Coding_Table_Final.xlsx/content"
TABLE = "wang_2026_aidependence4"
V = ["U", "D", "CT", "LM"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(io.BytesIO(get(URL)), read_only=True, data_only=True)
    study = {r[0]: r for r in list(wb["Study-Level Coding"].iter_rows(values_only=True))[1:] if r[0]}
    eff = defaultdict(dict)
    n = defaultdict(set)
    for r in list(wb["Effect-Size Coding"].iter_rows(values_only=True))[1:]:
        if not r[0]:
            continue
        a, b = str(r[1]).split("-")
        if a not in V or b not in V or a == b or frozenset((a, b)) in eff[r[0]]:
            raise SystemExit(f"{r[0]}: bad or repeated pair {r[1]}")
        v = str(r[2]).strip()
        float(v)
        eff[r[0]][frozenset((a, b))] = v
        n[r[0]].add(int(r[4]))
    long, records, held = [], [], []
    for sid, cells in eff.items():
        if len(n[sid]) != 1 or int(study[sid][5]) not in n[sid]:
            raise SystemExit(f"{sid}: sample sizes disagree {n[sid]} {study[sid][5]}")
        ni = n[sid].pop()
        v = [x for x in V if any(x in p for p in cells)]
        if len(cells) != len(v) * (len(v) - 1) // 2:
            held.append(sid)
            continue
        for a, i in enumerate(v):
            for j in v[:a + 1]:
                long.append({"stat": "cor", "var1": i, "var2": j,
                             "value": "1" if i == j else cells[frozenset((i, j))], "n": ni, "group": sid})
        s = study[sid]
        records.append({"group": sid, "n_obs": ni, "vars": v,
                        "population": f"object type {s[3]}, {s[2]}"})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / "records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} studies built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 zenodo_wang2026_aidependence.py <out dir>")
    main(sys.argv[1])
