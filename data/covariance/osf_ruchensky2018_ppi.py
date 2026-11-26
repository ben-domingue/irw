"""Covariance family (irw_cov, source = "cov"): Ruchensky et al. (2018) PPI and PPI-R content-scale correlation matrices.

Source: OSF project vyw67, "Evaluating the Structure of Psychopathic Personality
Traits: A Meta-Analysis of the Psychopathic Personality Inventory" (component
83bh6 "Data Files"), materials for Ruchensky, J. R., Edens, J. F., Corker, K. S.,
Donnellan, M. B., Witt, E. A., & Blonigen, D. M. (2018). Evaluating the structure
of psychopathic personality traits: A meta-analysis of the Psychopathic
Personality Inventory. Psychological Assessment, 30(6), 707-718,
https://doi.org/10.1037/pas0000520.
Licence: CC BY 4.0 (stated on the project and on component 83bh6).

Three deposit files are read with openpyxl (values only; nothing in them is run):
- "raw files/Meta Data PPI Correlation Matrix 8.3.2017.xlsx" (OSF file v438p) and
  "raw files/Meta Data PPI-R Correlation Matrix 8.3.2017.xlsx" (h4zgw): one row per
  sample (Study, Number, Type 0 = community / 1 = offender, c1 ... c28, n, n - 3).
  These are the final coding sheets (8.3.2017, after the authors' error check).
  c1 ... c28 are the 28 content-scale pairs in the order of "Meta Data Key
  8.3.2017.xlsx" (ME x SP, ME x F, ..., CN x STI), i.e. the upper triangle of the
  8 scales ME, SP (PPI-R: SOI), F, C, IN (PPI-R: RN), BE, CN, STI read row-wise.
  The analysis CSVs (ppi_corrs_8.3.2017.csv etc.) hold the same values rounded to
  2 decimals and are not used.
- "Checking for Errors 8.3.2017.xlsx" (a9x5q), sheets "PPI" / "PPI-R" (per-sample
  provenance: N used, N reported, NOTE on where the matrix came from, changes
  made) and "... Checking Sample 7.27.2017" (what the sample is called). Used to
  select samples and for the population field.

Only samples whose matrix the deposit records as reported are built:
- "article": the checking sheet says the matrix was taken from the publication
  (PPI: Curry et al. 2011, Neumann et al. 2008; PPI-R: Hughes et al. 2013, Ray &
  Jones 2012, and the PPI-R manual's community sample, Lilienfeld & Widows 2005);
- "author output": the primary authors sent their own output or filled in the
  meta-analysts' data form (PPI: Sadeh & Verona 2008, Mahaffey & Marcus 2006,
  Marcus & Hammack unpublished; PPI-R: Denson et al. 2009, LaMarre & Carlson 2009,
  Miller et al. 2011, Ray et al. 2009, Rufino & Boccaccini 2013, Seibert et al.
  2011, Young-Lundquist et al. 2012). These matrices are first published in the
  deposit (as for the personal-communication matrices of warne_2019_nonwesterng).
and, in addition, every cell is a short decimal (at most 3 places) and the N is
the single N the authors reported. Samples whose cells (all or some) are
full-precision values (computed by the meta-analysts from data sets the authors
sent), whose N the meta-analysts averaged or replaced, whose provenance the
deposit does not record, or which are combined data sets, are held (see
held.csv). No mean/SD rows: the M and SD files hold values the meta-analysts
computed (full precision; some converted from manual tables).

Modification (2026-11-18): reshaped to the long lower-triangle layout in
data/covariance/README.md, one table per instrument and one group per sample (the
deposit's Study label); values unchanged.

Usage: python3 data/covariance/osf_ruchensky2018_ppi.py <out dir>
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

CORR = {"ruchensky_2018_ppi8": "https://osf.io/download/v438p/",
        "ruchensky_2018_ppir8": "https://osf.io/download/h4zgw/"}
CHECK = "https://osf.io/download/a9x5q/"
SHEET = {"ruchensky_2018_ppi8": "PPI", "ruchensky_2018_ppir8": "PPI-R"}
VARS = {"ruchensky_2018_ppi8": ["ME", "SP", "F", "C", "IN", "BE", "CN", "STI"],
        "ruchensky_2018_ppir8": ["ME", "SOI", "F", "C", "RN", "BE", "CN", "STI"]}
# Study label -> (basis, a phrase the checking sheet's provenance cells must contain)
SELECT = {
    "ruchensky_2018_ppi8": {
        "Curry et al. (2011)": ("article", "we used the data from the article"),
        "Neumann et al. (2008)": ("article", "we used the publication"),
        "Sadeh and Verona (2008)": ("author output", "sent us the output and dataform"),
        "Mahaffey & Marcus (2006)": ("author output", "database and dataform from the author"),
        "Marcus & Hammack (unpublished)": ("author output", "database and dataform from the author"),
    },
    "ruchensky_2018_ppir8": {
        "Hughes et al. (2013)": ("article", "we used the article"),
        "Ray & Jones (2012)": ("article", "we used the article"),
        "PPI-R Manual (Lilienfeld & Widows, 2005)": ("article", "PPI-R manual has the correlation matrix"),
        "Denson et al. (2009)": ("author output", "sent Ed the output"),
        "LaMarre & Carlson (2009)": ("author output", "dataform"),
        "Miller et al. (2011)": ("author output", "sent us the output"),
        "Ray et al. (2009)": ("author output", "sent us output with an N of 85"),
        "Rufino & Bocaccini (2013)": ("author output", "sent us the output"),
        "Seibert et al. (2011)": ("author output", "on the dataform"),
        "Young-Lundquist et al. (2012)": ("author output", "sent us the output"),
    },
}


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
    """A stored number as text (shortest repr); stops on non-numbers and > 3 decimals."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise SystemExit(f"non-numeric correlation {v!r}")
    s = str(int(v)) if float(v).is_integer() else repr(float(v))
    if "e" in s or ("." in s and len(s.split(".")[1]) > 3):
        raise SystemExit(f"not a short decimal: {s}")
    return s


