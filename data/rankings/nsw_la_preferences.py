#!/usr/bin/env python3
##New South Wales Legislative Assembly elections, ballot-level preference data ->
##IRW rankings tables. Source: NSW Electoral Commission virtual tally room,
##https://pastvtr.elections.nsw.gov.au/<election>/LA/<district>/preferences
##("Preference Data for each ballot paper scrutinised at the election including
##informal papers"), one zip per district holding one tab-delimited text file
##(CRLF, UTF-8 BOM) with columns District, PollingPlaceName, BPNumber, Formality,
##CandidateName, PrefMarking, PrefCounted: one row per preference mark, BPNumber
##a virtual ballot id unique within the district, PrefMarking the mark as it
##appears on the paper (digits, "x", "/"), PrefCounted the Commission's
##interpretation (formal papers only). Licence: CC BY 4.0, (c) State of New South
##Wales through the NSW Electoral Commission (elections.nsw.gov.au/copyright).
##Elections: 2015-03-28 (SGE2015), 2019-03-23 (SG1901), 2023-03-25 (SG2301); 93
##single-member districts each, optional preferential instant runoff. No codebook
##beyond the field list on each preferences page.
##
##Usage:
##  python3 nsw_la_preferences.py list <raw dir> [2015|2019|2023]           # districts found on the site
##  python3 nsw_la_preferences.py build <raw dir> <out dir> --all [2023 ...] # every district of the given elections
##  python3 nsw_la_preferences.py build <raw dir> <out dir> rcv_nsw_20230325_la_ryde [...]
##
##`build` downloads each district's preferences page and zip into <raw dir> if
##absent (untrusted data; nothing in them is executed), writes one table per
##district to <out dir>, and upserts the table's row in design_tables.csv.
##
##Layout (data/rankings/README.md): one row per ballot x marked position.
##  id    the ballot (BPNumber re-keyed 1..n in file order; BPNumber is dropped)
##  task  1
##  item  candidate code c01.. (names sorted case-insensitively; never stored),
##        or (overvote) where more than one candidate carries the same mark
##  resp  the mark AS RECORDED (PrefMarking): a digit is the position; a single
##        tick or cross ("x", "X", "/") is a first preference, as the Commission
##        counts it; a numeral above the number of candidates or any other symbol
##        is not a position and gives no row (counted in the design evidence).
##        PrefCounted (the Commission's interpretation, which stops at the first
##        gap or repeat) is not used: the standard keeps marks as recorded, and
##        rank_compress() reproduces most of that interpretation.
##  cov_formality        Formal / Informal as the Commission ruled the paper
##  cov_voting_location  PollingPlaceName (a venue, or Absent / Postal / Declared Facility / ...)
##Rows with a blank CandidateName (a paper with no marks) give no row; such a
##paper still counts in n_ballots_cast. Duplicate marks (one candidate at two
##positions) are kept as recorded.
##Table names: rcv_nsw_<yyyymmdd>_la_<district slug with underscores>.
from __future__ import annotations

import csv
import io
import re
import sys
import urllib.parse
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from rank_common import code_candidates, design_counts, fetch, upsert_design, write_table

HOST = "https://pastvtr.elections.nsw.gov.au"
ELECTIONS = {
    # year: (site code, election date, results page listing the districts, preferences page pattern)
    "2015": ("SGE2015", "2015-03-28", "/SGE2015/la-home.htm", "/SGE2015/la/{slug}/preferences/index.htm"),
    "2019": ("SG1901", "2019-03-23", "/SG1901/LA/results", "/SG1901/LA/{slug}/preferences"),
    "2023": ("SG2301", "2023-03-25", "/SG2301/LA/results", "/SG2301/LA/{slug}/preferences"),
}
FIRST = {"x", "X", "/"}
LICENCE = "CC BY 4.0 (NSW Electoral Commission)"


def table_name(year: str, slug: str) -> str:
    return f"rcv_nsw_{ELECTIONS[year][1].replace('-', '')}_la_{slug.replace('-', '_')}"


def district_slugs(year: str, raw_dir: Path) -> list[str]:
    code, _, index, _ = ELECTIONS[year]
    page = fetch(HOST + index, raw_dir / f"{code}_districts.html").read_text(encoding="utf-8", errors="replace")
    pat = re.compile(rf'href="/{code}/la/([a-z0-9-]+)', re.I)
    slugs = sorted({m.group(1).lower() for m in pat.finditer(page)})
    return [s for s in slugs if s not in ("results", "state", "info", "status")]


def zip_href(year: str, slug: str, raw_dir: Path) -> str | None:
    code, _, _, pref = ELECTIONS[year]
    page = fetch(HOST + pref.format(slug=slug), raw_dir / f"{code}_{slug}_preferences.html")
    m = re.search(r'href="([^"]*\.zip)"', page.read_text(encoding="utf-8", errors="replace"), re.I)
    if not m:
        return None
    href = m.group(1)
    if href.startswith("/"):
        return HOST + urllib.parse.quote(urllib.parse.unquote(href))
    base = pref.format(slug=slug).rsplit("/", 1)[0] + "/"
    return HOST + base + urllib.parse.quote(href)


