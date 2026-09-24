"""Withdraw the IRI wording served by cucchi_2018_pts.

Ben ruled 2026-09-19 (irw#2228): the table is the Interpersonal Reactivity Index,
Perspective Taking subscale, and the IRI is ruled `block` (2026-09-06, irw#1955) --
the same register row that records dpt_noncog__interpersonal_reactivity as withdrawn
under it. The live copy goes the same way.

SCOPED BY READING THE WORDING, not by code prefix. Read back from the live table
2026-09-19 (irw_version 393): 35 item rows over 7 codes PTS1..PTS7, `instrument`
reading "Interpersonal Reactivity Index (IRI; Davis, 1983), Perspective Taking
subscale (7 items)", and the item text is the IRI verbatim --
  PTS1 'I sometimes find it difficult to see things from the "other guy's" point of view.'
  PTS3 'I sometimes try to understand my friends better by imagining how things look
        from their perspective.'
  PTS5 'I believe that there are two sides to every question and try to look at them both.'
  PTS7 'Before criticizing somebody, I try to imagine how I would feel if I were in
        their place.'
Whole table is IRI, so this is a whole-table withdrawal, not a partial.

WHY NO SWEEP CAUGHT IT. The register's match_item_code was `^iri`; these codes are
PTS1..PTS7. Found by @xingyi-zhang reading the deposit's .sav variable labels during
the #2268 rights pass. The register row is widened in the same PR that adds this tool
(match_item_text now carries fragments from all four IRI subscales), but NO corpus
sweep has been run under the widened pattern -- retroactive audits are paused -- so
nothing here shows the rest of the corpus is clean.

Scope is this one named table.

Published table, so the withdrawal takes effect at the NEXT release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_cucchi_iri")
import redivis

TARGETS = {
    "cucchi_2018_pts__items",  # IRI Perspective Taking, 7 codes / 35 item rows
}

# Must survive untouched: the response data table of the same name is NOT affected --
# only the item-text shard is touched here, and only this one table in it.
shards = {}
for shard in ("irw_text", "irw_text_2"):
    cur = redivis.user("datapages").dataset(shard, version="current")
    names = {t.name for t in cur.list_tables()}
    print(f"{shard}: {len(names)} published tables")
    for t in TARGETS & names:
        shards.setdefault(shard, set()).add(t)

found = {t for s in shards.values() for t in s}
if found != TARGETS:
    sys.exit(f"ABORT: not published anywhere: {sorted(TARGETS - found)}")
for s, ts in shards.items():
    print(f"  {s}: {sorted(ts)}")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

for shard, targets in shards.items():
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    print(f"\n{shard} draft tables before: {len(before)}")
    if targets - before:
        sys.exit(f"ABORT: target not in {shard} draft: {sorted(targets - before)}")
    for name in sorted(targets):
        ds.table(name).delete()
        print("deleted:", name)
    after = {t.name for t in redivis.user("datapages").dataset(shard, version="next").list_tables()}
    removed = before - after
    print(f"{shard} draft tables after: {len(after)}")
    assert removed == targets, f"MISMATCH in {shard}: removed={sorted(removed)}"
    assert len(after) == len(before) - len(targets), f"unexpected count change in {shard}"
    print(f"OK: exactly the {len(targets)} target(s) removed from {shard}.")
