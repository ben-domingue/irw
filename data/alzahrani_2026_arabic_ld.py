#!/usr/bin/env python3
# Arabic Lexicon Project: online visual lexical decision on 10,000 Modern
# Standard Arabic words and 10,000 nonwords, trial level.
# Alzahrani, A., Alshumrani, H., Aljuaythin, W., Mahfouz, I., Alsuwaiyan, L.,
# Aljadaan, N., Alghazo, S., Tiaiba, I., & Alanzi, Z. (2026). The Arabic Lexicon Project: Lexical decision data for
# 10,000 Modern Standard Arabic words. Behavior Research Methods.
# doi:10.3758/s13428-026-03115-9
# Data: OSF https://osf.io/py36e, CC BY-NC-SA 4.0 (OSF licence field and
# license.txt). File "Data/Lexical decision data/Trial level/
# trial_level_data.csv"; column meanings from trial_level_column_description.txt.
# The same author's KalimahNorms (word norms) is already in IRW.
#
# The deposit's own cleaning (R scripts/01_main_prepare_data.Rmd) kept the
# first completion of each quiz and dropped low-scoring sessions; that file is
# taken as deposited, with one exception: 88,301 rows (10.8%) are exact copies
# of another row (same person, quiz, page, item, timestamp, RT and response),
# 2 copies of each trial in 884 quizzes. The copies are dropped, leaving one
# row per trial.
#
# Layout (person-first):
#   id   = `user_private_id` (anonymous)
#   item = `item_shown_in_the_page`, the string shown; nonwords are items
#   resp = `correct` (1/0). Timeouts (`timeout` true, RT empty) are 0 in the
#          source and stay 0, with rt empty.
#   rt   = `user_reaction_time_in_milliseconds` / 1000 in seconds
#   date = `utc_date_and_time` as Unix seconds (the source's own timestamp)
#   trial_number  = `page_number`, position within the quiz (1-100)
#   trial_session = `session_number`, the person's quiz count; a person may
#          take many quizzes, so a person can meet an item more than once
#   trial_quiz    = `quiz_id`, the quiz (word list) taken
#   trial_device  = `user_device_type` (desktop / mobile; can vary by session)
#   itemcov_lexicality = `item_type` (word / nonword)
#   cov_group = L1_group / L2_group (native speakers vs learners)
#   cov_dialect = `arabic_dialect`
# Not carried: browser, OS, monitor and viewport sizes, and the ~90 item-norm
# columns on each row.
#
# Usage: python3 alzahrani_2026_arabic_ld.py <trial_level_data.csv> <out_dir>
import os
import sys

import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "trial_level_data.csv"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."

cols = ["utc_date_and_time", "session_number", "user_private_id", "user_device_type",
        "group", "arabic_dialect", "page_number", "quiz_id", "quiz_id_corrected",
        "item_shown_in_the_page", "item_type", "user_reaction_time_in_milliseconds",
        "user_response", "correct", "timeout"]
d = pd.read_csv(src, usecols=cols, keep_default_na=False, na_values=["", "NA"],
                low_memory=False)
n0 = len(d)
d = d.drop_duplicates()
assert n0 - len(d) == 88301, n0 - len(d)
assert not d.duplicated(["quiz_id_corrected", "page_number"]).any()
assert (d.groupby("quiz_id_corrected")[["user_private_id", "session_number"]].nunique() == 1).all().all()
assert set(d.correct) == {0, 1}
assert (d.timeout == d.user_reaction_time_in_milliseconds.isna()).all()
assert (d[d.timeout].correct == 0).all()
assert (d.groupby("item_shown_in_the_page").item_type.nunique() == 1).all()
assert (d.groupby("user_private_id")[["group", "arabic_dialect"]].nunique(dropna=False) == 1).all().all()

ts = pd.to_datetime(d.utc_date_and_time, utc=True, format="ISO8601")
out = pd.DataFrame({
    "id": d.user_private_id.astype(str),
    "item": d.item_shown_in_the_page.astype(str),
    "resp": d.correct.astype(int),
    "rt": d.user_reaction_time_in_milliseconds / 1000,
    "date": (ts - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds(),
    "trial_number": d.page_number.astype(int),
    "trial_session": d.session_number.astype(int),
    "trial_quiz": d.quiz_id.astype(int),
    "trial_device": d.user_device_type,
    "cov_group": d.group,
    "cov_dialect": d.arabic_dialect,
    "itemcov_lexicality": d.item_type,
})
out = out.sort_values(["id", "trial_session", "trial_number"]).reset_index(drop=True)

name = "alzahrani_2026_arabic_ld"
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
