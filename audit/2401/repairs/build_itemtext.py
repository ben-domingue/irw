#!/usr/bin/env python3
"""Rebuild five item-text tables for the #2401 audit (RULES.md Decisions 7 and 8).

Reads the live copies fetched with irw::irw_itemtext() into
/home/ben/irw-stage/2401-audit/itemtext/live/<table>__live.csv and writes
/home/ben/irw-stage/2401-audit/itemtext/<table>__items.csv. Nothing is uploaded.

bitew_2020_{lte,osss3,phq9,self_efficacy} -- administered-language fallback.
    The study was administered in Amharic (PLOS ONE 10.1371/journal.pone.0240914,
    Methods: "self-administered Amharic version of questionnaires"); the deposit (S1
    .sav) and S2 carry zero Ethiopic characters, so the Amharic wording is not
    recoverable. Per the 2026-09-01 schema fallback and the round-2 precedent
    (itemtext/language_backfill/round2/add_language.py): English STAYS in the base
    fields, `language` = Amharic, the four `_translated` columns are present and
    empty. No base text field moves -- asserted below.
    bitew_2020_self_efficacy additionally gains SEFFICAY (GSE item 1), which the
    response table has carried since the 2026-08-31 restore (table_changes.csv,
    #1655) and the item text never did, so the table failed the item-set join.

beck_2021_iesr -- IES-R rights block covers `*_translated` (Ben, 2026-09-29).
    The four `_translated` columns are emptied: item_text_translated was Weiss &
    Marmar's English IES-R verbatim, and the instructions/anchor English are
    renderings of the German IES-R, itself a derivative of the blocked instrument.
    The German base fields are untouched.

ali_2021_iesr is NOT built: its item_text is itself the English Weiss & Marmar
IES-R (22/22), so the ruling is a whole withdrawal, not a column removal -- held
for Ben.

Text is handled as strings at the csv level so IRW's literal "NA" survives.
After building: normalize_nulls.R over the staging dir, then validate_items.R
--table-sets, audit_batch.R and irw-validate (all passed 2026-09-29).
"""
import csv
from pathlib import Path

STAGE = Path("/home/ben/irw-stage/2401-audit/itemtext")
LIVE = STAGE / "live"
TR = ["instructions_translated", "section_prompt_translated",
      "item_text_translated", "option_text_translated"]
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"] + TR
UNTOUCHED = ["table", "section_id", "item", "instrument", "instructions",
             "section_prompt", "item_text", "correct_response", "option_text", "resp"]

# GSE item 1, Schwarzer & Jerusalem (1995) canonical English -- the same source as
# the nine items already shipped. The .sav labels SEFFICAY "perform difficult work"
# with the same never/sometimes/right/very/right value labels as SEFFICA1-9.
SEFFICAY = "I can always manage to solve difficult problems if I try hard enough"
GSE_OPTIONS = [("never", "0"), ("sometimes", "1"), ("right", "2"), ("very/right", "3")]


def read(t):
    with open(LIVE / f"{t}__live.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(t, rows):
    out = STAGE / f"{t}__items.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "NA") for c in COLS})
    return out


def same_text(a, b, t):
    for x, y in zip(a, b):
        for c in UNTOUCHED:
            assert (x.get(c) or "") == (y.get(c) or ""), f"{t}: {c} changed"


def bitew():
    for t in ["bitew_2020_lte", "bitew_2020_osss3", "bitew_2020_phq9",
              "bitew_2020_self_efficacy"]:
        live = read(t)
        assert "language" not in live[0], f"{t}: already has language"
        out = []
        for r in live:
            r = dict(r)
            r["language"] = "Amharic"
            for c in TR:
                r[c] = "NA"
            out.append(r)
        same_text(live, out, t)
        if t == "bitew_2020_self_efficacy":
            assert "SEFFICAY" not in {r["item"] for r in live}
            tmpl = live[0]
            for opt, resp in GSE_OPTIONS:
                r = {c: tmpl.get(c, "NA") for c in COLS}
                r.update(item="SEFFICAY", item_text=SEFFICAY, option_text=opt,
                         resp=resp, language="Amharic", **{c: "NA" for c in TR})
                out.append(r)
            items = {r["item"] for r in out}
            assert items == {"SEFFICAY"} | {f"SEFFICA{i}" for i in range(1, 10)}
        print(f"  {t:<28} {len(live):>3} -> {len(out):>3} rows  {write(t, out)}")


def beck():
    t = "beck_2021_iesr"
    live = read(t)
    assert set(TR) <= set(live[0]), f"{t}: no _translated columns live"
    out = []
    for r in live:
        r = dict(r)
        for c in TR:
            r[c] = "NA"
        out.append(r)
    same_text(live, out, t)
    assert all(r["language"] == "German" for r in out)
    assert all(r[c] == "NA" for r in out for c in TR)
    print(f"  {t:<28} {len(live):>3} -> {len(out):>3} rows  {write(t, out)}")


if __name__ == "__main__":
    bitew()
    beck()
