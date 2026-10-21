"""Fill itemtext/withdrawals.csv's `released` column from observed version history.

`released` is the version at which a withdrawal left `current` -- a draft deletion
is invisible until Ben publishes. The column has been left blank at write time ever
since the ledger existed, so it cannot say what has taken effect.

Method, per row: walk that dataset's released versions in order and find the first
version where the table is ABSENT having been PRESENT in an earlier one. That
transition is the release that withdrew it. Versions whose table list came back
empty are skipped, not read as an absence.

Deliberately conservative -- a row is left blank, and reported, when:
  * the table is still present in the newest version (not yet effective),
  * it never appears in any version (never released under that name),
  * or a wildcard dataset ("irw_text*") cannot be resolved to exactly one shard.

A withdrawal reversed before any release never left, so it stays blank -- which is
the right answer, not a gap: the cremer PANAS row is blank because that withdrawal
was undone on 10-17 before irw_text_3 ever published it.

Usage: stamp_released.py <index.json> <ledger.csv> [--apply]
"""
import csv, json, re, sys
from pathlib import Path

index_path, ledger_path = Path(sys.argv[1]), Path(sys.argv[2])
APPLY = "--apply" in sys.argv

idx = json.loads(index_path.read_text())
IDX = {ds: {v: set(names) for v, names in vers.items() if names}
       for ds, vers in idx.items()}

TEXT = ["irw_text", "irw_text_2", "irw_text_3"]
RESP = ["item_response_warehouse"] + [f"item_response_warehouse_{i}" for i in range(2, 9)]


def vkey(tag):
    return tuple(int(x) for x in re.findall(r"\d+", tag))


def first_absence(ds, table):
    """The version where `table` went missing, or a reason it cannot be said."""
    vers = IDX.get(ds)
    if not vers:
        return None, "dataset not indexed"
    order = sorted(vers, key=vkey)
    seen = False
    for tag in order:
        here = table in vers[tag]
        if here:
            seen = True
        elif seen:
            return tag, None
    if not seen:
        return None, "never present in any released version"
    return None, "still present in the newest version"


def candidates(ds):
    if not ds.endswith("*"):
        return [ds]
    stem = ds[:-1]
    pool = TEXT if stem.startswith("irw_text") else RESP
    return [d for d in pool if d.startswith(stem) or stem.startswith(d)] or pool


with ledger_path.open(newline="") as fh:
    rd = csv.DictReader(fh)
    cols, rows = rd.fieldnames, list(rd)

filled = 0
reasons = {}
resolved_ds = 0
partial_skipped = 0
for r in rows:
    if r["released"]:
        continue
    if r["kind"] == "partial":
        # A redaction leaves the table in place: it drops rows or blanks a column.
        # Absence cannot date it, so these are never stamped from version history.
        reasons[(r["dataset"], r["table"])] = "partial withdrawal -- absence cannot date a redaction"
        partial_skipped += 1
        continue
    hits = []
    for ds in candidates(r["dataset"]):
        tag, why = first_absence(ds, r["table"])
        if tag:
            hits.append((ds, tag))
        reasons.setdefault((r["dataset"], r["table"]), why)
    if len(hits) == 1:
        ds, tag = hits[0]
        r["released"] = tag
        filled += 1
        if ds != r["dataset"]:
            r["dataset"] = ds
            resolved_ds += 1
    elif len(hits) > 1:
        reasons[(r["dataset"], r["table"])] = f"ambiguous: left {hits}"

blank = [r for r in rows if not r["released"]]
print(f"filled {filled} of {filled + len(blank)} blank rows; "
      f"{resolved_ds} wildcard dataset names resolved; "
      f"{partial_skipped} partial rows skipped by rule")
import collections
why = collections.Counter(reasons.get((r["dataset"].rstrip('*') + '*', r["table"]))
                          or reasons.get((r["dataset"], r["table"]))
                          or "unknown" for r in blank)
for k, v in why.most_common():
    print(f"  left blank, {v}: {k}")
print("\nfilled by version (top 15):")
got = collections.Counter(r["released"] for r in rows if r["released"])
for k, v in sorted(got.items(), key=lambda kv: -kv[1])[:15]:
    print(f"  {k}: {v}")

if APPLY:
    with ledger_path.open("w", newline="") as fh:
        # The ledger is LF, not the csv module's default CRLF: writing it back with
        # the default turns every untouched row into a diff line.
        w = csv.DictWriter(fh, cols, quoting=csv.QUOTE_MINIMAL,
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {ledger_path}")
else:
    print("\nDRY RUN -- pass --apply to write.")
