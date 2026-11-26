"""Covariance family (irw_cov, source = "cov"): Yilmaz Kogar & Kogar (2023) PSS-10 item correlation matrices.

Source: OSF project ctvxf, component 2gjak "Data (After data collection)", for
Yilmaz Kogar, E., & Kogar, H. (2023). A systematic review and meta-analytic
confirmatory factor analysis of the perceived stress scale (PSS-10 and
PSS-14). Stress and Health, 40(1), https://doi.org/10.1002/smi.3285.
Licence of the deposit: CC BY 4.0 (stated on the node and the component). The
article itself is CC BY-NC 4.0; the matrices are taken from the deposit.

One deposit file is read, coding_sheet_PSS_10.xlsx (OSF file 8tvbm):
- sheet "Correlations": one row per sample whose 10 x 10 PSS-10 inter-item
  correlation matrix was coded, as the upper-triangle vector r1.2 ... r9.10
  (item i with item j; two headers carry a "*", r2.10* and r8.10*, which the
  authors' R code strips, as here), with study label, publication year, country,
  continent, language, publication type, sample description, N, percentage of
  women (sex), mean age (age), clinical (0/1), number of response options
  (res) and notes.
- sheet "Description": the item wording (F1.1 ... F1.10), used as variable
  descriptions, and the code labels.
The sheet "Factor Loadings" is model output and is not used, nor is
coding_sheet_PSS_14.xlsx, whose only correlation matrix is Figalova 2021.

Figalova 2021 (N = 1725) is not built: its raw item responses are the IRW core
table figalova_2021_pss, and a matrix computable from an IRW table is out of
scope (README, Scope). The script stops on any other sample it has not seen.

Values are the cells as stored (two decimals, as printed). Negatively and
positively worded items are correlated as reported (several samples have
negative correlations between the two item sets). No sample has a blank cell
or an off-diagonal |r| >= 1.

Modification (2026-11-18): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per sample (the deposit's study label);
items named I1-I10 as in the authors' R code (step1_corr_mat_PSS10.R).

Usage: python3 data/covariance/osf_yilmazkogar2023_pss.py <out dir>
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

URL = "https://osf.io/download/8tvbm/"
TABLE = "yilmazkogar_2023_pss10"
K = 10
V = [f"I{i}" for i in range(1, K + 1)]
EXPECTED = ["Figalova 2021", "Michaelides 2016", "Miranda 2022", "Park 2019",
            "SmithEmerson 2014", "Smith 2014", "Taylor 2015a", "Taylor 2015b"]
SKIP = {"Figalova 2021": "raw data are the IRW core table figalova_2021_pss"}


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
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise SystemExit(f"non-numeric correlation {v!r}")
    return str(int(v)) if float(v).is_integer() else repr(float(v))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(io.BytesIO(get(URL)), read_only=True, data_only=True)
    desc = {r[0]: r[1] for r in wb["Description"].iter_rows(values_only=True) if r[0]}
    items = {f"I{i}": desc[f"F1.{i}"].split(" - ", 1)[1].strip() for i in range(1, K + 1)}
    rows = list(wb["Correlations"].iter_rows(values_only=True))
    col = {h.replace("*", ""): j for j, h in enumerate(rows[0]) if h}   # as the authors' R code: r2.10* -> r2.10
    labels = [str(r[0]).strip() for r in rows[1:] if r[0]]
    if labels != EXPECTED:
        raise SystemExit(f"samples changed: {labels}")
    long, records, held = [], [], []
    for r in rows[1:]:
        if not r[0]:
            continue
        label = str(r[0]).strip()
        if label in SKIP:
            held.append((label, SKIP[label]))
            continue
        n = r[col["n"]]
        if not isinstance(n, (int, float)) or n != int(n) or n <= 0:
            raise SystemExit(f"{label}: bad N {n!r}")
        n = int(n)
        cell = {}
        for i in range(1, K + 1):
            for j in range(i + 1, K + 1):
                v = r[col[f"r{i}.{j}"]]
                if v is None:
                    raise SystemExit(f"{label}: blank r{i}.{j}")
                if abs(float(v)) >= 1:
                    raise SystemExit(f"{label}: |r| >= 1 at r{i}.{j}")
                cell[(j, i)] = txt(v)
        for a in range(1, K + 1):
            for b in range(1, a + 1):
                long.append({"stat": "cor", "var1": V[a - 1], "var2": V[b - 1],
                             "value": "1" if a == b else cell[(a, b)], "n": n, "group": label})
        records.append({"group": label, "n_obs": n,
                        **{k: r[col[k]] for k in ("pubyear", "country", "lang", "pubtype", "sample",
                                                  "sex", "age", "clinical", "res", "notes")}})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "items": items, "records": records, "held": held},
                  f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} samples built, {len(held)} not built {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_yilmazkogar2023_pss.py <out dir>")
    main(sys.argv[1])
