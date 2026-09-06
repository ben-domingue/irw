#!/usr/bin/env python3
"""`DOI (for paper)` hygiene: normalise the mechanical cases, classify the rest.

Issue #1690, off the back of the table-name audit (#1686). The column is meant
to hold one bare article DOI. It does not: a large minority of rows hold the
*deposit* DOI (figshare, Mendeley Data, Dataverse, OSF, Zenodo, Dryad, ICPSR),
and a long tail hold a `https://doi.org/` URL, a `data doi: ` prefix, a journal
supplement suffix, several DOIs in one cell, or free text.

Two jobs, deliberately kept apart:

  * `normalize()` -- the MECHANICAL half. Unwrapping a URL or dropping a
    `data doi: ` prefix does not change which object the cell points at, so it
    needs no judgement and no network. Called by stage_dict_row.py so new
    automated rows cannot reintroduce these forms.

  * `classify()` -- the JUDGEMENT half. It only says what a value *is*. Whether
    a deposit DOI should be replaced by the article's DOI or moved to a column
    of its own is the open schema question on #1690, and nothing here decides
    it; a data DOI is reported, never rewritten.

Run it to produce the correction list for the Data Dictionary sheet:

    python3 doi_hygiene.py                 ##live sheet
    python3 doi_hygiene.py dict.csv        ##a local snapshot
    python3 doi_hygiene.py --out fixes.csv

`--filter` is the same normalisation as a stdin/stdout filter, one value per
line, so callers in other languages do not reimplement it:

    cut -d, -f6 dict.csv | python3 doi_hygiene.py --filter

No code in this repository writes to a Google Sheet (#1708, ARCHITECTURE.md
section 3), so the output is a two-column paste for a human, not an edit.
"""
import csv
import io
import re
import sys
import urllib.request

DICT_CSV_URL = ("https://docs.google.com/spreadsheets/d/"
                "1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/export?format=csv&gid=0")

DOI_COL = "DOI (for paper)"

##Registrants that mint DOIs for *deposits*. A value with one of these prefixes
##is a data DOI, which is a different object from the paper -- and its year is a
##deposit year, which is what produced most of #1686's spurious year_mismatch
##flags. Kept in step with DATA_PREFIXES in metadata/check_dictionary_dois.R,
##minus the preprint servers, which are split out below.
DATA_PREFIXES = (
    "10.7910/",     ##Harvard Dataverse
    "10.17632/",    ##Mendeley Data
    "10.6084/",     ##figshare
    "10.5281/",     ##Zenodo
    "10.5061/",     ##Dryad
    "10.17605/",    ##OSF
    "10.5255/",     ##UK Data Service
    "10.3886/",     ##ICPSR / openICPSR
    "10.33009/",    ##ADA / Dataverse instances
    "10.34894/",    ##DataverseNL
    "10.5683/",     ##Borealis
    "10.48668/",    ##Dataverse instances
    "10.18712/",    ##DANS
    "10.4232/",     ##GESIS
    "10.17026/",    ##DANS EASY
    "10.57760/",    ##Science Data Bank
    "10.57903/",
    "10.17608/",    ##figshare institutional
    "10.23668/",
    "10.7802/",
    "10.21979/",
    "10.60507/",
    "10.25349/",
    "10.24433/",    ##Code Ocean
)

##Preprints are NOT a defect in this column. A preprint is the paper; it has
##authors and a year that mean what the column means. Separated from the data
##prefixes only because check_dictionary_dois.R lumps them together, and
##counting them as data DOIs overstates the problem by ~75 rows.
PREPRINT_PREFIXES = (
    "10.31234/",    ##PsyArXiv
    "10.31219/",    ##OSF Preprints
    "10.48550/",    ##arXiv
    "10.1101/",     ##bioRxiv / medRxiv
)

DOI_RE = re.compile(r"10\.\d{4,9}/\S+")
##Just the registrant prefix. Counting these, rather than DOI_RE matches, is what
##catches two DOIs run together with no separator ("10.1016/j.appdev.2017.03.003"
##immediately followed by "10.1080/..."), where the greedy \S+ swallows both and
##reports one.
DOI_PREFIX_RE = re.compile(r"10\.\d{4,9}/")


