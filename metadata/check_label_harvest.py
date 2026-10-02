#!/usr/bin/env python3
"""Flag data/ scripts whose covariate value labels were never harvested (#2770).

Covariate value labels (1 = hombre, 2 = mujer) reach a table page only through
metadata/covariate_labels/harvest.py + build.py, a manual stage (#1775): it
re-runs build scripts, so it cannot run in CI. The ingest skill runs it before a
data PR is opened. This is the fallback when that step was skipped: for each
script given, if it reads an SPSS or Stata file AND writes cov_* columns, and
the harvest has never run it (no row in covariate_labels/harvest_status.tsv,
which harvest.py commits), say so. A script harvested with no labels found is
not flagged: that is an answer, not an omission. Neither is a script listed in
covariate_labels/not_harvestable.tsv: the harvest cannot re-run R scripts, so
those were checked by hand against their source files, and any labels worth
shipping went into covariate_labels/manual.csv (#2789).

ADVISORY ONLY. It never fails the PR: a script may read a .sav whose covariates
carry no value labels at all, and only a harvest can tell. With --annotate the
message is a GitHub ::warning:: on the script.

    python3 metadata/check_label_harvest.py data/foo_2026.py [...] [--annotate]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATUS = REPO / "metadata" / "covariate_labels" / "harvest_status.tsv"
NOT_HARVESTABLE = REPO / "metadata" / "covariate_labels" / "not_harvestable.tsv"

READS_LABELLED = re.compile(
    r"read_sav|read_dta|read_spss|read_stata|read\.spss|read\.dta|pyreadstat|haven::|foreign::")
WRITES_COV = re.compile(r"""["'`]cov_|paste0?\(\s*["']cov_|\bcov_[a-z]""")


def harvested() -> set:
    """Script stems harvest.py has run, from its committed status file, plus
    the scripts checked by hand in not_harvestable.tsv."""
    done = set()
    if STATUS.exists():
        with STATUS.open(encoding="utf-8", newline="") as f:
            done |= {r["script"] for r in csv.DictReader(f, delimiter="\t")}
    if NOT_HARVESTABLE.exists():
        with NOT_HARVESTABLE.open(encoding="utf-8", newline="") as f:
            done |= {Path(r["script"]).stem for r in csv.DictReader(f, delimiter="\t")}
    return done


def needs_harvest(script: str, done: set) -> bool:
    try:
        src = (REPO / script).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if not (READS_LABELLED.search(src) and WRITES_COV.search(src)):
        return False
    return Path(script).stem not in done


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scripts", nargs="*")
    ap.add_argument("--annotate", action="store_true")
    a = ap.parse_args(argv)
    done = harvested()
    for s in a.scripts:
        if needs_harvest(s, done) and s.endswith(".R"):
            msg = (f"{s} reads an SPSS/Stata file and writes cov_* columns, and the covariate "
                   f"label harvest cannot run R scripts. Check the source's value labels by hand: "
                   f"add any worth shipping to metadata/covariate_labels/manual.csv, then list the "
                   f"script in metadata/covariate_labels/not_harvestable.tsv.")
            print(f"::warning file={s}::{msg}" if a.annotate else msg)
        elif needs_harvest(s, done):
            msg = (f"{s} reads an SPSS/Stata file and writes cov_* columns, and the covariate "
                   f"label harvest has never run it. Run: python3 metadata/covariate_labels/"
                   f"harvest.py --commit HEAD {Path(s).stem} && python3 metadata/covariate_labels/build.py")
            print(f"::warning file={s}::{msg}" if a.annotate else msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
