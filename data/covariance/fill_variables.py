"""Fill the `variables` column of data/covariance/matrices.csv from built table CSVs.

`variables` (Ben, 2026-11-18, #3594) records each matrix's variables in the
source's published order, separated by " | ", each optionally followed by
" = description". Redivis does not keep row order, so the order lives here.

The build scripts write every matrix in published order, one diagonal row per
variable, so the order is the order of a group's diagonal rows in the built CSV.
Descriptions come from variable_labels.csv (table, var, description, source),
which records where each label was taken from. A description already in
`variables` is kept; a name without one gets the label when there is one. A
value already present is checked against the built CSV (same names, once each). It refuses a group whose CSV it cannot find, whose
diagonal is missing a variable, or whose existing value names a different set.

Usage: python3 data/covariance/fill_variables.py <dir with built table CSVs> [...]
       (searched recursively; the first <table>.csv found is used)
"""
import csv
import sys
from collections import OrderedDict
from pathlib import Path

MATRICES = Path(__file__).with_name("matrices.csv")
LABELS = Path(__file__).with_name("variable_labels.csv")
SEP = " | "


def order_from_csv(path):
    """{group: [variables in diagonal-row order]} for one built table CSV."""
    groups = OrderedDict()
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            g = r.get("group", "") or ""
            seen = groups.setdefault(g, {"diag": [], "all": set()})
            seen["all"].update([r["var1"]] + ([r["var2"]] if r.get("var2") else []))
            if r["stat"] in ("cor", "cov") and r["var1"] == r["var2"] and r["var1"] not in seen["diag"]:
                seen["diag"].append(r["var1"])
    out = {}
    for g, s in groups.items():
        if set(s["diag"]) != s["all"]:
            raise SystemExit(f"{path} group {g!r}: variables without a diagonal row: {sorted(s['all'] - set(s['diag']))}")
        out[g] = s["diag"]
    return out


def names(value):
    return [e.split(" = ", 1)[0] for e in value.split(SEP)]


def main(dirs):
    built = {}
    for d in dirs:
        for p in sorted(Path(d).rglob("*.csv")):
            built.setdefault(p.stem, p)
    with open(MATRICES, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames)
        rows = list(reader)
    if "variables" not in cols:
        cols.append("variables")
    labels = {}
    if LABELS.exists():
        with open(LABELS, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if "|" in r["description"] or " = " in r["var"]:
                    raise SystemExit(f"variable_labels.csv: bad entry {r}")
                labels[(r["table"], r["var"])] = r["description"]
    used = set()
    cache, filled, kept = {}, 0, 0
    for r in rows:
        t = r["table"]
        if t not in built:
            raise SystemExit(f"{t}: no built CSV found")
        if t not in cache:
            cache[t] = order_from_csv(built[t])
        order = cache[t].get(r["group"])
        if order is None:
            raise SystemExit(f"{t} group {r['group']!r}: not in {built[t]}")
        cur = (r.get("variables") or "").strip()
        if cur:
            if sorted(names(cur)) != sorted(order) or len(set(names(cur))) != len(names(cur)):
                raise SystemExit(f"{t} group {r['group']!r}: variables {names(cur)} != built {order}")
            entries = cur.split(SEP)
            kept += 1
        else:
            entries = list(order)
            filled += 1
        out = []
        for e in entries:
            if " = " not in e and (t, e) in labels:
                e = f"{e} = {labels[(t, e)]}"
                used.add((t, e.split(" = ", 1)[0]))
            elif " = " in e:
                used.add((t, e.split(" = ", 1)[0]))
            out.append(e)
        r["variables"] = SEP.join(out)
        if any("|" in v for v in order):
            raise SystemExit(f"{t}: a variable name contains '|'")
    unused = sorted(k for k in labels if k not in used and k[0] in cache)
    if unused:
        print(f"note: {len(unused)} labels name no variable in any group, e.g. {unused[:5]}")
    with open(MATRICES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n")
        w.writeheader()
        for r in rows:
            r = dict(r)
            r["n_obs"] = int(r["n_obs"])
            w.writerow(r)
    print(f"{filled} filled, {kept} kept, {len(rows)} rows, {len(cache)} tables")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
