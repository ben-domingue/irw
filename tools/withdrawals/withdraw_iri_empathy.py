"""Withdraw alsecypiamh_wu_2022_empathy's item text: it is the IRI's wording (irw#2401).

The 2026-09-30 rights follow-up (audit/2401/triage/rights_translations_followup.csv) read
the table item by item: Empathy1-7 are the Interpersonal Reactivity Index's Empathic
Concern subscale (Davis 1980; IRI items 2, 4, 9, 14, 18, 20, 22), in English, all seven
exact. The IRI is a `block` row in itemtext/instrument_rights_register.csv (2026-09-06,
irw#1955); dpt_noncog__interpersonal_reactivity was withdrawn on the same grounds, and
the three QCAE tables lost their IRI items on 2026-09-30 (withdraw_translated_rights.py).
The sweep had missed this table because the register's IRI code pattern does not match
`Empathy*` codes. Ben ruled: withdraw (audit/2401/RULES.md, "Decisions, round 3").

WHOLE: every item is the IRI, so there is nothing to keep.
  irw_text  alsecypiamh_wu_2022_empathy__items  35 rows
The response table alsecypiamh_wu_2022_empathy stays: the rulings are about wording.

The itemtext/withdrawals.csv row was written by hand with `released` blank, so do NOT
call ledger.record() when applying. Other pending withdrawals in the irw_text draft
(ledger rows with `released` blank, e.g. ali_2021_iesr__items and the jiang_2024 item
text) are allowed to be missing from it.

Takes effect at the next release; Ben publishes. Dry run by default; APPLY=1 applies.
"""
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_iri_empathy")
import redivis

OWNER = "datapages"
DATASET = "irw_text"
TARGET = "alsecypiamh_wu_2022_empathy__items"
EXPECTED_ROWS = 35  # measured 2026-09-30, v28_0

apply = os.environ.get("APPLY") == "1"

_ledger = Path(__file__).resolve().parents[2] / "itemtext" / "withdrawals.csv"
with open(_ledger, newline="", encoding="utf-8") as fh:
    PENDING = {r["table"] for r in csv.DictReader(fh)
               if r["dataset"] == DATASET and not r["released"].strip()} - {TARGET}


def names(version):
    return {t.name for t in redivis.organization(OWNER).dataset(DATASET, version=version)
            .list_tables(max_results=5000)}


current = names("current")
if TARGET not in current:
    sys.exit(f"ABORT: {TARGET} is not published in {DATASET}")
q = f"SELECT COUNT(*) AS n FROM `{OWNER}.{DATASET}:current.{TARGET}`"
n = int(redivis.query(q).to_pandas_dataframe()["n"].iloc[0])
if n != EXPECTED_ROWS:
    sys.exit(f"ABORT: {TARGET} has {n} rows, expected {EXPECTED_ROWS}; re-read it first")
print(f"{DATASET}: {TARGET} live with {n} rows")

if not apply:
    print("\nDRY RUN -- nothing deleted, no draft opened. Re-run with APPLY=1.")
    sys.exit(0)

base = redivis.organization(OWNER).dataset(DATASET)
base.get()
base.properties.setdefault("nextVersion", None)
base.create_next_version(if_not_exists=True)
ds = redivis.organization(OWNER).dataset(DATASET, version="next")
before = {t.name for t in ds.list_tables(max_results=5000)}
if TARGET not in before:
    sys.exit(f"Nothing to do: {TARGET} is already gone from the {DATASET} draft")
keep = current - {TARGET}
missing = keep - before - PENDING
if missing:
    sys.exit(f"ABORT: draft is missing published tables: {sorted(missing)[:5]}")
ds.table(TARGET).delete()
print(f"deleted: {DATASET}/{TARGET}")
after = names("next")
assert before - after == {TARGET}, f"MISMATCH: removed={sorted(before - after)}"
assert keep - PENDING <= after, f"went missing: {sorted(keep - after)}"
print("OK. The withdrawal sits in the draft; it reaches users at the next release, which Ben cuts.")
