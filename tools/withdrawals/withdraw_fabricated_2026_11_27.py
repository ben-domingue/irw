"""Withdraw two deposits shipped by PR #3768 whose data do not look collected (Ben 2026-11-27: "let's do that").

lie_2026_* x4 (item_response_warehouse_6), Zenodo 24362742, data/lie_2026_ewallet_intention.py:
  The deposit's Google Forms export has 190 responses with timestamps from 2026-07-01 22:10:20.1 to 22:10:44.9,
  24.8 s in all, median gap 0.1 s. People did not fill these in; the rows were written by a program.

amin_2026_* x9 (item_response_warehouse_7), Zenodo 22105174, data/amin_2026_digital_marketing.py:
  The tables were built from the deposit's "Proceed Data.csv" (771 rows). It is not a recode of the deposit's own raw
  form export ("Raw Data_Instrument.xlsx", 775 eligible rows). For all 45 items, the per-item answer counts disagree
  by far more than the 4 dropped rows: e.g. IM3 raw 100/125/150/174/226 over five answers, processed 15/46/710
  over three. The raw counts are themselves suspiciously round. Many raw items also use answer scales that do not
  fit the statement (e.g. "Always..Never" for an attitude statement).

KEEP: lie_2026_emotional_value, lie_2026_environmental_care, lie_2026_environmental_knowledge,
lie_2026_green_marketing, lie_2026_green_purchase_intention. These come from a different deposit (Zenodo 22749662)
and are not withdrawn. Their presence is asserted when they live in the same shard as the targets. No item text was
uploaded for either withdrawn deposit (both held/not shipped in itemtext_provenance.csv).

Dry run by default. Set APPLY=1 to delete. Ledger rows are written only once a dataset's deletions verify.
"""
import csv, os, sys
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets

os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("withdraw_fabricated_2026_11_27")
import redivis

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger import LEDGER, record

OWNER = "datapages"  # metadata/redivis_config.R

PLAN = {
    "item_response_warehouse_6": {
        "targets": {"lie_2026_intention_to_use": 1140, "lie_2026_perceived_ease_of_use": 950,
                    "lie_2026_perceived_risk": 950, "lie_2026_perceived_usefulness": 1140},
        "note": "190 Google Forms timestamps within 24.8 s (median gap 0.1 s): generated, not collected; Zenodo 24362742",
    },
    "item_response_warehouse_7": {
        "targets": {f"amin_2026_{s}": 3855 for s in (
            "brand_awareness", "brand_trust", "content_marketing", "customer_engagement", "influencer_marketing",
            "purchase_intention", "search_engine_optimization", "social_media_advertising")} | {
            "amin_2026_email_marketing": 3848},
        "note": "processed CSV is not a recode of the deposit's raw form export (per-item marginals disagree on all "
                "45 items); Zenodo 22105174",
    },
}
KEEP = {"lie_2026_emotional_value", "lie_2026_environmental_care", "lie_2026_environmental_knowledge",
        "lie_2026_green_marketing", "lie_2026_green_purchase_intention"}

apply = os.environ.get("APPLY") == "1"


def names(dataset, version):
    return {t.name for t in redivis.organization(OWNER).dataset(dataset, version=version).list_tables(max_results=2000)}


for dataset, spec in PLAN.items():
    targets = set(spec["targets"])
    current = names(dataset, "current")
    if targets - current:
        sys.exit(f"ABORT: not in {dataset} current: {sorted(targets - current)}")
    keep_here = KEEP & current

    if not apply:
        try:
            before = names(dataset, "next")
            print(f"DRY RUN {dataset}: draft open, {len(before)} tables (current {len(current)}); "
                  f"targets in draft: {len(targets & before)}/{len(targets)}; keep here: {sorted(keep_here)}; "
                  f"draft vs current: +{len(before - current)} -{len(current - before)}")
        except Exception as exc:
            print(f"DRY RUN {dataset}: no draft open ({type(exc).__name__}); APPLY=1 would create one. "
                  f"targets {len(targets)}; keep here: {sorted(keep_here)}")
        continue

    ds = redivis.organization(OWNER).dataset(dataset)
    ds.create_next_version(if_not_exists=True)
    draft = redivis.organization(OWNER).dataset(dataset, version="next")
    before = {t.name for t in draft.list_tables(max_results=2000)}
    if targets - before:
        sys.exit(f"ABORT: not in the {dataset} draft: {sorted(targets - before)}")
    if keep_here - before:
        sys.exit(f"ABORT: keep set missing from {dataset} draft: {sorted(keep_here - before)}")
    for name in sorted(targets):
        draft.table(name).delete()
        print("deleted:", dataset, name)
    after = names(dataset, "next")
    removed = before - after
    assert removed == targets, f"MISMATCH in {dataset}: removed={sorted(removed)}"
    assert keep_here <= after, f"went missing from {dataset}: {sorted(keep_here - after)}"
    with LEDGER.open(newline="") as fh:
        logged = {r["table"] for r in csv.DictReader(fh) if r["script"].endswith(os.path.basename(__file__))}
    if targets - logged:
        record(targets - logged, dataset=dataset, reason="wrong_data", refs="#3768; Ben 2026-11-27",
               rows=spec["targets"], note=spec["note"], script=__file__)
    print(f"OK: removed exactly {len(targets)} tables from {dataset}. Draft must be RELEASED to take effect.")

if not apply:
    print("Nothing deleted. Re-run with APPLY=1.")
