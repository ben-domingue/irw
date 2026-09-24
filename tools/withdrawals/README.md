# tools/withdrawals/

One script per withdrawal: each removes specific tables from a Redivis **draft**,
so they disappear at the next release. Most delete item-text tables from
`irw_text` after a rights ruling (see `itemtext/instrument_rights_register.csv`).
The rest pull response tables for personal data, duplication or misnaming.
`withdraw_personal_data_2026_09_19.py`, `withdraw_online_addiction.py`,
`withdraw_joreskog_moustaki_2001.py`, `withdraw_zhou_2025_peer_relationship_w5.py`
and `retire_marcatto_ocs.py` fall in that group.

Each has already been run. They stay here because provenance records, the
rights register and `itemtext/extraction_batches/round_log.md` cite them by
path as the record of what was removed and why. Read the docstring before
rerunning one: they are dry-run by default (`APPLY=1` applies), and the table
they target may already be gone.

A new withdrawal goes here as `withdraw_<what>.py`, following the same shape:
a write token from `irw_secrets.load_write_token()`, an explicit `TARGETS`
list, dry run first.
