"""`Source via` is a closed vocabulary, not a provenance note (#2421).

The column names the intermediary COLLECTION a table was found through, such as
openESM, and the R and Python clients read it out to a user verbatim ("These
data were found via openESM..."). Seven `euls_2022_*` rows were staged with
`repos_weekly_2026-10-12`, an ingest batch name, and reached the released
biblio, where a user fetching one of them would have been told the data was
found via a batch. The batch is already recorded in automated_finding's
ledgers.

So the vocabulary is metadata/aggregators.csv's `key` column, and this pins the
staging guard: an unknown value is refused at entry, a known one passes, and an
unreadable vocabulary refuses nothing.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[0] / "stage_dict_row.py"

sys.path.insert(0, str(HERE.parents[0]))
from stage_dict_row import aggregator_keys  # noqa: E402


def stage(payload, tmp, aggregators=None):
    env = {"IRW_DICT_AUTO_PATH": str(tmp / "dictionary_auto.csv"),
           "IRW_CODEBOOK_INGEST_PATH": str(tmp / "codebook.csv"),
           "PATH": "/usr/bin:/bin"}
    if aggregators is not None:
        env["IRW_AGGREGATORS_PATH"] = str(aggregators)
    return subprocess.run([sys.executable, str(STAGE)], input=json.dumps(payload),
                          capture_output=True, text=True, env=env)


class VocabularyTest(unittest.TestCase):
    def test_aggregators_csv_is_the_vocabulary(self):
        keys = aggregator_keys()
        self.assertIsNotNone(keys)
        self.assertIn("openESM", keys)

    def test_a_batch_name_is_refused(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = stage({"table": "x_2020",
                         "source_via": "repos_weekly_2026-10-12"}, Path(d))
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("aggregators.csv", out.stdout + out.stderr)
        self.assertIn("repos_weekly_2026-10-12", out.stdout + out.stderr)

    def test_a_known_key_gets_past_this_check(self):
        ##It then fails on `public_reshare`, which proves the vocabulary check
        ##let it through rather than that the row is complete.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = stage({"table": "x_2020", "source_via": "openESM"}, Path(d))
        self.assertNotIn("aggregators.csv", out.stdout + out.stderr)

    def test_an_unreadable_vocabulary_refuses_nothing(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = stage({"table": "x_2020", "source_via": "anything"},
                        Path(d), aggregators=Path(d) / "missing.csv")
        self.assertNotIn("aggregators.csv", out.stdout + out.stderr)


if __name__ == "__main__":
    unittest.main()
