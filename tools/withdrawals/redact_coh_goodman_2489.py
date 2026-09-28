"""Drop four identifying covariates from the live coh_goodman_2023 tables (irw#2489).

The four tables come from one primary-care clinic's waiting room (Center for
Outpatient Health, St. Louis, 2013-14), so being in the sample is itself health
information. They shipped the respondent's high-school name, raw and cleaned
(`cov_hs_name`, `cov_hs_name_clean`), plus `cov_country_of_origin` and
`cov_country_of_schooling`. Among the 292 respondents with a cleaned school name,
school + location + age left 237 unique and every one in a group smaller than 5,
and every filled country value was held by one person. Ben ruled 2026-09-27:
option 2, drop those four columns and keep `cov_age`.

WHY FROM THE PUBLISHED TABLES, NOT THE SCRIPT. The source (openICPSR 193990) needs
a login and sits behind a Cloudflare challenge, so data/coh_goodman_2023.py cannot
be rerun here. It is fixed for the next rebuild; this tool applies the same change
to what is live. Only columns go: every row, id, item, resp and remaining
covariate is kept byte for byte. The published CSV is filtered with the csv module
because IRW's null is the literal string "NA", which a pandas round-trip would turn
into an empty cell (see withdraw_bfi2.py). push_one then replaces each table
(delete, recreate, upload) and confirms the row count, keeping its description.

Historical versions (item_response_warehouse_2 up to the last release) still serve
the columns; that is the open question on irw#2282.

Dry-run by default; re-run with APPLY=1. Takes effect when Ben releases the draft.
"""
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("redact_coh_goodman_2489")
import redivis
from red_up.push import push_one
import ledger

OWNER = "datapages"
SHARD = "item_response_warehouse_2"
TABLES = {f"coh_goodman_2023_{s}" for s in
          ("general_survey", "health_literacy", "racial_comp", "causal_beliefs")}
DROP = ["cov_hs_name", "cov_hs_name_clean", "cov_country_of_origin",
        "cov_country_of_schooling"]
SCRATCH = Path("/tmp/claude-1000/-home-ben-Dropbox-projects-irw/"
               "4b3a1fda-837d-497c-aa62-06e6e1bc6fc0/scratchpad/2489")

apply = os.environ.get("APPLY") == "1"
cur = redivis.user(OWNER).dataset(SHARD, version="current")
names = {t.name for t in cur.list_tables(max_results=5000)}
if TABLES - names:
    sys.exit(f"ABORT: not published in {SHARD}: {sorted(TABLES - names)}")

SCRATCH.mkdir(parents=True, exist_ok=True)
prepared = {}
for name in sorted(TABLES):
    src = SCRATCH / f"{name}.orig.csv"
    out = SCRATCH / f"{name}.csv"
    cur.table(name).download(str(src), overwrite=True)
    with open(src, newline="") as fh:
        rows = list(csv.reader(fh))
    header, body = rows[0], rows[1:]
    if set(DROP) - set(header):
        sys.exit(f"ABORT: {name} lacks {sorted(set(DROP) - set(header))}")
    keep = [i for i, c in enumerate(header) if c not in DROP]
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        w.writerow([header[i] for i in keep])
        w.writerows([r[i] for i in keep] for r in body)
    # Byte-for-byte check on what stays: every kept cell of every row unchanged.
    with open(out, newline="") as fh:
        back = list(csv.reader(fh))
    assert len(back) == len(rows), f"{name}: row count changed"
    assert all(b == [r[i] for i in keep] for b, r in zip(back, rows)), f"{name}: cells changed"
    prepared[name] = (out, len(body))
    print(f"prepared {name}: {len(body):,} rows, {len(header)} -> {len(keep)} columns")

if not apply:
    print("\nDRY RUN: nothing uploaded, no draft opened. Re-run with APPLY=1.")
    sys.exit(0)

base = redivis.user(OWNER).dataset(SHARD)
base.create_next_version(if_not_exists=True)
nxt = redivis.user(OWNER).dataset(SHARD, version="next")
before = {t.name for t in nxt.list_tables(max_results=5000)}
if TABLES - before:
    sys.exit(f"ABORT: not in the {SHARD} draft: {sorted(TABLES - before)}")
for name, (path, expected) in sorted(prepared.items()):
    # Replace only a draft copy that still matches what was published, so a
    # pending change to these tables from another session is never overwritten.
    live_n = cur.table(name).get().properties["numRows"]
    draft_n = nxt.table(name).get().properties["numRows"]
    if live_n != draft_n:
        sys.exit(f"ABORT: {name} differs in the draft ({draft_n} vs {live_n} rows)")
    res = push_one(nxt, path, name, expected)
    if res.error:
        sys.exit(f"ABORT: replace failed for {name}: {res.error}")
    print(f"replaced: {name} -- {res.actual:,} rows confirmed by count(*)")
after = {t.name for t in redivis.user(OWNER).dataset(SHARD, version="next").list_tables(max_results=5000)}
assert after == before, "unexpected table-set change in the draft"

ledger.record(TABLES, dataset=SHARD, reason="personal_data", kind="partial",
              refs="#2489 #2282", rows={n: e for n, (_, e) in prepared.items()},
              note="dropped cov_hs_name, cov_hs_name_clean, cov_country_of_origin, "
                   "cov_country_of_schooling (re-identification in a clinic sample)",
              script=__file__)
print(f"\nOK: {len(TABLES)} tables replaced in the {SHARD} draft; ledger rows written.")
