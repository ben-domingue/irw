"""Permitted response values from item-text anchors (#2152). Offline."""

from __future__ import annotations

import tempfile
import unittest
import unittest.mock
from pathlib import Path

from red_up import cli
from red_up.checks import check_all
from red_up.permitted import anchor_spans, lookup, staged_items
from red_up.targets import Target

RESPONSE = Target(name="item_response_warehouse_5", label="response data", kind="core")
TEXT = Target(name="irw_text_3", label="item text", kind="aux", source="text")


def rows(*triples):
    return [{"item": i, "resp": r, "option_text": t} for i, r, t in triples]


class AnchorSpans(unittest.TestCase):
    def test_span_fills_the_unlabelled_middle_and_a_hole(self):
        # arzamoncunill E1: resp rows {1,2,4,5,6,7} built from the data, 3
        # absent; anchors at 1 and 7 give the documented 1..7.
        spans = anchor_spans(rows(("E1", "1", "Never"), ("E1", "2", ""), ("E1", "4", ""),
                                  ("E1", "7", "Always")))
        self.assertEqual(list(spans["E1"]), [1, 2, 3, 4, 5, 6, 7])

    def test_older_format_without_resp_has_no_span(self):
        self.assertEqual(anchor_spans([{"item": "a", "raw_resp": "1", "option_text": "x"},
                                       {"item": "a", "raw_resp": "5", "option_text": "y"}]), {})

    def test_one_label_is_not_a_span(self):
        self.assertEqual(anchor_spans(rows(("q", "1", "Yes"), ("q", "2", ""))), {})

    def test_non_integer_anchor_drops_the_item(self):
        self.assertEqual(anchor_spans(rows(("q", "0.5", "low"), ("q", "3", "high"))), {})

    def test_numeric_item_codes_are_also_int_keys(self):
        spans = anchor_spans(rows(("3", "0", "No"), ("3", "4", "Very")))
        self.assertIn("3", spans)
        self.assertIn(3, spans)

    def test_arrow_values_are_accepted(self):
        spans = anchor_spans([{"item": "a", "resp": 1, "option_text": "x"},
                              {"item": "a", "resp": 5.0, "option_text": "y"},
                              {"item": "a", "resp": None, "option_text": None}])
        self.assertEqual(list(spans["a"]), [1, 2, 3, 4, 5])


class Lookup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "item_response_warehouse_5").mkdir()
        (self.root / "irw_text_3").mkdir()
        self.data = self.root / "item_response_warehouse_5" / "x_2024_scale.csv"
        self.data.write_text("id,item,resp\n" + "".join(
            f"{i},q{j},{(i + j) % 5 + 1}\n" for i in range(1, 30) for j in (1, 2)))

    def _items(self, folder, body):
        p = self.root / folder / "x_2024_scale__items.csv"
        p.write_text(body)
        return p

    def test_staged_sibling_is_found(self):
        p = self._items("irw_text_3", "item,resp,option_text\nq1,1,lo\nq1,5,hi\n")
        self.assertEqual(staged_items(self.data, "x_2024_scale"), p)

    def test_batch_history_is_ignored(self):
        self._items("irw_text_3", "item,resp,option_text\nq1,1,lo\nq1,5,hi\n")
        (self.root / "irw_text_3" / "provenance.csv").write_text("table\n")
        self.assertIsNone(staged_items(self.data, "x_2024_scale"))

    def test_no_item_text_anywhere(self):
        pv, why = lookup(self.data, "x_2024_scale", {}, {"irw_text_3"}, "datapages")
        self.assertIsNone(pv)
        self.assertEqual(why, "no item text")

    def test_unreadable_published_table_is_reported_not_raised(self):
        index = {"x_2024_scale__items": ["irw_text_3"]}
        with unittest.mock.patch("red_up.permitted._from_redivis", side_effect=OSError("down")):
            pv, why = lookup(self.data, "x_2024_scale", index, {"irw_text_3"}, "datapages")
        self.assertIsNone(pv)
        self.assertTrue(why.startswith("could not read"), why)

    def _validate(self):
        report, = check_all([(self.data, "x_2024_scale")])
        cli._validate([report], RESPONSE, [RESPONSE, TEXT], {}, "datapages", enabled=True)
        return report

    def test_out_of_span_response_blocks(self):
        # Data run 1..5; the item text says the scale is 1..4.
        self._items("irw_text_3", "item,resp,option_text\nq1,1,lo\nq1,4,hi\nq2,1,lo\nq2,4,hi\n")
        report = self._validate()
        self.assertTrue(any("resp_outside_permitted" in e for e in report.errors), report.errors)

    def test_in_span_responses_pass(self):
        self._items("irw_text_3", "item,resp,option_text\nq1,1,lo\nq1,5,hi\nq2,1,lo\nq2,5,hi\n")
        report = self._validate()
        self.assertFalse(any("resp_outside_permitted" in e for e in report.errors), report.errors)

    def test_without_item_text_behaviour_is_unchanged(self):
        report = self._validate()
        self.assertFalse(any("permitted" in m for m in report.errors + report.warnings),
                         report.errors + report.warnings)



if __name__ == "__main__":
    unittest.main()
