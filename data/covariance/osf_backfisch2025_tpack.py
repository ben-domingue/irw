"""Covariance family (irw_cov, source = "cov"): Backfisch, Scherer, Schneider & Lachner (2025) TPACK MASEM.

Source: OSF project neyp5, "A Meta-Analysis of the Validity Evidence of
Technological Pedagogical and Content Knowledge (TPACK) Self-Report
Assessments" (Backfisch, I., Scherer, R., Schneider, J., & Lachner, A. (2025).
How valid, really? A meta-analysis of the validity evidence of Technological
Pedagogical and Content Knowledge (TPACK) self-report assessments. Educational
Research Review, 49, 100718, https://doi.org/10.1016/j.edurev.2025.100718).
Licence: CC BY 4.0 (stated on the node).

One deposit file is read: "Supplementary-Material/S6-Supplementary-Material_
Data-Codebook.xlsx", sheet "RQ1-RQ2-Data": one row per sample (Reference) with
N and the Pearson correlations among self-reported CK, PK, PCK, TCK, TPK, TPCK
and TK (columns CorrXY, per the RQ1-RQ2-Codebook sheet). Excel doubles are
written in their shortest round-trip form.

A dimension with no correlation in a sample was not measured there and is
dropped (Ben, 2026-11-17). A pair between two measured dimensions that the
sample did not report is written as a row with an empty value (blank cells
allowed, Ben, 2026-11-18); a sample with fewer than two measured dimensions
or an off-diagonal |r| >= 1 is not built and is listed in the records file.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per sample (the sheet's Reference).
Modification (2026-11-18): unreported pairs among measured dimensions are
written as empty values instead of holding the sample.

Usage: python3 data/covariance/osf_backfisch2025_tpack.py <out dir>
"""
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

import openpyxl

NODE = "neyp5"
NAME = "S6-Supplementary-Material_Data-Codebook.xlsx"
TABLE = "backfisch_2025_tpack7"
V = ["CK", "PK", "PCK", "TCK", "TPK", "TPCK", "TK"]


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
    todo = [f"https://api.osf.io/v2/nodes/{NODE}/files/osfstorage/"]
    while todo:
        for f in listing(todo.pop()):
            a = f["attributes"]
            if a["kind"] == "folder":
                todo.append(f["relationships"]["files"]["links"]["related"]["href"])
            elif a["name"] == NAME:
                return get(f["links"]["download"])
    raise SystemExit(f"{NAME} not found")


def fmt(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise SystemExit(f"non-numeric cell {v!r}")
    return str(v) if isinstance(v, int) else repr(float(v))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(io.BytesIO(fetch()), read_only=True, data_only=True)
    rows = list(wb["RQ1-RQ2-Data"].iter_rows(values_only=True))
    hdr = list(rows[0])
    col = {}
    for a in range(len(V)):
        for b in range(a + 1, len(V)):
            name = f"Corr{V[a]}{V[b]}"
            col[(a, b)] = col[(b, a)] = hdr.index(name)
    long, records, held = [], [], []
    for r in rows[1:]:
        if r[0] is None:
            continue
        label = " ".join(str(r[hdr.index("Reference")]).split())
        ni = int(r[hdr.index("N")])
        if any(rec["group"] == label for rec in records) or label in [h[0] for h in held]:
            raise SystemExit(f"duplicate label {label}")
        keep = list(range(len(V)))
        while True:   # drop dimensions with no reported cell among those still kept
            k2 = [i for i in keep if any(r[col[(i, x)]] is not None for x in keep if x != i)]
            if k2 == keep:
                break
            keep = k2
        cells = [r[col[(i, x)]] for a, i in enumerate(keep) for x in keep[:a]]
        if len(keep) < 2 or all(c is None for c in cells):
            held.append((label, "fewer than two measured dimensions"))
            continue
        if any(c is not None and abs(c) >= 1 for c in cells):
            held.append((label, "|r| >= 1"))
            continue
        for a, i in enumerate(keep):
            for x in keep[:a + 1]:
                long.append({"stat": "cor", "var1": V[i], "var2": V[x],
                             "value": "1" if i == x else ("" if r[col[(i, x)]] is None else fmt(r[col[(i, x)]])),
                             "n": ni, "group": label})
        records.append({"group": label, "n_obs": ni, "dropped": [V[i] for i in range(len(V)) if i not in keep],
                        "n_blank": sum(c is None for c in cells),
                        "population": r[hdr.index("Population")], "sample_id": r[hdr.index("SampleID")],
                        "article_id": r[hdr.index("ArticleID")]})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} samples built, {len(held)} held")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_backfisch2025_tpack.py <out dir>")
    main(sys.argv[1])
