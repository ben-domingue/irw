#!/usr/bin/env python3
# CzeLeD: online visual lexical decision on 12,242 Czech word forms and
# matched pseudowords, trial level.
# Chromý, J., Ceháková, M., Preininger, M., Smolík, F., Henyš, J., & Brand, J.
# (2026).
# Morphologically annotated lexical decision data for 12,242 Czech word forms.
# Scientific Data. doi:10.1038/s41597-026-07196-1
# Data: OSF https://osf.io/d35vg, CC BY 4.0 (OSF licence field). Files
# "Trial level data/CzeLeD_trials_cleaned.csv" and
# "CzeLeD_demographics_cleaned.csv"; column meanings from the deposit's
# *_description.txt files. An older, unlicensed version at OSF tw9x8 is not
# used.
#
# The authors' cleaned files are used as deposited: their cleaning
# (CzeLeD_data_cleaning.Rmd) swaps the keys for one participant who had
# evidently reversed them and drops two below-chance participants.
#
# Layout (person-first):
#   id   = `Participant`
#   item = `Stimulus`, the string shown; pseudowords are items. Seven word
#          forms (je, letech, ...) carry two source ItemNo codes because they
#          were annotated as two different forms in two lists; nobody saw both,
#          and the string shown is the same, so they are one item.
#   resp = `Correct` (1/0; equals Response == CorrectKey on every row)
#   rt   = `RT` / 1000 in seconds, as recorded (no trimming; a few are minutes
#          long)
#   trial_number = `Order` (1-449, position in the person's list)
#   trial_list   = `List` (1-41)
#   itemcov_lexicality = word (lemma, wordform) / nonword (pseudo_lm, pseudo_wf)
#   itemcov_type = `Type`: lemma, wordform, pseudo_lm, pseudo_wf
#   cov_gender, cov_age, cov_handedness from the demographics file
# Practice trials (List == "practice", 15 strings) are dropped.
#
# Usage: python3 chromy_2026_czeled.py <Trial level data dir> <out_dir>
import os
import sys

import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "Trial level data"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
lit = dict(keep_default_na=False, na_values=["", "NA"])

t = pd.read_csv(os.path.join(src, "CzeLeD_trials_cleaned.csv"), low_memory=False, **lit)
g = pd.read_csv(os.path.join(src, "CzeLeD_demographics_cleaned.csv"), **lit).set_index("Participant")
t = t[t.List != "practice"].copy()
assert g.index.is_unique and set(t.Participant) <= set(g.index)
assert not t.duplicated(["Participant", "Stimulus"]).any()
assert not t.duplicated(["Participant", "Order"]).any()
assert ((t.Response == t.CorrectKey).astype(int) == t.Correct).all()
assert set(t.Type) == {"lemma", "wordform", "pseudo_lm", "pseudo_wf"}
assert (t.groupby("Stimulus").Type.nunique() == 1).all()
assert (t.groupby("Participant").List.first() == g.List.reindex(t.Participant.unique()).sort_index()).all()

out = pd.DataFrame({
    "id": t.Participant.astype(str),
    "item": t.Stimulus.astype(str),
    "resp": t.Correct.astype(int),
    "rt": t.RT / 1000,
    "trial_number": t.Order.astype(int),
    "trial_list": t.List.str.replace("List", "", regex=False).astype(int),
})
for s, c in [("Gender", "cov_gender"), ("Age", "cov_age"), ("Handedness", "cov_handedness")]:
    out[c] = out.id.map(g[s])
out["itemcov_lexicality"] = t.Type.map({"lemma": "word", "wordform": "word",
                                        "pseudo_lm": "nonword", "pseudo_wf": "nonword"}).values
out["itemcov_type"] = t.Type.values
out = out.sort_values(["id", "trial_number"]).reset_index(drop=True)

name = "chromy_2026_czeled"
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
