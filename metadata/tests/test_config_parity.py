"""Unit tests for metadata/check_config_parity.py (#1733).

The parity check has a failure mode worse than being wrong: being vacuous. If a
config file is reformatted past its parser and every extraction comes back
empty, the three empty sets compare equal and the check reports green while
comparing nothing. `test_parser_floor_rejects_a_truncated_config` is the
load-bearing test here -- the rest verify that real drift is reported.

Fixtures are synthetic miniatures of the three files rather than copies of
them, so these tests keep passing when a seventh warehouse is added. That the
parsers handle the *real* files is checked by CI running the script itself
against the real checkouts, which is the more important of the two checks.
"""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_config_parity as ccp  # noqa: E402


PIPELINE_R = """
IRW_OWNER <- "datapages"
IRW_CORE_DATASETS <- c(
  "item_response_warehouse",
  "item_response_warehouse_2",
  "item_response_warehouse_3",
  "item_response_warehouse_4",
  "item_response_warehouse_5",
  "item_response_warehouse_6"
)
IRW_TEXT_DATASETS <- c(
  "irw_text",
  "irw_text_2"
)
IRW_AUX_DATASETS <- c(
  meta = "irw_meta",
  sim  = "irw_simsyn",
  comp = "irw_competitions",
  nom  = "irw_nominal"
)
"""

RPKG_R = """
.irw_datasource_specs <- list(
  core = list(
    list(user = "datapages", dataset = "item_response_warehouse:as2e"),
    list(user = "datapages", dataset = "item_response_warehouse_2:epbx"),
    list(user = "datapages", dataset = "item_response_warehouse_3:5xaj"),
    list(user = "datapages", dataset = "item_response_warehouse_4:980f"),
    list(user = "datapages", dataset = "item_response_warehouse_5:3ykx"),
    list(user = "datapages", dataset = "item_response_warehouse_6:fpe6")
  ),
  sim = list(
    list(user = "datapages", dataset = "irw_simsyn:0btg")
  ),
  comp = list(
    list(user = "datapages", dataset = "irw_competitions:cmd7")
  ),
  nom = list(
    list(user = "datapages", dataset = "irw_nominal:614n")
  )
)
.irw_meta_spec <- list(user = "datapages", dataset = "irw_meta:bdxt")
.irw_itemtext_specs <- list(
  list(user = "datapages", dataset = "irw_text:07b6"),
  list(user = "datapages", dataset = "irw_text_2:ae47")
)
"""

CONFIG_PY = '''
from typing import Tuple, ClassVar

MAIN_REFS: ClassVar[Tuple[Tuple[str, str], ...]] = (
    ("datapages", "item_response_warehouse:as2e"),
    ("datapages", "item_response_warehouse_2:epbx"),
    ("datapages", "item_response_warehouse_3:5xaj"),
    ("datapages", "item_response_warehouse_4:980f"),
    ("datapages", "item_response_warehouse_5:3ykx"),
    ("datapages", "item_response_warehouse_6:fpe6"),
)
SIM_REF: ClassVar[Tuple[str, str]] = ("datapages", "irw_simsyn:0btg")
COMP_REF: ClassVar[Tuple[str, str]] = ("datapages", "irw_competitions:cmd7")
NOM_REF: ClassVar[Tuple[str, str]] = ("datapages", "irw_nominal:614n")
META_REF: ClassVar[Tuple[str, str]] = ("datapages", "irw_meta:bdxt")
ITEMTEXT_REFS: ClassVar[Tuple[Tuple[str, str], ...]] = (
    ("datapages", "irw_text:07b6"),
    ("datapages", "irw_text_2:ae47"),
)
VERSION: str = "0.1.2"
'''

EXPECTED = {
    "core": [
        "item_response_warehouse",
        "item_response_warehouse_2",
        "item_response_warehouse_3",
        "item_response_warehouse_4",
        "item_response_warehouse_5",
        "item_response_warehouse_6",
    ],
    "text": ["irw_text", "irw_text_2"],
    "meta": ["irw_meta"],
    "sim": ["irw_simsyn"],
    "comp": ["irw_competitions"],
    "nom": ["irw_nominal"],
}


class ParserTests(unittest.TestCase):
    """Each parser reduces its file to the same bare, hash-free names."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, text):
        p = self.tmp / name
        p.write_text(text)
        return p

    def test_pipeline_config(self):
        got = ccp.parse_pipeline_config(self.write("redivis_config.R", PIPELINE_R))
        self.assertEqual(got, EXPECTED)

    def test_rpkg_config_strips_version_hashes(self):
        got = ccp.parse_rpkg_config(self.write("redivis-config.R", RPKG_R))
        self.assertEqual(got, EXPECTED)

    def test_python_config_strips_version_hashes(self):
        got = ccp.parse_python_config(self.write("config.py", CONFIG_PY))
        self.assertEqual(got, EXPECTED)

    def test_rpkg_user_field_is_not_mistaken_for_a_dataset(self):
        """`user = "datapages"` sits beside every `dataset =` in the same block."""
        got = ccp.parse_rpkg_config(self.write("redivis-config.R", RPKG_R))
        self.assertNotIn("datapages", got["core"])

    def test_parser_floor_rejects_a_truncated_config(self):
        """A file the parser can no longer read must ERROR, never pass green.

        This is the test that keeps the whole check honest: without the floor,
        a reformatted file yields empty sets that compare equal to each other.
        """
        truncated = "\n".join(
            ln for ln in RPKG_R.splitlines()
            if "item_response_warehouse_" not in ln
        )
        with self.assertRaises(ccp.ParseError):
            ccp.parse_rpkg_config(self.write("redivis-config.R", truncated))


class CompareTests(unittest.TestCase):
    def configs(self, **overrides):
        base = {name: dict(EXPECTED) for name in ("pipeline", "rpkg", "pypkg")}
        for name, cfg in overrides.items():
            base[name] = cfg
        return base

    def test_agreement_reports_nothing(self):
        self.assertEqual(ccp.compare(self.configs()), [])

    def test_missing_source_is_reported(self):
        """The real #1733 defect: Python-pkg carried no irw_nominal for months."""
        pypkg = {k: v for k, v in EXPECTED.items() if k != "nom"}
        problems = ccp.compare(self.configs(pypkg=pypkg))
        self.assertEqual(len(problems), 1)
        self.assertIn("nom", problems[0])
        self.assertIn("MISSING", problems[0])
        self.assertIn("pypkg", problems[0])

    def test_extra_shard_in_one_file_is_reported(self):
        rpkg = dict(EXPECTED)
        rpkg["core"] = EXPECTED["core"] + ["item_response_warehouse_7"]
        problems = ccp.compare(self.configs(rpkg=rpkg))
        self.assertEqual(len(problems), 1)
        self.assertIn("core", problems[0])

    def test_shard_order_is_compared(self):
        """Same names, wrong order: clients would resolve tables to a stale shard."""
        pypkg = dict(EXPECTED)
        pypkg["text"] = list(reversed(EXPECTED["text"]))
        problems = ccp.compare(self.configs(pypkg=pypkg))
        self.assertEqual(len(problems), 1)
        self.assertIn("ORDER", problems[0])

    def test_unsharded_source_order_is_not_compared(self):
        """Only `core` and `text` are shard lists; the rest are single datasets."""
        self.assertEqual(ccp.SHARDED, ("core", "text"))


if __name__ == "__main__":
    unittest.main()
