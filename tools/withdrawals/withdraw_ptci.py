"""Withdraw the PTCI wording served by ptcichina_zhan_2024.

Ben ruled 2026-09-19 (irw#2228): the PTCI is `block`. No traceable permission from
any rights holder -- the 1999 article is APA copyright and prints all 36 items in
Appendix A with no reproduction note (and the authors DID mark permissions where they
applied: a borrowed table carries "Copyright 1998 by Guilford Press. Reprinted with
permission"), while OxCADAT -- run by two of the five co-authors -- hosts the PTCI
under "All Rights Reserved". APA's most permissive PsycTests tier names "making tests
publicly available online" among the PROHIBITED examples. Register row added in the
same PR as this tool.

SCOPED BY READING THE WORDING. Read back from the live table 2026-09-19 (irw_version
393): 231 item rows over 33 codes ptci1..ptci33, `instrument` reading "Posttraumatic
Cognitions Inventory (PTCI)", and the item text is Foa et al. 1999 Appendix A verbatim
IN ENGLISH --
  ptci11 'I have to be especially careful because you never know what can happen next.'
  ptci16 'I will never be able to feel normal emotions again.'
  ptci30 'There is something about me that made the event happen.'
Whole table is PTCI, so this is a whole-table withdrawal, not a partial.

NOTE THE LANGUAGE TRAP. The table's `language` column says Chinese and the inventory
WAS administered in Chinese, but the wording actually shipped is the original English:
neither the OSF deposit (tj8rh) nor the paywalled article publishes the Chinese
wording. So the exposure is the English PTCI, and withdrawing it costs nothing that
respondents actually read. The batch_304 extraction PTCI_Chinese_Zhan_2024 is held
under the same ruling.

AFTER THIS LANDS: ptcichina_zhan_2024 carries a public item-text note on the issues
page describing the English wording and the ptci13 renumbering. That note describes
text that will no longer exist -- itemtext_issues.qmd is hand-maintained YAML in the
datapages/irw repo and does not update itself. Diff it before the next site build.

Scope is this one named table. No corpus sweep has been run under the new register
row; nothing here shows the corpus is otherwise clean of PTCI wording.

Published table, so the withdrawal takes effect at the NEXT release; Ben publishes.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_ptci")
import redivis

TARGETS = {
    "ptcichina_zhan_2024__items",  # PTCI, English wording, 33 codes / 231 item rows
}

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
