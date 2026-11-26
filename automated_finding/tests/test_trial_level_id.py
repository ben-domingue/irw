"""Trial-level files get their id found instead of a row-position id (#2607).

`_looks_like_id` (>=50% unique) fails on one-row-per-trial data by
construction, because each subject owns many rows. The capuchin Joint Simon
supplement (martinez_2024, 10 monkeys x ~280 trials, trial numbering
restarting each session) went to the row-position fallback, then to the
`human_review` default in retriage, whose archive discovery reads as
exclusions. Offline and synthetic, shaped like that file.
"""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from irw_retriage_ha import classify  # noqa: E402
from irw_triage_updated import (  # noqa: E402
    TRIALS_MARKER, _trial_level_id, coerce_to_irw, triage_dataset,
)


def _capuchin_like(monkeys=10, sessions=4, trials=30):
    rows = []
    for m in range(monkeys):
        for s in range(sessions):
            for t in range(1, trials + 1):
                rows.append({
                    "dyad": f"pair{m // 2}",
                    "monkey": f"m{m}",
                    "date": f"2022-03-{s + 10}",
                    "condition": ["full", "half"][t % 2],
                    "trial_number": t,
                    "trial_type": t % 4 + 1,
                    "latency": 1.0 + t / 10,
                    "correct": (m + s + t) % 2,
                })
    return pd.DataFrame(rows)


class TrialLevelId(unittest.TestCase):

    def test_capuchin_shape_finds_monkey_and_session_key(self):
        tid, keys = _trial_level_id(_capuchin_like())
        self.assertEqual(tid, "monkey")      # not the dyad it sat in
        self.assertEqual(keys, ["monkey", "date", "trial_number"])

    def test_coerce_hands_off_as_trials_candidate_not_row_position(self):
        c = coerce_to_irw(_capuchin_like())
        self.assertIsNone(c.df)              # never melted: no below_min_n
        self.assertEqual(c.method, "trials_candidate")
        joined = " ".join(c.notes)
        self.assertIn(TRIALS_MARKER, joined)
        self.assertNotIn("row position", joined)

    def test_triage_then_retriage_routes_to_worth_retrying(self):
        t = triage_dataset(_capuchin_like())
        self.assertEqual(t.flag, "human_assistance")
        # the batch joins with " | " and caps at 400 chars; the marker must survive
        reasons = " | ".join(t.reasons)[:400]
        flag, _ = classify(pd.Series({"reasons": reasons, "title": "Joint Simon"}))
        self.assertEqual(flag, "worth_retrying")

    def test_bare_trial_column_without_session(self):
        df = pd.DataFrame({"subject": [s for s in range(6) for _ in range(40)],
                           "Trial": list(range(1, 41)) * 6,
                           "acc": [i % 2 for i in range(240)]})
        self.assertEqual(_trial_level_id(df), ("subject", ["subject", "Trial"]))

    def test_wide_person_file_without_trial_index_is_untouched(self):
        # one row per person, no trial index: keep the row-position fallback
        df = pd.DataFrame({"gender": [1, 2] * 60,
                           **{f"q{i}": [(r + i) % 5 + 1 for r in range(120)]
                              for i in range(8)}})
        self.assertIsNone(_trial_level_id(df))
        c = coerce_to_irw(df)
        self.assertEqual(c.method, "wide-to-long")
        self.assertTrue(any("row position" in n for n in c.notes))

    def test_trial_type_is_not_a_trial_index(self):
        df = _capuchin_like().drop(columns="trial_number")
        self.assertIsNone(_trial_level_id(df))

    def test_non_unique_key_is_not_trial_level(self):
        df = _capuchin_like()
        df = pd.concat([df, df], ignore_index=True)   # every trial twice
        self.assertIsNone(_trial_level_id(df))


if __name__ == "__main__":
    unittest.main()
