#!/usr/bin/env python3
"""Flag availability-audit rows whose verdict is contradicted by a sibling table.

Written under issue #1751 / roadmap 7.1, after `gilbert_meta_109`/`_110`/`_111` --
three tables built by one script from one .dta -- were classified BLOCKED /
UNAVAILABLE / BLOCKED-by-inference. One sibling had already read the raw file and
answered the question the other two were marked blocked on.

Two independent checks:

  A. SIBLING CONTRADICTION. Group audited tables by the data/ script that writes
     them, then flag groups holding a BLOCKED row whose stated failure is an
     ACCESS failure while some sibling's source_checked shows the shared source
     was in fact read. Mixed classifications alone are NOT a defect -- siblings
     routinely measure different third-party instruments with different
     publication routes -- so the access/substance distinction is what carries
     the signal. Output still needs reading by eye.

  B. TARGET-CLASS DRIFT. Count Dataverse BLOCKED rows by WAF wording vs. by any
     access failure. The WAF phrasing is only one way an author described the
     same bot-challenge, so a regex keyed to it undercounts what the API route
     (itemtext/dataverse_api_route.md) can address.

Usage:  python3 itemtext/sibling_consistency_sweep.py [--out DIR]
"""
import argparse, csv, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "itemtext", "availability_audit_full.csv")
DATA = os.path.join(ROOT, "data")

# A table name only counts as "built by" a script if it appears on a line that
# writes a file -- otherwise an incidental mention pulls unrelated tables into
# the group (data/wang_2016_*.py mentions gomez_2020_mpq without building it).
WRITE = re.compile(r"write[._]csv|write\.table|to_csv|save\(|saveRDS|glue\(|\.csv|\.RData", re.I)

# The verdict blames reaching the source, not the source's contents.
ACCESS = re.compile(
    r"\bWAF\b|bot.?challenge|no fetchable content|empty content|returned no content|returned empty|"
    r"\b40[234]\b|inaccessible|not accessible|could not (be )?access|unable to (access|fetch|reach|retrieve)|"
    r"access failure|failed to (load|fetch|render)|unfetchable|JS-rendered|0-byte|login wall|captcha|"
    r"timed out|timeout|could not be retrieved|dead link|broken link", re.I)

# The row shows somebody actually opened the underlying data/source artifact.
REACHED = re.compile(
    r"data/|local repo|local dictionary|raw file|\.dta|\.sav|\.do\b|codebook|API|"
    r"processing script|source script|supplement|supplementary|S\d+ [Ff]ile", re.I)

DATAVERSE = re.compile(r"dataverse|harvard", re.I)
WAF_ONLY = re.compile(r"\bWAF\b|bot.?challenge|no fetchable content", re.I)


def load_audit():
    with open(AUDIT, newline="") as f:
        return {r["table"]: r for r in csv.DictReader(f)}


def build_script_map(audit):
    """table -> {scripts that write it}, matching whole names only."""
    names = sorted(audit, key=len, reverse=True)  # longest first: _110 before _11
    pat = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(n) for n in names) + r")(?![A-Za-z0-9_])")
    script2tbl = defaultdict(set)
    for fn in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, fn)
        if not os.path.isfile(p):
            continue
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for line in text.splitlines():
            if WRITE.search(line):
                for name in set(pat.findall(line)):
                    script2tbl[fn].add(name)
    return script2tbl


def check_siblings(audit, script2tbl):
    hits = []
    for script, tables in sorted(script2tbl.items()):
        if len(tables) < 2:
            continue
        blocked = [t for t in tables if audit[t]["classification"] == "BLOCKED"]
        others = [t for t in tables if audit[t]["classification"] != "BLOCKED"]
        if not blocked or not others:
            continue
        reached = [t for t in others if REACHED.search(audit[t]["source_checked"])]
        if not reached:
            continue
        for t in sorted(blocked):
            r = audit[t]
            if not ACCESS.search(r["reasoning"] + " " + r["source_checked"]):
                continue  # blocked on substance, not access -- no contradiction
            hits.append({
                "script": script,
                "blocked_table": t,
                "blocked_source": r["source_checked"],
                "blocked_reasoning": r["reasoning"],
                "siblings_that_reached_source": "; ".join(
                    f"{s} [{audit[s]['classification']}]" for s in sorted(reached)),
                "sibling_sources": " || ".join(sorted({audit[s]["source_checked"] for s in reached})),
            })
    return hits


def check_target_class(audit):
    blocked = [r for r in audit.values() if r["classification"] == "BLOCKED"]
    dv = [r for r in blocked if DATAVERSE.search(r["source_checked"] + r["reasoning"])]
    waf = [r for r in dv if WAF_ONLY.search(r["source_checked"] + r["reasoning"])]
    acc = [r for r in dv if ACCESS.search(r["source_checked"] + r["reasoning"])]
    return blocked, dv, waf, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="directory for the candidates CSV")
    args = ap.parse_args()

    audit = load_audit()
    script2tbl = build_script_map(audit)
    groups = {s: t for s, t in script2tbl.items() if len(t) >= 2}

    print(f"audited tables: {len(audit)};  data/ scripts writing >=2 of them: {len(groups)}")

    hits = check_siblings(audit, script2tbl)
    print(f"\n[A] BLOCKED-on-access rows with a sibling that reached the source: "
          f"{len(hits)} across {len({h['script'] for h in hits})} scripts")
    for h in hits:
        print(f"\n  * {h['blocked_table']}   ({h['script']})")
        print(f"      blocked: {h['blocked_reasoning'][:140]}")
        print(f"      sibling: {h['siblings_that_reached_source'][:180]}")

    blocked, dv, waf, acc = check_target_class(audit)
    print(f"\n[B] BLOCKED total {len(blocked)};  citing Dataverse/Harvard {len(dv)}")
    print(f"      ...matching WAF wording      {len(waf)}")
    print(f"      ...blocked on ANY access     {len(acc)}  <- what the API route addresses")
    extra = [r for r in acc if r not in waf]
    if extra:
        print(f"    {len(extra)} Dataverse rows a WAF-keyed regex misses:")
        for r in sorted(extra, key=lambda r: r["table"]):
            print(f"      {r['table']}")

    if args.out and hits:
        path = os.path.join(args.out, "sibling_retry_candidates.csv")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(hits[0]))
            w.writeheader()
            w.writerows(hits)
        print(f"\nwrote {len(hits)} rows -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