def normalize(value):
    """Strip the mechanical wrappers. Returns (cleaned, [rules applied]).

    Never touches which object the DOI names -- see the module docstring.
    """
    if value is None:
        return "", []
    original = str(value).strip()
    s = original
    rules = []

    ##`data doi: 10.6084/...` and `doi:10.1371/...`. The literal prefix is a
    ##note about the value, not part of it.
    stripped = re.sub(r"(?i)^\s*(?:data\s+doi|doi)\s*:\s*", "", s)
    if stripped != s:
        s, _ = stripped.strip(), rules.append("drop-doi-prefix")

    ##A resolver URL and the DOI it resolves resolve identically; the bare form
    ##is what every consumer in this repo (`norm_doi`, the tagger, Crossref
    ##lookups) expects.
    stripped = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", s)
    if stripped != s:
        s, _ = stripped.strip(), rules.append("unwrap-doi-url")

    ##`.s001` is a PLOS/Frontiers *supplementary file* under the article's DOI.
    ##It resolves to the supplement, not the article; the article is the stem.
    stripped = re.sub(r"\.s\d{3}$", "", s)
    if stripped != s:
        s, _ = stripped.strip(), rules.append("drop-supplement-suffix")

    stripped = s.rstrip(".").strip()
    if stripped != s:
        s, _ = stripped, rules.append("drop-trailing-period")

    return s, rules


def classify(value):
    """What the (normalised) cell is. Says nothing about what it should be."""
    s = (value or "").strip()
    if not s:
        return "empty"
    if not DOI_PREFIX_RE.search(s):
        return "free_text"
    if len(DOI_PREFIX_RE.findall(s)) > 1 or "\n" in s:
        return "multiple"
    if s.startswith(PREPRINT_PREFIXES):
        return "preprint_doi"
    if s.startswith(DATA_PREFIXES):
        return "data_doi"
    return "article_doi"


def load_rows(source):
    if source:
        with open(source, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    with urllib.request.urlopen(DICT_CSV_URL) as resp:
        text = resp.read().decode("utf-8")
    ##StringIO, not splitlines(): a Reference or Notes cell holding a newline is
    ##quoted in the export, and splitting on "\n" first tears the row apart --
    ##which silently glued imps2025_hf's two DOIs into one plausible-looking
    ##value and made a `multiple` row read as `article_doi`.
    return list(csv.DictReader(io.StringIO(text, newline="")))


def filter_stdin():
    """One value per line in, the normalised value per line out. Line count is
    preserved, so a caller can paste the result back as a column."""
    for line in sys.stdin.read().splitlines():
        sys.stdout.write(normalize(line)[0] + "\n")
    return 0


def main(argv):
    if "--filter" in argv:
        return filter_stdin()
    out_path = None
    if "--out" in argv:
        i = argv.index("--out")
        out_path = argv[i + 1]
        del argv[i:i + 2]
    source = argv[0] if argv else None

    rows = load_rows(source)
    if rows and DOI_COL not in rows[0]:
        sys.exit(f"no {DOI_COL!r} column in {source or 'the sheet'}")

    corrections = []
    counts = {}
    examples = {}
    for r in rows:
        raw = r.get(DOI_COL, "")
        clean, rules = normalize(raw)
        if rules:
            corrections.append({
                "table": r.get("table", ""),
                "current": raw.strip(),
                "corrected": clean,
                "rules": " ".join(rules),
                "contributor": r.get("Contributor", "").strip(),
            })
        label = classify(clean)
        counts[label] = counts.get(label, 0) + 1
        examples.setdefault(label, (r.get("table", ""), clean))

    print(f"{len(rows)} dictionary rows\n")
    print("what the column holds, after mechanical normalisation:")
    for label in ("article_doi", "data_doi", "preprint_doi", "empty",
                  "free_text", "multiple"):
        n = counts.get(label, 0)
        if not n:
            continue
        tab, ex = examples[label]
        print(f"  {label:<13} {n:>5}   e.g. {tab} -> {ex[:60] or '(blank)'}")

    print(f"\nmechanically fixable cells: {len(corrections)}")
    by_rule = {}
    for c in corrections:
        for rule in c["rules"].split():
            by_rule[rule] = by_rule.get(rule, 0) + 1
    for rule, n in sorted(by_rule.items(), key=lambda kv: -kv[1]):
        print(f"  {rule:<24} {n:>4}")

    if out_path:
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(
                fh, fieldnames=["table", "current", "corrected", "rules", "contributor"])
            w.writeheader()
            w.writerows(corrections)
        print(f"\nwrote {out_path}")
    print("\ndata_doi is REPORTED, never rewritten: whether those rows get the "
          "article's DOI\nor a column of their own is the open question on #1690.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
