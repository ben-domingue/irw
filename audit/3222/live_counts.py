"""Audit every core table with density > 1: live counts vs published metadata.

Published `density` above 1 means the row says there are more responses than
person-item cells. That is normal for repeated measures, and this asks which of
the 768 are something else: a stale n_participants/n_items, or real unkeyed
duplicate id-item pairs the metadata cannot explain.

One query per table, batched with UNION ALL, nothing exported.
"""
import os, re, sys, time, json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

META = Path("/home/ben/Dropbox/projects/irw/src/metadata")
CONFIG = Path("/home/ben/Dropbox/projects/irw/src/metadata/redivis_config.R")
OCC = {'rater','wave','timepoint','trialnum','trial','order','session','occasion',
       'period','block','subtest'}

def owner():
    m = re.search(r'IRW_OWNER\s*<-\s*"([^"]+)"', CONFIG.read_text())
    if not m: sys.exit("no IRW_OWNER")
    return m.group(1)

def sql(own, ds, t):
    ref = f"`{own}.{ds}.{t}`"
    return (f"SELECT '{t}' AS tbl, COUNT(*) AS n_rows, "
            f"COUNT(DISTINCT CAST(id AS STRING)) AS n_ids, "
            f"COUNT(DISTINCT CAST(item AS STRING)) AS n_it, "
            f"COUNT(*) - COUNT(DISTINCT CONCAT(CAST(id AS STRING),'|#|',CAST(item AS STRING))) "
            f"AS dup_pairs FROM {ref}")

def main():
    tok = Path("~/.redivis_api_token").expanduser()
    if "REDIVIS_API_TOKEN" not in os.environ and tok.exists():
        os.environ["REDIVIS_API_TOKEN"] = tok.read_text().strip()
    import redivis
    own = owner()

    m = pd.read_csv(META / "metadata.csv")
    m["density"] = pd.to_numeric(m["density"], errors="coerce")
    hi = m[m["density"] > 1].copy()
    def cols(v): return [c.strip() for c in re.split(r"[|,]", v)] if isinstance(v, str) else []
    hi["cs"] = hi["variables"].map(cols)
    hi["has_occ"] = hi["cs"].map(lambda cs: any(c in OCC or c.startswith("trial_") for c in cs))
    hi["has_date"] = hi["cs"].map(lambda cs: "date" in cs)
    todo = hi[~hi["has_occ"] & ~hi["has_date"]] if "--unexplained" in sys.argv else hi
    print(f"{len(hi)} tables above 1; querying {len(todo)}")

    batches, cur = [], []
    for _, r in todo.iterrows():
        cur.append(r)
        if len(cur) == 8: batches.append(cur); cur = []
    if cur: batches.append(cur)

    def run(s):
        for a in range(4):
            try: return redivis.query(s).to_pandas_dataframe()
            except Exception as e:
                if "429" in str(e) and a < 3: time.sleep(15); continue
                raise
    def one(b):
        try:
            return run("\nUNION ALL\n".join(sql(own, r["dataset"], r["table"]) for r in b)).to_dict("records")
        except Exception:
            out = []
            for r in b:
                try: out += run(sql(own, r["dataset"], r["table"])).to_dict("records")
                except Exception as e: print(f"  FAIL {r['table']}: {type(e).__name__}", flush=True)
            return out

    rows, t0 = [], time.time()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, res in enumerate(pool.map(one, batches), 1):
            rows += res
            print(f"  batch {i}/{len(batches)}  {int(time.time()-t0)}s  {len(rows)} tables", flush=True)
    live = pd.DataFrame(rows)
    out = todo.merge(live, left_on="table", right_on="tbl", how="left")
    out.to_csv(sys.argv[sys.argv.index("--out")+1] if "--out" in sys.argv
               else "density_audit.csv", index=False)
    print("wrote", len(out), "rows")

if __name__ == "__main__":
    main()
