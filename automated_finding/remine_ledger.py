"""Re-mine a verdict out of the seen ledger: build the candidates, then the leads.

The ledger records a Step 2 verdict permanently. When the resolver or reader
that produced that verdict is later fixed, the keys behind it are not
rejections -- they are candidates nobody ever looked at. #3076 is the
concrete case: `_zenodo_files()` reads the record id out of a `/records/<id>`
landing URL, a re-mine carries only the DOI, so every zenodo row reached no
resolver at all and was retired as `no_usable_file`. 2,223 `human_assistance`
and 2,639 `no_usable_file` keys carry verdicts of that kind.

This script is the two ends of such a re-mine. The middle is unchanged:

    python remine_ledger.py candidates --source zenodo --flag human_assistance \
        --out runs/remine_zenodo_rest.csv
    python irw_batch_updated.py runs/remine_zenodo_rest.csv \
        --out runs/remine_zenodo_rest_triage.csv --ignore-seen-keys --retriage
    python remine_ledger.py leads runs/remine_zenodo_rest_triage.csv \
        --out leads/repos_ledger_remine_<date>_zenodo_rest.csv

`--ignore-seen-keys` is not optional on a re-mine: without it the run consults
the very ledger it is re-mining and skips every key. It also suppresses the
Step 2b write-back and the `human_review/` archive, which is correct here --
a re-mine must not rewrite the record it is reading (#3073).

Two things this adds over the ad-hoc version of the 2026-10-18 batches.

**`candidates --exclude-worked` drops a key the corpus already answered.**
A ledger verdict is not the only thing that went stale: a key can have been
shipped, or closed for a recorded reason, by some later batch that reached it
another way. Of the 49 leads the 2026-10-18 zenodo rate check called `todo`,
20 were already live tables and 11 carried a recorded closure, so its real
new-lead rate was 18/100 rather than 49/100 (#3077). `check_shipped.py`
already knows how to answer that question against every dictionary, every
`data/**` script and the `leads/`+`human_review/` files; this reuses it, so
the download budget goes to keys that are actually open.

**`leads` applies the 2026-09-20 filter with the NC guard.**
`"cc-by-nc".startswith("cc-by")` is true, so a naive licence test passes NC;
three CC BY-NC deposits reached the 2026-10-18 lead list that way before the
filter was tightened. `nc` and `nd` are rejected explicitly here, once, rather
than per batch script.

Every row of the triage gets a status, leads and non-leads alike, because a
batch's unworked leads are standing records (SKILL, 2026-09-20) -- that rule
is why #3077 exists at all.
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# DOI prefix -> the `source` name _resolve_data_files_any_order() dispatches on.
# Host dispatch runs first and handles most rows once #3076 follows a bare DOI
# to its landing page; `source` is the fallback, and a wrong one is what
# retired 87 datacite rows in the 2026-08-24 run.
PREFIX_SOURCE = {
    "10.5281":  "zenodo",
    "10.17632": "mendeley",
    "10.6084":  "figshare",
    "10.5061":  "dryad",
    "10.17605": "osf",
    "10.7910":  "dataverse",
    "10.5683":  "dataverse",   # Scholars Portal / Borealis
    "10.34894": "dataverse",   # DANS / SURF
    # Dataverse installations with their own prefix. These must carry
    # source="dataverse": a blank source reaches no resolver, because
    # _host_resolver does not list their hosts and dispatch then has nothing
    # to fall through to. Verified by following each DOI -- every one lands on
    # /dataset.xhtml?persistentId=, which is _dataverse_files' input.
    "10.17026": "dataverse",   # DANS SSH datastations.nl
    "10.15139": "dataverse",   # Odum / dataverse.unc.edu
    "10.11588": "dataverse",   # heiDATA, Heidelberg
    "10.7939":  "dataverse",   # University of Alberta
    "10.21950": "dataverse",
    "10.25338": "dataverse",   # UC Davis
}
# Institutional figshare portals: their article ids are served by the central
# figshare API, so a blank source is right -- dispatch falls through on the
# figshare-shaped URL. Listed only to document that the omission is deliberate:
#   10.15131 Sheffield, 10.48420 Manchester, 10.60809 Malta, 10.5522 UCL,
#   10.25403, 10.23642 USN, 10.4121 4TU, 10.17028 Loughborough, 10.25415 UJ.
# Keys that are not repo-resolver work at all: an article SI DOI belongs to the
# PLOS/PMC connectors, and re-mining it from here just re-downloads an article.
ARTICLE_PREFIXES = {"10.1371", "10.3389", "10.1016", "10.1038", "10.1080",
                    "10.1007", "10.1177", "10.3390", "10.1111", "10.1186"}

LEADS_COLS = ["status", "source", "doi", "url", "license", "n_participants",
              "n_items", "refined_flag", "data_file", "reasons"]

# The 2026-09-20 leads filter.
OK_LICENCE = ("cc0", "cc-by", "cc-by-sa", "publicdomain", "public-domain")
# Both the abbreviated and the spelled-out forms. OSF reports a licence by
# NAME -- "CC-By Attribution-NonCommercial 4.0 International",
# "CC-By Attribution-NoDerivatives 4.0" -- so a token test for {"nc","nd"}
# alone misses it while `startswith("cc-by")` happily passes it. Three OSF
# keys that the ledger had correctly flagged `license_restricted` came back
# "open" from an earlier version of this check for exactly that reason.
BAD_LICENCE = ("nc", "nd")
BAD_LICENCE_SUBSTR = ("noncommercial", "non-commercial", "noderiv",
                      "no-deriv", "nonderiv", "sharealike-noncommercial")
N_MIN, N_MAX = 100, 50_000
ITEMS_MIN, ITEMS_MAX = 8, 700
LEAD_FLAGS = {"good", "worth_retrying", "recoverable_format", "human_review",
              "wrong_file_selected"}
DROP_FLAGS = {"aggregate_continuous", "not_item_response", "conj"}


def source_of(key: str) -> str:
    m = re.search(r"(10\.\d{4,9})/", key or "")
    if m:
        return PREFIX_SOURCE.get(m.group(1), "")
    low = (key or "").lower()
    for name in ("zenodo", "figshare", "osf.io", "dryad", "dataverse",
                 "mendeley"):
        if name in low:
            return "osf" if name == "osf.io" else name
    return ""


def licence_code(lic: str) -> str:
    """Normalise a repository's licence string to a bare code.

    A Dataverse installation may report the licence as a block of HTML -- the
    heiDATA record for 10.11588/data/kpy585 answers "Licensed under a <a
    href='http://creativecommons.org/licenses/by/4.0/'>Creative Commons
    Attribution 4.0 ...". A prefix test on that is false, so a CC BY deposit
    reads as `unknown` and is skipped. Pull the code out of the deed URL when
    one is there, since that is the unambiguous part."""
    lic = (lic or "").strip().lower()
    m = re.search(r"creativecommons\.org/(?:licenses|publicdomain)/"
                  r"([a-z0-9-]+)", lic)
    if m:
        code = m.group(1)
        return "cc0" if code in ("zero", "mark") else f"cc-{code}"
    lic = lic.replace("_", "-").replace(" ", "-")
    # Zenodo's own licence id for CC0 1.0 is `cc-zero`, which fails a
    # `startswith("cc0")` test. Three CC0 deposits in the 2026-10-18 zenodo_rest
    # batch C carried it. It did no harm there because the leads file had
    # already normalised them, but a caller resolving licences straight from
    # the Zenodo API would have dropped every CC0 Zenodo deposit as unknown.
    if lic in ("cc-zero", "cc-zero-1.0") or lic.startswith("cc-zero-"):
        return "cc0"
    if lic in ("publicdomain", "public-domain-mark", "pd"):
        return "cc0"
    return lic


def is_nc(lic: str) -> bool:
    """A non-commercial licence, abbreviated or spelled out -- not ND."""
    lic = licence_code(lic)
    parts = set(re.split(r"[-/]+", lic))
    if "nd" in parts or "noderiv" in lic or "no-deriv" in lic or "nonderiv" in lic:
        return False
    return ("nc" in parts or "noncommercial" in lic or "non-commercial" in lic)


def licence_ok(lic: str) -> bool:
    """cc0 / cc-by / cc-by-sa only. NC and ND are rejected explicitly, because
    a prefix test passes them: `"cc-by-nc".startswith("cc-by")` is true."""
    lic = licence_code(lic)
    if not lic or lic == "unknown":
        return False
    parts = set(re.split(r"[-/]+", lic))
    if parts & set(BAD_LICENCE):
        return False
    if any(s in lic for s in BAD_LICENCE_SUBSTR):
        return False
    return any(lic.startswith(ok) for ok in OK_LICENCE)


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def cmd_candidates(a):
    path = a.ledger if os.path.isabs(a.ledger) else os.path.join(HERE, a.ledger)
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8"))
            if r.get("flag") == a.flag]
    if a.refined_flag:
        rows = [r for r in rows if r.get("refined_flag") == a.refined_flag]
    keys = [r["key"] for r in rows]
    print(f"{len(keys)} ledger key(s) with flag={a.flag}"
          + (f" refined_flag={a.refined_flag}" if a.refined_flag else ""))

    # Dedupe on the canonical DOI. The ledger holds a Mendeley deposit under
    # every version it was seen as -- 10.17632/p622ddkyxf, .1 and .2 are three
    # keys and one deposit -- and without this the pool hands a fork the same
    # file several times. `canonical_doi` already collapses them (it is what
    # `load_seen_keys` canonicalises with); this pool build simply never
    # called it. 9 of the 22 mendeley blank-flag leads were redundant.
    from irw_discover_updated import canonical_doi
    picked, skipped = [], collections.Counter()
    seen_canon = {}
    for k in keys:
        src = source_of(k)
        m = re.search(r"(10\.\d{4,9})/", k)
        if m and m.group(1) in ARTICLE_PREFIXES:
            skipped["article SI DOI -- the PLOS/PMC path, not this one"] += 1
            continue
        if a.include_unrecognised:
            # An institution's own figshare- or Dataverse-powered portal has
            # its own DOI prefix (10.15131 Sheffield, 10.48420 Manchester,
            # 10.4121 4TU, 10.17026 DANS, 10.15139 Odum, ...), so no prefix
            # map will ever be complete. Emit these with a blank `source` and
            # let dispatch do it: #3076 follows the bare DOI to its real
            # landing page, _host_resolver reads the host off that, and a
            # figshare-shaped article URL falls through to _figshare_files
            # even when the host is unlisted -- which is how the UJ deposit
            # the ledger had retired was recovered.
            if src:
                skipped[f"source {src} (this run wants the unrecognised ones)"] += 1
                continue
        elif a.source and src != a.source:
            skipped[f"source {src or 'unrecognised'}"] += 1
            continue
        elif not src:
            skipped["no source could be derived from the key"] += 1
            continue
        # A ledger key is a DOI *or* a landing URL -- every OSF key is the
        # latter (`https://osf.io/<guid>/`). Putting a URL in `doi` leaves
        # `url` empty, so `_resolve_to_landing` has nothing to follow,
        # `_host_resolver` sees "" and `_osf_files("")` fails its guid regex
        # and returns no files. The row then reads as "no resolvable tabular
        # file on landing page", which is the #3076 verdict all over again
        # on a deposit that is public and holds an .xlsx. Put each form in
        # the column that dispatch actually reads.
        canon = canonical_doi(k.lower())
        if canon in seen_canon:
            skipped[f"another version of the same deposit is already in the pool"] += 1
            continue
        seen_canon[canon] = k
        if k.lower().startswith(("http://", "https://")):
            picked.append({"source": src, "title": "", "url": k, "doi": ""})
        else:
            picked.append({"source": src, "title": "", "url": "", "doi": k})

    exclude = set()
    for fp in a.exclude or []:
        for r in csv.DictReader(open(fp, encoding="utf-8", errors="replace")):
            for v in r.values():
                for mm in re.finditer(r"10\.\d{4,9}/\S+", (v or "").lower()):
                    exclude.add(mm.group(0).rstrip('",;)'))
    if exclude:
        before = len(picked)
        picked = [p for p in picked if p["doi"].lower() not in exclude]
        skipped["named in --exclude"] += before - len(picked)

    if a.exclude_worked and picked:
        sys.path.insert(0, HERE)
        import check_shipped as cs
        dicts = cs.dictionary_rows(sheets=not a.no_sheets)
        scripts, leads = cs.script_texts(), cs.lead_rows()
        keep = []
        for p in picked:
            st, ev = cs.classify(p["doi"], cs.key_forms(p["doi"]),
                                 dicts, scripts, leads)
            if st == "shipped":
                skipped["already in the IRW"] += 1
            elif st.startswith("closed:"):
                skipped["closed earlier with a recorded reason"] += 1
            else:
                keep.append(p)
        picked = keep

    if a.sample and a.sample < len(picked):
        random.Random(a.seed).shuffle(picked)
        picked = picked[:a.sample]
        print(f"sampled {len(picked)} (seed {a.seed})")

    out = a.out if os.path.isabs(a.out) else os.path.join(HERE, a.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["source", "title", "url", "doi"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(picked)
    for why, n in skipped.most_common():
        print(f"  skipped {n:5}  {why}")
    print(f"\n{len(picked)} candidate(s) -> {out}")
    print("Next: python irw_batch_updated.py %s --out runs/<name>_triage.csv "
          "--ignore-seen-keys --retriage" % os.path.relpath(out, HERE))


def cmd_leads(a):
    tri = {}
    for r in csv.DictReader(open(a.triage, encoding="utf-8")):
        tri[(r.get("doi") or r.get("url") or "").lower()] = r
    ha = a.retriage
    if not ha:
        for cand in (a.triage + ".retriage_ha.csv",
                     os.path.splitext(a.triage)[0] + ".retriage_ha.csv"):
            if os.path.exists(cand):
                ha = cand
                break
    if ha and os.path.exists(ha):
        for r in csv.DictReader(open(ha, encoding="utf-8")):
            k = (r.get("doi") or r.get("url") or "").lower()
            if k in tri:
                tri[k]["refined_flag"] = r.get("refined_flag", "")
                tri[k]["refined_reason"] = r.get("refined_reason", "")
    else:
        print("!! no retriage_ha.csv found -- Step 2b did not run, so every "
              "human_assistance row is unclassified. Fix that before "
              "believing this file.", file=sys.stderr)

    out_rows, tally = [], collections.Counter()
    for r in tri.values():
        flag = (r.get("flag") or "").strip()
        refined = (r.get("refined_flag") or "").strip()
        eff = refined or flag
        lic = r.get("license", "")
        n, items = _num(r.get("n_participants")), _num(r.get("n_items"))
        if eff in DROP_FLAGS:
            status = f"skipped: {eff}"
        elif not licence_ok(lic) and is_nc(lic) and not a.allow_nc:
            # Two rules disagree and the later one is not in the filter.
            # `datastandard.md` "Before you start", ruled 2026-10-01: CC BY-NC
            # and BY-NC-SA PROCEED, because `Derived_License` records the NC
            # licence so commercial reuse can identify and exclude the table.
            # The pipeline's leads filter is cc0/cc-by/cc-by-sa only, set
            # 2026-09-20 -- nineteen days EARLIER -- and was never updated;
            # #3077 restates the narrow form. So an NC row is not a licence
            # rejection, it is a pending ruling, and it is kept visible rather
            # than buried in a `skipped` status. `--allow-nc` treats them as
            # leads once that ruling lands.
            status = (f"deferred: licence {licence_code(lic)} is non-commercial"
                      f" -- datastandard.md says proceed (2026-10-01), this"
                      f" filter says cc0/cc-by/cc-by-sa (2026-09-20); wants a"
                      f" ruling")
        elif not licence_ok(lic) and not (is_nc(lic) and a.allow_nc):
            status = f"skipped: licence {lic or 'unknown'} is not cc0/cc-by/cc-by-sa"
        elif flag not in LEAD_FLAGS and not refined:
            status = f"skipped: {flag or 'no flag'}"
        elif n is None or items is None:
            status = f"deferred: N unknown until the file is read ({eff})"
        elif not (N_MIN <= n <= N_MAX):
            status = f"skipped: N={n:.0f} outside {N_MIN}-{N_MAX}"
        elif not (ITEMS_MIN <= items <= ITEMS_MAX):
            status = f"skipped: {items:.0f} items outside {ITEMS_MIN}-{ITEMS_MAX}"
        else:
            status = "todo"
        tally[status.split(":")[0]] += 1
        out_rows.append({"status": status, "source": r.get("source", ""),
                         "doi": r.get("doi", ""), "url": r.get("url", ""),
                         "license": lic,
                         "n_participants": r.get("n_participants", ""),
                         "n_items": r.get("n_items", ""),
                         "refined_flag": refined or flag,
                         "data_file": r.get("data_file", ""),
                         "reasons": r.get("reasons", "")})
    out_rows.sort(key=lambda r: (r["status"] != "todo",
                                 -(_num(r["n_participants"]) or 0)))
    out = a.out if os.path.isabs(a.out) else os.path.join(HERE, a.out)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LEADS_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    for st, n in tally.most_common():
        print(f"  {st:10} {n}")
    print(f"\n{len(out_rows)} row(s) -> {out}")
    print("Every row carries a status; none may be left without one.")


def cmd_shipcheck(a):
    """Re-status a leads file's `todo` rows against what actually shipped.

    The leads filter answers "does this row pass the shape and licence
    tests". It does not answer "is this deposit missing from the IRW", and
    those are different questions: 31 of the 2026-10-18 rate check's 49
    `todo` rows were already live tables or already closed. A lead nobody
    checked that way is a download budget spent on an answered question, so
    this runs as its own step rather than living in a batch's head."""
    sys.path.insert(0, HERE)
    import check_shipped as cs
    dicts = cs.dictionary_rows(sheets=not a.no_sheets)
    scripts = cs.script_texts()
    for path in a.leads:
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
        if not rows:
            continue
        fields = list(rows[0].keys())
        leads = cs.lead_rows(skip=(os.path.abspath(path),))
        changed = collections.Counter()
        for r in rows:
            if (r.get("status") or "").strip() != "todo":
                continue
            st, ev = cs.classify(r["doi"] or r.get("url", ""),
                                 cs.key_forms(r["doi"] or r.get("url", "")),
                                 dicts, scripts, leads)
            if st == "shipped":
                r["status"] = f"already_in_irw: {ev}"
                changed["already in the IRW"] += 1
            elif st.startswith("closed:"):
                r["status"] = f"{st[len('closed: '):]}: closed earlier in {ev}"
                changed["closed earlier"] += 1
            else:
                changed["still a lead"] += 1
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"{os.path.basename(path):55} "
              + ", ".join(f"{n} {k}" for k, n in changed.most_common()))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("candidates", help="ledger keys -> a candidates CSV")
    c.add_argument("--ledger", default="repo_triage_seen_keys.csv")
    c.add_argument("--flag", default="human_assistance")
    c.add_argument("--refined-flag")
    c.add_argument("--source", help="keep only this source (zenodo, mendeley, "
                                    "figshare, dryad, osf, dataverse)")
    c.add_argument("--exclude", action="append", metavar="CSV",
                   help="drop any key whose DOI appears in this file "
                        "(repeatable) -- e.g. an earlier batch's leads file")
    c.add_argument("--exclude-worked", action="store_true",
                   help="drop keys check_shipped.py reports as shipped or "
                        "closed; 31 of the 2026-10-18 batch's 100 were")
    c.add_argument("--no-sheets", action="store_true",
                   help="--exclude-worked without the Sheets exports (offline)")
    c.add_argument("--include-unrecognised", action="store_true",
                   help="keep ONLY the keys no prefix maps, with a blank "
                        "source, so host dispatch resolves them -- the "
                        "institutional figshare/Dataverse portals")
    c.add_argument("--sample", type=int)
    c.add_argument("--seed", type=int, default=0)
    c.add_argument("--out", required=True)
    c.set_defaults(func=cmd_candidates)

    lp = sub.add_parser("leads", help="a triage output -> a tracked leads CSV")
    lp.add_argument("triage")
    lp.add_argument("--retriage", help="Step 2b output (default: alongside)")
    lp.add_argument("--allow-nc", action="store_true",
                    help="treat CC BY-NC / BY-NC-SA as leads, per "
                         "datastandard.md's 2026-10-01 ruling. Off by default "
                         "because the pipeline filter and #3077 both still say "
                         "cc0/cc-by/cc-by-sa; ND is never allowed either way")
    lp.add_argument("--out", required=True)
    lp.set_defaults(func=cmd_leads)

    s = sub.add_parser("shipcheck", help="re-status a leads file's todo rows "
                                         "against the corpus -- run before "
                                         "working any batch of leads")
    s.add_argument("leads", nargs="+")
    s.add_argument("--no-sheets", action="store_true")
    s.set_defaults(func=cmd_shipcheck)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
