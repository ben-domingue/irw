"""Did the deposits a run flagged `good` actually reach the IRW?

A `good` triage verdict is a prediction, not a shipped table: early repos
batches only shipped a `good` row if someone got to it, and the key went into
`repo_triage_seen_keys.csv` either way, so every later run skipped it. The
2026-10 cross-check of the ledger's 128 `good` keys found 69 shipped, 23
closed with a recorded reason and **36 still unworked** -- 6 of which appear
in no leads file at all (irw#3051).

Nothing here downloads anything. Each ledger key is matched, on the caller's
own key rule, against:

  1. every dictionary: `dictionary_auto*.csv` and the four Sheets exports;
  2. `data/**` processing scripts, which carry the deposit URL or DOI in
     their header -- an independent check, and the one that catches a table
     shipped under a dictionary row that records only the paper DOI;
  3. `leads/*.csv` and `human_review/*.csv`, to tell a lead nobody has
     opened from one closed for a reason.

    python check_shipped.py                      # the repos ledger's good keys
    python check_shipped.py --flag human_review  # or any other verdict
    python check_shipped.py --out leads/repos_ledger_good_keys_<date>.csv

The Sheets exports are optional: without network, pass --no-sheets. Measured
2026-10-18, it changes nothing -- of the 69 shipped keys, 64 are matched by
dictionary_auto.csv, 4 by their processing script and exactly 1 only by a
Sheet row. (26 Sheet ROWS match, but a key needs only one hit, so the row
count is not the number of decisions the Sheets make.) Run with the Sheets
when you have network anyway: the margin is one key, not zero.
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
SHEET_IDS = (  # same four the biblio stage reads; metadata/02_biblio.R
    "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s",   # core
    "1WZZYyVC2cmw8CUJM69qP0F_ZlQjQfdkCZbdsG-8mUrs",
    "12tM4vADKcUm5LGOGRwQ5_HKkdYa3mZUaKbFUqgs2U_w",   # nominal
    "1_2SR1_miAqUy0HWFQqo5vrBVrIN4V1FU6RfavBc7WdA",
)
SHEET_URL = ("https://docs.google.com/spreadsheets/d/{}/export"
             "?format=csv&gid=1337607315")
# A status in a leads file that records a decision: the row is not a lead.
CLOSED = {"rejected_content", "skipped_pii", "blocked_licence", "below_n",
          "aggregate_continuous", "already_in_irw", "done", "shipped",
          "skipped"}


def norm(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^https?://(www\.)?", "", s)
    return s.rstrip("/")


def key_forms(key: str) -> set:
    """Every string a dictionary row or script might carry for this key.

    A ledger key is a DOI, url or title. The same deposit is written as a
    versioned DOI, a collapsed one, a record URL carrying only the numeric
    id, or a Dataverse persistent id -- so match on all of them."""
    from irw_discover_updated import canonical_doi
    k = norm(key)
    out = {k, canonical_doi(k)}
    m = re.search(r"(10\.\d{4,9}/[^\s,;\"']+)", k)
    if m:
        out.add(norm(m.group(1)))
        out.add(canonical_doi(norm(m.group(1))))
    for form in list(out):
        tail = form.rsplit("/", 1)[-1]
        if len(tail) > 5:
            out.add(tail)
        m2 = re.search(r"(\d{5,})(?:\.v\d+)?$", form)   # zenodo/figshare ids
        if m2:
            out.add(m2.group(1))
    return {x for x in out if x and len(x) > 5}


def dictionary_rows(sheets=True, cache_dir=None):
    """(source, table, haystack) for every dictionary row we can read."""
    rows = []
    for p in sorted(glob.glob(os.path.join(HERE, "dictionary_auto*.csv"))):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            rows.append((os.path.basename(p), r.get("table", ""),
                         " ".join(norm(r.get(c, "")) for c in
                                  ("URL (for data)", "DOI (for data)",
                                   "DOI (for paper)", "Notes"))))
    if not sheets:
        return rows
    import urllib.request
    for sid in SHEET_IDS:
        try:
            with urllib.request.urlopen(SHEET_URL.format(sid), timeout=60) as fh:
                text = fh.read().decode("utf-8", "replace")
        except Exception as exc:
            print(f"!! could not read sheet {sid[:6]} ({exc}); the lead count "
                  f"below is overstated by whatever it holds", file=sys.stderr)
            continue
        for r in csv.DictReader(text.splitlines()):
            rows.append((f"sheet:{sid[:6]}", r.get("table", ""),
                         " ".join(norm(r.get(c, "")) for c in
                                  ("URL (for data)", "DOI (for paper)", "Notes"))))
    return rows


def script_texts():
    out = []
    for root, _, files in os.walk(os.path.join(SRC, "data")):
        for fn in files:
            if fn.endswith((".py", ".R", ".r")):
                fp = os.path.join(root, fn)
                try:
                    out.append((os.path.relpath(fp, SRC),
                                norm(open(fp, encoding="utf-8",
                                          errors="replace").read())))
                except Exception:
                    pass
    return out


OWN_HEADER = ["key", "date", "status", "evidence"]


def lead_rows(skip=()):
    """(file, status, haystack) per row of every leads / human_review file.

    This script's own output lives in `leads/`, so a second run would read
    the previous run's file and report every `lead: unseen` key as already
    tracked -- citing itself as the evidence. Skipped by header shape rather
    than by name, so a renamed or older output is skipped too."""
    out = []
    skip = {os.path.abspath(p) for p in skip if p}
    for d in ("leads", "human_review"):
        for fp in sorted(glob.glob(os.path.join(HERE, d, "*.csv"))):
            if os.path.abspath(fp) in skip:
                continue
            try:
                rows = list(csv.DictReader(open(fp, encoding="utf-8",
                                                errors="replace")))
            except Exception:
                continue
            with open(fp, encoding="utf-8", errors="replace") as fh:
                if (next(csv.reader(fh), None) or []) == OWN_HEADER:
                    continue    # one of this script's own outputs
            for r in rows:
                out.append((os.path.basename(fp),
                            (r.get("status") or r.get("refined_flag") or "").strip(),
                            norm(" ".join(v or "" for v in r.values() if v))))
    return out


def classify(key, forms, dicts, scripts, leads):
    hit = [(s, t) for s, t, hay in dicts if any(f in hay for f in forms)]
    if hit:
        return "shipped", f"dictionary {hit[0][0]}: {hit[0][1]}"
    scr = [fp for fp, txt in scripts if any(f in txt for f in forms)]
    if scr:
        return "shipped", (f"script {scr[0]} (no dictionary row carries this "
                           f"key -- worth a look)")
    seen = [(f, st) for f, st, hay in leads if any(x in hay for x in forms)]
    if not seen:
        return "lead: unseen", "in no leads or human_review file"
    f0, st0 = seen[0]
    base = st0.split(":")[0].strip().lower()
    if base in CLOSED:
        return f"closed: {st0}"[:120], f0
    if st0:
        return "lead: unworked", f"{f0} -- status {st0!r}"
    return "lead: unworked", f"{f0} -- that file records no status"


def main():
    sys.path.insert(0, HERE)
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ledger", default="repo_triage_seen_keys.csv")
    ap.add_argument("--key-field", default="key")
    ap.add_argument("--flag", default="good",
                    help="which verdict to check (default: good)")
    ap.add_argument("--refined-flag",
                    help="check a Step 2b bucket instead, e.g. recoverable_format")
    ap.add_argument("--out", help="write the per-key result here")
    ap.add_argument("--no-sheets", action="store_true",
                    help="skip the Sheets exports (offline; overstates leads)")
    a = ap.parse_args()

    path = a.ledger if os.path.isabs(a.ledger) else os.path.join(HERE, a.ledger)
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if a.refined_flag:
        rows = [r for r in rows if r.get("refined_flag") == a.refined_flag]
        what = f"refined_flag={a.refined_flag}"
    else:
        rows = [r for r in rows if r.get("flag") == a.flag]
        what = f"flag={a.flag}"
    if not rows:
        raise SystemExit(f"{a.ledger}: no rows with {what}")
    print(f"{len(rows)} key(s) in {a.ledger} with {what}", flush=True)

    out_path = (a.out if not a.out or os.path.isabs(a.out)
                else os.path.join(HERE, a.out))
    dicts = dictionary_rows(sheets=not a.no_sheets)
    scripts, leads = script_texts(), lead_rows(skip=(out_path,))
    print(f"against {len(dicts)} dictionary rows, {len(scripts)} scripts, "
          f"{len(leads)} leads/human_review rows\n", flush=True)

    out = []
    for r in rows:
        key = r[a.key_field]
        status, why = classify(key, key_forms(key), dicts, scripts, leads)
        out.append({"key": key, "date": r.get("date", ""),
                    "status": status, "evidence": why})

    counts = collections.Counter(o["status"].split(":")[0] for o in out)
    for k, n in counts.most_common():
        print(f"  {k:10} {n}")
    for o in out:
        if o["status"].startswith("lead"):
            print(f"  LEAD {o['key']:45} {o['date']}  {o['evidence'][:70]}")
    if a.out:
        p = a.out if os.path.isabs(a.out) else os.path.join(HERE, a.out)
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, ["key", "date", "status", "evidence"],
                               lineterminator="\n")
            w.writeheader()
            w.writerows(out)
        print(f"\n-> {p}")


if __name__ == "__main__":
    main()
