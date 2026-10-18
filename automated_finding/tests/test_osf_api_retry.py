"""An OSF 503 is a transient refusal, not an empty deposit.

Regression test for the defect the 2026-10-16 PMC monthly run exposed: 10 of
its 13 `download_failed` rows were `503 Service Temporarily Unavailable` from
api.osf.io on a single attempt, which reads in the output exactly like a dead
link -- so ten OSF deposits were recorded as failures without ever being
listed. Offline, synthetic.
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import irw_batch_updated  # noqa: E402


class _Resp:
    def __init__(self, status):
        self.status_code = status
        self.headers = {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"{self.status_code} Server Error",
                                                response=self)

    def json(self):
        return {"data": {}}


class OsfApiRetryTest(unittest.TestCase):
    URL = "https://api.osf.io/v2/guids/abcde/"

    def _run(self, statuses):
        seen = []

        def fake_get(url, params=None, headers=None, timeout=None):
            seen.append(url)
            return _Resp(statuses[min(len(seen) - 1, len(statuses) - 1)])

        with mock.patch.object(irw_batch_updated.requests, "get", fake_get), \
             mock.patch.object(irw_batch_updated.time, "sleep", lambda *_: None):
            try:
                return irw_batch_updated._osf_api_get(self.URL, {}), seen, None
            except requests.exceptions.HTTPError as e:
                return None, seen, e

    def test_503_is_retried_then_succeeds(self):
        r, seen, err = self._run([503, 503, 200])
        self.assertIsNone(err)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(seen), 3, "a 503 must be retried, not believed")

    def test_a_persistent_503_still_raises(self):
        r, seen, err = self._run([503])
        self.assertIsNotNone(err)
        self.assertEqual(len(seen), 4, "four attempts, then give up")

    def test_a_404_is_not_retried(self):
        r, seen, err = self._run([404])
        self.assertIsNotNone(err)
        self.assertEqual(len(seen), 1, "a hard 404 must not be retried")

    def test_429_is_retried(self):
        r, seen, err = self._run([429, 200])
        self.assertIsNone(err)
        self.assertEqual(len(seen), 2)


if __name__ == "__main__":
    unittest.main()
