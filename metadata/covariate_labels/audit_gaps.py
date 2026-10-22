#!/usr/bin/env python3
"""Stage 0 of the covariate_labels generator: which LIVE tables ship coded
covariates that the build has never examined.

This exists because the thing that goes wrong is not running `build.py` -- it
is nobody knowing a harvest was owed. `cassidy_2024_*` (9 tables, 10 coded
covariates, every one labelled in its `.sav`) shipped on 2026-10-21 under a
batch log that said no harvest was needed, and nothing contradicted it: the
harvest is a manual stage, so a script that is never harvested produces no
error, no empty file and no row anywhere. It is invisible by construction.
The same shape produced the 36 empty logs in `harvest_empty.tsv` (#3155).

So this reports the gap from the COMMITTED record alone -- no
`~/.cache/irw/covariate_labels/logs`, no network, no re-running of any script
-- which is what lets it run anywhere, including CI:

    metadata/metadata.csv                     which tables are live
    metadata/table_scripts.csv                table -> the script(s) that built it
    metadata/column_docs.csv                  which cov_* columns each table ships
    data/*.py, data/*.R                       which of those read a labelled source
    metadata/covariate_labels.csv             which tables HAVE labels
    metadata/covariate_labels/coverage.csv    which pairs were considered, and why left out
    metadata/covariate_labels/harvest_empty.tsv   harvests that produced nothing

A live table is reported when it ships at least one `cov_*` column, its script
reads an SPSS/Stata file, and the table appears in neither
`covariate_labels.csv` nor `coverage.csv`. The `cov_*` requirement matters:
without it the report was 902 tables, a third of which ship no covariates at
all and so could never have a covariate label -- noise that would have got the
whole check ignored. That is a
deliberately weak claim -- "never examined", not "wrong". A table can be
legitimately absent from `covariate_labels.csv` for several good reasons (it
ships label strings rather than codes, its codes are a recode, fewer than half
its codes carry labels), but every one of those reasons is RECORDED IN
`coverage.csv`. Silence in both files means no one has looked, and that is the
only state this script treats as a defect.

Classes reported, because they need different actions:

  never_examined      no harvest log was ever built for this script.
                      -> harvest.py <stem>, then build.py
  harvest_empty       the harvest ran and recorded nothing. `harvest_empty.tsv`
                      says why; 32 of its 36 rows are "the raw source file was
                      not on disk", which usually means the script cannot fetch
                      its own input (see `cassidy_2024_uncertainty_attachment`
                      for the fix) -> make it self-fetching, then re-harvest
  r_script            an R script, which `harvest.py` cannot re-run at all
                      -> a hand-checked row in manual.csv (#2789)
  considered_none_kept  examined, but every pair was excluded. Usually correct
                      (a recode, label strings, too few labelled codes); listed
                      so a wrong exclusion is visible rather than buried in
                      3,700 coverage rows.

    python3 metadata/covariate_labels/audit_gaps.py
    python3 metadata/covariate_labels/audit_gaps.py --ratchet  # CI: fail on a NEW gap only
    python3 metadata/covariate_labels/audit_gaps.py --strict   # exit 1 on any never_examined
    python3 metadata/covariate_labels/audit_gaps.py --write    # refresh gaps.csv

`--ratchet` is the form worth running automatically. `--strict` fails today on
447 tables, so as a gate it would block every PR and promptly be disabled;
`--ratchet` grandfathers whatever `gaps.csv` already records and fails only on
a table that is newly in the gap. The backlog then shrinks monotonically and
cannot grow silently.

The honest limit: a table enters this report only once it is LIVE, so a new
script's gap is caught on the first run after its tables are released, not in
the PR that adds it. Catching it earlier would need the harvest logs, which
are machine-local -- and the point of this script is that it needs nothing but
the repo.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# Same regex harvest.py uses to pick its candidates, so the two agree on what
# "reads a labelled source" means. Kept in sync by the test, not by hope.
READS_PY = re.compile(r"pyreadstat|read_spss|read_stata")
# The R equivalents. haven::read_sav / read_dta, foreign::read.spss.
READS_R = re.compile(r"read_sav|read_dta|read\.spss|read\.dta|haven|foreign")

CLASSES = ("never_examined", "harvest_empty", "r_script",
           "considered_none_kept")


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def script_reads_labelled(rel: str) -> bool:
    """True when data/<script> opens an SPSS/Stata file."""
    p = REPO / rel
    if not p.exists():
        return False
    text = p.read_text(errors="replace")
    pat = READS_R if p.suffix.lower() == ".r" else READS_PY
    return bool(pat.search(text))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any live table is never_examined")
    ap.add_argument("--ratchet", action="store_true",
                    help="exit 1 only on a gap absent from the committed "
                         "gaps.csv (the form to run in CI)")
    ap.add_argument("--write", action="store_true",
                    help="refresh gaps.csv beside coverage.csv")
    a = ap.parse_args()

    live = {r["table"] for r in read_csv(REPO / "metadata" / "metadata.csv")}
    ships_cov = set()
    for r in read_csv(REPO / "metadata" / "column_docs.csv"):
        if r["column"].startswith("cov_"):
            ships_cov.add(r["table"])
    scripts_for = {}
    for r in read_csv(REPO / "metadata" / "table_scripts.csv"):
        scripts_for[r["table"]] = [s.strip() for s in
                                   (r["scripts"] or "").split(";") if s.strip()]
    labelled = {r["table"] for r in
                read_csv(REPO / "metadata" / "covariate_labels.csv")}
    coverage = read_csv(HERE / "coverage.csv")
    considered = {r["table"] for r in coverage}
    kept = {r["table"] for r in coverage if r["status"] == "included"}
    empty_harvest = {r["script"] for r in
                     csv.DictReader((HERE / "harvest_empty.tsv")
                                    .open(newline="", encoding="utf-8"),
                                    delimiter="\t")}
    empty_why = {r["script"]: r["why_empty"] for r in
                 csv.DictReader((HERE / "harvest_empty.tsv")
                                .open(newline="", encoding="utf-8"),
                                delimiter="\t")}

    rows = []
    for table in sorted(live):
        if table not in ships_cov:
            continue                      # no covariates: none to label
        rel = [s for s in scripts_for.get(table, []) if script_reads_labelled(s)]
        if not rel:
            continue
        stems = [Path(s).stem for s in rel]
        if table in labelled:
            continue                      # has labels: nothing owed
        if table in considered:
            if table in kept:
                continue                  # some pairs kept, just not all
            why = sorted({r["reason"] for r in coverage
                          if r["table"] == table and r["reason"]})
            rows.append(dict(table=table, scripts=";".join(rel),
                             klass="considered_none_kept",
                             detail=(why[0][:160] if why else "")))
            continue
        if any(Path(s).suffix.lower() == ".r" for s in rel):
            rows.append(dict(table=table, scripts=";".join(rel),
                             klass="r_script",
                             detail="harvest.py cannot re-run R; needs a "
                                    "hand-checked manual.csv row"))
        elif any(s in empty_harvest for s in stems):
            s = next(s for s in stems if s in empty_harvest)
            rows.append(dict(table=table, scripts=";".join(rel),
                             klass="harvest_empty",
                             detail=empty_why.get(s, "")[:160]))
        else:
            rows.append(dict(table=table, scripts=";".join(rel),
                             klass="never_examined",
                             detail="no harvest log was ever built for this "
                                    "script"))

    by_class = {k: [r for r in rows if r["klass"] == k] for k in CLASSES}
    print(f"{len(live)} live tables, {len(ships_cov)} of them shipping at "
          f"least one cov_* column.\n{len(rows)} ship cov_* from a script that "
          "reads an SPSS/Stata file and carry no covariate labels:\n")
    for k in CLASSES:
        n = len(by_class[k])
        print(f"  {k:22s} {n:5d} table(s)"
              f"{'' if n else '   (clear)'}")
        for r in by_class[k][:6]:
            print(f"      {r['table']:48s} {r['scripts']}")
        # The detail is the actionable half -- what to DO about this class --
        # so print it once per class rather than per table, where it would
        # repeat identically for every table one script built.
        if by_class[k]:
            details = sorted({r["detail"] for r in by_class[k] if r["detail"]})
            for d in details[:2]:
                print(f"        -> {d}")
        if n > 6:
            print(f"      ... and {n - 6} more (see --write / gaps.csv)")
    print()

    if a.write:
        out = HERE / "gaps.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["table", "scripts", "klass",
                                               "detail"],
                               lineterminator="\n")
            w.writeheader()
            w.writerows(sorted(rows, key=lambda r: (r["klass"], r["table"])))
        print(f"{len(rows)} rows -> {out}")

    if a.ratchet:
        known = set()
        prev = HERE / "gaps.csv"
        if prev.exists():
            known = {r["table"] for r in read_csv(prev)}
        new = sorted(r["table"] for r in rows if r["table"] not in known)
        gone = len(known) - len({r["table"] for r in rows} & known)
        print(f"ratchet: {len(known)} gap(s) recorded in gaps.csv, "
              f"{len(new)} new, {gone} closed since")
        if new:
            print("FAIL: these live tables are newly in the covariate-label "
                  "gap and are not recorded in gaps.csv:", file=sys.stderr)
            for t in new[:20]:
                print(f"  {t}", file=sys.stderr)
            print("Run harvest.py for the script that builds them, then "
                  "build.py; or refresh gaps.csv with --write if the gap is "
                  "accepted for now.", file=sys.stderr)
            return 1
        return 0

    if a.strict and by_class["never_examined"]:
        print(f"FAIL: {len(by_class['never_examined'])} live table(s) have "
              "never been examined by the covariate-label build. Run "
              "harvest.py for the named script(s), then build.py.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
