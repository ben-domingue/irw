"""Covariance family (irw_cov, source = "cov"): Scherhag et al. (2026) HEXACO + Disintegration MASEM.

Source: Zenodo record 8303338 (https://doi.org/10.5281/zenodo.8303338), "Dataset
for MASEM HEXACO-D", CC BY 4.0: the coded studies of Scherhag, Bosnjak,
Burgard, Lazarevic & Knezevic (2026), "Does Disintegration qualify as a separate
trait extending the HEXACO model? A preregistered meta-analysis exploring
discriminant validity", Collabra: Psychology, 12(1), 162289,
https://doi.org/10.1525/collabra.162289. Preregistration and codebook: OSF dz3mc.

Data_MASEM_HEXACO-D.xlsx has one row per sample with the 21 raw (uncorrected)
correlations among the HEXACO domain scores H, E, X, A, C, O and Disintegration
(D) in columns o_r_HE ... o_r_OD, and the sample size o_ni. Per the codebook,
o_r_compute = 1 means the authors computed the correlations from raw total
scores rather than copying reported ones (Ben, 2026-11-17: matrices computed
from microdata are included, with a note). o_r_facetlvl only says facet-level
correlations also exist and does not affect these values. The alphas (o_rel_*,
"Cronbach's alpha of the ... scale" in the codebook) are written as `rel` rows
for the domains in that sample's matrix, as stored; a blank alpha is skipped.

A variable with no correlation in a sample was not measured there and is
dropped (Ben, 2026-11-17); a sample still holding a blank cell is not built and
is printed. A sample with an off-diagonal correlation of +-1 is a coding slip
(Knezevic2023a study 4 has E-X = 1 with identical E and X columns) and is not
built either. Values are written in shortest round-trip form, i.e. as stored.

Modification (2026-11-17): reshaped to the long lower-triangle layout in
data/covariance/README.md, one group per sample, labelled
"<report_ID> study <study_ID> sample <sample_ID>".
Modification (2026-11-18): Cronbach's alpha per domain (o_rel_*) added as
`rel` rows after each sample's matrix rows.

Usage: python3 data/covariance/zenodo_scherhag2026_hexacod.py <out dir>
"""
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

import openpyxl

URL = "https://zenodo.org/api/records/8303338/files/Data_MASEM_HEXACO-D.xlsx/content"
TABLE = "scherhag_2026_hexacod7"
V = ["H", "E", "X", "A", "C", "O", "D"]
K = len(V)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def num(x):
    if x is None or isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    try:
        return float(str(x).strip())
    except ValueError:
        raise SystemExit(f"unreadable correlation {x!r}")


def label(x):
    return str(int(x)) if isinstance(x, float) and x.is_integer() else str(x).strip()


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ws = openpyxl.load_workbook(io.BytesIO(get(URL)), read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    ix = {k: i for i, k in enumerate(rows[0]) if k}
    long, records, held, unity = [], [], [], []
    for r in rows[1:]:
        if not r[0]:
            continue
        group = f"{str(r[0]).strip()} study {label(r[ix['study_ID']])} sample {label(r[ix['sample_ID']])}"
        if any(rec["group"] == group for rec in records) or group in held:
            raise SystemExit(f"duplicate group {group}")
        ni = int(r[ix["o_ni"]])
        M = [[None] * K for _ in range(K)]
        for i in range(K):
            M[i][i] = 1.0
            for j in range(i):
                M[i][j] = M[j][i] = num(r[ix[f"o_r_{V[j]}{V[i]}"]])
        keep = [i for i in range(K) if any(M[i][j] is not None for j in range(K) if j != i)]
        dropped = [V[i] for i in range(K) if i not in keep]
        if len(keep) < 2 or any(M[i][j] is None for a, i in enumerate(keep) for j in keep[:a]):
            held.append(group)
            continue
        if any(abs(M[i][j]) >= 1 for a, i in enumerate(keep) for j in keep[:a]):
            # Knezevic2023a study 4: E-X = 1 and the E and X columns are identical, a coding slip
            unity.append(group)
            continue
        for a, i in enumerate(keep):
            for j in keep[:a + 1]:
                long.append({"stat": "cor", "var1": V[i], "var2": V[j],
                             "value": "1" if i == j else repr(M[i][j]), "n": ni, "group": group})
        for i in keep:   # Cronbach's alpha as stored; blank skipped
            a = num(r[ix[f"o_rel_{V[i]}"]])
            if a is None:
                continue
            if not 0 < a <= 1:
                raise SystemExit(f"{group}: alpha {a} for {V[i]} out of range")
            long.append({"stat": "rel", "var1": V[i], "var2": "", "value": repr(a), "n": ni, "group": group})
        records.append({"group": group, "n_obs": ni, "dropped": dropped,
                        "computed": int(r[ix["o_r_compute"]] or 0),
                        "population": ", ".join(str(r[ix[c]]).strip() for c in ("s_targetpop", "t_country")
                                                if r[ix[c]] not in (None, "")),
                        "note": str(r[ix["notes"]] or "").strip()})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / "records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held, "unity": unity}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} samples built, {len(held)} held {held}, "
          f"{len(unity)} held for an off-diagonal correlation of 1 {unity}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 zenodo_scherhag2026_hexacod.py <out dir>")
    main(sys.argv[1])
