#!/usr/bin/env python3
# MALD 1.1, the Massive Auditory Lexical Decision database: auditory lexical
# decision on English words and pseudowords, trial level.
# Tucker, B. V., Brenner, D., Danielson, D. K., Kelley, M. C., Nenadić, F., &
# Sims, M. (2019). The Massive Auditory Lexical Decision (MALD) database.
# Behavior Research Methods, 51, 1187-1204. doi:10.3758/s13428-018-1056-1
# Data: University of Alberta Scholaris, doi:10.7939/r3-kh0r-r116 (MALD 1.1),
# dc.rights.uri = CC BY-NC 4.0. Files MALD1_1_ResponseData.txt and
# MALD1_1_SubjectData.txt. Licence resolved on irw#1303; Ben pulled #1303
# forward on 2026-11-27.
#
# Both .txt files have a leading row-name column the header does not name, so
# they are read with index_col=0 (otherwise every column shifts by one).
#
# Layout (person-first):
#   id   = `Subject`
#   item = `Item`: the word's spelling, or the pseudoword's phonetic spelling as
#          the source gives it (e.g. "aarihng")
#   resp = `ACC` (TRUE/FALSE -> 1/0)
#   rt   = `RT` / 1000 in seconds; RT is 0 on 3,112 trials (3,111 of them
#          errors), which are no-response trials, so rt is left empty there
#   trial_number  = `Trial`, position within the session
#   trial_session = `Session`, the MALD item-set number (1-134) the trial
#          belongs to; a person did 1-3 sessions
#   itemcov_lexicality = word / nonword (ItemData `IsWord`)
#   cov_release (MALD1 or MALD1.1), cov_age, cov_sex, cov_handedness,
#   cov_native_lang, cov_education_level, cov_english_proficiency (source
#   codes), from SubjectData. Not carried: the per-person accuracy and RT
#   summaries (Hits, Dprime, MeanRT, ...), which are computed from these
#   trials, and free-text language-history fields.
# The item "null" (9 trials) is read literally (see rd()).
# "brown" occurs twice in session 85, so four people have two "brown" trials;
# both are kept and told apart by trial_number.
#
# Usage: python3 tucker_2019_mald.py <dir with MALD1_1_*Data.txt> <out_dir>
import os
import sys

import numpy as np
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "."
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."

def rd(name, literal=False):
    # literal: only an empty cell is missing, so the real word "null" stays an
    # item instead of becoming NaN (pandas' default NA strings include "null")
    kw = dict(keep_default_na=False, na_values=[""]) if literal else {}
    return pd.read_csv(os.path.join(src, name), sep="\t", index_col=0, low_memory=False, **kw)

r = rd("MALD1_1_ResponseData.txt", literal=True)
s = rd("MALD1_1_SubjectData.txt")
it = rd("MALD1_1_ItemData.txt", literal=True)
assert s.Subject.is_unique and set(r.Subject) <= set(s.Subject)
assert it.Item.is_unique and set(r.Item) <= set(it.Item)
assert not r.duplicated(["Subject", "Session", "Trial"]).any()
assert r.ACC.dtype == bool
assert (r.groupby("Subject").Release.nunique() == 1).all()

lex = it.set_index("Item").IsWord.map({True: "word", False: "nonword"})
s = s.set_index("Subject")
rel = r.groupby("Subject").Release.first()

out = pd.DataFrame({
    "id": r.Subject.astype(int),
    "item": r.Item.astype(str),
    "resp": r.ACC.astype(int),
    "rt": np.where(r.RT == 0, np.nan, r.RT / 1000),
    "trial_number": r.Trial.astype(int),
    "trial_session": r.Session.astype(int),
})
out["cov_release"] = out.id.map(rel)
for src_col, col in [("Age", "cov_age"), ("Sex", "cov_sex"), ("Handedness", "cov_handedness"),
                     ("NativeLang", "cov_native_lang"), ("EducationLevel", "cov_education_level"),
                     ("EnglishProficiency", "cov_english_proficiency")]:
    out[col] = out.id.map(s[src_col])
out["itemcov_lexicality"] = out.item.map(lex)
assert out.itemcov_lexicality.notna().all()
out = out.sort_values(["id", "trial_session", "trial_number"]).reset_index(drop=True)

name = "tucker_2019_mald"
os.makedirs(out_dir, exist_ok=True)
out.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
print(f"{name}: rows={len(out)} ids={out.id.nunique()} items={out.item.nunique()} "
      f"resp={out.resp.min()}-{out.resp.max()} rt_empty={out.rt.isna().sum()} "
      f"rt={out.rt.min():.3f}-{out.rt.max():.3f}")
