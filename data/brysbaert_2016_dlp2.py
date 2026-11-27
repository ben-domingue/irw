#!/usr/bin/env python3
# Dutch Lexicon Project 2: visual lexical decision on ~30,000 Dutch words and
# matched nonwords, trial level.
# Brysbaert, M., Stevens, M., Mandera, P., & Keuleers, E. (2016). The impact of
# word prevalence on lexical decision times: Evidence from the Dutch Lexicon
# Project 2. Journal of Experimental Psychology: Human Perception and
# Performance, 42(3), 441-458. doi:10.1037/xhp0000159
# Data: OSF https://osf.io/jfkvw, CC BY-NC-SA 4.0 (license.txt; the OSF licence
# field says "Other"). Files dlp2_trials0.tsv and dlp2_trials1.tsv (inside the
# .tsv.zip files, one per stimulus list) and dlp2_participants.tsv.
# 81 participants, each responding to 30,808 or 30,809 trials (62 blocks).
# Admitted under the 50-person floor for lexical decision and word-recognition
# tasks (Ben, 2026-11-27).
#
# Design (article, "Stimuli"): blocks of 500; the first two blocks were shown
# again at the end (source blocks 58-59, `repetition` = 1), so every person
# meets ~1,000 items twice. Both occurrences are kept and told apart by
# trial_number and trial_repetition.
#
# Layout (person-first):
#   id   = `participant`
#   item = `spelling`; nonwords are items ("email" and "zoeven" carry two
#          source item ids; nobody saw both, so each is one item)
#   resp = `corrn` (1 correct, 0 error)
#   rt   = `rtR` / 1000 in seconds, the raw RT. Six negative rtR values are
#          left empty. The source's cleaned/imputed RT columns (rtC, rtI,
#          is_imputed, ...) are not used.
#   trial_number = `observation` restarted at 1 for each person (`trial` + 1),
#          presentation order
#   trial_block  = `block` (0-61, as in the source)
#   trial_repetition = `repetition` (1 = the end-of-experiment repeat of
#          blocks 0-1)
#   itemcov_lexicality = word / nonword (`lexicality` W / N)
#   cov_gender, cov_age (whole years; the source gives fractional years),
#   cov_handedness (the hand used for "word"), cov_region (`orig_nl`:
#   Vlaanderen / Nederland, as spelled in the source), cov_lextale_nl
#   (LexTALE Dutch proportion correct, `lextale_nl_mean_correct`)
# Dropped: 558 trials flagged `is_missing` (no response recorded; accuracy is
# empty in the source).
#
# Usage: python3 brysbaert_2016_dlp2.py <dir with dlp2_*.tsv> <out_dir>
import os
import sys

import numpy as np
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "."
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
lit = dict(sep="\t", keep_default_na=False, na_values=["", "NA"], low_memory=False)

cols = ["participant", "block", "trial", "repetition", "spelling", "lexicality",
        "handedness", "r", "corrn", "is_missing", "rtR"]
d = pd.concat([pd.read_csv(os.path.join(src, f"dlp2_trials{i}.tsv"), usecols=cols, **lit)
               for i in (0, 1)], ignore_index=True)
p = pd.read_csv(os.path.join(src, "dlp2_participants.tsv"), **lit).set_index("participant")
assert p.index.is_unique and set(d.participant) <= set(p.index)
assert not d.duplicated(["participant", "trial"]).any()
assert (d.is_missing == 1).sum() == 558 and (d[d.is_missing == 1].corrn.isna()).all()
d = d[d.is_missing == 0]
assert ((d.r == d.lexicality).astype(int) == d.corrn).all()
assert (d.groupby("spelling").lexicality.nunique() == 1).all()
assert not d[d.repetition == 0].duplicated(["participant", "spelling"]).any()
assert (d.groupby("participant").handedness.nunique() == 1).all()

hand = d.groupby("participant").handedness.first()
out = pd.DataFrame({
    "id": d.participant.astype(int),
    "item": d.spelling.astype(str),
    "resp": d.corrn.astype(int),
    "rt": np.where(d.rtR < 0, np.nan, d.rtR / 1000),
    "trial_number": d.trial.astype(int) + 1,
    "trial_block": d.block.astype(int),
    "trial_repetition": d.repetition.astype(int),
})
out["cov_gender"] = out.id.map(p.gender)
out["cov_age"] = out.id.map(np.floor(p.age)).astype("Int64")
out["cov_handedness"] = out.id.map(hand)
out["cov_region"] = out.id.map(p.orig_nl)
out["cov_lextale_nl"] = out.id.map(p.lextale_nl_mean_correct)
out["itemcov_lexicality"] = d.lexicality.map({"W": "word", "N": "nonword"}).values
out = out.sort_values(["id", "trial_number"]).reset_index(drop=True)

name = "brysbaert_2016_dlp2"
os.makedirs(out_dir, exist_ok=True)
out.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
print(f"{name}: rows={len(out)} ids={out.id.nunique()} items={out.item.nunique()} "
      f"resp={out.resp.min()}-{out.resp.max()} rt_empty={out.rt.isna().sum()} "
      f"rt={out.rt.min():.3f}-{out.rt.max():.1f}")
