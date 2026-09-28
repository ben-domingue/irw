"""Parse failures are not "aggregate" data (#2221).

The retriage used to bucket a misread file as `aggregate_continuous` from its
reason text alone. reread_hint() now looks again while the file is in hand;
the retriage routes its finding to `recoverable_format`. Offline, synthetic.
"""
import io
import random
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from irw_triage_updated import (REREAD_MARKER, _small_int_block,  # noqa: E402
                                reread_hint, triage_dataset, load_table)
import irw_retriage_ha as R  # noqa: E402


def _survey(n=300, items=10, seed=0, sep=","):
    """id, two continuous covariates, then a 1-5 item block -- peerj.8949's shape."""
    rng = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        rows.append([i, round(rng.uniform(140, 190), 1), round(rng.uniform(300, 700), 1)]
                    + [rng.randint(1, 5) for _ in range(items)])
    df = pd.DataFrame(rows, columns=["id", "Height (cm)", "6MWT (m)"]
                      + [f"Item {k}" for k in range(1, items + 1)])
    return df.to_csv(index=False, sep=sep).encode()


class Hint(unittest.TestCase):
    def test_block_is_the_shared_small_integer_columns(self):
        df = pd.read_csv(io.BytesIO(_survey()))
        self.assertEqual(_small_int_block(df), [f"Item {k}" for k in range(1, 11)])

    def test_covariates_melted_in_become_a_recoverable_hint(self):
        content = _survey()
        t = triage_dataset(load_table(content, filename="s1.csv"))
        self.assertEqual(t.flag, "human_assistance")
        hint = reread_hint(content, "s1.csv", t)
        self.assertIsNotNone(hint)
        self.assertTrue(hint.startswith(REREAD_MARKER))
        self.assertIn("10 items x 300 respondents", hint)
        self.assertIn("binary covariates", hint, "the caveat must travel with it")

    def test_semicolon_file_read_as_comma(self):
        content = _survey(sep=";")
        t = triage_dataset(load_table(content, filename="s2.csv"))
        self.assertEqual(t.flag, "human_assistance")
        hint = reread_hint(content, "s2.csv", t)
        self.assertIsNotNone(hint)
        self.assertIn("sep=';'", hint)

    def test_good_triage_gets_no_hint(self):
        rows = [(i, f"q{j}", 1 + (i * j) % 5) for i in range(1, 200) for j in range(1, 8)]
        content = pd.DataFrame(rows, columns=["id", "item", "resp"]).to_csv(index=False).encode()
        t = triage_dataset(load_table(content, filename="ok.csv"))
        self.assertEqual(t.flag, "good")
        self.assertIsNone(reread_hint(content, "ok.csv", t))


class Retriage(unittest.TestCase):
    def test_hint_routes_to_recoverable_format(self):
        row = pd.Series({"reasons": f"{REREAD_MARKER} header=1, the file triages as good "
                                    "(12 items x 3962 respondents) | resp has >50 unique "
                                    "values after wide-to-long melt", "n_participants": 3962,
                         "n_items": 20, "n_responses": 80000, "title": "t"})
        flag, reason = R.classify(row)
        self.assertEqual(flag, "recoverable_format")
        self.assertTrue(reason.startswith(REREAD_MARKER))

    def test_without_a_hint_rule_9_is_unchanged(self):
        row = pd.Series({"reasons": "resp has >50 unique values after wide-to-long melt",
                         "n_participants": 300, "n_items": 20, "n_responses": 6000,
                         "title": "t"})
        self.assertEqual(R.classify(row)[0], "aggregate_continuous")


if __name__ == "__main__":
    unittest.main()
