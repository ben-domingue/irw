import os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_hexaco")
import redivis

TARGETS = {"sv-maia2_randelovic_2021_hexaco60__items",
           "sv-maia2_randelovic_2021_hexaco100__items"}
KEEP    = "dasilva_2019_hexaco24__items"   # Brief HEXACO Inventory, CC BY -- must survive

ds = redivis.user("datapages").dataset("irw_text", version="next")
before = {t.name for t in ds.list_tables()}
print("draft tables before:", len(before))
print("targets present:", sorted(TARGETS & before))
print("keep present before:", KEEP in before)
missing = TARGETS - before
if missing:
    sys.exit(f"ABORT: target not in draft: {missing}")

if os.environ.get("APPLY") != "1":
    print("\nDRY RUN -- nothing deleted. Re-run with APPLY=1.")
    sys.exit(0)

for name in sorted(TARGETS):
    ds.table(name).delete()
    print("deleted:", name)

ds2 = redivis.user("datapages").dataset("irw_text", version="next")
after = {t.name for t in ds2.list_tables()}
removed = before - after
print("\ndraft tables after:", len(after))
print("removed set:", sorted(removed))
assert removed == TARGETS, f"MISMATCH: removed={removed} targets={TARGETS}"
assert KEEP in after, "dasilva_2019_hexaco24__items went missing"
assert len(after) == len(before) - 2, "unexpected count change"
print("OK: exactly the two targets removed; dasilva_2019_hexaco24__items intact.")
