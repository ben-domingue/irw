"""Covariance family (irw_cov, source = "cov"): Brady et al. (2005), Table 2.

Source (since 2026-11-19): Zenodo record 12579101
(https://doi.org/10.5281/zenodo.12579101), "PLS-SEM from Correlation Matrix"
(Arteaga Moreno, 2024), CC BY 4.0: the workbook "Suplementary material MBR.xlsm",
sheets "Brady et  al. 2015 S1 R OV" (study 1) and "Brady et  al. 2015 S2 R OV"
(study 2), whose description says "The correlation matrix comes from: Brady, M.,
Knight, G., Cronin JR, J., Tomas, G., Hult, M., & Keillor, B. (2005) ... Journal
of Retailing, 81(3), 215-230" (the sheet names misprint the year as 2015).

History: the table was first built (2026-11-17) from Zenodo record 23912643
(Navarro-Munoz, Malagon-Selma, Gallarza & Arteaga, MIT), a transcription of the
same two matrices. Its depositor withdrew that record on 2026-11-18 as a
"duplicate" (HTTP 410). Ben (2026-11-19) chose to keep the table and repoint it.
Rebuilt from this workbook, the table is byte-identical to the first build.

The workbook is read with openpyxl (data only, keep_vba=False); its macros are
never run. Study 2's cells are stored exactly as printed (two decimals). Study
1's cells are stored with floating-point noise (e.g. 0.7400000000000007): the
sheet holds the printed matrix as recomputed by the workbook. Each study-1 cell
is written at two decimals, the precision Brady et al. print, and the script
stops if any cell is more than 1e-9 from a two-decimal value; this recovers the
printed value and changes nothing else.

Sample sizes (study 1 n = 1138, study 2 n = 329) are not in the workbook; they
come from the withdrawn deposit's brady24full.py, which transcribes the paper.
Variables are written in the order of the paper's Table 2 (as transcribed in the
withdrawn deposit), not the workbook's alphabetical order.

Modification: reshaped to the long lower-triangle layout in
data/covariance/README.md; no value is changed.

Usage: python3 data/covariance/zenodo_brady2005.py <out dir>
"""
import csv
import io
import sys
import urllib.request
from pathlib import Path

import openpyxl

URL = ("https://zenodo.org/api/records/12579101/files/"
       "Suplementary%20material%20MBR.xlsm/content")
TABLE = "brady_2005_service15"
N = {"study1": 1138, "study2": 329}
SHEETS = {"study1": "Brady et  al. 2015 S1 R OV", "study2": "Brady et  al. 2015 S2 R OV"}
ORDER = ["SQ1", "SQ2", "SQ3", "SQ4", "SAT1", "SAT2", "SAT3", "VAL1", "VAL2", "VAL3",
         "SAC1", "SAC2", "BI1", "BI2", "BI3"]


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def matrix(ws):
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    head = [str(c).strip() if c is not None else None for c in rows[0]]
    if sorted(h for h in head if h) != sorted(ORDER):
        raise SystemExit(f"{ws.title}: unexpected header {head}")
    cell = {}
    for r in rows[1:len(ORDER) + 1]:
        name = str(r[0]).strip()
        if name not in ORDER:
            raise SystemExit(f"{ws.title}: unexpected row label {name!r}")
        for j, v in enumerate(r[1:len(head)], 1):
            cell[(name, head[j])] = v
    return cell


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(io.BytesIO(fetch()), read_only=True, data_only=True, keep_vba=False)
    rows = []
    for group, sheet in SHEETS.items():
        cell = matrix(wb[sheet])
        for i, v1 in enumerate(ORDER):
            for v2 in ORDER[:i + 1]:
                if v1 == v2:
                    value = "1"
                else:
                    x, y = cell[(v1, v2)], cell[(v2, v1)]
                    if abs(x - y) > 1e-9:
                        raise SystemExit(f"{group} {v1}-{v2}: not symmetric ({x}, {y})")
                    r2 = round(x, 2)
                    if abs(x - r2) > 1e-9:
                        raise SystemExit(f"{group} {v1}-{v2}: {x!r} is not a two-decimal value")
                    if group == "study2" and x != r2:
                        raise SystemExit(f"study2 {v1}-{v2}: expected an exact two-decimal value, got {x!r}")
                    value = repr(r2)
                rows.append({"stat": "cor", "var1": v1, "var2": v2, "value": value,
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
