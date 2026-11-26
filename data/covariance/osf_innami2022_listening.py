"""Covariance family (irw_cov, source = "cov"): In'nami et al. (2022) L2 listening MASEM.

Source: OSF project xvnf2, "Examining Second Language Listening and
Metacognitive Awareness: A Meta-Analytic Structural Equation Modeling
Approach" (In'nami, Cheung, Koizumi & Wallace, Language Learning,
https://doi.org/10.1111/lang.12548). Licence: CC BY 4.0 (stated on the node).
data.R holds two R `dput` lists of study correlation matrices with a sample
size vector `n`: cordat6variables (LC, DA, MT, PK, PE, PS: listening
comprehension and the five metacognitive-awareness subscales) and
cordat5variables, which is the same 32 studies without LC (checked), so only
the six-variable list is built.

The file is R code. It is parsed as TEXT with regular expressions and never
evaluated. dput writes doubles with 17 significant digits (0.34999999999999998);
each value is written in its shortest round-trip form (0.35), i.e. the same
double, which is the published two- or three-decimal value.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per study (study01 ... in file order; the
deposit has no study labels). A variable whose diagonal is NA was not measured
in that study and is dropped there (Ben, 2026-11-17); a study still holding a
blank cell is not built and is printed.

Usage: python3 data/covariance/osf_innami2022_listening.py <out dir>
"""
import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

NODE = "xvnf2"
FILE = "data.R"
OBJECT = "cordat6variables"
TABLE = "innami_2022_l2listening6"
BLOCK = (r"c\(([^)]*)\)\s*,\s*\.Dim\s*=\s*c\(\s*(\d+)L\s*,\s*(\d+)L\s*\)\s*,"
         r"\s*\.Dimnames\s*=\s*list\(\s*c\(([^)]*)\)")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def fetch():
    listing = json.loads(get(f"https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/"))
    url = next(f["links"]["download"] for f in listing["data"] if f["attributes"]["name"] == FILE)
    return get(url).decode("utf-8")


def shortest(s):
    s = s.strip()
    return s if s == "NA" else repr(float(s))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    text = fetch()
    parts = re.split(r"^(\w+) <-\s*$", text, flags=re.M)
    body = dict(zip(parts[1::2], parts[2::2]))[OBJECT]
    blocks = body.split("structure(")[1:]
    mats = []
    for b in blocks:
        m = re.match(BLOCK, b)
        if not m:
            raise SystemExit("unparsed matrix block: " + b[:80])
        vals = [shortest(x) for x in m.group(1).split(",")]
        k = int(m.group(2))
        names = [x.strip().strip('"') for x in m.group(4).split(",")]
        if len(vals) != k * k or len(names) != k:
            raise SystemExit("matrix size mismatch")
        mats.append((names, [[vals[c * k + r] for c in range(k)] for r in range(k)]))   # column-major
    n = [int(float(x)) for x in re.search(r"\bn\s*=\s*c\(([^)]*)\)", blocks[-1]).group(1).split(",")]
    if len(n) != len(mats):
        raise SystemExit(f"{len(mats)} matrices but {len(n)} sample sizes")
    long, records, held = [], [], []
    for s, ((names, M), ni) in enumerate(zip(mats, n), 1):
        group = f"study{s:02d}"
        keep = [i for i in range(len(names)) if M[i][i] != "NA"]
        dropped = [names[i] for i in range(len(names)) if i not in keep]
        if any(M[i][j] != M[j][i] for i in keep for j in keep):
            raise SystemExit(f"{group}: not symmetric")
        if len(keep) < 2 or any(M[i][j] == "NA" for a, i in enumerate(keep) for j in keep[:a]):
            held.append(group)
            continue
        for a, i in enumerate(keep):
            for j in keep[:a + 1]:
                long.append({"stat": "cor", "var1": names[i], "var2": names[j],
                             "value": "1" if i == j else M[i][j], "n": ni, "group": group})
        records.append({"group": group, "n_obs": ni, "dropped": dropped})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / "records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} studies built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_innami2022_listening.py <out dir>")
    main(sys.argv[1])
