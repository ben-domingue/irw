"""Run the validator over the 922 legacy .Rdata tables (#1703, sub-item 1.5).

    python3 -m irw_validate.sweep_legacy ../data/pub -o legacy_sweep.csv

These tables predate every checker in the project. `data/pub/` is not merely
outside this repository -- it is not under version control at all, a local
working directory -- so this is a one-off sweep someone runs, never CI.

Uses the `legacy` profile: `upload` minus rules that postdate the tables. The
`cov_` prefix convention is one of those; failing a 2019 table for not
anticipating it would produce noise rather than findings.

**Deliberately gentle.** This machine runs other people's work -- vignette
renders, package checks, other agents. A sweep of 3 GB is easy to write in a way
that makes the laptop unusable for twenty minutes, so:

* one file at a time, frame released before the next is opened;
* single-threaded -- numpy and its BLAS will otherwise spawn a thread per core
  for operations that gain nothing from it here;
* `--max-mb` skips files above a size and records the skip rather than passing
  them silently (default 64 MB, which covers all but ~20 of the 922);
* results are appended **as each table finishes**, not held until the end -- the
  first version buffered everything and wrote once, so a run that timed out at
  420 seconds produced no file at all and `--resume` had nothing to resume from;
* `--resume` re-reads that CSV and skips tables already done, so it can be
  stopped and picked up later;
* and it is worth running under `nice -n 19`, which the module suggests on
  startup if it is not already niced.

Slower, finishes, and leaves the machine usable while it does.
"""
from __future__ import annotations

import argparse
import csv
import gc
import os
import pathlib
import sys
import time

# Before numpy is imported anywhere: one thread. A per-core BLAS pool buys
# nothing for row counts and value_counts, and is most of what makes a sweep
# like this feel like a hang to whoever else is on the machine.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(prog="irw_validate.sweep_legacy")
    ap.add_argument("directory", help="directory of .Rdata tables")
    ap.add_argument("-o", "--out", default="legacy_sweep.csv",
                    help="where to write the per-finding CSV")
    ap.add_argument("--profile", default="legacy")
    ap.add_argument("--limit", type=int, default=0, help="stop after N files (for a trial run)")
    ap.add_argument("--max-mb", type=float, default=64.0,
                    help="skip files larger than this, recording the skip (default 64)")
    ap.add_argument("--resume", action="store_true",
                    help="skip tables already present in the output CSV")
    args = ap.parse_args(argv)

    try:
        if os.nice(0) < 10:
            print("tip: run this under `nice -n 19` -- it shares the machine with "
                  "vignette renders and other agents", file=sys.stderr)
    except (AttributeError, OSError):
        pass

    from .core import validate_file

    files = sorted(pathlib.Path(args.directory).glob("*.Rdata"))
    if args.limit:
        files = files[: args.limit]
    if not files:
        print(f"no .Rdata files under {args.directory}", file=sys.stderr)
        return 2

    FIELDS = ["table", "check", "severity", "message",
              "n_rows", "n_items", "n_participants"]
    out_path = pathlib.Path(args.out)
    done: set = set()
    if args.resume and out_path.exists():
        with out_path.open() as fh:
            done = {r["table"] for r in csv.DictReader(fh)}
        print(f"resuming: {len(done)} tables already recorded")
    fresh = not out_path.exists() or not args.resume
    sink = out_path.open("w" if fresh else "a", newline="")
    writer = csv.DictWriter(sink, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()

    def record(**kw):
        """One row, flushed. A sweep that loses its work on Ctrl-C is not resumable."""
        writer.writerow({k: kw.get(k, "") for k in FIELDS})
        sink.flush()

    n_findings = 0

    unreadable = clean = skipped = 0
    started = time.time()
    for i, path in enumerate(files, 1):
        if path.stem in done:
            continue
        size_mb = path.stat().st_size / 1024 ** 2
        if size_mb > args.max_mb:
            skipped += 1
            record(table=path.stem, check="size_skipped", severity="info",
                   message=f"{size_mb:.0f} MB exceeds --max-mb={args.max_mb:.0f}; not "
                           f"opened. Re-run with a higher cap when the machine is idle.")
            n_findings += 1
            continue
        try:
            report = validate_file(path, profile=args.profile)
        except Exception as exc:                      # a bad file must not stop the sweep
            unreadable += 1
            record(table=path.stem, check="unreadable", severity="error",
                   message=f"{type(exc).__name__}: {exc}"[:300])
            n_findings += 1
            print(f"[{i}/{len(files)}] {path.stem}: UNREADABLE {type(exc).__name__}", flush=True)
            continue
        st = report.stats or {}
        if not report.findings:
            clean += 1
            # a row per table either way, so --resume knows it was done
            record(table=path.stem, check="", severity="ok",
                   n_rows=st.get("n_responses", ""), n_items=st.get("n_items", ""),
                   n_participants=st.get("n_participants", ""))
        for f in report.findings:
            record(table=path.stem, check=f.check, severity=f.severity,
                   message=f.message[:300], n_rows=st.get("n_responses", ""),
                   n_items=st.get("n_items", ""), n_participants=st.get("n_participants", ""))
            n_findings += 1
        if i % 25 == 0 or i == len(files):
            print(f"[{i}/{len(files)}] {clean} clean, {n_findings} findings, "
                  f"{unreadable} unreadable, {time.time()-started:.0f}s", flush=True)
        gc.collect()

    sink.close()
    print(f"\n{len(files)} tables: {clean} with nothing to report, "
          f"{len(files) - clean - skipped} with at least one finding, "
          f"{unreadable} unreadable, {skipped} skipped for size")
    print(f"wrote {n_findings} findings to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
