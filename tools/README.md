# tools/

Scripts that changed published data once, kept because provenance records
cite them by path. **They have already run.** Do not rerun one to "check" it:
most of them write to a Redivis draft.

| Folder | Holds |
|---|---|
| `withdrawals/` | One script per table withdrawal, plus `ledger.py`, the live helper that appends each withdrawal to `itemtext/withdrawals.csv`. See its README |
| `repairs/` | One script per one-off repair |

New one-offs of either kind go here, not at the top of another directory.
Every Redivis write still goes through `red_up` or its helpers (see
`red_up/README.md`).
