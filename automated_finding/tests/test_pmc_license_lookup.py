"""An empty Europe PMC core result is a failed lookup, not an absent licence.

Regression test for the defect the 2026-09-20 recycled-term sweep exposed:
34 of its 34 `unknown` licence rows re-checked as `cc-by` minutes later,
because fetch_core_license read an empty resultList as "" and check_license
normalised that to `unknown` -- a sticky verdict on a DOI that then went
into the seen ledger.
"""
import irw_discover_pmc as pmc


def test_empty_result_retries_then_reports_lookup_failure(monkeypatch):
    calls = []

    def fake_get(params):
        calls.append(params)
        return {"resultList": {"result": []}}

    monkeypatch.setattr(pmc, "_europepmc_get", fake_get)
    monkeypatch.setattr(pmc.time, "sleep", lambda *_: None)
    assert pmc.fetch_core_license("PMC1") == pmc.LICENSE_LOOKUP_FAILED
    assert len(calls) == 3, "an empty result must be retried, not believed"


def test_empty_result_that_recovers_returns_the_licence(monkeypatch):
    bodies = [{"resultList": {"result": []}},
              {"resultList": {"result": [{"license": "cc by"}]}}]
    monkeypatch.setattr(pmc, "_europepmc_get", lambda p: bodies.pop(0))
    monkeypatch.setattr(pmc.time, "sleep", lambda *_: None)
    assert pmc.fetch_core_license("PMC1") == "cc by"


def test_record_without_a_licence_field_is_a_real_absence(monkeypatch):
    calls = []

    def fake_get(params):
        calls.append(params)
        return {"resultList": {"result": [{"title": "no licence here"}]}}

    monkeypatch.setattr(pmc, "_europepmc_get", fake_get)
    assert pmc.fetch_core_license("PMC1") == ""
    assert len(calls) == 1, "a record that WAS read must not be retried"


def test_lookup_failure_is_inconclusive_so_the_doi_is_not_ledgered():
    assert "license_lookup_failed" in pmc.INCONCLUSIVE_FLAGS
