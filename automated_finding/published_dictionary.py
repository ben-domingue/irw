"""The published dictionary record: what `biblio.csv` says about a table.

The Data Dictionary sheet is the human entry surface, not the record. Three
mechanisms correct metadata at EXPORT time and deliberately leave the sheet
alone -- `DESCRIPTION_OVERRIDES` (wrong Descriptions), `apply_license_attribution`
(ODC-By second sources), `apply_osf_permission` (`Permission via Email` on 115
rows) -- and `dictionary_auto.csv` rows reach the export without passing
through the sheet. So a tool that reads the sheet reads the uncorrected
values, and misses every automated row that was never pasted there (#2067).
The export (`metadata/*biblio*.csv`, refreshed by the weekly pipeline) is what
users see; tools that want the record read it here.

One loader, so the tagger and the naming audit cannot disagree about which
file is the record. Keyed on the lowercased table name: 307 names differ from
their other rows only by case.

It does NOT carry the sheet's intake columns (`Contributor`, `Date`, `Notes`,
`Public Reshare?`) -- those describe the entry, not the table, and the export
drops them. A tool that selects rows by them still reads the entry surface for
the selection, and the export for the values.
"""
from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: Every source's export. Same columns in all four (02_biblio.R writes them).
BIBLIO_FILES = ("biblio.csv", "nominal_biblio.csv", "comps_biblio.csv",
                "simsyn_biblio.csv")

#: biblio column -> the name callers use.
FIELDS = {
    "Description": "description",
    "URL__for_data_": "url",
    "Reference_x": "reference",
    "DOI__for_paper_": "doi",
    "DOI__for_data_": "data_doi",
    "Original_License": "original_license",
    "Derived_License": "derived_license",
}


def _clean(v) -> str:
    v = (v or "").strip()
    return "" if v in ("NA", "nan") else v


def load_published(root: Path = REPO) -> dict:
    """lowercase table -> {description, url, reference, doi, data_doi,
    original_license, derived_license, file}. The first file wins on a
    collision, and core's biblio.csv is read first."""
    out = {}
    for name in BIBLIO_FILES:
        path = Path(root) / "metadata" / name
        if not path.is_file():
            continue
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                key = _clean(row.get("table")).lower()
                if not key or key in out:
                    continue
                rec = {dst: _clean(row.get(src)) for src, dst in FIELDS.items()}
                rec["file"] = f"metadata/{name}"
                out[key] = rec
    return out


def load_auto_rows(root: Path = REPO) -> dict:
    """lowercase table -> its row in automated_finding/dictionary_auto.csv, in
    the sheet's column names. For a table the weekly export has not reached yet."""
    path = Path(root) / "automated_finding" / "dictionary_auto.csv"
    out = {}
    if not path.is_file():
        return out
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row.get("table.lower") or row.get("table") or "").strip().lower()
            if key and key not in out:
                out[key] = row
    return out
