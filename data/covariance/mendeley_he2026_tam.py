"""Covariance family (irw_cov, source = "cov"): He (2026) TAM and students' AI adoption MASEM.

Source: Mendeley Data 6t8vvhy7vp v1 (https://doi.org/10.17632/6t8vvhy7vp.1), "Data
for 'Understanding Students' Adoption of Artificial Intelligence in Higher
Education Based on TAM: A Meta-Analytic Structural Equation Modeling Study'"
(He, Mengyao, 2026), CC BY 4.0 (Mendeley and DataCite rightsList). Same
depositor and file layout as zenodo_he2026_utaut.py (a separate UTAUT MASEM);
many primary studies appear in both deposits, with different construct sets. No published paper was found (Crossref, 2026-11-17), so the dataset is
cited.

Appendixes.xlsx:
- Appendix 3: one row per study and construct pair (Study ID, N, Var 1, Var 2,
  r, two reliabilities), plus a per-study key from each abbreviation to the
  construct's name in that study. The abbreviations are the meta-analysts'
  harmonised constructs (e.g. BI is "Behavioral Intention" in most studies and
  "Adoption Intention" in one); they are kept as deposited. Reliabilities are
  not part of the layout.
- Appendix 1: Study ID -> short citation (the group label).
- Appendix 2: Study ID -> country, AI type and major (the population).
Study ID 17 has two samples ("17-CN", "17-INT"); there is no study 19.

The script checks that N is constant within a study and no pair is repeated.
A pair among the constructs a study measured that it did not report is
written as a row with an empty value (blank cells allowed, Ben, 2026-11-18);
the missing pairs are listed per study in <TABLE>_records.json.
Values are written in shortest round-trip form, i.e. as stored.

Modification (2026-11-17): pivoted from pairwise rows to the long lower-triangle
layout in data/covariance/README.md, one group per study, labelled
"study <ID>: <citation>".
Modification (2026-11-18): unreported pairs among measured constructs are
written as empty values instead of holding the study.

Usage: python3 data/covariance/mendeley_he2026_tam.py <out dir>
"""
import csv
import io
import json
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

import openpyxl

URL = "https://data.mendeley.com/public-files/datasets/6t8vvhy7vp/files/7d7c1483-d203-4d31-8b76-e8add96c1350/file_downloaded"
TABLE = "he_2026_tam22"
ORDER = ["PEU", "PU", "ATU", "BI", "UB", "PE", "EE", "SI", "FC", "SN", "PT", "PR",
         "SE", "PEN", "AILIT", "AIA", "ETH", "US", "SAT", "OQ", "MOT", "SA"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def sheet(wb, name):
    ws = next(w for w in wb.worksheets if w.title.strip() == name)
    return [r for r in list(ws.iter_rows(values_only=True))[1:] if r[0] is not None]


def clean(x):
    return re.sub(r"\s+", " ", str(x)).strip() if x not in (None, "", "/") else ""


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(io.BytesIO(get(URL)), read_only=True, data_only=True)
    cite = {str(r[0]): clean(r[1]) for r in sheet(wb, "Appendix 1")}
    chars = {str(r[0]): r for r in sheet(wb, "Appendix 2")}
    pairs = defaultdict(list)
    for r in sheet(wb, "Appendix 3"):
        pairs[str(r[0])].append(r)
    long, records, held = [], [], []
    for sid, rs in pairs.items():
        ns = {int(r[1]) for r in rs}
        if len(ns) != 1:
            raise SystemExit(f"study {sid}: N differs across pairs {ns}")
        ni = ns.pop()
        r_of = {}
        for r in rs:
            a, b = clean(r[2]), clean(r[3])
            if a == b or a not in ORDER or b not in ORDER or frozenset((a, b)) in r_of:
                raise SystemExit(f"study {sid}: bad or repeated pair {a}-{b}")
            if not isinstance(r[4], (int, float)):
                raise SystemExit(f"study {sid}: r {r[4]!r}")
            r_of[frozenset((a, b))] = float(r[4])
        v = [x for x in ORDER if any(x in p for p in r_of)]
        base = sid.split("-")[0]
        missing = sorted("-".join(sorted(p)) for p in
                         (frozenset((x, y)) for i, x in enumerate(v) for y in v[:i]) if p not in r_of)
        group = f"study {sid}: {cite.get(sid) or cite[base]}"
        for a, i in enumerate(v):
            for j in v[:a + 1]:
                long.append({"stat": "cor", "var1": i, "var2": j,
                             "value": "1" if i == j else (repr(r_of[frozenset((i, j))])
                                                          if frozenset((i, j)) in r_of else ""),
                             "n": ni, "group": group})
        c = chars.get(sid) or chars[base]
        records.append({"group": group, "n_obs": ni, "vars": v, "missing": missing,
                        "population": "; ".join(x for x in (clean(c[4]), clean(c[5]), clean(c[9])) if x)})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} studies built, {len(held)} held")
    for rec in records:
        if rec["missing"]:
            print("blank cells:", rec["group"], rec["missing"])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 mendeley_he2026_tam.py <out dir>")
    main(sys.argv[1])
