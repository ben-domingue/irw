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
* `--resume` re-reads the output CSV and skips tables already done, so it can be
  stopped with Ctrl-C and picked up later;
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

    done: set = set()
    rows: list = []
    if args.resume and pathlib.Path(args.out).exists():
        with open(args.out) as fh:
            rows = list(csv.DictReader(fh))
        done = {r["table"] for r in rows}
        print(f"resuming: {len(done)} tables already recorded")

    unreadable = clean = skipped = 0
    started = time.time()
    for i, path in enumerate(files, 1):
        if path.stem in done:
            continue
        size_mb = path.stat().st_size / 1024 ** 2
        if size_mb > args.max_mb:
            skipped += 1
            rows.append({"table": path.stem, "check": "size_skipped", "severity": "info",
                         "message": f"{size_mb:.0f} MB exceeds --max-mb={args.max_mb:.0f}; "
                                    f"not opened. Re-run with a higher cap when the "
                                    f"machine is idle.",
                         "n_rows": "", "n_items": "", "n_participants": ""})
            continue
        try:
            report = validate_file(path, profile=args.profile)
        except Exception as exc:                      # a bad file must not stop the sweep
            unreadable += 1
            rows.append({"table": path.stem, "check": "unreadable", "severity": "error",
                         "message": f"{type(exc).__name__}: {exc}"[:300],
                         "n_rows": "", "n_items": "", "n_participants": ""})
            print(f"[{i}/{len(files)}] {path.stem}: UNREADABLE {type(exc).__name__}", flush=True)
            continue
        st = report.stats or {}
        if not report.findings:
            clean += 1
        for f in report.findings:
            rows.append({"table": path.stem, "check": f.check, "severity": f.severity,
                         "message": f.message[:300],
                         "n_rows": st.get("n_responses", ""),
                         "n_items": st.get("n_items", ""),
                         "n_participants": st.get("n_participants", "")})
        if i % 25 == 0 or i == len(files):
            print(f"[{i}/{len(files)}] {clean} clean, {len(rows)} findings, "
                  f"{unreadable} unreadable, {time.time()-started:.0f}s", flush=True)
        gc.collect()

    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["table", "check", "severity", "message",
                                           "n_rows", "n_items", "n_participants"])
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(files)} tables: {clean} with nothing to report, "
          f"{len(files) - clean - skipped} with at least one finding, "
          f"{unreadable} unreadable, {skipped} skipped for size")
    print(f"wrote {len(rows)} findings to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
