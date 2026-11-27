#!/usr/bin/env python3
# Spanish pseudoword lexical decision megastudy, trial level.
# Martínez-Tomás, C., Guasch, M., Lázaro, M., Baciero, A., Ferré, P., &
# Hinojosa, J. A. (2026). Meaningless, but not emotionless: Evidence from a
# megastudy of pseudoword lexical decisions. Behavior Research Methods.
# doi:10.3758/s13428-026-03186-8
# Data: OSF https://osf.io/mh3xe, CC0 1.0 (OSF licence field). Files
# data/rts_data.csv, data/participants_data.csv, data/items_data.csv; column
# meanings from the deposit's README.pdf.
#
# Layout (person-first):
#   id   = `participant` (anonymous code)
#   item = the letter string (`item`); pseudowords are items
#   resp = 1 - `error` (README: 0 = correct, 1 = error). Timeouts have error
#          and rt both NA in the source (5,267 trials); they are written as
#          resp 0 with rt empty, as for the other lexical decision tables.
#   rt   = `rt` / 1000 in seconds
#   trial_number = `trial` ("trial order of presentation", 1-480)
#   trial_list   = `list` (item list, 1-25)
#   itemcov_lexicality = word (conditions 1, 7) / nonword (2-6)
#   itemcov_condition  = `it_condition` as the README's labels: base word,
#          R+S, R+NonS, NonR+S, NonR+NonS, control pseudoword, control word
#   cov_age, cov_gender (README: 1 = male, 2 = female; written as labels)
# Not carried: item norms (length, neighbourhood, bigram, wordlikeness,
# valence, arousal) and per-person accuracy summaries.
#
# Usage: python3 martineztomas_2026_pseudoword_ld.py <data dir> <out_dir>
import os
import sys

import numpy as np
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "data"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
lit = dict(keep_default_na=False, na_values=["", "NA"])

r = pd.read_csv(os.path.join(src, "rts_data.csv"), **lit)
p = pd.read_csv(os.path.join(src, "participants_data.csv")).set_index("participant")
it = pd.read_csv(os.path.join(src, "items_data.csv"), **lit).set_index("item")
assert p.index.is_unique and it.index.is_unique
assert set(r.participant) <= set(p.index) and set(r["item"]) <= set(it.index)
assert not r.duplicated(["participant", "trial"]).any()
assert not r.duplicated(["participant", "item"]).any()
assert set(r.error.dropna()) == {0, 1}
assert (r.error.isna() == r.rt.isna()).all()
g = r.groupby("participant").list.agg(["nunique", "first"])
assert (g["nunique"] == 1).all() and (g["first"] == p.list.reindex(g.index)).all()

cond = {1: "base word", 2: "R+S", 3: "R+NonS", 4: "NonR+S", 5: "NonR+NonS",
        6: "control pseudoword", 7: "control word"}
out = pd.DataFrame({
    "id": r.participant.astype(str),
    "item": r["item"].astype(str),
    "resp": (1 - r.error.fillna(1)).astype(int),
    "rt": r.rt / 1000,
    "trial_number": r.trial.astype(int),
    "trial_list": r.list.astype(int),
})
out["cov_age"] = out.id.map(p.age)
out["cov_gender"] = out.id.map(p.gender.map({1: "male", 2: "female"}))
c = out.item.map(it.it_condition)
out["itemcov_lexicality"] = np.where(c.isin([1, 7]), "word", "nonword")
out["itemcov_condition"] = c.map(cond)
assert out.cov_gender.notna().all() and out.itemcov_condition.notna().all()
out = out.sort_values(["id", "trial_number"]).reset_index(drop=True)

name = "martineztomas_2026_pseudoword_ld"
os.makedirs(out_dir, exist_ok=True)
out.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
print(f"{name}: rows={len(out)} ids={out.id.nunique()} items={out.item.nunique()} "
      f"resp={out.resp.min()}-{out.resp.max()} rt_empty={out.rt.isna().sum()} "
      f"rt={out.rt.min():.3f}-{out.rt.max():.3f}")
