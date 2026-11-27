#!/usr/bin/env python3
# British Lexicon Project: visual lexical decision on 28,730 mono- and
# disyllabic English words and as many nonwords, trial level.
# Keuleers, E., Lacey, P., Rastle, K., & Brysbaert, M. (2012). The British
# Lexicon Project: Lexical decision data for 28,730 monosyllabic and disyllabic
# English words. Behavior Research Methods, 44, 287-304.
# doi:10.3758/s13428-011-0118-4
# Data: OSF https://osf.io/b5sdk, CC BY-NC-SA 4.0 (license.txt; the OSF licence
# field says "Other"). File blp-trials.txt (inside blp-trials.txt.zip); column
# meanings from the article's "Trial-level data" section.
# 78 participants, each responding to about 28,700 trials over ~16 hours.
# Admitted under the 50-person floor for lexical decision and word-recognition
# tasks (Ben, 2026-11-27).
#
# Layout (person-first):
#   id   = `participant`
#   item = `spelling`; nonwords are items
#   resp = `accuracy` (1 if the response matched the lexicality, else 0; the
#          26 "O" responses are 0)
#   rt   = `rt.raw` / 1000 in seconds: the uncleaned RT. The source's `rt`
#          column sets errors and outliers to NA; it is not used.
#   date = `unix.seconds` + `unix.microseconds` / 1e6 (Unix time, source's own)
#   trial_number = `order`, presentation order for the participant
#   trial_block  = `block` (blocks of 500 trials)
#   itemcov_lexicality = word / nonword (`lexicality` W / N)
# Not carried: previous-trial columns, environment (lab computer), timing
# error, and the derived day/session counters.
#
# Source quirks handled:
#   * "cay" and "tike" each appear as both a word and a nonword stimulus (two
#     trial ids each, about equally often), so their 154 trials are dropped.
#   * 51 nonwords were shown to the same participant twice under two trial
#     ids; both trials are kept and told apart by trial_number.
#
# Usage: python3 keuleers_2012_blp.py <blp-trials.txt> <out_dir>
import os
import sys

import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "blp-trials.txt"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."

cols = ["participant", "lexicality", "block", "order", "trial", "spelling", "response",
        "accuracy", "rt.raw", "unix.seconds", "unix.microseconds"]
d = pd.read_csv(src, sep="\t", usecols=cols, keep_default_na=False,
                na_values=["", "NA"], low_memory=False)
n0 = len(d)
d = d[~d.spelling.isin(["cay", "tike"])]
assert n0 - len(d) == 154
assert not d.duplicated(["participant", "order"]).any()
assert (d.groupby("spelling").lexicality.nunique() == 1).all()
assert ((d.response == d.lexicality).astype(int) == d.accuracy).all()
assert d["rt.raw"].notna().all()

out = pd.DataFrame({
    "id": d.participant.astype(int),
    "item": d.spelling.astype(str),
    "resp": d.accuracy.astype(int),
    "rt": d["rt.raw"] / 1000,
    "date": d["unix.seconds"] + d["unix.microseconds"] / 1e6,
    "trial_number": d.order.astype(int),
    "trial_block": d.block.astype(int),
    "itemcov_lexicality": d.lexicality.map({"W": "word", "N": "nonword"}),
})
out = out.sort_values(["id", "trial_number"]).reset_index(drop=True)

name = "keuleers_2012_blp"
# The shared checks (irw_validate.contract `no_validator`): fails block,
# warnings are printed (concentrated 0/1 responses are expected here).
_checks = run_qc(out)
_fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
assert not _fails, _fails
for _c in _checks:
    if _c.status == "warn":
        print(f"  [qc warn] {_c.name}: {_c.detail[:120]}")
os.makedirs(out_dir, exist_ok=True)
out.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
print(f"{name}: rows={len(out)} ids={out.id.nunique()} items={out.item.nunique()} "
      f"resp={out.resp.min()}-{out.resp.max()} rt={out.rt.min():.3f}-{out.rt.max():.1f}")
