#!/usr/bin/env python3
# SpaVerb-LD: visual lexical decision on 4,562 Spanish verbs and 4,562
# pseudoverbs, trial level.
# Pérez-Sánchez, M. Á., Marín-Serrano, J., San Miguel-Abella, R., Herrera, E.,
# & González-Nosti, M. (2025). A dataset of word recognition accuracy, times,
# and prevalence for 4,562 verbs and 4,562 pseudoverbs of Spanish. Scientific
# Data. doi:10.1038/s41597-025-06339-0
# Data: OSF https://osf.io/5cpsh (doi:10.17605/OSF.IO/5CPSH), CC BY 4.0 (OSF
# licence field; the article itself is CC BY-NC-ND, which covers the article,
# not the deposit). File SpaVerb-LD_raw_database.csv. The analysis copy at
# OSF 2f9us carries no licence and is not used.
#
# Column meanings are from the article's Data Records section.
# Layout (person-first):
#   id   = `participant` (UMU = Murcia, OVI = Oviedo)
#   item = the letter string (`item`); pseudoverbs are items
#   resp = `ACC` (1 correct, 0 incorrect or timeout)
#   rt   = |`RT`| / 1000 in seconds. DMDX signs latencies (negative =
#          incorrect); -1500 is a timeout, written as resp 0 with rt empty.
#   trial_block = `block` (1-18): the item set the participant saw. Items were
#          shown in random order within a block and the order is not in the
#          deposit, so there is no trial index.
#   itemcov_lexicality = word / nonword (`item_type`)
#   cov_age, cov_gender (M/W), cov_hand (dominant hand, L/R), cov_dialect
#          (`native`: 1 = European Spanish, 2 = American Spanish)
# Not carried: the model-based prevalence columns (preval_*), which are IRW-
# style derived estimates rather than responses, and `item_id`/`part_block`.
#
# Source quirks handled:
#   * "despasar" is both a verb (item_id 1011633) and a pseudoverb (9011665);
#     the pseudoverb copy is a real verb, so its 28 rows are dropped.
#   * UMU176 reports R in block 5 and L in block 8; cov_hand is left empty for
#     that person.
#
# Usage: python3 perezsanchez_2025_spaverb_ld.py <SpaVerb-LD_raw_database.csv> <out_dir>
import os
import sys

import numpy as np
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "SpaVerb-LD_raw_database.csv"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."

d = pd.read_csv(src, encoding="utf-8-sig")
n0 = len(d)
d = d[~((d["item"] == "despasar") & (d["item_type"] == "pseudoword"))]
assert n0 - len(d) == 28
assert not d.duplicated(["participant", "item"]).any()
assert set(d.ACC) == {0, 1}
assert ((d.RT > 0) == (d.ACC == 1)).all()
assert (d.groupby("item").item_type.nunique() == 1).all()
assert (d.groupby("participant")[["age", "gender", "native"]].nunique() == 1).all().all()

hand = d.groupby("participant").hand.agg(lambda s: s.iloc[0] if s.nunique() == 1 else np.nan)

timeout = d.RT == -1500
out = pd.DataFrame({
    "id": d.participant.astype(str),
    "item": d["item"].astype(str),
    "resp": d.ACC.astype(int),
    "rt": np.where(timeout, np.nan, d.RT.abs() / 1000),
    "trial_block": d.block.astype(int),
    "cov_age": d.age.astype(int),
    "cov_gender": d.gender,
    "cov_hand": d.participant.map(hand),
    "cov_dialect": d.native.map({1: "European Spanish", 2: "American Spanish"}),
    "itemcov_lexicality": d.item_type.map({"word": "word", "pseudoword": "nonword"}),
})
assert out.cov_dialect.notna().all() and out.itemcov_lexicality.notna().all()
out = out.sort_values(["id", "trial_block", "item"]).reset_index(drop=True)

name = "perezsanchez_2025_spaverb_ld"
os.makedirs(out_dir, exist_ok=True)
out.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
print(f"{name}: rows={len(out)} ids={out.id.nunique()} items={out.item.nunique()} "
      f"resp={out.resp.min()}-{out.resp.max()} timeouts={int(timeout.sum())} "
      f"rt={out.rt.min():.3f}-{out.rt.max():.3f}")
