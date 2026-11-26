"""Covariance family (irw_cov, source = "cov"): Berki et al. (2026) sport commitment MASEM.

Source: OSF project 7wa68, "Exploring the Determinants of Sport Commitment: A
comprehensive Review with Meta-Analytic Structural Equation Modeling", CC BY 4.0
(stated on the node); the paper is Berki, T., Kushihashi, M., Szantai, L., &
Piko, B. (2026), International Review of Sport and Exercise Psychology, 1-25,
https://doi.org/10.1080/1750984X.2026.2620706.

RAW_DATA.xlsx, sheet "Correlations", has one row per sample: study label, N,
mean age and the 21 correlations among EC, SE, VO, OP, PI_L, SC and SS_E in
columns named <var>_<var>. The deposit does not expand the abbreviations; they
are the Sport Commitment Model constructs (enthusiastic commitment, sport
enjoyment, valuable opportunities, other priorities, personal investments-loss,
social constraints, social support-emotional), and are kept as deposited.

A variable with no correlation in a sample was not measured there and is
dropped (Ben, 2026-11-17), repeating until every remaining variable has a
reported cell with another one. A pair between two variables the sample did measure
but did not report is written as a row with an empty value (Ben, 2026-11-18). A
sample with fewer than two measured variables, or an off-diagonal |r| >= 1, is
not built and is printed. Values are written in shortest round-trip form, i.e. as stored.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per sample (the sheet's label, whitespace
collapsed).
Modification (2026-11-18): unreported pairs among measured variables are empty
values instead of holding the sample (blank cells allowed, #3582).

Usage: python3 data/covariance/osf_berki2026_sportcommit.py <out dir>
"""
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

import openpyxl

NODE = "7wa68"
FILE = "RAW_DATA.xlsx"
SHEET = "Correlations"
TABLE = "berki_2026_sportcommit7"
V = ["EC", "SE", "VO", "OP", "PI_L", "SC", "SS_E"]
K = len(V)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def fetch():
    listing = json.loads(get(f"https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/"))
    url = next(f["links"]["download"] for f in listing["data"] if f["attributes"]["name"] == FILE)
    return get(url)


def num(x):
    if x is None or isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    raise SystemExit(f"unreadable correlation {x!r}")


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ws = openpyxl.load_workbook(io.BytesIO(fetch()), read_only=True, data_only=True)[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    ix = {k: i for i, k in enumerate(rows[0]) if k}
    pairs = {f"{V[j]}_{V[i]}": (i, j) for i in range(K) for j in range(i)}
    if set(pairs) != set(ix) - {"Studies", "N", "Age"}:
        raise SystemExit(f"unexpected columns {sorted(ix)}")
    long, records, held = [], [], []
    for r in rows[1:]:
        if not r[0]:
            continue
        group = re.sub(r"\s+", " ", str(r[0])).strip()
        if any(rec["group"] == group for rec in records) or group in held:
            raise SystemExit(f"duplicate group {group}")
        ni = int(r[ix["N"]])
        M = [[1.0 if i == j else None for j in range(K)] for i in range(K)]
        for col, (i, j) in pairs.items():
            M[i][j] = M[j][i] = num(r[ix[col]])
        keep = list(range(K))
        while True:                       # drop variables with no reported cell among the rest
            k2 = [i for i in keep if any(M[i][j] is not None for j in keep if j != i)]
            if k2 == keep:
                break
            keep = k2
        dropped = [V[i] for i in range(K) if i not in keep]
        lower = [M[i][j] for a, i in enumerate(keep) for j in keep[:a]]
        if len(keep) < 2 or any(x is not None and abs(x) >= 1 for x in lower):
            held.append(group)
            continue
        for a, i in enumerate(keep):
            for j in keep[:a + 1]:
                value = "1" if i == j else ("" if M[i][j] is None else repr(M[i][j]))
                long.append({"stat": "cor", "var1": V[i], "var2": V[j],
                             "value": value, "n": ni, "group": group})
        records.append({"group": group, "n_obs": ni, "dropped": dropped, "age": r[ix["Age"]],
                        "blank": [f"{V[i]}-{V[j]}" for a, i in enumerate(keep) for j in keep[:a]
                                  if M[i][j] is None]})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / "records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} samples built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_berki2026_sportcommit.py <out dir>")
    main(sys.argv[1])
