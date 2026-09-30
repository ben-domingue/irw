#!/usr/bin/env python3
"""Drop rights-blocked items from three QCAE item-text tables (#2401).

History. The 2026-09-29 rights sweep flagged 8 tables only through their
`_translated` columns (audit/2401/triage/rights_translated.csv). The first pass of
this script blanked the `_translated` wording only (RULES.md Decision 7). Ben then
ruled the same day that a `block` row covers the instrument IN EVERY LANGUAGE, in
item_text as well as `*_translated` (RULES.md, "A block covers translations"). So:

  queiros_2018_qcae (Portuguese), gomez_2022_qcae and powell_2018_qcae (English) --
      QCAE items 1-6 are Davis's Interpersonal Reactivity Index (IRI, block): PT
      items 1, 3, 4, 5, 6 and FS item 2. Their rows are DROPPED (the partial-withdrawal
      pattern of withdraw_bfi2.py / eammi_grahe_2018_swb: rows removed, table kept).
      The other 25 QCAE items, the instructions and the anchors are the QCAE's own
      and are unchanged. 124 -> 100 rows each.
      gomez_2022_qcae's codes for items 1 and 2 are QCAE1r / QCAE2r (the deposit's
      reverse-keyed columns); the wording is still the IRI's.

  jablonska_2020_swls and sun_2025_morality_study2_meaning are WHOLE withdrawals
      (Polish SWLS; Chinese MLQ-Presence), so nothing is built for them; the earlier
      _translated-only jablonska staging was removed.

Reads /home/ben/irw-stage/2401-audit/itemtext/live/<table>__live.csv (fetched with
irw::irw_itemtext(), current version) and writes <table>__items.csv beside live/.
Rows are handled as csv strings so IRW's literal "NA" survives. Nothing is uploaded.
"""
import csv
from pathlib import Path

STAGE = Path("/home/ben/irw-stage/2401-audit/itemtext")
LIVE = STAGE / "live"

DROP = {
    "queiros_2018_qcae": {f"QCAE_{i}" for i in range(1, 7)},
    "gomez_2022_qcae": {"QCAE1r", "QCAE2r", "QCAE3", "QCAE4", "QCAE5", "QCAE6"},
    "powell_2018_qcae": {f"QCAE{i}" for i in range(1, 7)},
}
# One IRI stem per table, as a check that the dropped items are the IRI's.
IRI_STEM = "look at everybody’s side of a disagreement"


def build(t, drop):
    with open(LIVE / f"{t}__live.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        header, live = rd.fieldnames, list(rd)
    items = {r["item"] for r in live}
    assert drop <= items, f"{t}: missing {sorted(drop - items)}"
    txt = "item_text_translated" if "item_text_translated" in header else "item_text"
    assert any(IRI_STEM in r[txt] for r in live if r["item"] in drop), f"{t}: IRI stem not in drop set"
    out = [r for r in live if r["item"] not in drop]
    assert not any(IRI_STEM in r[c] for r in out for c in header), f"{t}: IRI stem survives"
    assert len({r["item"] for r in out}) == len(items) - len(drop)
    dst = STAGE / f"{t}__items.csv"
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(out)
    print(f"  {t:<20} {len(live):>3} -> {len(out):>3} rows, "
          f"{len(items)} -> {len(items) - len(drop)} items -> {dst}")


if __name__ == "__main__":
    for t, d in DROP.items():
        build(t, d)
