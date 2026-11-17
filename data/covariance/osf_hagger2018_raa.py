"""Covariance family (irw_cov, source = "cov"): Hagger, Polet & Lintunen (2018) RAA MASEM.

Source: OSF project w4hfr, "The reasoned action approach applied to health
behavior: Role of past behavior and test of some key moderators using
meta-analytic structural equation modeling" (Hagger, Polet & Lintunen, Social
Science & Medicine, 213, 85-94, https://doi.org/10.1016/j.socscimed.2018.07.038),
a reanalysis of the studies in McEachan et al. (2016, Annals of Behavioral
Medicine, 50, 592-612, https://doi.org/10.1007/s12160-016-9798-4).
Licence: CC BY 4.0 (stated on the node).

Three deposit files are read:
- "Raw data and moderator coding/mceachan.txt": the 81 study correlation
  matrices the MASEM analysed, one per line, as metaSEM stacked vectors (the
  lower triangle with diagonal, column by column) over Int, AA, IA, SN, DN, Aut,
  Cap, Beh, PB.
- "MASEM R code and output/R code McEachan RAA.txt": the sample size vector `n`,
  in the same order. The file is R code; it is parsed as TEXT and never run.
- "Main data file/RAA_reanalysis_data_file_FINAL.xlsx": the extraction sheet,
  used only for each study's label and behaviour. It lists 89 studies; the 8
  without a matrix (no data obtained, as the sheet says) are not in the
  analysis file. Each matrix is matched to its row by n and by all 36
  correlations; the only differences are that the analysis file rounds 16
  intention-affective attitude correlations to two decimals (the sheet has
  three or four). The analysis file's values are used.

In the stacked vectors every diagonal is 1, measured or not. A variable with no
correlation in a study was not measured there and is dropped (Ben, 2026-11-17);
a study still holding a blank cell is not built and is printed.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per study (the sheet's label).

Usage: python3 data/covariance/osf_hagger2018_raa.py <out dir>
"""
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

import openpyxl

NODE = "w4hfr"
FILES = {"mat": "mceachan.txt", "code": "R code McEachan RAA.txt",
         "sheet": "RAA_reanalysis_data_file_FINAL.xlsx"}
TABLE = "hagger_2018_raa9"
V = ["Int", "AA", "IA", "SN", "DN", "Aut", "Cap", "Beh", "PB"]
K = len(V)


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
    """A sheet cell as a number, or None ("Not measured", blank). Some cells hold text like '0.42'."""
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return float(x)
    try:
        return float(str(x).strip())
    except ValueError:
        return None


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw = fetch()
    lines = [l.split() for l in raw["mat"].decode("utf-8").splitlines() if l.strip()]
    if any(len(l) != K * (K + 1) // 2 for l in lines):
        raise SystemExit("a line is not a 9-variable stacked vector")
    code = raw["code"].decode("utf-8")
    n = [int(x) for x in re.search(r"^n <-\s*c\(([^)]*)\)", code, re.M).group(1).split(",")]
    if len(n) != len(lines):
        raise SystemExit(f"{len(lines)} matrices but {len(n)} sample sizes")

    ws = openpyxl.load_workbook(io.BytesIO(raw["sheet"]), read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr = list(rows[1])
    pair = hdr.index("Intention-Affective attitude")
    beh = hdr.index("Behavior")
    studies = [r for r in rows[2:] if isinstance(r[0], int)]

    long, records, held, j = [], [], [], 0
    for s, (vals, ni) in enumerate(zip(lines, n)):
        M = unstack(vals)
        upper = [M[a][b] for a in range(K) for b in range(a + 1, K)]
        while True:                       # the next sheet row with this n and these values
            if j >= len(studies):
                raise SystemExit(f"matrix {s + 1}: no matching row in the sheet")
            r = studies[j]
            j += 1
            cells = r[pair:pair + len(upper)]
            if r[4] == ni and all(
                    (t == "NA") == (num(v) is None) and (t == "NA" or abs(float(t) - num(v)) < 0.0051)
                    for t, v in zip(upper, cells)):
                break
        label = re.sub(r"\s+", " ", str(r[1])).strip()
        if any(rec["group"] == label for rec in records) or label in held:
            raise SystemExit(f"duplicate label {label}")
        if any(M[i][i] != "1.000" for i in range(K)):
            raise SystemExit(f"{label}: diagonal is not 1")
        keep = [i for i in range(K) if any(M[i][x] != "NA" for x in range(K) if x != i)]
        dropped = [V[i] for i in range(K) if i not in keep]
        if len(keep) < 2 or any(M[i][x] == "NA" for a, i in enumerate(keep) for x in keep[:a]):
            held.append(label)
            continue
        for a, i in enumerate(keep):
            for x in keep[:a + 1]:
                long.append({"stat": "cor", "var1": V[i], "var2": V[x],
                             "value": "1" if i == x else M[i][x], "n": ni, "group": label})
        records.append({"group": label, "n_obs": ni, "dropped": dropped,
                        "behaviour": re.sub(r"\s+", " ", str(r[beh] or "")).strip()})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / "records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} studies built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_hagger2018_raa.py <out dir>")
    main(sys.argv[1])
