"""#2029 follow-up: is the "NA" token scattered across respondents, or
concentrated in whole items / whole ids?

The DART signature (#2093): two items 100% "NA" in a table only 0.43% "NA"
overall -- a scoring lookup that failed, not people who skipped. Scattered
NA is consistent with ordinary missingness; a whole item or a whole person
being 100% NA is not something respondents do.

Table list comes from the landed sweep (irw_validate/results/), so this makes
no metadata scan. One aggregate query per table; nothing is exported.
Resumable: finished tables are appended immediately and skipped on re-run.
"""
import csv, os, sys, threading, warnings
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore")
os.environ.setdefault("REDIVIS_API_TOKEN",
                      open(os.path.expanduser("~/.redivis_api_token")).read().strip())
import redivis

SRC = "/home/ben/Dropbox/projects/irw/src/irw_validate/results/resp_string_na_2026-09-07.csv"
OUT = sys.argv[1] if len(sys.argv) > 1 else "irw_validate/results/na_concentration.csv"

COLS = ["table", "shard", "n_rows", "n_na", "pct_na",
        "n_items", "n_items_all_na", "na_in_all_na_items", "n_items_no_na",
        "n_ids", "n_ids_all_na", "na_in_all_na_ids", "n_ids_no_na",
        "pct_na_in_all_na_items", "pct_na_in_all_na_ids"]

SQL = """
WITH t AS (SELECT id, item, resp FROM `datapages.{shard}.{table}`),
pi AS (SELECT item, COUNT(*) n, COUNTIF(resp='NA') n_na FROM t GROUP BY item),
pd AS (SELECT id,   COUNT(*) n, COUNTIF(resp='NA') n_na FROM t GROUP BY id)
SELECT
 (SELECT COUNT(*) FROM t) n_rows,
 (SELECT COUNTIF(resp='NA') FROM t) n_na,
 (SELECT COUNT(*) FROM pi) n_items,
 (SELECT COUNTIF(n_na=n) FROM pi) n_items_all_na,
 (SELECT IFNULL(SUM(n_na),0) FROM pi WHERE n_na=n) na_in_all_na_items,
 (SELECT COUNTIF(n_na=0) FROM pi) n_items_no_na,
 (SELECT COUNT(*) FROM pd) n_ids,
 (SELECT COUNTIF(n_na=n) FROM pd) n_ids_all_na,
 (SELECT IFNULL(SUM(n_na),0) FROM pd WHERE n_na=n) na_in_all_na_ids,
 (SELECT COUNTIF(n_na=0) FROM pd) n_ids_no_na
"""

with open(SRC) as fh:
    targets = [(r["table"], r["shard"]) for r in csv.DictReader(fh)
               if float(r["n_resp_na_token"] or 0) > 0]

done = set()
if os.path.exists(OUT):
    with open(OUT) as fh:
        done = {r["table"] for r in csv.DictReader(fh)}
todo = [t for t in targets if t[0] not in done]
print(f"{len(targets)} tables with the token; {len(done)} already done; {len(todo)} to run",
      flush=True)

lock = threading.Lock()
new = not os.path.exists(OUT)
fh_out = open(OUT, "a", newline="")
w = csv.DictWriter(fh_out, fieldnames=COLS)
if new:
    w.writeheader(); fh_out.flush()

failures = []

def run(job):
    table, shard = job
    try:
        d = redivis.query(SQL.format(shard=shard, table=table)).to_pandas_dataframe()
    except Exception as e:
        with lock:
            failures.append((table, str(e)[:120]))
            print(f"  ! {table}: {str(e)[:120]}", flush=True)
        return
    r = {c: (int(d[c][0]) if c in d else 0) for c in
         ["n_rows", "n_na", "n_items", "n_items_all_na", "na_in_all_na_items",
          "n_items_no_na", "n_ids", "n_ids_all_na", "na_in_all_na_ids", "n_ids_no_na"]}
    r["table"], r["shard"] = table, shard
    r["pct_na"] = round(100 * r["n_na"] / r["n_rows"], 3) if r["n_rows"] else 0
    r["pct_na_in_all_na_items"] = round(100 * r["na_in_all_na_items"] / r["n_na"], 2) if r["n_na"] else 0
    r["pct_na_in_all_na_ids"] = round(100 * r["na_in_all_na_ids"] / r["n_na"], 2) if r["n_na"] else 0
    with lock:
        w.writerow(r); fh_out.flush()
        print(f"  {table}: {r['pct_na']}% NA | items all-NA {r['n_items_all_na']}/{r['n_items']} "
              f"({r['pct_na_in_all_na_items']}% of NA) | ids all-NA {r['n_ids_all_na']}/{r['n_ids']}",
              flush=True)

with ThreadPoolExecutor(max_workers=4) as ex:
    list(ex.map(run, todo))
fh_out.close()
print(f"\ndone. {len(failures)} failures.", flush=True)
for t, e in failures:
    print("  FAIL", t, e, flush=True)
