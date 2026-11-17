"""Checks for covariance-matrix tables (the `irw_cov` family, `source = "cov"`).

A cov table holds one published correlation or covariance matrix, not responses:
one row per cell of the lower triangle (diagonal included), plus optional rows for
each variable's SD and mean. The layout is the draft standard in
`data/covariance/README.md`. Its rules are numbered V1-V8 so they cannot be
confused with the core standard's C1-C7, conjoint's J1-J8 or rankings' R1-R8.

There is no `id`, `item` or `resp`, so the core checks would fail every table at
C1; this module runs instead of them, and a contributor can check a table first:

    python3 -m irw_validate.cov table.csv [table.csv ...]

A matrix that is not positive definite is reported (V8, a warning) and never
blocked. Published matrices are often non-PD through rounding, pairwise deletion
or a typo in the original (Burt 1915), and the table keeps the numbers as
published; the user needs to know, and `cov_metadata` carries the flag.

No PII screen runs: a cov table holds no row per person, and its variable names
are test or scale names.

Exit codes as for `irw-validate`: 0 ok, 1 something blocks, 2 bad input.
"""
from __future__ import annotations

import sys
from pathlib import Path

from .extra import check_name
from .model import Finding, Report

REQUIRED = ("stat", "var1", "var2", "value", "n")
OPTIONAL = ("group",)
MATRIX_STATS = {"cor", "cov"}
MOMENT_STATS = {"sd", "mean"}
#: Published correlations are rounded to two or three places; a diagonal of
#: 0.9995 or an |r| of 1.0004 is rounding, not an error.
TOL = 1e-3


def _f(check: str, severity: str, message: str, table: str, details: tuple = ()) -> Finding:
    return Finding(check, severity, message, table=table, group="cov", details=details)


def _blank(s):
    return s.isna() | (s.astype(str).str.strip() == "")


def _check_matrix(sub, gname, table, out, stats):
    """V4, V5 and V8 for one group's matrix rows. Returns the variable order."""
    import numpy as np
    where = f" (group {gname})" if gname is not None else ""
    start = len(out)
    kinds = set(sub["stat"])
    if len(kinds) > 1:
        out.append(_f("cov_stat", "error", f"[V2] both cor and cov rows{where}; one matrix per group", table))
        return []
    kind = kinds.pop()
    # variable order: first appearance across var1 then var2, which for a lower
    # triangle written row by row is the published order
    order = list(dict.fromkeys(list(sub["var1"]) + list(sub["var2"])))
    pos = {v: i for i, v in enumerate(order)}
    k = len(order)
    m = np.full((k, k), np.nan)
    seen = set()
    dup = []
    for a, b, v in zip(sub["var1"], sub["var2"], sub["value"]):
        key = frozenset((a, b))
        if key in seen:
            dup.append(f"{a}~{b}")
            continue
        seen.add(key)
        m[pos[a], pos[b]] = m[pos[b], pos[a]] = v
    if dup:
        out.append(_f("cov_cells", "error", f"[V4] {len(dup)} cells given twice{where}: {dup[:4]}",
                      table, tuple(dup)))
    missing = int(np.isnan(m).sum())
    if missing:
        holes = [f"{order[i]}~{order[j]}" for i in range(k) for j in range(i + 1) if np.isnan(m[i, j])]
        out.append(_f("cov_cells", "error",
                      f"[V4] {len(holes)} cells missing from the lower triangle{where}: {holes[:4]}; "
                      "a cell the source left blank is not a table this family can hold",
                      table, tuple(holes)))
        return order
    d = np.diag(m)
    if kind == "cor":
        off = np.abs(d - 1) > TOL
        if off.any():
            out.append(_f("cov_values", "error",
                          f"[V5] cor diagonal not 1 for {[order[i] for i in np.where(off)[0]][:4]}{where}", table))
        big = int((np.abs(m[np.tril_indices(k, -1)]) > 1 + TOL).sum())
        if big:
            out.append(_f("cov_values", "error", f"[V5] {big} correlations outside [-1, 1]{where}", table))
    else:
        if (d <= 0).any():
            out.append(_f("cov_values", "error", f"[V5] cov diagonal has a variance <= 0{where}", table))
        else:
            r = m / np.sqrt(np.outer(d, d))
            big = int((np.abs(r[np.tril_indices(k, -1)]) > 1 + TOL).sum())
            if big:
                out.append(_f("cov_values", "error",
                              f"[V5] {big} covariances imply a correlation outside [-1, 1]{where}", table))
    if all(f.severity != "error" for f in out[start:]):
        ev = float(np.linalg.eigvalsh(m).min())
        stats.setdefault("min_eigenvalue", {})[gname if gname is not None else ""] = ev
        if ev <= 0:
            out.append(_f("cov_pd", "warn",
                          f"[V8] matrix is not positive definite{where} (smallest eigenvalue {ev:.4g}); "
                          "kept as published, flagged in cov_metadata", table))
    stats.setdefault("matrix_type", {})[gname if gname is not None else ""] = kind
    stats.setdefault("n_vars", {})[gname if gname is not None else ""] = k
    return order


