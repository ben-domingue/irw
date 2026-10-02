#!/usr/bin/env python3
"""Stage 1 of the covariate_labels generator (irw#1775): re-run data/ scripts
under the recording hook and keep what they read and wrote.

Why re-run the scripts rather than read the source files directly: the only
thing that knows which source file, which column, and which rows end up in a
shipped table is the script. Re-running it under ``hook/sitecustomize.py``
captures the value labels of every SPSS/Stata file it opens *and* the
``cov_*`` columns of every table it writes, so ``build.py`` can tie the two
together and check that the shipped codes are the codes the labels describe.
Reading sources directly would mean re-deriving each script's download,
subsetting and column mapping by hand, for ~300 scripts.

Safety:
* Scripts run in a **detached checkout** (``--checkout``, created with
  ``git worktree add --detach`` if missing), never in your working tree, so
  the CSVs they write land in that checkout's untracked ``data/`` and
  ``automated_finding/irw_output/``. Delete the checkout afterwards with
  ``git worktree remove --force``.
* The hook makes ``import redivis`` and ``import red_up`` fail, so no script
  can upload.
* One script at a time, under ``nice -n 10`` and a per-script timeout. Do not
  parallelise: some scripts load multi-GB files.

This is a **manual** stage, not part of the weekly pipeline: the scripts
download from OSF/Zenodo/Dataverse/... and some read local files, so a CI run
would be slow, flaky and incomplete. Re-run it when a script that ships coded
covariates is added or changed, then run ``build.py``.

    python3 metadata/covariate_labels/harvest.py                    # every script that reads .sav/.dta
    python3 metadata/covariate_labels/harvest.py estevez_2021_homework_motivation
    python3 metadata/covariate_labels/harvest.py --force ...       # re-run scripts already logged
"""
import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HOOK = HERE / "hook"
DEFAULT_LOGS = Path.home() / ".cache" / "irw" / "covariate_labels" / "logs"
DEFAULT_CHECKOUT = Path.home() / "irw-wt" / "covariate-labels-harvest"
READS_LABELLED = re.compile(r"pyreadstat|read_spss|read_stata")


def candidate_scripts(data_dir: Path) -> list[str]:
    """data/*.py that can open an SPSS/Stata file."""
    return sorted(p.stem for p in data_dir.glob("*.py")
                  if READS_LABELLED.search(p.read_text(errors="replace")))


def ensure_checkout(checkout: Path, commit: str) -> str:
    if not checkout.exists():
        subprocess.run(["git", "-C", str(REPO), "fetch", "-q", "origin"], check=True)
        subprocess.run(["git", "-C", str(REPO), "worktree", "add", "--detach",
                        str(checkout), commit], check=True)
    return subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scripts", nargs="*", help="script stems (default: every candidate)")
    ap.add_argument("--from-file", type=Path, help="file of script stems, one per line")
    ap.add_argument("--commit", default="origin/main", help="commit to check out (default origin/main)")
    ap.add_argument("--checkout", type=Path, default=DEFAULT_CHECKOUT)
    ap.add_argument("--logs", type=Path, default=DEFAULT_LOGS)
    ap.add_argument("--timeout", type=int, default=900, help="seconds per script")
    ap.add_argument("--force", action="store_true", help="re-run scripts that already have a log")
    a = ap.parse_args(argv)

    sha = ensure_checkout(a.checkout, a.commit)
    data = a.checkout / "data"
    names = list(a.scripts)
    if a.from_file:
        names += [ln.strip().removesuffix(".py") for ln in a.from_file.read_text().splitlines() if ln.strip()]
    names = names or candidate_scripts(data)
    a.logs.mkdir(parents=True, exist_ok=True)
    status = a.logs / "status.tsv"
    if not status.exists():
        status.write_text("script\texit\tseconds\tcommit\n")

    for i, b in enumerate(names, 1):
        log, out = a.logs / f"{b}.jsonl", a.logs / f"{b}.out"
        if log.exists() and not a.force:
            continue
        if not (data / f"{b}.py").exists():
            print(f"[{i}/{len(names)}] {b}: no such script at {sha[:8]}", file=sys.stderr)
            continue
        log.unlink(missing_ok=True)
        env = dict(os.environ, COVLAB_LOG=str(log), PYTHONPATH=str(HOOK),
                   MPLBACKEND="Agg", PYTHONUNBUFFERED="1")
        env.pop("REDIVIS_API_TOKEN", None)  # belt and braces: no write token in reach
        t0 = time.time()
        with open(out, "w") as fh:
            rc = subprocess.run(["nice", "-n", "10", "timeout", str(a.timeout), sys.executable, f"{b}.py"],
                                cwd=data, env=env, stdout=fh, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL).returncode
        log.touch()  # an empty log still marks the script as attempted
        with open(status, "a") as fh:
            fh.write(f"{b}\t{rc}\t{time.time() - t0:.0f}\t{sha}\n")
        print(f"[{i}/{len(names)}] {b}: exit {rc} ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
