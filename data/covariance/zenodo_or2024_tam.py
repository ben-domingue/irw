"""Covariance family (irw_cov, source = "cov"): Or (2024) TAM MASEM.

Source: Zenodo record 11124570 (https://doi.org/10.5281/zenodo.11124570),
"35 Years of the Technology Acceptance Model: Insights from Meta-analytic
Structural Equation Modelling" (Caleb Or), CC BY 4.0. The paper is Or, C.
(2024), The Open/Technology in Education, Society, and Scholarship Association
Journal, 4(3), 1-26, https://doi.org/10.18357/otessaj.2024.4.3.66.
"MASEM R Code verison2.txt" defines 44 study correlation matrices among
perceived usefulness (PU), perceived ease of use (PEOU), intention to use (ITU)
and actual use (AU), collects them in `caleb_dataset`, names them, and gives
`sample_size` in that order. The "Model 2" file holds the same matrices
(checked when this script was written).

The file is R code. It is parsed as TEXT and never evaluated.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per study (the deposit's own object names).
A variable whose diagonal is NA was not measured in that study and is dropped
there (Ben, 2026-11-17); a study still holding a blank cell is not built and is
printed.

Usage: python3 data/covariance/zenodo_or2024_tam.py <out dir>
"""
import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

RECORD = "11124570"
MEMBER = "MASEM R Code verison2.txt"
TABLE = "or_2024_tam4"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def fetch():
    rec = json.loads(get(f"https://zenodo.org/api/records/{RECORD}"))
    url = next(f["links"]["self"] for f in rec["files"] if f["key"].endswith(".zip"))
    z = zipfile.ZipFile(io.BytesIO(get(url)))
    name = next(n for n in z.namelist() if n.endswith(MEMBER))
    return z.read(name).decode("utf-8", errors="strict").replace("\r\n", "\n").replace("\r", "\n")


def cvec(s):
    return [x.strip().strip('"') for x in s.split(",")]


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    text = fetch()
    rn = cvec(re.search(r'^rownames\s*=\s*c\(([^)]*)\)', text, re.M).group(1))
    cn = cvec(re.search(r'^colnames\s*=\s*c\(([^)]*)\)', text, re.M).group(1))
    if rn != cn:
        raise SystemExit("row and column names differ")
    k = len(rn)
    mats = {name: cvec(vals) for name, vals, nrow in
            re.findall(r'^(\w+)\s*<-\s*matrix\(c\(([^)]*)\),\s*nrow\s*=\s*(\d+)', text, re.M)}
    order = cvec(re.search(r'^names\(caleb_dataset\)\s*<-\s*c\(([^)]*)\)', text, re.M).group(1))
    listed = cvec(re.search(r'^caleb_dataset\s*<-\s*list\(([^)]*)\)', text, re.M).group(1))
    n = [int(x) for x in cvec(re.search(r'^sample_size\s*<-\s*c\(([^)]*)\)', text, re.M).group(1))]
    if listed != order or len(order) != len(n) or set(order) != set(mats):
        raise SystemExit("study list, names, matrices and sample sizes do not line up")
    long, records, held = [], [], []
    for study, ni in zip(order, n):
        v = mats[study]
        if len(v) != k * k:
            raise SystemExit(f"{study}: {len(v)} values")
        M = [[v[c * k + r] for c in range(k)] for r in range(k)]          # column-major
        if any(M[i][j] != M[j][i] for i in range(k) for j in range(k)):
            raise SystemExit(f"{study}: not symmetric")
        keep = [i for i in range(k) if M[i][i] != "NA"]
        dropped = [rn[i] for i in range(k) if i not in keep]
        if len(keep) < 2 or any(M[i][j] == "NA" for a, i in enumerate(keep) for j in keep[:a]):
            held.append(study)
            continue
        for a, i in enumerate(keep):
            for j in keep[:a + 1]:
                long.append({"stat": "cor", "var1": rn[i], "var2": rn[j], "value": M[i][j],
                             "n": ni, "group": study})
        records.append({"group": study, "n_obs": ni, "dropped": dropped})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / "records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} studies built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 zenodo_or2024_tam.py <out dir>")
    main(sys.argv[1])