def validate_cov_frame(df, *, label: str = "") -> Report:
    """Check one cov table against rules V1-V8."""
    import pandas as pd
    table = Path(label).stem if label else ""
    report = Report(label=label, profile="upload", kind="cov")
    out = report.findings
    report.checks_run = ["cov_required_columns", "cov_stat", "cov_cells", "cov_values",
                         "cov_moments", "cov_n", "cov_columns", "cov_pd"]
    cols = list(df.columns)

    # V1: required columns; stat, var1, value and n never blank
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        out.append(_f("cov_required_columns", "error", f"[V1] missing required column(s): {', '.join(missing)}", table))
        out.extend(check_name(table))
        return report
    for c in ("stat", "var1", "value", "n"):
        nb = int(_blank(df[c]).sum())
        if nb:
            out.append(_f("cov_required_columns", "error", f"[V1] {nb} rows with no {c}", table))

    # V7 (columns): nothing undefined
    undefined = [c for c in cols if c not in REQUIRED + OPTIONAL]
    if undefined:
        out.append(_f("cov_columns", "error", f"[V7] column(s) with no defined meaning: {', '.join(undefined)}",
                      table, tuple(undefined)))

    # V2: stat vocabulary
    stat = df["stat"].astype(str).str.strip()
    bad = sorted(set(stat) - MATRIX_STATS - MOMENT_STATS)
    if bad:
        out.append(_f("cov_stat", "error", f"[V2] stat value(s) {bad[:5]}; allowed: cor, cov, sd, mean", table))

    # V6: value numeric, n a positive integer
    val = pd.to_numeric(df["value"], errors="coerce")
    nonnum = int((val.isna() & ~_blank(df["value"])).sum())
    if nonnum:
        out.append(_f("cov_values", "error", f"[V6] {nonnum} value entries are not numbers", table))
    n = pd.to_numeric(df["n"], errors="coerce")
    badn = int(((n % 1 != 0) | (n < 1) | (n.isna() & ~_blank(df["n"]))).sum())
    if badn:
        out.append(_f("cov_n", "error", f"[V6] n: {badn} values that are not positive integers", table))
    if out and any(f.severity == "error" for f in out):
        out.extend(check_name(table))
        return report

    df = df.assign(stat=stat, value=val, n=n.astype(int),
                   var1=df["var1"].astype(str).str.strip(),
                   var2=df["var2"].where(~_blank(df["var2"]), None))
    df["var2"] = df["var2"].map(lambda x: None if x is None or pd.isna(x) else str(x).strip())
    if "group" in cols and _blank(df["group"]).any():
        ## groupby drops a blank group, so its rows were never checked at all.
        out.append(_f("cov_group", "error",
                      f"{int(_blank(df['group']).sum())} rows with a blank group (a table with a group column needs one on every row)", table))
        out.extend(check_name(table))
        return report
    groups = [(None, df)] if "group" not in cols else [(g, s) for g, s in df.groupby("group", sort=False, dropna=False)]
    report.stats["n_groups"] = len(groups)
    for gname, sub in groups:
        where = f" (group {gname})" if gname is not None else ""
        mat = sub[sub["stat"].isin(MATRIX_STATS)]
        mom = sub[sub["stat"].isin(MOMENT_STATS)]
        # V3: cell rows name two variables, moment rows one
        if mat["var2"].isna().any():
            out.append(_f("cov_cells", "error", f"[V3] {int(mat['var2'].isna().sum())} cor/cov rows with no var2{where}", table))
            continue
        if mom["var2"].notna().any():
            out.append(_f("cov_moments", "error", f"[V3] {int(mom['var2'].notna().sum())} sd/mean rows with a var2{where}", table))
        if mat.empty:
            out.append(_f("cov_cells", "error", f"[V4] no cor or cov rows{where}", table))
            continue
        order = _check_matrix(mat, gname, table, out, report.stats)
        # V7 (moments): one per variable, for variables in the matrix, sd > 0
        for s in ("sd", "mean"):
            r = mom[mom["stat"] == s]
            stray = sorted(set(r["var1"]) - set(order))
            if stray:
                out.append(_f("cov_moments", "error", f"[V7] {s} for variable(s) not in the matrix{where}: {stray[:4]}", table))
            if r["var1"].duplicated().any():
                out.append(_f("cov_moments", "error", f"[V7] a variable has two {s} rows{where}", table))
        if ((mom["stat"] == "sd") & (mom["value"] <= 0)).any():
            out.append(_f("cov_moments", "error", f"[V7] sd <= 0{where}", table))
        report.stats.setdefault("has_sd", {})[gname if gname is not None else ""] = bool((mom["stat"] == "sd").any())
        report.stats.setdefault("n_obs", {})[gname if gname is not None else ""] = int(mat["n"].max())
    report.stats["n_rows"] = int(len(df))
    out.extend(check_name(table))
    return report


def validate_cov_file(path, *, label: str | None = None) -> Report:
    import pandas as pd
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, low_memory=False, keep_default_na=False, na_values=[""])
    return validate_cov_frame(df, label=label or str(path))


def main(argv=None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print(__doc__.strip().splitlines()[0])
        print("usage: python3 -m irw_validate.cov table.csv [...]")
        return 2
    worst = 0
    for p in args:
        try:
            r = validate_cov_file(p)
        except (FileNotFoundError, ValueError) as exc:
            print(f"{p}: cannot read ({exc})")
            worst = max(worst, 2)
            continue
        s = r.stats
        status = "blocked" if r.errors else "passes"
        print(f"{p}: {status} (cov draft standard; {s.get('n_groups', '?')} group(s), "
              f"vars {s.get('n_vars', '?')}, N {s.get('n_obs', '?')})")
        for f in r.findings:
            print(f"  {f.severity.upper():5} {f.check:22} {f.message}")
        if r.errors:
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    sys.exit(main())
