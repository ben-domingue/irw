"""An OSF 503 is a transient refusal, not an empty deposit.

Regression test for the defect the 2026-10-16 PMC monthly run exposed: 10 of
its 13 `download_failed` rows were `503 Service Temporarily Unavailable` from
api.osf.io on a single attempt, which reads in the output exactly like a dead
link -- so ten cc-by OSF deposits were recorded as failures without ever
being listed. Offline, synthetic.
"""
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import irw_batch_updated as batch  # noqa: E402


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


def test_503_is_retried_then_succeeds(monkeypatch):
    seen = []

    def fake_get(url, params=None, headers=None, timeout=None):
        seen.append(url)
        return _Resp(503 if len(seen) < 3 else 200)

    monkeypatch.setattr(batch.requests, "get", fake_get)
    monkeypatch.setattr(batch.time, "sleep", lambda *_: None)
    r = batch._osf_api_get("https://api.osf.io/v2/guids/abcde/", {})
    assert r.status_code == 200
    assert len(seen) == 3, "a 503 must be retried, not believed"


def test_a_persistent_503_still_raises(monkeypatch):
    seen = []

    def fake_get(url, params=None, headers=None, timeout=None):
        seen.append(url)
        return _Resp(503)

    monkeypatch.setattr(batch.requests, "get", fake_get)
    monkeypatch.setattr(batch.time, "sleep", lambda *_: None)
    with pytest.raises(requests.exceptions.HTTPError):
        batch._osf_api_get("https://api.osf.io/v2/guids/abcde/", {})
    assert len(seen) == 4


def test_a_404_is_not_retried(monkeypatch):
    seen = []

    def fake_get(url, params=None, headers=None, timeout=None):
        seen.append(url)
        return _Resp(404)

    monkeypatch.setattr(batch.requests, "get", fake_get)
    monkeypatch.setattr(batch.time, "sleep", lambda *_: None)
    with pytest.raises(requests.exceptions.HTTPError):
        batch._osf_api_get("https://api.osf.io/v2/guids/abcde/", {})
    assert len(seen) == 1, "a hard 404 must not be retried"
