"""Covariance family (irw_cov, source = "cov"): Zhang, Zhang, Schwarzer & Hagger (2019) HAPA MASEM.

Source: OSF project 5nfqs, "A Meta Analysis of the Health Action Process
Approach" (Zhang, C.-Q., Zhang, R., Schwarzer, R., & Hagger, M. S., Health
Psychology, 38(7), 623-637, https://doi.org/10.1037/hea0000728).
Licence: CC BY 4.0 (stated on the node).

Three deposit files are read:
- "MetaSEM analysis/Data files/hapa_data_full_pb.txt": the 108 study
  correlation matrices of the full model with past behaviour, one per line, as
  metaSEM stacked vectors (lower triangle with diagonal, column by column) over
  PB, B, ASE, MSE, RSE, OE, RP, INT, AP, CP (the names in the analysis script).
  The other analysis files (hapa_data_full.txt etc.) are subsets of these
  variables with identical values.
- "MetaSEM analysis/R analysis scripts/METASEM R script hapa_full_pb.txt": the
  sample size vector `n` (same order) and `var.names`. The file is R code; it
  is parsed as TEXT and never run.
- "Master data files/hapa_data_full.xlsx": the coding sheet, used only for each
  study's label and behaviour. Each analysed matrix is matched to a sheet row
  by n and all 55 stacked values.

A variable with no correlation in a study was not measured there and is
dropped (Ben, 2026-11-17). A pair between two measured variables that the
study did not report is written as a row with an empty value (blank cells
allowed, Ben, 2026-11-18); a study with fewer than two measured variables or
an off-diagonal |r| >= 1 is held and listed in records.json.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per study (the sheet's label).
Modification (2026-11-18): unreported pairs among measured variables are
written as empty values instead of holding the study.

Usage: python3 data/covariance/osf_zhang2019_hapa.py <out dir>
"""
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

import openpyxl

NODE = "5nfqs"
FILES = {"mat": "hapa_data_full_pb.txt",
         "code": "METASEM R script hapa_full_pb.txt",
         "sheet": "hapa_data_full.xlsx"}
TABLE = "zhang_2019_hapa10"
V = ["PB", "B", "ASE", "MSE", "RSE", "OE", "RP", "INT", "AP", "CP"]
K = len(V)
L = K * (K + 1) // 2


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def listing(url):
    out = []
    while url:
        d = json.loads(get(url))
        out += d["data"]
        url = d["links"].get("next")
    return out


def fetch():
    """Walk the node's folders and download the three files by name."""
    found, todo = {}, [f"https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/"]
    while todo and len(found) < len(FILES):
        for f in listing(todo.pop()):
            a = f["attributes"]
            if a["kind"] == "folder":
                todo.append(f["relationships"]["files"]["links"]["related"]["href"])
            elif a["name"] in FILES.values():
                found[a["name"]] = get(f["links"]["download"])
    return {k: found[v] for k, v in FILES.items()}


def unstack(vals):
    M = [[None] * K for _ in range(K)]
    it = iter(vals)
    for c in range(K):
        for r in range(c, K):
            M[r][c] = M[c][r] = next(it)
    return M


def num(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return float(x)
    try:
        return float(str(x).strip())
    except ValueError:
        return None


def same(text_vals, cells):
    return all((t == "NA") == (num(v) is None) and (t == "NA" or abs(float(t) - num(v)) < 1e-9)
               for t, v in zip(text_vals, cells))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw = fetch()
    lines = [l.split() for l in raw["mat"].decode("utf-8").splitlines() if l.strip()]
    if any(len(l) != L for l in lines):
        raise SystemExit("a line is not a 10-variable stacked vector")
    code = raw["code"].decode("utf-8")
    names = re.findall(r'"([^"]+)"', re.search(r"^var\.names <-\s*c\(([^)]*)\)", code, re.M).group(1))
    if names != V:
        raise SystemExit(f"variable names changed: {names}")
    n = [int(x) for x in re.search(r"^n <-\s*c\(([^)]*)\)", code, re.M).group(1).split(",")]
    if len(n) != len(lines):
        raise SystemExit(f"{len(lines)} matrices but {len(n)} sample sizes")

    ws = openpyxl.load_workbook(io.BytesIO(raw["sheet"]), read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr = list(rows[0])
    beh = hdr.index("behaviour")
    first = hdr.index("pb_beh") - 1           # the PB diagonal precedes pb_beh
    studies = [r for r in rows[1:] if r[0]]
    used = set()

    long, records, held = [], [], []
    for s, (vals, ni) in enumerate(zip(lines, n)):
        hits = [j for j, r in enumerate(studies)
                if j not in used and r[1] == ni and same(vals, r[first:first + L])]
        if not hits:
            raise SystemExit(f"matrix {s + 1}: no matching row in the sheet")
        j = hits[0]
        used.add(j)
        r = studies[j]
        label = re.sub(r"\s+", " ", str(r[0])).strip()
        if any(rec["group"] == label for rec in records) or label in [h[0] for h in held]:
            raise SystemExit(f"duplicate label {label}")
        M = unstack(vals)
        if any(float(M[i][i]) != 1 for i in range(K)):
            raise SystemExit(f"{label}: diagonal is not 1")
        keep = list(range(K))
        while True:   # drop variables with no reported cell among those still kept
            k2 = [i for i in keep if any(M[i][x] != "NA" for x in keep if x != i)]
            if k2 == keep:
                break
            keep = k2
        dropped = [V[i] for i in range(K) if i not in keep]
        cells = [M[i][x] for a, i in enumerate(keep) for x in keep[:a]]
        if len(keep) < 2 or all(c == "NA" for c in cells):
            held.append((label, "fewer than two measured variables"))
            continue
        if any(c != "NA" and abs(float(c)) >= 1 for c in cells):
            held.append((label, "|r| >= 1"))
            continue
        for a, i in enumerate(keep):
            for x in keep[:a + 1]:
                long.append({"stat": "cor", "var1": V[i], "var2": V[x],
                             "value": "1" if i == x else ("" if M[i][x] == "NA" else M[i][x]),
                             "n": ni, "group": label})
        records.append({"group": label, "n_obs": ni, "dropped": dropped,
                        "n_blank": cells.count("NA"),
                        "behaviour": re.sub(r"\s+", " ", str(r[beh] or "")).strip()})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} studies built, {len(held)} held")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_zhang2019_hapa.py <out dir>")
    main(sys.argv[1])
