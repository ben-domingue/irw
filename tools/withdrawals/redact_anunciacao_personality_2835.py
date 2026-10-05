"""Drop three identifying covariates from the 13 live anunciacao_2025_personality_* tables (irw#2835).

The tables published the respondent's exact date of birth (`cov_dob`, 18,659 distinct values on
_order), plus two free-text columns that single people out beside `cov_age` and `cov_sex`:
`cov_institution` (19,268 distinct values, 17,751 of them held by fewer than 5 respondents, e.g.
small named schools) and `cov_profession` (15,074 distinct, 13,150 held by fewer than 5). Counts
from a server-side query on _order, 2026-10-05, ~273k respondents. Ben ruled 2026-10-05: strip the
three columns in place rather than withdraw (the responses are fine); keep cov_age, cov_sex,
cov_education (11 values) and cov_segment (3).

WHY FROM THE PUBLISHED TABLES. The tables total ~28M rows and come from a Stata build
(data/anunciacao_2025_personality.do, fixed in the same commit for the next rebuild). Only the three
columns go: every row, id, item, resp and remaining covariate is kept byte for byte. The published
CSV is filtered with the csv module, streaming, because IRW's null is the literal string "NA",
which a pandas round-trip would turn into an empty cell (see withdraw_bfi2.py); streaming keeps
memory flat on 2.5M-row tables. push_one then replaces each table (delete, recreate, upload),
confirms the row count with count(*), and keeps its description.

One table at a time: download, filter, verify, upload, delete the scratch files. Resumable: a
table whose draft copy already lacks the three columns is skipped. A draft copy that differs from
the published one in row count is never overwritten (another session's pending change).

Historical versions (item_response_warehouse_2 up to the last release) still serve the columns;
that is the open question on irw#2282.

Its ledger rows are committed with this script; APPLY=1 adds them only if they are missing.
Dry run by default (checks every target's columns, uploads nothing); re-run with APPLY=1.
Takes effect when Ben releases the draft.
"""
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("redact_anunciacao_personality_2835")
import redivis
from red_up.push import push_one
from ledger import LEDGER, record

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

OWNER = "datapages"
SHARD = "item_response_warehouse_2"
PREFIX = "anunciacao_2025_personality_"
ROWS = {PREFIX + k: v for k, v in {
    "achievement": 2455605, "affiliation": 2455605, "aggression": 1364225, "autonomy": 2455605,
    "change": 1909915, "deference": 2455605, "dominance": 1909915, "exhibition": 2455605,
    "intraception": 1909915, "nurturance": 2182760, "order": 1637070, "persistence": 2182760,
    "succorance": 1909915}.items()}
TABLES = set(ROWS)
DROP = ["cov_dob", "cov_institution", "cov_profession"]
NOTE = ("dropped cov_dob, cov_institution, cov_profession (exact birth dates; free-text "
        "institution and profession unique to small groups)")
SCRATCH = Path("/home/ben/irw-stage/2835-anunciacao")

apply = os.environ.get("APPLY") == "1"


def columns(table):
    return [v.name for v in table.list_variables()]


cur = redivis.user(OWNER).dataset(SHARD, version="current")
names = {t.name for t in cur.list_tables(max_results=5000)}
if TABLES - names:
    sys.exit(f"ABORT: not published in {SHARD}: {sorted(TABLES - names)}")
for name in sorted(TABLES):
    t = cur.table(name).get()
    cols = columns(t)
    missing = set(DROP) - set(cols)
    if missing:
        sys.exit(f"ABORT: published {name} lacks {sorted(missing)}")
    n = t.properties["numRows"]
    if n != ROWS[name]:
        sys.exit(f"ABORT: published {name} has {n:,} rows, expected {ROWS[name]:,}")
    print(f"ok {name}: {n:,} rows, {len(cols)} -> {len(cols) - len(DROP)} columns")

if not apply:
    print("\nDRY RUN: nothing downloaded or uploaded, no draft opened. Re-run with APPLY=1.")
    sys.exit(0)

base = redivis.user(OWNER).dataset(SHARD)
base.create_next_version(if_not_exists=True)
nxt = redivis.user(OWNER).dataset(SHARD, version="next")
before = {t.name for t in nxt.list_tables(max_results=5000)}
if TABLES - before:
    sys.exit(f"ABORT: not in the {SHARD} draft: {sorted(TABLES - before)}")

SCRATCH.mkdir(parents=True, exist_ok=True)
for name in sorted(TABLES):
    draft = nxt.table(name).get()
    if not set(DROP) & set(columns(draft)):
        print(f"skip {name}: draft copy already stripped")
        continue
    if draft.properties["numRows"] != ROWS[name]:
        sys.exit(f"ABORT: {name} differs in the draft ({draft.properties['numRows']} rows)")
    src, out = SCRATCH / f"{name}.orig.csv", SCRATCH / f"{name}.csv"
    cur.table(name).download(str(src), overwrite=True)
    with open(src, newline="") as fi, open(out, "w", newline="") as fo:
        r, w = csv.reader(fi), csv.writer(fo, quoting=csv.QUOTE_MINIMAL)
        header = next(r)
        keep = [i for i, c in enumerate(header) if c not in DROP]
        w.writerow([header[i] for i in keep])
        n = 0
        for row in r:
            w.writerow([row[i] for i in keep])
            n += 1
    if n != ROWS[name]:
        sys.exit(f"ABORT: {name} downloaded {n:,} rows, expected {ROWS[name]:,}")
    # Byte-for-byte check on what stays: every kept cell of every row unchanged.
    with open(src, newline="") as fa, open(out, newline="") as fb:
        ra, rb = csv.reader(fa), csv.reader(fb)
        m = 0
        for a, b in zip(ra, rb):
            assert b == [a[i] for i in keep], f"{name}: cells changed at row {m}"
            m += 1
        assert next(ra, None) is None and next(rb, None) is None, f"{name}: lengths differ"
    res = push_one(nxt, out, name, n)
    if res.error:
        sys.exit(f"ABORT: replace failed for {name}: {res.error}")
    print(f"replaced: {name} -- {res.actual:,} rows confirmed by count(*)")
    src.unlink()
    out.unlink()

nxt = redivis.user(OWNER).dataset(SHARD, version="next")
after = {t.name for t in nxt.list_tables(max_results=5000)}
assert after == before, "unexpected table-set change in the draft"
left = [n for n in sorted(TABLES) if set(DROP) & set(columns(nxt.table(n).get()))]
assert not left, f"still carrying dropped columns: {left}"

with open(LEDGER, newline="") as fh:
    have = {(r["table"], r["script"]) for r in csv.DictReader(fh)}
script = "tools/withdrawals/redact_anunciacao_personality_2835.py"
todo = {t for t in TABLES if (t, script) not in have}
if todo:
    record(todo, dataset=SHARD, reason="personal_data", kind="partial", refs="#2835 #2282",
           rows={t: ROWS[t] for t in todo}, note=NOTE, script=__file__)
print(f"\nOK: {len(TABLES)} tables stripped in the {SHARD} draft.")