def read_marks(zpath: Path) -> list[dict]:
    with zipfile.ZipFile(zpath) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".txt")]
        if len(names) != 1:
            raise ValueError(f"{zpath.name}: expected one .txt in the zip, found {names}")
        text = z.read(names[0]).decode("utf-8-sig", errors="replace")
    return list(csv.DictReader(io.StringIO(text, newline=""), delimiter="\t"))


def convert(year: str, slug: str, marks: list[dict], source_file: str) -> tuple[list[dict], dict]:
    papers: dict[str, list[dict]] = defaultdict(list)
    for r in marks:
        papers[r["BPNumber"]].append(r)
    names = {r["CandidateName"] for r in marks if r["CandidateName"].strip()}
    codes = code_candidates(names)
    n_cand = len(codes)
    rows, dropped = [], Counter()
    overvotes = 0
    for i, (bp, rs) in enumerate(papers.items(), start=1):
        by_pos: dict[int, list[str]] = defaultdict(list)
        for r in rs:
            name, mark = r["CandidateName"].strip(), r["PrefMarking"].strip()
            if not name or not mark:
                continue
            if mark in FIRST:
                pos = 1
            elif mark.isdigit():
                pos = int(mark)
                if pos < 1 or pos > n_cand:
                    dropped["numeral outside 1..n_candidates"] += 1
                    continue
            else:
                dropped[f"symbol {mark!r}"] += 1
                continue
            by_pos[pos].append(codes[name])
        cov = {"cov_formality": rs[0]["Formality"], "cov_voting_location": rs[0]["PollingPlaceName"]}
        for pos in sorted(by_pos):
            cands = by_pos[pos]
            if len(cands) > 1:
                overvotes += 1
                rows.append({"id": i, "task": 1, "item": "(overvote)", "resp": pos, **cov})
            else:
                rows.append({"id": i, "task": 1, "item": cands[0], "resp": pos, **cov})
    counts = design_counts(rows)
    formality = Counter(rs[0]["Formality"] for rs in papers.values())
    dropped_txt = "; ".join(f"{k}: {v}" for k, v in sorted(dropped.items())) or "none"
    design = {"table": table_name(year, slug), "source_file": source_file, "collection": "pastvtr.elections.nsw.gov.au",
              "jurisdiction": f"New South Wales, district of {slug.replace('-', ' ').title()}", "date": ELECTIONS[year][1],
              "office": f"Legislative Assembly, {year} state general election", "method": "irv", "seats": 1,
              "n_positions": n_cand, "n_candidates": n_cand,
              "n_ballots_cast": len(papers), "n_ballots_eligible_est": len(papers),
              "n_ballots_with_marks": counts["n_ballots_with_marks"],
              "n_duplicate_marks": counts["n_duplicate_marks"], "n_overvotes": overvotes, "n_writeins": 0,
              "write_in_allowed": "no", "candidate_order": "fixed",
              "evidence": f"NSWEC preference data {source_file} (read 2026-10-15), one row per mark; optional preferential "
                          f"instant runoff, one member; n_positions = n_candidates (every candidate may be numbered); "
                          f"formality as ruled by the Commission: {dict(formality)}; marks not stored: {dropped_txt}; "
                          f"ballot order fixed by the Commission's draw (no rotation); counts computed by "
                          f"nsw_la_preferences.py"}
    return rows, design


def build_one(year: str, slug: str, raw_dir: Path, out_dir: Path) -> str:
    url = zip_href(year, slug, raw_dir)
    if url is None:
        return f"{table_name(year, slug)}: no preference zip on the site, skipped"
    fname = urllib.parse.unquote(url.rsplit("/", 1)[1])
    zpath = fetch(url, raw_dir / ELECTIONS[year][0] / fname)
    rows, design = convert(year, slug, read_marks(zpath), fname)
    write_table(out_dir / f"{design['table']}.csv", rows)
    upsert_design(design)
    return (f"{design['table']}: {design['n_ballots_cast']} ballots, {design['n_ballots_with_marks']} with marks, "
            f"{design['n_candidates']} candidates, {design['n_overvotes']} overvotes, {len(rows)} rows")


def main(argv: list[str]) -> int:
    if argv[:1] == ["list"] and len(argv) >= 2:
        raw_dir = Path(argv[1])
        for year in argv[2:] or sorted(ELECTIONS):
            slugs = district_slugs(year, raw_dir)
            print(f"{year}: {len(slugs)} districts: {' '.join(slugs)}")
        return 0
    if argv[:1] == ["build"] and len(argv) >= 4:
        raw_dir, out_dir = Path(argv[1]), Path(argv[2])
        out_dir.mkdir(parents=True, exist_ok=True)
        if argv[3] == "--all":
            jobs = [(y, s) for y in (argv[4:] or sorted(ELECTIONS)) for s in district_slugs(y, raw_dir)]
        else:
            jobs = []
            for t in argv[3:]:
                m = re.fullmatch(r"rcv_nsw_(\d{4})\d{4}_la_([a-z0-9_]+)", t)
                if not m:
                    print(f"{t}: not a table name this script builds", file=sys.stderr)
                    return 1
                jobs.append((m.group(1), m.group(2).replace("_", "-")))
        for year, slug in jobs:
            try:
                print(build_one(year, slug, raw_dir, out_dir), flush=True)
            except Exception as exc:  # one bad district must not stop the batch
                print(f"{table_name(year, slug)}: FAILED {exc}", file=sys.stderr, flush=True)
        return 0
    print(__doc__ or "usage: see header", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
