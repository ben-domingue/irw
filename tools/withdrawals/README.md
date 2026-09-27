# tools/withdrawals/

One script per withdrawal: each removes specific tables from a Redivis **draft**,
so they disappear at the next release. Most delete item-text tables from
`irw_text` after a rights ruling (see `itemtext/instrument_rights_register.csv`).
The rest pull response tables for personal data, duplication or misnaming.
`withdraw_personal_data_2026_09_19.py`, `withdraw_online_addiction.py`,
`withdraw_joreskog_moustaki_2001.py`, `withdraw_zhou_2025_peer_relationship_w5.py`, `withdraw_sun_2025_study1_informant.py`, `withdraw_renamed_2198.py`
and `retire_marcatto_ocs.py` fall in that group.

Each has already been run. They stay here because provenance records, the
rights register and `itemtext/extraction_batches/round_log.md` cite them by
path as the record of what was removed and why. Read the docstring before
rerunning one: they are dry-run by default (`APPLY=1` applies), and the table
they target may already be gone.

A new withdrawal goes here as `withdraw_<what>.py`, following the same shape:
a write token from `irw_secrets.load_write_token()`, an explicit `TARGETS`
list, dry run first -- and, once its draft assertions pass, one call to
`ledger.record(...)` so each withdrawn table gets a row in
`itemtext/withdrawals.csv`, then commit that file with the script.

## `itemtext/withdrawals.csv` -- the record keyed by table name (#2155)

The rights register is organised by instrument, and only tables built by the
batch pipeline have a `provenance.csv`. So for an older table nothing keyed by
its own name said why it was gone: `git grep aspirations_sonmez_2022` found
nothing, and #2132 was filed claiming there was no record. `withdrawals.csv`
is the reverse index -- one row per withdrawn table, whatever the reason.

- **Append-only.** Never rewrite or remove a row. The one column filled later
  is `released`: the version at which the withdrawal left `current`, since a
  draft deletion is invisible until Ben publishes.
- `reason` is one of `rights`, `wrong_data`, `duplicate`, `personal_data`,
  `misnamed`, `unlicensed`. A `rights` row names the register `family`.
- `dataset` ending in `*` means the script found the shard at run time and
  did not record which one.
- `itemtext/tests/test_withdrawals.py` fails a pull request that adds a script
  here without its rows in the ledger.

**The backfill (2026-09-27) is from these scripts only**, so it is not a
complete history. Its `withdrawn` dates are the date each script was
committed, which is not always the date it was applied. Its `released` column
is blank. PSS round 1, and the two PSS tables handled before
`withdraw_pss_sweep.py`, are included from that script's `ROUND1`/`ALREADY`
sets and have no script of their own. Withdrawals made by hand or by other
tools are not in it (PROMIS, for example).
