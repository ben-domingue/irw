"""Withdraw SWLS item text. Ben ruled 2026-09-09: be conservative.

The Satisfaction With Life Scale is published by Ed Diener under three different
statements of terms, all fetched 2026-09-09:

  labs.psychology.illinois.edu/~ediener/SWLS.html
      "The scale is copyrighted but you are free to use it without permission or
       charge by all professionals (researchers and practitioners) as long as you
       give credit to the authors."
  labs.psychology.illinois.edu/~ediener/scales.html
      "The scale is in the public domain and therefore you are free to use it
       without permission or charge..." plus "Permission is not needed to employ
       the scales... because permission is granted here."
  eddiener.com/scales
      "The use of these scales is permitted for non-commercial purposes only."

Same holder, same scale, three formulations -- one of them a non-commercial
restriction. Ben ruled that rather than resolve which governs, IRW takes the
conservative path: the restriction governs and the wording does not ship. This
supersedes the 2026-09-04 SWLS ruling ("the terms of the page you took the
wording from govern") for this instrument.

Consistency: IRW already blocks the Flourishing Scale and SPANE on the same
eddiener.com sentence, so this aligns the SWLS with its siblings rather than
creating a new position.

Whole-table withdrawals only. eammi_grahe_2018_swb is NOT here: it pools the
SWLS with swb_6 ("I have high self-esteem"), which nothing restricts, so it needs
a PARTIAL withdrawal (rows removed, table kept) -- see the ecps_sahm precedent.

Every target was checked item by item first. Three tables initially read as mixed
and were not: their "non-SWLS" items were SWLS items with wording variants my
matcher missed -- "In most ways, my life is close to my ideal" (added comma),
"I am satisfied with life" (no "my"), "In the most ways my life is close to my
ideal" (added "the"). A substring count is a lower bound, always.

All targets are published, so each withdrawal takes effect at the next release.
Dry-run by default; re-run with APPLY=1.
"""
import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_swls")
import redivis

TARGETS = {
    "irw_text": {
        "alsecypiamh_wu_2022_swls__items",
        "dudasova_2021_swls__items",
        "duboz_2021_swls__items",
        "campos_2023_swls__items",
        "extremera_2016_swls__items",
        "altahla_2024_swls__items",
    },
    "irw_text_2": {
        "medvedev_2018_sl__items",
        "lee_2024_swls__items",
        "liu_2018_swls__items",
        "kern_2021_life_satisfaction__items",
    },
}
# Must survive: mixed table, needs a partial withdrawal, never a delete.
KEEP = {"eammi_grahe_2018_swb__items"}

for shard, targets in TARGETS.items():
    cur = {t.name for t in redivis.user("datapages").dataset(shard, version="current").list_tables()}
    missing = targets - cur
    if missing:
        sys.exit(f"ABORT: not published in {shard}: {sorted(missing)}")
    print(f"{shard}: {len(cur)} published, {len(targets)} targets all present")
    if KEEP & cur:
        print(f"  keep-set present (must survive): {sorted(KEEP & cur)}")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted, no draft created. Re-run with APPLY=1.")
    sys.exit(0)

for shard, targets in TARGETS.items():
    base = redivis.user("datapages").dataset(shard)
    base.create_next_version(if_not_exists=True)
    ds = redivis.user("datapages").dataset(shard, version="next")
    before = {t.name for t in ds.list_tables()}
    keep_before = KEEP & before
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
    assert KEEP & after == keep_before, "ABORT: eammi_grahe_2018_swb went missing"
    assert len(after) == len(before) - len(targets), f"unexpected count change in {shard}"
    print(f"OK: exactly the {len(targets)} targets removed from {shard}; keep-set intact.")
