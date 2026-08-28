"""Narrow a raw candidate list to open-licensed deposits with a tabular file.

One network probe per candidate (`resolve_data_files`), no downloads. Cuts a
sweep's output down to the rows triage should actually spend time on, and
records the largest tabular file's size so `rank_leads.py` can score by data
volume.

Generalised from the per-batch copies (runs/prefilter_zenodo_2026-08-28.py and
friends). The Zenodo URL backfill is kept: Zenodo's InvenioRDM migration
dropped links["html"], and although from_zenodo() now reads the right field,
candidate CSVs written before that fix still carry an empty `url` that is
recoverable from the DOI.

    python3 prefilter_candidates.py --in runs/candidates_x.csv \
                                    --out runs/prefilter_x.csv
"""
import argparse
import concurrent.futures as cf
import csv
import random
import re
import time
from collections import Counter

from irw_batch_updated import resolve_data_files

TABULAR = re.compile(
    r"\.(csv|tsv|tab|txt|xlsx?|sav|dta|sas7bdat|rdata|rda|rds|por)$", re.I)
OPEN_LIC = re.compile(
    r"(cc0|creative\s*commons\s*zero|public\s*domain|cc[-\s]?by(?![-\s]?n)"
    r"|attribution\s*4\.0|attribution\s*3\.0|odbl|open\s*data\s*commons)",
    re.I)


def backfill_url(r):
    if r["source"] == "zenodo" and not (r.get("url") or "").strip():
        m = re.search(r"zenodo\.(\d+)", r.get("doi") or "")
        if m:
            r["url"] = f"https://zenodo.org/records/{m.group(1)}"
    return r


def probe(row):
    row = backfill_url(dict(row))
    last = ""
    for attempt in range(4):
        try:
            files, lic, _sk = resolve_data_files(row)
            lic = lic or ""
            files = files or []
            tab = [f for f in files if TABULAR.search(f[1] or "")]
            # Size is the third element as of 2026-08-28; tolerate older
            # 2-tuples rather than crashing on a stale pickle/caller.
            nbytes = max([f[2] for f in tab if len(f) > 2] or [0])
            if not tab:
                verdict = "no_tabular_file"
            elif not OPEN_LIC.search(lic):
                verdict = "license_unclear" if lic else "license_missing"
            else:
                verdict = "keep"
            return {**row, "n_files": len(files), "license": lic,
                    "bytes": nbytes,
                    "tabular": "|".join(f[1] for f in tab[:8]),
                    "verdict": verdict}
        except Exception as e:  # noqa: BLE001
            last = type(e).__name__
            time.sleep((2 ** attempt) + random.random() * 2)
    return {**row, "n_files": 0, "license": "", "bytes": 0, "tabular": "",
            "verdict": f"resolve_error:{last}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.inp)))
    print(f"{len(rows)} rows; probing with {args.workers} workers", flush=True)
    out = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(probe, rows), 1):
            out.append(r)
            if i % 100 == 0:
                k = sum(1 for x in out if x["verdict"] == "keep")
                print(f"  {i}/{len(rows)}  keep={k}", flush=True)

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    for k, v in Counter(x["verdict"] for x in out).most_common():
        print(f"{k:34s} {v}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
