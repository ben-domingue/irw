"""Cache (run this first; `stamp_released_versions.py` reads its JSON)

Cache {dataset: {version_tag: [table names]}} for every released version.

Needed to fill itemtext/withdrawals.csv's `released` column, which records the
version a withdrawal took effect in. Resumable: the JSON is rewritten after each
version, so a rate-limit stop loses at most one version's work.
"""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
os.environ["REDIVIS_API_TOKEN"] = irw_secrets.load_write_token("version_table_index")
import redivis

CACHE = Path(sys.argv[1])
DATASETS = sys.argv[2:]
idx = json.loads(CACHE.read_text()) if CACHE.exists() else {}

def retry(fn, what, tries=5):
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if i == tries - 1:
                raise
            w = 5 * 2 ** i
            print(f"    retry {i+1} on {what}: {type(e).__name__}; {w}s", flush=True)
            time.sleep(w)

for name in DATASETS:
    got = idx.setdefault(name, {})
    vers = retry(lambda: redivis.user("datapages").dataset(name).list_versions(),
                 f"list_versions {name}")
    tags = []
    for v in vers:
        p = v.properties
        if p.get("isReleased") is False:
            continue
        tags.append(p.get("tag") or p.get("versionTag") or str(p.get("id")))
    print(f"{name}: {len(tags)} released versions", flush=True)
    for tag in tags:
        if tag in got:
            continue
        names = retry(lambda t=tag: [x.name for x in redivis.user("datapages")
                                     .dataset(name, version=t).list_tables(max_results=2000)],
                      f"{name}@{tag}")
        got[tag] = names
        CACHE.write_text(json.dumps(idx))
        print(f"  {name}@{tag}: {len(names)} tables", flush=True)
print("done")
