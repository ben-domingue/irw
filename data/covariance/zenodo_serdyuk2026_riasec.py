"""Covariance family (irw_cov, source = "cov"): Serdyuk et al. (2026) 18-item RIASEC inventory, Ukraine, four groups.

Source: Zenodo record 22639698 (https://doi.org/10.5281/zenodo.22639698),
"Vocational interest profiles of ICT students and IT professionals in Ukraine:
group-level data and analysis code" (Serdyuk A, Vakaliuk TA, Antoniuk DS,
Vyhovska OA, 2026). Licence (record and LICENSE-CC-BY-4.0.txt): data,
questionnaires and documents CC BY 4.0; code MIT. The article is submitted to
SN Social Sciences; no published paper was found on Crossref (2026-11-17), so
the dataset is cited.

zenodo_package.zip, data/:
- groups_item_corr_{FY,UY,IT,UNI}.csv: 18 x 18 Pearson correlations among the
  items R1 ... C3, rounded to 4 decimals by the depositors. Computed by the
  depositors from individual responses that are not public (README).
- groups_item_stats.csv (FY, UY, IT) and groups_item_stats_UNI.csv: per-item n,
  mean, sd; written as `mean` / `sd` rows. Response frequencies f1-f4 are not
  part of the layout.
Group n (CODEBOOK.md): FY 83 (first-year ICT students; ICT-adapted item
version), UY 67 (ICT students years 2-4), IT 39 (IT professionals), UNI 265
(all years 2-4 respondents across six faculties; UY is its ICT subset). Every
item was mandatory, so there are no missing responses and n is the group n.
R, E and C items differ in content between the ICT (FY) and general versions.

Checks: each matrix is square with the item order of the header, symmetric,
unit diagonal, |r| < 1 off the diagonal; item stats n equals the group n.
Values are written in shortest round-trip form of the deposited decimals
(unchanged).

Modification (2026-11-17): full matrices reduced to the long lower-triangle
layout in data/covariance/README.md, one group per sample (FY, UY, IT, UNI);
item means and SDs added as moment rows.

Usage: python3 data/covariance/zenodo_serdyuk2026_riasec.py <out dir>
"""
import csv
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = "https://zenodo.org/api/records/22639698/files/zenodo_package.zip/content"
TABLE = "serdyuk_2026_riasec18"
GROUPS = {"FY": 83, "UY": 67, "IT": 39, "UNI": 265}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def rows(z, name):
    return list(csv.reader(io.StringIO(z.read(name).decode("utf-8"))))


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(io.BytesIO(get(URL)))
    stats = {}
    for r in csv.DictReader(io.StringIO(z.read("data/groups_item_stats.csv").decode())):
        stats[(r["group"], r["item"])] = r
    for r in csv.DictReader(io.StringIO(z.read("data/groups_item_stats_UNI.csv").decode())):
        stats[("UNI", r["item"])] = r
    long, records = [], []
    for g, n in GROUPS.items():
        m = rows(z, f"data/groups_item_corr_{g}.csv")
        items = m[0][1:]
        if len(items) != 18 or [r[0] for r in m[1:]] != items:
            raise SystemExit(f"{g}: row and column names differ")
        val = {(a, b): float(x) for r in m[1:] for a, b, x in
               ((r[0], c, x) for c, x in zip(items, r[1:]))}
        for a in items:
            if val[(a, a)] != 1:
                raise SystemExit(f"{g}: diagonal {a}")
            for b in items:
                if val[(a, b)] != val[(b, a)]:
                    raise SystemExit(f"{g}: asymmetric {a}-{b}")
                if a != b and abs(val[(a, b)]) >= 1:
                    raise SystemExit(f"{g}: |r| >= 1 {a}-{b}")
        for k, a in enumerate(items):
            for b in items[:k + 1]:
                long.append({"stat": "cor", "var1": a, "var2": b,
                             "value": "1" if a == b else repr(val[(a, b)]),
                             "n": n, "group": g})
        for stat in ("sd", "mean"):
            for a in items:
                s = stats[(g, a)]
                if int(s["n"]) != n:
                    raise SystemExit(f"{g}: item stats n {s['n']}")
                long.append({"stat": stat, "var1": a, "var2": "",
                             "value": repr(float(s[stat])), "n": n, "group": g})
        records.append({"group": g, "n_obs": n, "vars": items})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": []}, f, indent=1)
    print(f"wrote {TABLE}.csv: {len(records)} groups built")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 zenodo_serdyuk2026_riasec.py <out dir>")
    main(sys.argv[1])