def norm(s):
    return " ".join(str(s).split()).lower()


def checking(wb, sheet):
    """Study number -> (citation, provenance text, updated N); and number -> sample description."""
    prov = {}
    for r in list(wb[sheet].iter_rows(values_only=True))[1:]:
        if r[0] is None:
            continue
        text = " | ".join(str(x) for x in (r[2], r[5], r[9]) if x is not None)
        prov[r[0]] = (r[1], text, r[12])
    desc = {}
    name = next(s for s in wb.sheetnames if s.startswith(sheet + " - Checking Sample"))
    for r in list(wb[name].iter_rows(values_only=True))[1:]:
        if r[0] is not None:
            desc[r[0]] = (r[4] or "").strip()
    return prov, desc


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    chk = openpyxl.load_workbook(io.BytesIO(get(CHECK)), read_only=True, data_only=True)
    for table, url in CORR.items():
        prov, desc = checking(chk, SHEET[table])
        V = VARS[table]
        rows = list(openpyxl.load_workbook(io.BytesIO(get(url)), read_only=True,
                                           data_only=True).worksheets[0].iter_rows(values_only=True))
        hdr = list(rows[0])
        if hdr[:3] != ["Study", "Number", "Type"] or hdr[3:31] != [f"c{i}" for i in range(1, 29)] or hdr[31] != "n":
            raise SystemExit(f"{table}: unexpected header {hdr}")
        pairs = [(i, j) for i in range(8) for j in range(i + 1, 8)]   # c1..c28, row-wise upper triangle
        long, records, seen = [], [], set()
        for r in rows[1:]:
            if r[0] is None or r[0] not in SELECT[table]:
                continue
            label, num, typ, n = r[0], r[1], r[2], r[31]
            basis, phrase = SELECT[table][label]
            cite, ptext, n_upd = prov[num]
            if norm(label).split()[0] != norm(cite).split()[0]:
                raise SystemExit(f"{table} {label}: checking sheet row {num} is {cite!r}")
            if norm(phrase) not in norm(ptext):
                raise SystemExit(f"{table} {label}: provenance changed: {ptext!r}")
            if "average" in norm(ptext):
                raise SystemExit(f"{table} {label}: N averaged: {ptext!r}")
            if not isinstance(n, int) or n <= 0 or n != n_upd:
                raise SystemExit(f"{table} {label}: N {n!r} vs checking sheet {n_upd!r}")
            if typ not in (0, 1):
                raise SystemExit(f"{table} {label}: Type {typ!r}")
            cell = {}
            for k, (i, j) in enumerate(pairs):
                v = r[3 + k]
                s = txt(v)
                if abs(float(v)) >= 1:
                    raise SystemExit(f"{table} {label}: |r| >= 1 at c{k + 1}")
                cell[(j, i)] = s
            for a in range(8):
                for b in range(a + 1):
                    long.append({"stat": "cor", "var1": V[a], "var2": V[b],
                                 "value": "1" if a == b else cell[(a, b)], "n": n, "group": label})
            seen.add(label)
            records.append({"group": label, "number": num, "type": typ, "n_obs": n, "basis": basis,
                            "provenance": ptext, "sample": desc.get(num, "")})
        missing = set(SELECT[table]) - seen
        if missing:
            raise SystemExit(f"{table}: selected samples not found: {sorted(missing)}")
        with open(out / f"{table}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
            w.writeheader()
            w.writerows(long)
        with open(out / f"{table}_records.json", "w") as f:
            json.dump({"table": table, "variables": V, "records": records}, f, indent=1, ensure_ascii=False)
        print(f"wrote {table}.csv: {len(records)} samples")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_ruchensky2018_ppi.py <out dir>")
    main(sys.argv[1])
