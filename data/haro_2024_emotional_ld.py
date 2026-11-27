#!/usr/bin/env python3
# Large-scale Spanish lexical decision study of emotional word recognition,
# trial level.
# Haro, J., Hinojosa, J. A., & Ferré, P. (2024). The role of individual
# differences in emotional word recognition: Insights from a large-scale
# lexical decision study. Behavior Research Methods.
# doi:10.3758/s13428-024-02488-z
# Data: OSF https://osf.io/cbtqy, CC BY 4.0 (OSF licence field). File data.csv.
#
# Layout (person-first):
#   id   = the participant code with the source's "block_N_sj_" prefix removed
#          (each person did exactly one block, so the prefix only repeats
#          trial_block; 977 people either way)
#   item = the letter string (`word_string`); nonwords are items
#   resp = 1 - `error` (0 correct, 1 error). error = 99 marks a timeout, with
#          rt empty in the source (5,728 trials); written as resp 0 with rt
#          empty, as for the other lexical decision tables.
#   rt   = `rt` / 1000 in seconds
#   trial_number = `trial_num` (21-620; the first 20 positions are not in the
#          file)
#   trial_block  = `block`, the item set the person saw
#   itemcov_lexicality = word / nonword (`lexicality` 1 / 0)
#   cov_age, cov_gender (Femenino / Masculino / Otro, as in the source)
#   cov_operas_ex, _ee, _co, _ag, _op: the participant's OPERAS personality
#          scores (extraversion, emotional stability, conscientiousness,
#          agreeableness, openness) as given in the source
# Not carried: the word norms on each row (valence, arousal, frequency, ...)
# and the source `word` id.
#
# Usage: python3 haro_2024_emotional_ld.py <data.csv> <out_dir>
import os
import sys

import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "data.csv"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."

d = pd.read_csv(src, keep_default_na=False, na_values=["", "NA"], low_memory=False)
d["sj"] = d.participant.str.replace(r"^block_\d+_sj_", "", regex=True)
assert d.participant.str.extract(r"^block_(\d+)_")[0].astype(int).eq(d.block).all()
assert d.groupby("sj").participant.nunique().max() == 1
assert not d.duplicated(["sj", "word_string"]).any()
assert not d.duplicated(["sj", "trial_num"]).any()
assert set(d.error) == {0, 1, 99} and ((d.error == 99) == d.rt.isna()).all()
assert set(d.lexicality) == {0, 1} and (d.groupby("word_string").lexicality.nunique() == 1).all()
ops = ["OPERAS_EX", "OPERAS_EE", "OPERAS_CO", "OPERAS_AG", "OPERAS_OP"]
assert (d.groupby("sj")[["age", "gender"] + ops].nunique(dropna=False) == 1).all().all()

out = pd.DataFrame({
    "id": d.sj.astype(str),
    "item": d.word_string.astype(str),
    "resp": (d.error == 0).astype(int),
    "rt": d.rt / 1000,
    "trial_number": d.trial_num.astype(int),
    "trial_block": d.block.astype(int),
    "cov_age": d.age,
    "cov_gender": d.gender,
})
for c in ops:
    out["cov_" + c.lower()] = d[c]
out["itemcov_lexicality"] = d.lexicality.map({1: "word", 0: "nonword"})
out = out.sort_values(["id", "trial_number"]).reset_index(drop=True)

name = "haro_2024_emotional_ld"
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
      f"resp={out.resp.min()}-{out.resp.max()} rt_empty={out.rt.isna().sum()} "
      f"rt={out.rt.min():.3f}-{out.rt.max():.3f}")
