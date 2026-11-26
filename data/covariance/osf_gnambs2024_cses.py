"""Covariance family (irw_cov, source = "cov"): Gnambs & Schroeders (2024) Core Self-Evaluations Scale item correlations.

Source: OSF project zjvwg, coded data and code for Gnambs, T., & Schroeders, U.
(2024). Reliability and factorial validity of the Core Self-Evaluations Scale:
A meta-analytic investigation of wording effects. European Journal of
Psychological Assessment, 40(5), 343-359,
https://doi.org/10.1027/1015-5759/a000783 (open access, CC BY 4.0).
Licence of the deposit: CC BY 4.0 (stated on the node).

Files read (OSF file ids in FILES):
- codings/_samples.xlsx, sheet "Samples": one row per sample with study label,
  publication year (pyr), country (cntry), language (lang), publication type
  (pub), N (n), percentage of women (fem), mean age (age), response options
  (res), the kind of data coded (data: 1 raw data, 2 correlation matrix, 3 EFA,
  4 CFA) and the polarity of the negatively worded items (pol: 1 original
  coding, 2 reverse coded). This is the sheet the authors' code reads
  (code/1-3_preprocess_data.r). Sheet "CSES" gives the 12 items' wording,
  reverse-scoring flag and facet, used as variable descriptions.
- codings/_samples_tg.xlsx, sheet "Samples": the same rows plus `source` (where
  the coded matrix came from); used only for that column, after checking that
  n, pyr and pol agree with _samples.xlsx.
- codings/<study>.xlsx, sheet "correlations": the 12 x 12 item correlation
  matrix (lower triangle with diagonal), for the five samples with data = 2.

Only samples coded as a correlation matrix (data = 2) are built. Samples coded
from raw data (data = 1) were computed by the meta-analysts from openly
available raw data (data/covariances, rawdata/readme.txt) and are not published
matrices; samples coded as EFA/CFA loadings (data = 3, 4) are model output.
Values are the cells as stored. Three of the five matrices were "Received by
email" from the primary authors (the deposit's `source`), so for them the
deposit is the first publication of the matrix; the notes say which.

Modification (2026-11-18): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per sample (the deposit's study label).
Values unchanged; no sample has a blank cell or an off-diagonal |r| >= 1.

Usage: python3 data/covariance/osf_gnambs2024_cses.py <out dir>
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

FILES = {"_samples": "qbvpc", "_samples_tg": "bxvsc",
         "förster2013": "643fa87438485308bd495785", "gu2015": "uxwz6",
         "scheurer2013": "643fa87940b2c107ace8fc21", "smedema2015": "643fa87a18ff9107360483fe",
         "zenger2015": "643fa87dc76c0708ba135e99"}
TABLE = "gnambs_2024_cses12"
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


def book(key):
    return openpyxl.load_workbook(io.BytesIO(get(f"https://osf.io/download/{FILES[key]}/")),
                                  read_only=True, data_only=True)


def txt(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise SystemExit(f"non-numeric correlation {v!r}")
    return str(int(v)) if float(v).is_integer() else repr(float(v))


def sheet(wb, name):
    rows = list(wb[name].iter_rows(values_only=True))
    hdr = [h for h in rows[0]]
    return [dict(zip(hdr, r)) for r in rows[1:] if r and r[0]]


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wb = book("_samples")
    samples = sheet(wb, "Samples")
    items = sheet(wb, "CSES")
    tg = {r["study"]: r for r in sheet(book("_samples_tg"), "Samples")}
    long, records = [], []
    for s in samples:
        if s["data"] != 2:
            continue
        label = s["study"]
        if label not in FILES:
            raise SystemExit(f"new correlation-matrix sample {label}: add its file id")
        t = tg[label]
        if (t["n"], t["pyr"], t["pol"]) != (s["n"], s["pyr"], s["pol"]):
            raise SystemExit(f"{label}: _samples and _samples_tg disagree")
        rows = list(book(label)["correlations"].iter_rows(values_only=True))
        if list(rows[0]) != V or len(rows) != K + 1:
            raise SystemExit(f"{label}: unexpected layout")
        n = int(s["n"])
        for a in range(K):
            for b in range(a + 1):
                v = rows[a + 1][b]
                if v is None:
                    raise SystemExit(f"{label}: blank cell {V[a]}-{V[b]}")
                if a == b and v != 1:
                    raise SystemExit(f"{label}: diagonal {v}")
                if a != b and abs(float(v)) >= 1:
                    raise SystemExit(f"{label}: |r| >= 1 at {V[a]}-{V[b]}")
                long.append({"stat": "cor", "var1": V[a], "var2": V[b],
                             "value": "1" if a == b else txt(v), "n": n, "group": label})
            if any(x is not None for x in rows[a + 1][a + 1:]):
                raise SystemExit(f"{label}: values above the diagonal")
        records.append({"group": label, "n_obs": n, "source": t["source"],
                        **{k: s[k] for k in ("pyr", "cntry", "lang", "pub", "fem", "age", "res", "pol")}})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "items": items, "records": records}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} samples")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_gnambs2024_cses.py <out dir>")
    main(sys.argv[1])
