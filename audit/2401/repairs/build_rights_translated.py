#!/usr/bin/env python3
"""Blank rights-blocked wording from `*_translated` columns (#2401, RULES.md Decision 7).

Follow-up to build_itemtext.py (beck_2021_iesr). The 2026-09-29 rights sweep flagged
8 tables only through their `_translated` columns (audit/2401/triage/
rights_translated.csv); each was read item by item (audit/2401/repairs/
rights_translated.md). Two are confirmed and built here:

jablonska_2020_swls -- the whole table is the SWLS (Polish). item_text_translated
    is Diener's canonical English SWLS, 5/5 verbatim; option_text_translated is an
    English rendering of the Polish SWLS anchors (a derivative, as with beck's
    German anchors). Both columns go to NA on every row. The Polish base is kept.

queiros_2018_qcae -- the QCAE (Reniers et al. 2011) takes six items from Davis's
    IRI. item_text_translated goes to NA for QCAE_1..QCAE_6 only (the sweep caught
    1, 4, 5, 6; 2 and 3 are the IRI's FS "usually objective when I watch a movie or
    play" and PT "look at everybody's side of a disagreement", missed on wording/
    curly-apostrophe variants). The other 25 items, the QCAE instructions and the
    anchors are the QCAE's own and stay. Portuguese base kept.

NOT built: sun_2025_morality_study2_meaning (MLQ-Presence 5/5; the MLQ row covers
translations, so the Chinese base is itself blocked -- a whole withdrawal, held for
Ben). The other five flags were false positives.

Reads /home/ben/irw-stage/2401-audit/itemtext/live/<table>__live.csv (fetched with
irw::irw_itemtext(), --version current) and writes <table>__items.csv beside live/.
Text is handled as csv strings so IRW's literal "NA" survives. Nothing is uploaded.
"""
import csv
from pathlib import Path

STAGE = Path("/home/ben/irw-stage/2401-audit/itemtext")
LIVE = STAGE / "live"

PLAN = {
    "jablonska_2020_swls": {"cols": ["item_text_translated", "option_text_translated"],
                            "items": None},  # every row
    "queiros_2018_qcae": {"cols": ["item_text_translated"],
                          "items": {f"QCAE_{i}" for i in range(1, 7)}},
}


def build(t, cols, items):
    with open(LIVE / f"{t}__live.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        header, live = rd.fieldnames, list(rd)
    assert set(cols) <= set(header), f"{t}: missing {cols}"
    if items is not None:
        assert items <= {r["item"] for r in live}, f"{t}: items not all present"
    out, n = [], 0
    for r in live:
        r = dict(r)
        if items is None or r["item"] in items:
            for c in cols:
                if r[c] != "NA":
                    n += 1
                r[c] = "NA"
        out.append(r)
    # nothing but the targeted cells changed
    for a, b in zip(live, out):
        for c in header:
            if a[c] != b[c]:
                assert c in cols and (items is None or a["item"] in items), f"{t}: {c} changed"
    dst = STAGE / f"{t}__items.csv"
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(out)
    print(f"  {t:<24} {len(out):>3} rows, {n} cells blanked -> {dst}")


if __name__ == "__main__":
    for t, p in PLAN.items():
        build(t, p["cols"], p["items"])
