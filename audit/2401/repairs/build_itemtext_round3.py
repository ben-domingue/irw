#!/usr/bin/env python3
"""Item-text follow-ups from the #2401 rebuild batch (audit/2401/repairs/itemtext_followups.md).

amatus_cipora_2024_fsmas_se -- option_text for FSMAS_SE1-SE4 reversed.
    The AMATUS codebook marks SE1-SE4 Reversed = yes and the stored values are
    reverse-keyed on those four (all inter-item correlations positive; the stored
    items sum to score_FSMAS_SE), so on SE1-SE4 resp 1 = "no" ... 5 = "yes". The live
    table labelled every item 1 = "yes" ... 5 = "no". SE5-SE9 are unchanged, and no
    field other than option_text on SE1-SE4 changes (asserted below). Approved by Ben.

tuason_2021_covid_coping_enjoy is NOT built: the live __items table carries no
public_note column, so only its provenance row changes.

Reads /home/ben/irw-stage/2401-audit/itemtext_round3/live/<table>__live.csv
(irw::irw_itemtext(), current version, 2026-09-30) and writes <table>__items.csv
beside live/. Rows are handled as csv strings so IRW's literal "NA" survives.
Nothing is uploaded.
"""
import csv
from pathlib import Path

STAGE = Path("/home/ben/irw-stage/2401-audit/itemtext_round3")
LIVE = STAGE / "live"

T = "amatus_cipora_2024_fsmas_se"
REVERSED = {f"FSMAS_SE{i}" for i in range(1, 5)}
LIVE_MAP = {"1": "yes", "2": "rather yes", "3": "partly partly", "4": "rather no", "5": "no"}
FIXED_MAP = {"1": "no", "2": "rather no", "3": "partly partly", "4": "rather yes", "5": "yes"}


def main():
    with open(LIVE / f"{T}__live.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        header, live = rd.fieldnames, list(rd)
    assert len(live) == 45
    assert {r["item"] for r in live} == {f"FSMAS_SE{i}" for i in range(1, 10)}
    assert all(LIVE_MAP[r["resp"]] == r["option_text"] for r in live), "live map not as documented"
    out = []
    for r in live:
        r2 = dict(r)
        if r["item"] in REVERSED:
            r2["option_text"] = FIXED_MAP[r["resp"]]
        out.append(r2)
    for a, b in zip(live, out):
        for c in header:
            if c == "option_text" and a["item"] in REVERSED:
                continue
            assert a[c] == b[c], f"{a['item']} {c} changed"
    changed = sum(a["option_text"] != b["option_text"] for a, b in zip(live, out))
    assert changed == 16, changed  # 4 items x 4 non-midpoint levels
    dst = STAGE / f"{T}__items.csv"
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(out)
    print(f"  {T}: {len(out)} rows, {changed} option_text cells changed -> {dst}")


if __name__ == "__main__":
    main()
