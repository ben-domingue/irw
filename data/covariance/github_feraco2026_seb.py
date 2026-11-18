"""Covariance family (irw_cov, source = "cov"): Living SEB Skills Project matrices.

Source: GitHub feracotommaso/living_SEB_review, pinned at commit
ee8e208830b28ef779d4e98367730f8e931d8307 (Feraco, Calderan & Pellegrino, 2026,
European Journal of Personality, https://doi.org/10.1177/08902070261467477).
Licence: the curated dataset under data/ is CC BY 4.0 (README "Licensing" table;
LICENSE-PROCESSED-DATA is the CC BY 4.0 legal code).

The review team computed these Pearson matrices themselves from the primary
studies' open raw data (data/3.1opendata_to_cor.R, `cor(x, use =
"pairwise.complete")`, written with writexl at full double precision; 0145a and
0150a by scripts/extraction/articles/*.R). They are not the matrices printed in
the primary papers. Files read (never executed):
- data/3.meta_data/matrices/<id>.xlsx (headers = variable names, row i is
  variable i) or <id>.csv where the repo has a CSV (CSV is canonical there);
- data/3.meta_data/coding/records.csv: the sample N (`n`) and citation per matrix;
- data/3.meta_data/pair_n/<id>.csv: pairwise n per cell, where given (0145a, 0150a).

Matrices left out: extracted from the primary paper rather than computed
(0087a, 0128a, 0138a, 0141a), and 0104a (no records row; review-only for data
quality, config/coding/matrix_exclusions.csv).

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per matrix id. Values unchanged.

Usage: python3 data/covariance/github_feraco2026_seb.py <out dir>
"""
import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import openpyxl

SHA = "ee8e208830b28ef779d4e98367730f8e931d8307"
BASE = f"https://raw.githubusercontent.com/feracotommaso/living_SEB_review/{SHA}/"
TABLE = "feraco_2026_seb"
IDS = ["0013a", "0018a", "0018b", "0026a", "0030a", "0030b", "0034a", "0035a", "0043a",
       "0045a", "0048a", "0049a", "0050a", "0050b", "0053c", "0053d", "0053e", "0053f",
       "0053g", "0068a", "0070a", "0071a", "0080a", "0095a", "0100a", "0107a", "0108a",
       "0118a", "0120a", "0120b", "0126a", "0132a", "0134a", "0145a", "0150a"]
CSV_IDS = {"0132a", "0145a", "0150a"}
PAIR_IDS = {"0145a", "0150a"}


def get(path):
    return subprocess.run(["curl", "-4", "-sfL", "--max-time", "120", "--retry", "4", "--retry-all-errors", BASE + path],
                          check=True, capture_output=True).stdout


def num(x):
    if x is None or (isinstance(x, str) and x.strip() in ("", "NA")):
        return None
    if isinstance(x, bool):
        raise SystemExit(f"boolean cell {x}")
    return float(x)


def read_matrix(mid):
    if mid in CSV_IDS:
        rows = list(csv.reader(io.StringIO(get(f"data/3.meta_data/matrices/{mid}.csv").decode("utf-8"))))
        V = rows[0][1:]
        if [r[0] for r in rows[1:]] != V:
            raise SystemExit(f"{mid}: row and column names differ")
        M = [[num(c) for c in r[1:]] for r in rows[1:]]
    else:
        ws = openpyxl.load_workbook(io.BytesIO(get(f"data/3.meta_data/matrices/{mid}.xlsx")),
                                    read_only=True, data_only=True).worksheets[0]
        rows = list(ws.iter_rows(values_only=True))
        V = [str(v) for v in rows[0]]
        M = [[num(c) for c in r] for r in rows[1:]]
    if len(M) != len(V) or any(len(r) != len(V) for r in M):
        raise SystemExit(f"{mid}: not square")
    return V, M


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rec = {r["matrix_id"]: r for r in csv.DictReader(io.StringIO(
        get("data/3.meta_data/coding/records.csv").decode("utf-8")))}
    long, records, held = [], [], []
    for mid in IDS:
        r = rec[mid]
        N = int(r["n"])
        V, M = read_matrix(mid)
        K = len(V)
        pn = {}
        if mid in PAIR_IDS:
            for p in csv.DictReader(io.StringIO(get(f"data/3.meta_data/pair_n/{mid}.csv").decode("utf-8"))):
                pn[frozenset((p["var1"], p["var2"]))] = int(p["n"])
        if any(M[i][j] != M[j][i] for i in range(K) for j in range(K)):
            raise SystemExit(f"{mid}: not symmetric")
        keep = [i for i in range(K) if any(M[i][x] is not None for x in range(K) if x != i)]
        dropped = [V[i] for i in range(K) if i not in keep]
        bad = [(V[i], V[x]) for a, i in enumerate(keep) for x in keep[:a]
               if M[i][x] is None or abs(M[i][x]) >= 1]
        if bad or any(M[i][i] != 1 for i in keep):
            held.append({"group": mid, "cells": bad[:5]})
            continue
        for a, i in enumerate(keep):
            for x in keep[:a + 1]:
                n = N if i == x or mid not in PAIR_IDS else pn[frozenset((V[i], V[x]))]
                long.append({"stat": "cor", "var1": V[i], "var2": V[x],
                             "value": "1" if i == x else repr(M[i][x]), "n": n, "group": mid})
        ns = [l["n"] for l in long if l["group"] == mid and l["var1"] != l["var2"]]
        records.append({"group": mid, "n_obs": N, "pair_n": [min(ns), max(ns)] if mid in PAIR_IDS else None,
                        "n_vars": len(keep), "dropped": dropped, "doi": r["doi"],
                        "author_et_al": r["author_et_al"], "year": r["year"],
                        "title": r["title"], "journal": r["journal"], "open_data": r["open_data"],
                        "country": r["country"], "age_class": r["age_class"], "age": r["age"]})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} matrices built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 github_feraco2026_seb.py <out dir>")
    main(sys.argv[1])
