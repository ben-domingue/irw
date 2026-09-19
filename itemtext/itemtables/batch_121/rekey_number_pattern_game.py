"""Re-key number_pattern_game__items from set to set:target (#1856).

The response table's item was the stimulus set, so batch_121 shipped one
template per set with the rated number as [TARGET] (see notes.csv). The table
now keys item on set:target (data/number_pattern_game.R), which makes the
target known per item. This expands each set's published rows to one copy per
target that set was rated on, with [TARGET] filled in. Nothing else changes:
instrument, instructions, option_text and resp are carried over as published.

    python3 rekey_number_pattern_game.py published_items.csv numbergame_data.csv OUT.csv

published_items.csv is the live irw_text_2 table (510 rows, item 1..255);
numbergame_data.csv is the Dataverse original, doi:10.7910/DVN/A8ZWLF. Old
item k is the k-th set in that file's order, as the previous script numbered it.
"""
import re
import sys

import pandas as pd

pub_path, src_path, out_path = sys.argv[1:4]
pub = pd.read_csv(pub_path, keep_default_na=False)
src = pd.read_csv(src_path)

sets = {i + 1: s for i, s in enumerate(pd.unique(src["set"]))}
nums = lambda s: sorted(int(x) for x in re.findall(r"\d+", s))       # noqa: E731
shown = pub["item_text"].str.extract(r"previous output: ([^\n]*)")[0]
assert all(nums(sh) == nums(sets[int(i)]) for i, sh in zip(pub["item"], shown)), \
    "published item text does not match the set order it was keyed on"

pub["set"] = pub["item"].map(lambda i: sets[int(i)].replace(" ", ""))
pairs = (src.assign(set=src["set"].str.replace(" ", ""))[["set", "target"]]
         .drop_duplicates())
out = pub.merge(pairs, on="set", how="inner")
out["item"] = out["set"] + ":" + out["target"].astype(str)
out["item_text"] = [t.replace("[TARGET]", str(g))
                    for t, g in zip(out["item_text"], out["target"])]
out = out[pub.columns.drop("set")].sort_values(["item", "resp"])

assert out["item"].nunique() == len(pairs)
assert len(out) == 2 * len(pairs)
assert not out["item_text"].str.contains(r"\[TARGET\]").any()
out.to_csv(out_path, index=False)
print(f"{len(pub)} rows / {pub['item'].nunique()} items -> "
      f"{len(out)} rows / {out['item'].nunique()} items")
