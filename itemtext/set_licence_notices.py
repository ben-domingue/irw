#!/usr/bin/env python3
"""Write the licence notice onto item-text tables whose wording is under an open licence.

    python3 itemtext/set_licence_notices.py            # dry run: print what would change
    python3 itemtext/set_licence_notices.py --apply    # write the notices into each shard's draft

Rule 18 of the item-text licensing rules (2026-09-25): wording under CC BY-SA ships,
but every such table has to carry the licence -- the source, the licence link and
what IRW changed (CC BY-SA 4.0 s3(a)). IRW's own disclaimer otherwise says item
text "implies no license", which is wrong for these tables: users already hold a
licence from the source.

Redivis has no licence field, so the notice goes in the table's `description`.
`red_up` reads a table's description back before it replaces the table, so a
notice written here survives later re-uploads. A NEW upload of a listed table
starts with no description: run this again after uploading one.

`itemtext_licences.csv` is the list, one row per table. Adding a row is how a
new table gets its notice. The notice sits between two marker lines, so running
this again replaces it rather than stacking a second copy, and any other text in
the description is kept.

A table belongs here only when the WORDING is under the licence, not just the
deposit: the Veterans_Affairs_SSVF tables come from a CC BY-SA repository, but
their wording is from the FOIA files, which that repository marks public domain,
so they carry no notice. emobank_buechel_2017's wording is from the EACL paper,
not its CC BY-SA GitHub deposit.

Writes go to each shard's draft only (`red_up.push.open_draft`, which opens one
if none is open). Releasing the draft is Ben's.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LICENCES = HERE / "itemtext_licences.csv"
LIVE = HERE / "live_tables.csv"
BEGIN = "--- Item text licence ---"
END = "--- end licence ---"


def notice(row: dict) -> str:
    return "\n".join([
        BEGIN,
        f"The item wording in this table is licensed {row['licence']} ({row['licence_url']}).",
        f"Source: {row['attribution']}",
        f"Changes: {row['changes']} IRW's changes are released under the same licence.",
        "The source's authors did not make or endorse this table.",
        END,
    ])


def merged(old: str | None, block: str) -> str:
    old = old or ""
    if BEGIN in old and END in old:
        head, rest = old.split(BEGIN, 1)
        tail = rest.split(END, 1)[1]
        return (head + block + tail).strip()
    return (old.rstrip() + "\n\n" + block).strip() if old.strip() else block


def live_shards() -> dict[str, str]:
    lines = [l for l in LIVE.read_text().splitlines() if not l.startswith("#")]
    return {r["table"].lower(): r["shard"] for r in csv.DictReader(lines)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true", help="write to the drafts (default: dry run)")
    args = ap.parse_args()

    rows = list(csv.DictReader(LICENCES.open()))
    shards = live_shards()
    missing = [r["table"] for r in rows if r["table"].lower() not in shards]
    if missing:
        print("not live (skipped; refresh live_tables.csv if just uploaded):", ", ".join(missing))

    sys.path.insert(0, str(HERE.parent))
    from red_up.auth import authenticate
    from red_up.push import open_draft
    from red_up.targets import load_registry

    authenticate()
    owner, _ = load_registry()
    drafts: dict[str, object] = {}
    changed = 0
    for r in rows:
        shard = shards.get(r["table"].lower())
        if not shard:
            continue
        if args.apply and shard not in drafts:
            drafts[shard] = open_draft(owner, shard)
        import redivis
        ds = drafts.get(shard) or redivis.organization(owner).dataset(shard)
        by_name = {t.name.lower(): t for t in ds.list_tables()}
        table = by_name.get(f"{r['table']}__items".lower())
        if table is None:
            print(f"{r['table']}: no __items table in {shard}; skipped")
            continue
        old = table.get().properties.get("description")
        new = merged(old, notice(r))
        if new == (old or ""):
            print(f"{shard}/{table.name}: already current")
            continue
        changed += 1
        print(f"{shard}/{table.name}: {'writing' if args.apply else 'would write'} notice")
        if args.apply:
            table.update(description=new)
    print(f"{changed} table(s) {'updated in draft' if args.apply else 'to update (dry run)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
