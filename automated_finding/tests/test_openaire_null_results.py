"""OpenAIRE reports an empty result set as an explicit JSON null.

`{}.get(k, {})` only substitutes its default when the key is MISSING, so
`{"response": {"results": null}}` made from_openaire() raise
`'NoneType' object has no attribute 'get'`, which it turned into
SourceUnavailable -- i.e. a query OpenAIRE answered with "nothing found" was
recorded as "source not searched". 28 of the 134 queries in the 2026-10-28
sweep went that way.
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import irw_discover_updated as d  # noqa: E402


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _run(payload):
    with mock.patch.object(d.requests, "get", return_value=_Resp(payload)):
        return list(d.from_openaire("anything"))


ONE_HIT = {
    "metadata": {"oaf:entity": {"oaf:result": {
        "title": {"$": "A dataset"},
        "pid": [{"@classid": "doi", "$": "10.5281/zenodo.1"}],
        "dateofacceptance": {"$": "2024-01-02"},
    }}}
}


class TestOpenaireNullResults(unittest.TestCase):
    def test_dig_treats_explicit_null_as_absent(self):
        self.assertEqual(d._dig({"a": None}, "a", "b", default=[]), [])
        self.assertEqual(d._dig({"a": {"b": None}}, "a", "b", default=0), 0)
        self.assertEqual(d._dig({"a": {"b": 7}}, "a", "b"), 7)
        self.assertEqual(d._dig(None, "a", default="x"), "x")
        self.assertEqual(d._dig({"a": "scalar"}, "a", "b", default="x"), "x")

    def test_null_results_is_no_hits_not_an_outage(self):
        for payload in ({"response": None},
                        {"response": {"results": None}},
                        {"response": {"results": {"result": None}}}):
            self.assertEqual(_run(payload), [], payload)

    def test_null_total_does_not_crash(self):
        payload = {"response": {"results": {"result": [ONE_HIT]},
                                "header": {"total": None}}}
        hits = _run(payload)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].doi, "10.5281/zenodo.1")

    def test_single_hit_returned_unwrapped(self):
        payload = {"response": {"results": {"result": ONE_HIT},
                                "header": {"total": {"$": "1"}}}}
        hits = _run(payload)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].title, "A dataset")

    def test_a_real_outage_still_raises(self):
        def boom(*a, **k):
            raise RuntimeError("Read timed out")
        with mock.patch.object(d.requests, "get", boom):
            with self.assertRaises(d.SourceUnavailable):
                list(d.from_openaire("anything"))


if __name__ == "__main__":
    unittest.main()
