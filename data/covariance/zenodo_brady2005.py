"""Covariance family (irw_cov, source = "cov"): Brady et al. (2005), Table 2.

Source: Zenodo record 23912643 (https://doi.org/10.5281/zenodo.23912643), the
supporting material of Navarro-Munoz, Malagon-Selma, Gallarza & Arteaga,
"Reanalysis of published PLS-SEM models from reported correlation matrices".
Licence: MIT. Its `brady_S.py` transcribes the two indicator correlation
matrices of Brady et al. (2005, Journal of Retailing, Table 2) as lower
triangles; `brady24full.py` gives the sample sizes (study 1 n = 1138, study 2
n = 329).

The file is parsed as text, never executed. Variables are in the order of the
transcription (the `ART` list). Modification (2026-11-17): reshaped to the long
lower-triangle layout in data/covariance/README.md; no value is changed.

Not taken from this deposit: the Gallarza et al. (2015) matrix, because the
deposit also publishes the 585 x 33 raw responses it was computed from (a core
response-table candidate, out of scope for cov).

Usage: python3 data/covariance/zenodo_brady2005.py <out dir>
"""
import ast
import csv
import io
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = ("https://zenodo.org/records/23912643/files/"
       "PLSSEM_reanalysis_code_and_data.zip?download=1")
TABLE = "brady_2005_service15"
N = {"study1": 1138, "study2": 329}


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return zipfile.ZipFile(io.BytesIO(r.read()))


def literal(src, name):
    m = re.search(rf"^{name}\s*=\s*(\[.*?\])\s*$", src, re.S | re.M)
    if not m:
        raise SystemExit(f"{name} not found in brady_S.py")
    return ast.literal_eval(m.group(1))   # a literal only; nothing is run


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    z = fetch()
    member = next(n for n in z.namelist() if n.endswith("brady_S.py"))
    src = z.read(member).decode("utf-8")
    names = literal(src, "ART")
    rows = []
    for group, key in (("study1", "LOW1"), ("study2", "LOW2")):
        low = literal(src, key)
        if len(low) != len(names) or any(len(r) != i for i, r in enumerate(low)):
            raise SystemExit(f"{key} is not a {len(names)}-variable lower triangle")
        for i, v1 in enumerate(names):
            for j in range(i + 1):
                value = 1 if i == j else low[i][j]
                rows.append({"stat": "cor", "var1": v1, "var2": names[j], "value": repr(value),
                             "n": N[group], "group": group})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {TABLE}.csv ({len(rows)} rows) to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 zenodo_brady2005.py <out dir>")
    main(sys.argv[1])
