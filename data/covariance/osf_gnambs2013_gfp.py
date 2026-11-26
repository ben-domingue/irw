"""Covariance family (irw_cov, source = "cov"): Gnambs (2013) self- and peer-rated Big Five correlation matrices.

Source: OSF project 7hdqx, "The elusive general factor of personality: The
acquaintance effect" (data and scripts for Gnambs, T. (2013). The elusive
general factor of personality: The acquaintance effect. European Journal of
Personality, 27(5), 507-520, https://doi.org/10.1002/per.1933).
Licence: CC BY 4.0 (stated on the node).

One deposit file is read, data/data.xls (OSF file ycrj4), with xlrd:
- sheet "Codings": one row per coded multi-informant matrix (83 rows), giving
  study label, dependency id (rows with the same `dependent` share a sample),
  publication type, country, N (n), number of women (female), type of peer
  rater (peers), number of peers (npeers), length of acquaintance in months
  (duration), mean age (age), self- and peer-report instruments and their
  lengths, the SD (sdos ... sdnp) and reliability (relos ... relnp) of each of
  the five trait scores in self- and peer-reports, and the correlations of the
  10 x 10 multi-informant matrix: within self-reports (ocss = openness with
  conscientiousness, both self-rated), within peer-reports (ocpp) and across
  informants (ocsp = openness self-rated with conscientiousness peer-rated;
  cosp is the other cell). The last columns are inter-rater reliabilities of
  multiple peers (cono ...), not used.
- sheet "Codebook": the meaning of the columns, quoted above.

Each row is one group, labelled "<study> #<k>" (k = the row's order among the
rows of that study in the sheet). Variables are Os Cs Es As Ns (self) and Op Cp
Ep Ap Np (peer). A variable with no reported correlation in a row is dropped
from that row's matrix; a cell among the remaining variables that the row
does not report is written as an empty value (blank cells allowed, Ben,
2026-11-18). Many rows report only the five self-peer agreement
correlations, so their matrices are mostly blank. SDs and reliabilities are
written as `sd` and `rel` rows for variables kept in the matrix, as stored
(SDs are on each instrument's own score scale), except the SDs of
westerlund2009 #1 and ashton2009 #1, which look averaged by the meta-analyst
(SD_SKIP below). The deposit does not say
whether the correlations are Pearson; matrix_type is "unknown".

Values are as stored (two decimals as printed); no off-diagonal |r| >= 1. The
deposit's R syntax caps N at 800 for the analyses; the stored N is used here.

Modification (2026-11-18): reshaped to the long lower-triangle layout in
data/covariance/README.md; group labels added as described.

Usage: python3 data/covariance/osf_gnambs2013_gfp.py <out dir>
"""
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import xlrd

URL = "https://osf.io/download/ycrj4/"
TABLE = "gnambs_2013_gfp10"
T = "ocean"
V = [t.upper() + r for r in "sp" for t in T]          # Os Cs Es As Ns Op Cp Ep Ap Np
# SDs not written: their stored values are not two-decimal printed values but look like
# the meta-analyst's averages (westerlund2009: 9.504999999999999, 1.1250000000000002, i.e. a
# spreadsheet formula result; ashton2009: 0.605, 0.625 among two-decimal values).
SD_SKIP = {"westerlund2009 #1", "ashton2009 #1"}
NAME = dict(o="openness", c="conscientiousness", e="extraversion", a="agreeableness", n="neuroticism")


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
    if isinstance(v, bool) or not isinstance(v, float):
        raise SystemExit(f"non-numeric value {v!r}")
    return str(int(v)) if v.is_integer() else repr(v)


def cells(get_col):
    """{(var_i, var_j): value} for every coded correlation, var order as V."""
    out = {}
    for r in "sp":                                   # within an informant
        for a, x in enumerate(T):
            for y in T[a + 1:]:
                out[(x.upper() + r, y.upper() + r)] = get_col(f"{x}{y}{r}{r}")
    for x in T:                                      # across informants
        for y in T:
            out[(x.upper() + "s", y.upper() + "p")] = get_col(f"{x}{y}sp")
    return out


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ws = xlrd.open_workbook(file_contents=get(URL)).sheet_by_name("Codings")
    hdr = ws.row_values(0)
    col = {h: j for j, h in enumerate(hdr) if h}
    long, records, held, count = [], [], [], {}
    for i in range(1, ws.nrows):
        r = ws.row_values(i)
        study = str(r[col["study"]]).strip()
        count[study] = count.get(study, 0) + 1
        label = f"{study} #{count[study]}"
        n = r[col["n"]]
        if not isinstance(n, float) or not n.is_integer() or n <= 0:
            raise SystemExit(f"{label}: bad N {n!r}")
        n = int(n)
        c = cells(lambda k: r[col[k]])
        if len(c) != 45:
            raise SystemExit("cell map is not 45 cells")
        rep = {k: txt(v) for k, v in c.items() if v != ""}
        if any(abs(float(v)) >= 1 for v in rep.values()):
            held.append((label, "|r| >= 1"))
            continue
        keep = [v for v in V if any(v in k for k in rep)]
        if len(keep) < 2:
            held.append((label, "fewer than two variables with a reported correlation"))
            continue
        blank = 0
        for a, x in enumerate(keep):
            for y in keep[:a + 1]:
                v = "1" if x == y else rep.get((y, x), rep.get((x, y), ""))
                blank += v == ""
                long.append({"stat": "cor", "var1": x, "var2": y, "value": v, "n": n, "group": label})
        moments = {}
        for stat, pre in (("sd", "sd"), ("rel", "rel")):
            if stat == "sd" and label in SD_SKIP:
                continue
            for v in keep:
                x = r[col[f"{pre}{v[0].lower()}{v[1]}"]]
                if x != "":
                    if stat == "rel" and not 0 < x <= 1:
                        raise SystemExit(f"{label}: reliability {x}")
                    long.append({"stat": stat, "var1": v, "var2": "", "value": txt(x), "n": n, "group": label})
                    moments.setdefault(stat, []).append(v)
        records.append({"group": label, "n_obs": n, "vars": keep, "n_reported": len(rep), "n_blank": blank,
                        "moments": moments,
                        **{k: r[col[k]] for k in ("dependent", "pubtype", "country", "female", "peers", "npeers",
                                                  "duration", "age", "scales", "itemss", "scalep", "itemsp")}})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "variables": {v: f"{NAME[v[0].lower()]}, {'self' if v[1] == 's' else 'peer'}-report"
                                                 for v in V},
                   "records": records, "held": held}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} matrices built, {len(held)} held {held}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 osf_gnambs2013_gfp.py <out dir>")
    main(sys.argv[1])
