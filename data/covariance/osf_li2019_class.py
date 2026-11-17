"""Covariance family (irw_cov, source = "cov"): Li, Liu & Hunter (2019) CLASS MASEM.

Source: OSF project x5964 ("Example 2 - Analysis in metaSEM"), a component of
wh6d3, the materials of Jak, Li, Kolbe, de Jonge & Cheung (2021), "Meta-analytic
structural equation modeling made easy", Research Synthesis Methods 12,
https://doi.org/10.1002/jrsm.1498. Licence: CC BY 4.0 (stated on the node).
Data_Li.dat holds the study-level correlations among the ten CLASS dimensions
compiled by Li, Liu & Hunter (2019), one row per study: 45 correlations
(PC_NC, PC_TS, ..., QF_LM, i.e. the upper triangle row by row), N, and grade.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per study (study01 ... in file order; the
deposit has no study labels). Values are copied as the text the file gives, so
nothing is rounded. A variable with no correlation in a study was not measured
there and is dropped from that study (Ben, 2026-11-17); a study still holding a
blank cell is not built and is printed.

Usage: python3 data/covariance/osf_li2019_class.py <out dir>
"""
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

NODE = "x5964"
FILE = "Data_Li.dat"
TABLE = "li_2019_class10"
VARS = ["PC", "NC", "TS", "RSP", "BM", "PD", "ILF", "CD", "QF", "LM"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def fetch():
    listing = json.loads(get(f"https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/"))
    url = next(f["links"]["download"] for f in listing["data"] if f["attributes"]["name"] == FILE)
    return get(url).decode("utf-8")


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(io.StringIO(fetch()), delimiter="\t"))
    pairs = [(a, b) for i, a in enumerate(VARS) for b in VARS[i + 1:]]
    assert all(f"{a}_{b}" in rows[0] for a, b in pairs), "unexpected columns"
    long, records, held = [], [], []
    for k, r in enumerate(rows, 1):
        group = f"study{k:02d}"
        r_of = {(a, b): r[f"{a}_{b}"].strip() for a, b in pairs}
        r_of.update({(b, a): v for (a, b), v in list(r_of.items())})
        blank = lambda v: v in ("", "NA")
        measured = [v for v in VARS if any(not blank(r_of[(v, w)]) for w in VARS if w != v)]
        dropped = [v for v in VARS if v not in measured]
        if len(measured) < 2 or any(blank(r_of[(a, b)]) for i, a in enumerate(measured) for b in measured[:i]):
            held.append(group)
            continue
        n = int(r["N"])
        for i, a in enumerate(measured):
            for b in measured[:i + 1]:
                long.append({"stat": "cor", "var1": a, "var2": b,
                             "value": "1" if a == b else r_of[(a, b)], "n": n, "group": group})
        records.append({"group": group, "n_obs": n, "grade": r["grade"], "dropped": dropped})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / "records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} studies built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_li2019_class.py <out dir>")
    main(sys.argv[1])
