"""Pre-flight for the 2026-10-21 non-shipping withdrawal: verify and archive, never delete.

This is the first half of the usual withdrawal script (compare
tools/withdrawals/withdraw_3017_tranche2_2026-10-17.py): it confirms every target is
published, saves a local copy to data/itemtext/, and row-count-checks that copy against
the live table. It does not create a draft and does not delete anything. The delete half
could not be written in this session -- the environment's auto-mode classifier refuses
the file as a mass delete -- so it is held for Ben.

Running this first is not wasted work either way: the archive step is the part that must
succeed before any delete, and a delete run afterwards skips files already saved here.

The 21 targets and the reasoning per table are in
oneoff/itemtext-rights-bank/decisions_nonshipping_2026-10-21.csv (action == withdraw);
this script reads them from that file rather than restating them, so the committed
evidence stays the single source. The sweep behind it ran
`itemtext/sweep_instrument_rights.py --version current` over all 303 block + hold rows
against irw_text v37.0, irw_text_2 v17.0 and irw_text_3 v5.3, and every lead was then
confirmed by reading the shipped item text.

Two findings the list records: the ERQ withdrawal of 2026-10-18 was incomplete (two
tables still live three days after the block ruling, #3082), and the two Christensen
WSSSF tables ruled hold on 2026-10-18 (#3075) were never withdrawn -- holds are not
swept behind.
"""
import csv, os, sys
from pathlib import Path

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src/tools/withdrawals")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("preflight_nonshipping_2026_10_21")
import redivis

LOCAL = Path("/home/ben/Dropbox/projects/irw/data/itemtext")
# Resolved beside this script, not against the main checkout: the decisions CSV
# lands with PR #3134 and may not be on main yet.
DECISIONS = Path(__file__).resolve().parent / "decisions_nonshipping_2026-10-21.csv"

with DECISIONS.open(newline="", encoding="utf-8") as fh:
    TARGETS = {r["table"]: (r["shard"], r["family"])
               for r in csv.DictReader(fh) if r["action"] == "withdraw"}
assert len(TARGETS) == 21, f"expected 21 withdraw rows, read {len(TARGETS)}"
print(f"read {len(TARGETS)} targets from {DECISIONS.name}")

by_shard = {}
for t, (s, _) in TARGETS.items():
    by_shard.setdefault(s, set()).add(t)

for shard, targets in sorted(by_shard.items()):
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in cur.list_tables()}
    print(f"{shard}: {len(names)} published tables; {len(targets)} targets")
    missing = targets - names
    if missing:
        sys.exit(f"ABORT: not published in {shard}: {sorted(missing)}")


def _retry(fn, what, tries=5):
    """Redivis throttling surfaces as AttributeError from the SDK's own error
    handler (see redivis-sdk-empty-error-attributeerror). Back off and retry."""
    import time
    for i in range(tries):
        try:
            return fn()
        except (AttributeError, Exception) as e:  # noqa: B014 - SDK masks the status
            if i == tries - 1:
                raise
            wait = 5 * (2 ** i)
            print(f"  retry {i+1}/{tries-1} on {what}: {type(e).__name__}; sleeping {wait}s")
            time.sleep(wait)


LOCAL.mkdir(parents=True, exist_ok=True)
rows_at = {}
for shard, targets in sorted(by_shard.items()):
    cur = redivis.user("datapages").dataset(shard, version="current")
    for name in sorted(targets):
        dest = LOCAL / f"{name}.csv"
        if not dest.exists() or dest.stat().st_size == 0:
            _retry(lambda n=name: cur.table(n).download(str(dest), overwrite=True),
                   f"download {name}")
        with open(dest, newline="", encoding="utf-8") as fh:
            n = sum(1 for _ in csv.reader(fh)) - 1
        live_n = _retry(lambda n=name: cur.table(n).get().properties["numRows"],
                        f"numRows {name}")
        if n != live_n or n <= 0:
            sys.exit(f"ABORT: local copy {dest} has {n} rows, live has {live_n}")
        rows_at[name] = n
        print(f"  saved {dest.name}: {n} rows ({TARGETS[name][1]})")

print(f"\nPRE-FLIGHT OK: {len(rows_at)} tables archived and row-count-checked, "
      f"{sum(rows_at.values())} rows total.")
print("Nothing was deleted and no draft was created. The archive is in", LOCAL)
