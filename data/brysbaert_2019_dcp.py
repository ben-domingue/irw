#!/usr/bin/env python3
# Dutch Crowdsourcing Project (DCP): online Dutch vocabulary test run as a
# lexical decision task, trial level.
# Brysbaert, M., Keuleers, E., & Mandera, P. (2019). Recognition times for 54
# thousand Dutch words: Data from the Dutch Crowdsourcing Project. Psychologica
# Belgica, 59(1), 281-300. doi:10.5334/pb.491
# Data: OSF https://osf.io/5fk8d, CC BY-NC 4.0 (license.txt on OSF and inside
# the tarball; the OSF licence field says "Other"). Tarball
# dutch-raw-data.tar.gz, folder dutch-vocabtest-20131203-cleaned-native.lang.nl:
# lexical-decision.csv (trials), sessions.csv (exp_id -> profile_id) and
# profiles.csv (people). All three are tab-separated despite the .csv name.
#
# Encoding mirrors spalex_aguasvivas_2020 (same platform): one table, id is the
# person (`profile_id`), and only each person's FIRST session is kept
# (`profile_id_session` == 1). Later sessions are the same people coming back,
# up to 489 times, so they would repeat items and practice the task; 328,723
# people and 328,723 sessions of 100 trials each remain.
#
# Layout:
#   id   = `profile_id`
#   item = `spelling`; nonwords are items
#   resp = `accuracy` (1/0; equals response == lexicality on every row)
#   rt   = `rt` / 1000 in seconds; values <= 0 (clock glitches, ~0.03% of
#          trials) are left empty
#   date = the session's `time_start` as Unix seconds (no per-trial time)
#   trial_number = `trial_order` + 1 (1-100)
#   itemcov_lexicality = word / nonword (`lexicality` W / N)
#   cov_exp_id = the session kept (`exp_id`), as in spalex_aguasvivas_2020
#   cov_touch = the session was on a touch screen (`touch`)
#   cov_gender, cov_age, cov_country, cov_province, cov_education,
#   cov_handedness, cov_no_foreign_lang, cov_best_foreign: from profiles.csv,
#   as given (Dutch labels; no_foreign_lang 999 is in the source and is kept;
#   age: see Cleaning below). native_language is Dutch for everyone (the
#   folder is the native-speaker subset) and is not carried; nor are browser
#   ids and the source's derived RT columns (rt_adjbox, rt_zscore).
#
# Cleaning: cov_age is left empty where the source gives 0 (evidently "not
# given": thousands of people) or more than 100. Strings that the source uses
# both as a word and as a nonword stimulus are dropped entirely (a first pass
# over the trial file finds them; the counts are printed).
#
# The trial file is 2.8 GB, so it is read in chunks and written as it goes.
#
# Usage: python3 brysbaert_2019_dcp.py <folder with the three files> <out_dir>
import os
import sys

import numpy as np
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "dutch-vocabtest-20131203-cleaned-native.lang.nl"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
name = "brysbaert_2019_dcp"
lit = dict(sep="\t", keep_default_na=False, na_values=[""])

s = pd.read_csv(os.path.join(src, "sessions.csv"), **lit)
p = pd.read_csv(os.path.join(src, "profiles.csv"), **lit).set_index("profile_id")
assert s.exp_id.is_unique and p.index.is_unique and set(s.profile_id) <= set(p.index)
first = s[s.profile_id_session == 1]
assert first.profile_id.is_unique and first.profile_id.nunique() == s.profile_id.nunique()
first = first.set_index("exp_id")
start = (pd.to_datetime(first.time_start) - pd.Timestamp("1970-01-01")).dt.total_seconds()

# first pass: strings carrying both lexicalities
pairs = set()
for c in pd.read_csv(os.path.join(src, "lexical-decision.csv"), chunksize=5_000_000,
                     usecols=["spelling", "lexicality"], **lit):
    pairs.update(map(tuple, c.drop_duplicates().itertuples(index=False)))
lexn = pd.Series([s for s, _ in pairs]).value_counts()
both = set(lexn[lexn > 1].index)
print(f"strings with both lexicalities, dropped: {len(both)} {sorted(both)[:20]}")
age = p.age.where((p.age > 0) & (p.age <= 100)).round().astype("Int64")

pcov = {"gender": "cov_gender", "age": "cov_age", "country": "cov_country",
        "province": "cov_province", "education": "cov_education",
        "handedness": "cov_handedness", "no_foreign_lang": "cov_no_foreign_lang",
        "best_foreign": "cov_best_foreign"}
cols = ["id", "item", "resp", "rt", "date", "trial_number", "cov_exp_id", "cov_touch"] + \
       list(pcov.values()) + ["itemcov_lexicality"]

os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, name + ".csv")
n = 0
dropped = 0
ids, items, rt_empty = set(), set(), 0
per_session = {}
with open(path, "w", encoding="utf-8", newline="") as fh:
    pd.DataFrame(columns=cols).to_csv(fh, index=False)
    for c in pd.read_csv(os.path.join(src, "lexical-decision.csv"), chunksize=2_000_000,
                         usecols=["exp_id", "spelling", "lexicality", "rt", "accuracy",
                                  "response", "trial_order"], **lit):
        c = c[c.exp_id.isin(first.index) & ~c.spelling.isin(both)]
        assert ((c.response == c.lexicality).astype(int) == c.accuracy).all()
        assert set(c.lexicality) <= {"W", "N"}
        pid = c.exp_id.map(first.profile_id)
        o = pd.DataFrame({
            "id": pid.astype(int),
            "item": c.spelling.astype(str),
            "resp": c.accuracy.astype(int),
            "rt": np.where(c.rt <= 0, np.nan, c.rt / 1000),
            "date": c.exp_id.map(start),
            "trial_number": c.trial_order.astype(int) + 1,
            "cov_exp_id": c.exp_id.astype(int),
            "cov_touch": c.exp_id.map(first.touch),
        })
        for k, v in pcov.items():
            o[v] = pid.map(age if k == "age" else p[k]).values
        o["itemcov_lexicality"] = c.lexicality.map({"W": "word", "N": "nonword"}).values
        o[cols].to_csv(fh, index=False, header=False)
        n += len(o)
        rt_empty += int(o.rt.isna().sum())
        ids.update(o.id.unique())
        items.update(o["item"].unique())
        for e, k in c.groupby("exp_id").size().items():
            per_session[e] = per_session.get(e, 0) + k
        print(f"  {n:,} rows", flush=True)

print(f"{name}: rows={n} ids={len(ids)} items={len(items)} sessions={len(per_session)} "
      f"rt_empty={rt_empty} trials/session min={min(per_session.values())} "
      f"max={max(per_session.values())}")
