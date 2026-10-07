"""Checks for conjoint-experiment tables (the `irw_conjoint` source).

A conjoint table does not have the core layout. There is no `item` or `resp`:
one row is one respondent x task x profile, with the profile's attribute levels
in `attr_` columns and the answers in `choice` and/or `rating`. The layout is the
draft conjoint standard, written down in `data/conjoint/README.md`. Its rules are
numbered J1-J7 so they cannot be confused with the core standard's C1-C7.

The core checks (`validate_file`) would fail every one of these tables on C1, so
`red_up` runs this module instead for the `conj` source. It replaces the R
checker the first conjoint tables were built with (data/conjoint/check_conj.R),
so the rules live in one place.

    python3 -m irw_validate.conjoint table.csv [table.csv ...]

Exit codes as for `irw-validate`: 0 ok, 1 something blocks, 2 bad input.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from .extra import MIN_IDS, check_name
from .model import Finding, Report

REQUIRED = ("id", "task", "profile")
#: Named columns a conjoint table may carry besides the prefixed ones.
NAMED = {"id", "task", "profile", "choice", "rating", "rt", "date", "wave", "treat"}
PREFIXES = ("attr_", "attrpos_", "cov_", "trial_", "choice_", "rating_")
OUTCOME = re.compile(r"^(choice|rating)(_.+)?$")
CHOICE = re.compile(r"^choice(_.+)?$")
#: Column names that usually mean an identifier or a location was kept. A hint,
#: not a rule: the README's intake rules say to strip these at ingest.
PII = re.compile(r"(^|_)(ip(_?address)?|lat(itude)?|lon(gitude)?|lng|gps|prolific(_?id)?|"
                 r"worker(_?id)?|mturk(_?id)?|email|response_?id|respondent_?id_raw)($|_)", re.I)


def _f(check: str, severity: str, message: str, table: str, details: tuple = ()) -> Finding:
    return Finding(check, severity, message, table=table, group="conjoint", details=details)


def validate_conjoint_frame(df, *, label: str = "") -> Report:
    """Check one conjoint table against rules J1-J7 and the intake floor."""
    table = Path(label).stem if label else ""
    report = Report(label=label, profile="upload", kind="conjoint")
    out = report.findings
    cols = list(df.columns)
    report.checks_run = ["conj_required_columns", "conj_duplicates", "conj_outcomes",
                         "conj_choice", "conj_rating", "conj_attributes", "conj_columns",
                         "conj_pii_hint", "sample_floor"]

    # J1: rows and keys
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        out.append(_f("conj_required_columns", "error",
                      f"[J1] missing required column(s): {', '.join(missing)}", table))
    else:
        for c in REQUIRED:
            n = int(df[c].isna().sum())
            if n:
                out.append(_f("conj_required_columns", "error", f"[J1] {n} rows with no {c}", table))
        # J2: one row per respondent x task x profile
        dup = int(df.duplicated(list(REQUIRED)).sum())
        if dup:
            out.append(_f("conj_duplicates", "error",
                          f"[J2] {dup} duplicated id-task-profile rows", table))
        pt = df.groupby(["id", "task"]).size().value_counts().sort_index()
        report.stats["profiles_per_task"] = {int(k): int(v) for k, v in pt.items()}

    # J3: outcomes
    outcomes = [c for c in cols if OUTCOME.match(c)]
    if not outcomes:
        out.append(_f("conj_outcomes", "error",
                      "[J3] no outcome column (choice, rating, choice_<name>, rating_<name>)", table))
    for c in outcomes:
        vals = df[c].dropna()
        if CHOICE.match(c):
            bad = sorted(set(vals.unique()) - {0, 1})
            if bad:
                out.append(_f("conj_choice", "error", f"[J3] {c} is not 0/1 (also {bad[:5]})", table))
            elif not missing:
                s = df.dropna(subset=[c]).groupby(["id", "task"])[c].sum()
                many, none = int((s > 1).sum()), int((s == 0).sum())
                if many:
                    out.append(_f("conj_choice", "error",
                                  f"[J3] {c}: {many} tasks with more than one chosen profile", table))
                if none:
                    out.append(_f("conj_choice", "warn",
                                  f"[J3] {c}: {none} tasks with no chosen profile -- valid only "
                                  "when the design offered an opt-out; say so in the script header "
                                  "and the processing note", table))
        else:
            import pandas as pd  # deferred like core: red_up imports this module without pandas
            if not pd.api.types.is_numeric_dtype(df[c]):
                out.append(_f("conj_rating", "error", f"[J3] {c} is not numeric", table))
    if outcomes and not missing:
        allna = df[outcomes].isna().all(axis=1).sum()
        if allna:
            out.append(_f("conj_outcomes", "warn",
                          f"[J3] {int(allna)} rows with no outcome at all; omit them", table))

    # J4: attributes, as displayed text
    attrs = [c for c in cols if c.startswith("attr_")]
    if len(attrs) < 2:
        out.append(_f("conj_attributes", "error", f"[J4] {len(attrs)} attr_ column(s); at least 2", table))
    empty = [c for c in attrs if df[c].isna().all()]
    if empty:
        out.append(_f("conj_attributes", "error", f"[J4] attr_ column(s) entirely missing: {', '.join(empty)}",
                      table, tuple(empty)))
    import pandas as pd
    coded = [c for c in attrs if c not in empty and pd.api.types.is_numeric_dtype(df[c])
             and df[c].dropna().nunique() > 1 and (df[c].dropna() % 1 == 0).all()
             and df[c].dropna().max() <= 20]
    if coded:
        out.append(_f("conj_attributes", "warn",
                      f"[J4] attr_ column(s) look like numeric codes, not displayed text: "
                      f"{', '.join(coded)}. Fine if the levels really are numbers (an age, a size).",
                      table, tuple(coded)))

    # J7: column names
    undefined = [c for c in cols if c not in NAMED and not c.startswith(PREFIXES)]
    if undefined:
        out.append(_f("conj_columns", "error",
                      f"[J7] column(s) with no defined meaning: {', '.join(undefined)}",
                      table, tuple(undefined)))
    pii = [c for c in cols if PII.search(c)]
    if pii:
        out.append(_f("conj_pii_hint", "warn",
                      f"column name(s) suggest an identifier or a location: {', '.join(pii)}. "
                      "Platform IDs, IP addresses and coordinates are stripped at ingest.",
                      table, tuple(pii)))

    # intake policy
    if "id" in cols:
        n = int(df["id"].nunique())
        report.stats["n_respondents"] = n
        if n < MIN_IDS:
            out.append(_f("sample_floor", "warn",
                          f"{n} unique ids; IRW intake policy sets a flat floor of {MIN_IDS}", table))
    report.stats["n_rows"] = int(len(df))
    out.extend(check_name(table))
    return report


def validate_conjoint_file(path, *, label: str | None = None) -> Report:
    import pandas as pd
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, low_memory=False)
    return validate_conjoint_frame(df, label=label or str(path))


def main(argv=None) -> int:
    paths = (argv if argv is not None else sys.argv[1:])
    if not paths:
        print(__doc__.strip().splitlines()[0])
        print("usage: python3 -m irw_validate.conjoint table.csv [...]")
        return 2
    worst = 0
    for p in paths:
        try:
            r = validate_conjoint_file(p)
        except (FileNotFoundError, ValueError) as exc:
            print(f"{p}: cannot read ({exc})")
            worst = max(worst, 2)
            continue
        status = "blocked" if r.errors else "passes"
        print(f"{p}: {status} (conjoint draft standard; {r.stats.get('n_respondents', '?')} respondents, "
              f"{r.stats.get('n_rows', '?')} rows)")
        for f in r.findings:
            print(f"  {f.severity.upper():5} {f.check:22} {f.message}")
        if r.errors:
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    sys.exit(main())
