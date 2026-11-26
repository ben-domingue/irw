"""Covariance family (irw_cov, source = "cov"): Gnambs & Staufenbiel (2018) GHQ-12 item correlation matrices.

Source: OSF project z5c4q, "Meta-Analyses on the Structure of the General
Health Questionnaire (GHQ-12)" (coded data and R syntax for Gnambs, T., &
Staufenbiel, T. (2018). The structure of the General Health Questionnaire
(GHQ-12): two meta-analytic factor analyses. Health Psychology Review, 12(2),
179-194, https://doi.org/10.1080/17437199.2018.1426484).
Licence: CC BY 4.0 (stated on the node).

One deposit file is read, data/Codings.xlsx (OSF file npbkv):
- sheet "Correlation matrices": one row per sample whose primary report printed
  the 12 x 12 inter-item correlation matrix of the GHQ-12, as the lower
  triangle R1.2 ... R11.12 (item i with item j), with the sample's study label,
  publication year (PYR), survey year (SYR), country (CNTRY), language (LANG),
  publication type (PUB), N, proportion of women (SEX), mean age (AGE), number
  of response categories (CAT), scoring (SCORE) and a free-text NOTE.
- sheet "Coding guide": the item wording used as variable descriptions
  (F1.1 ... F1.12 give items 1-12 in GHQ-12 order) and the code labels.
The sheets "Factor loadings (GHQ-12)" and "Factor loadings (GHQ-XX)" are factor
solutions (model output) and are not used: matrices reproduced from loadings
are out of scope (README, Scope).

Values are the cells as stored (2 or 3 decimals, as printed in the primary
reports). No sample has a blank cell or an off-diagonal |r| >= 1; the script
stops if that changes. The deposit does not say whether the correlations are
Pearson, so matrix_type is "unknown".

Modification (2026-11-18): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per sample (the deposit's STUDY label);
items named I1-I12 as in the authors' R syntax ("1.1 Prepare summary data.R").

Usage: python3 data/covariance/osf_gnambs2018_ghq.py <out dir>
"""
import csv
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import openpyxl

URL = "https://osf.io/download/npbkv/"
TABLE = "gnambs_2018_ghq12"
K = 12
V = [f"I{i}" for i in range(1, K + 1)]


def get(url):
    """GET with retries: OSF answers 403/429 when downloads come too fast."""
    for wait in (0, 5, 15, 45, 90):
        time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (403, 429, 502, 503):
                raise
    raise SystemExit(f"download failed after retries: {url}")


def txt(v):
    """A stored number as text: Python's shortest repr, so 0.387 stays 0.387."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise SystemExit(f"non-numeric correlation {v!r}")
    return str(int(v)) if float(v).is_integer() else repr(float(v))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(io.BytesIO(get(URL)), read_only=True, data_only=True)
    guide = {r[0]: r[1] for r in wb["Coding guide"].iter_rows(values_only=True) if r[0]}
    items = []
    for i in range(1, K + 1):
        d = guide[f"F1.{i}"]
        items.append(d.split(":", 1)[1].strip())
    rows = list(wb["Correlation matrices"].iter_rows(values_only=True))
    hdr = list(rows[0])
    col = {h: j for j, h in enumerate(hdr) if h}
    long, records = [], []
    for r in rows[1:]:
        if not r[0]:
            continue
        label = str(r[col["STUDY"]]).strip()
        if any(x["group"] == label for x in records):
            raise SystemExit(f"duplicate label {label}")
        n = r[col["N"]]
        if not isinstance(n, (int, float)) or n != int(n) or n <= 0:
            raise SystemExit(f"{label}: bad N {n!r}")
        n = int(n)
        cell = {}
        for i in range(1, K + 1):
            for j in range(i + 1, K + 1):
                v = r[col[f"R{i}.{j}"]]
                if v is None:
                    raise SystemExit(f"{label}: blank R{i}.{j}")
                if abs(float(v)) >= 1:
                    raise SystemExit(f"{label}: |r| >= 1 at R{i}.{j}")
                cell[(j, i)] = txt(v)
        for a in range(1, K + 1):
            for b in range(1, a + 1):
                long.append({"stat": "cor", "var1": V[a - 1], "var2": V[b - 1],
                             "value": "1" if a == b else cell[(a, b)], "n": n, "group": label})
        records.append({"group": label, "n_obs": n,
                        **{k.lower(): r[col[k]] for k in
                           ("PYR", "SYR", "CNTRY", "LANG", "PUB", "SEX", "AGE", "CAT", "SCORE", "NOTE")}})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "items": dict(zip(V, items)), "records": records},
                  f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} samples")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_gnambs2018_ghq.py <out dir>")
    main(sys.argv[1])
