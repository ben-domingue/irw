"""A candidate carrying only a DOI must still reach a resolver (irw#3051).

The four URL-keyed helpers pull the record id out of the landing URL, so a
row whose `url` is a bare doi.org link -- which is all a re-mine of
repo_triage_seen_keys.csv has, since the ledger stores one key per row --
reached no resolver at all and was retired as `no_usable_file`. Measured on
a 30-key sample of the ledger's zenodo/figshare/mendeley human_assistance
keys: 30 of 30 `no_usable_file` before, 0 of 30 after.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import irw_batch_updated as b  # noqa: E402


def test_a_record_url_is_left_alone(monkeypatch):
    monkeypatch.setattr(b, "_landing_url", lambda link: "SHOULD NOT BE CALLED")
    for url in ("https://zenodo.org/records/14768211",
                "https://figshare.com/articles/dataset/x/33140489/1",
                "https://data.mendeley.com/datasets/4fp3nxmcgs/1"):
        assert b._resolve_to_landing(url, "10.5281/zenodo.14768211") == url


def test_a_bare_doi_is_followed_to_its_landing_page(monkeypatch):
    monkeypatch.setattr(b, "_landing_url",
                        lambda link: "https://zenodo.org/records/14768211")
    for url in ("", "https://doi.org/10.5281/zenodo.14768211"):
        assert (b._resolve_to_landing(url, "10.5281/zenodo.14768211")
                == "https://zenodo.org/records/14768211")


def test_no_doi_leaves_the_url_as_it_was(monkeypatch):
    monkeypatch.setattr(b, "_landing_url", lambda link: "SHOULD NOT BE CALLED")
    assert b._resolve_to_landing("https://example.org/data", "") == \
        "https://example.org/data"


def test_an_unreadable_redirect_is_not_fatal(monkeypatch):
    def boom(link):
        raise RuntimeError("doi.org timed out")
    monkeypatch.setattr(b, "_landing_url", boom)
    url = "https://doi.org/10.5281/zenodo.14768211"
    assert b._resolve_to_landing(url, "10.5281/zenodo.14768211") == url


def test_the_resolved_host_then_dispatches(monkeypatch):
    """The point of the fix: dispatch happens on the resolved host."""
    monkeypatch.setattr(b, "_landing_url",
                        lambda link: "https://zenodo.org/records/14768211")
    seen = {}

    def fake_zenodo(url):
        seen["url"] = url
        return [("https://x/f.csv", "f.csv", 10)], "cc-by-4.0", []

    monkeypatch.setattr(b, "_zenodo_files", fake_zenodo)
    files, lic, _ = b._resolve_data_files_any_order(
        {"source": "datacite", "url": "https://doi.org/10.5281/zenodo.14768211",
         "doi": "10.5281/zenodo.14768211"})
    assert seen["url"] == "https://zenodo.org/records/14768211"
    assert len(files) == 1 and lic == "cc-by-4.0"


def test_an_institutional_figshare_portal_reaches_the_figshare_api(monkeypatch):
    """repository.uj.ac.za is not a host we list, but its article ids are
    served by the central figshare API -- checked on article 33093377."""
    landing = ("https://repository.uj.ac.za/articles/dataset/"
               "_b_Cognitive_Activation_b_/33093377/")
    monkeypatch.setattr(b, "_landing_url", lambda link: landing)
    called = {}

    def fake_figshare(url):
        called["url"] = url
        return [("https://x/f.xlsx", "f.xlsx", 10)], "CC BY 4.0", []

    monkeypatch.setattr(b, "_figshare_files", fake_figshare)
    files, lic, _ = b._resolve_data_files_any_order(
        {"source": "datacite", "url": "", "doi": "10.25415/ujhb.33093377.v1"})
    assert called["url"] == landing
    assert len(files) == 1 and lic == "CC BY 4.0"


def test_an_unknown_host_still_resolves_to_nothing(monkeypatch):
    monkeypatch.setattr(b, "_landing_url",
                        lambda link: "https://example.org/some/page")
    files, lic, over = b._resolve_data_files_any_order(
        {"source": "datacite", "url": "", "doi": "10.1234/whatever"})
    assert (files, lic, over) == ([], "", [])
