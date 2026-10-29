#!/usr/bin/env python3
##Debian Project votes (Project Leader elections and General Resolutions) -> IRW
##rankings tables. Source: the Debian Project's published vote records at
##https://www.debian.org/vote/<year>/vote_<nnn> (results page) and
##https://www.debian.org/vote/<year>/vote_<nnn>_tally.txt (the tally sheet: one
##line per ballot, "V: <ranks> <hmac>"). Debian web pages are licensed MIT (Expat)
##or GPL-2+ at the reader's option (https://www.debian.org/license); older pages
##under the Open Publication License. Tally sheets exist from 2006 (2005 and
##earlier publish only the pairwise matrix). Debian uses the Condorcet /
##Schwartz sequential dropping method; a ballot ranks each option with a digit
##(1 = most preferred), may rank options EQUALLY, and leaves unranked options as
##"-". No codebook beyond the tally sheet's own header.
##
##Usage:
##  python3 debian_votes.py build <raw dir> <out dir> --all
##  python3 debian_votes.py build <raw dir> <out dir> debian_2025_dpl [...]
##
##`build` downloads each vote's results page and tally sheet into <raw dir> if
##absent (untrusted data; nothing in them is executed), writes one table per vote
##to <out dir>, and upserts each table's row in design_tables.csv beside this script.
##
##Layout (data/rankings/README.md): one row per ballot x ranked option.
##  id    the ballot, re-keyed 1..n in tally-sheet order (the HMAC is dropped)
##  task  1 throughout (one vote per table)
##  item  for a Project Leader election, the candidate's code c01.. (names sorted
##        case-insensitively, README "Candidate codes"; names are never stored);
##        for a General Resolution, the option label as printed on the results
##        page (policies, not people). The default options "None of the above" /
##        "Further Discussion" are stored in lower case as the same two strings in
##        every table ("none of the above", "further discussion").
##  resp  the rank given, 1 = best, as recorded. Debian allows equal ranks, so a
##        ballot can hold two rows with the same resp (reported in the design
##        record's evidence as n_tied_ballots; see README ruling R9 once made).
##        Unranked options ("-") have no row.
##Votes with only two options (a proposal against "Further Discussion") are skipped:
##a two-object choice is a competitions-family record, not a ranking.
##Table names: debian_<year>_dpl, debian_<year>_gr_<slug>.
from __future__ import annotations

import html
import re
import sys
from collections import Counter
from pathlib import Path

from rank_common import code_candidates, fetch, upsert_design, write_table

BASE = "https://www.debian.org/vote"
LICENCE = "MIT (Expat) / GPL-2+ (debian.org/license)"
NOTA = {"none of the above", "further discussion"}
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                       "september", "october", "november", "december"], start=1)}
MONTHS.update({m[:3]: i for m, i in list(MONTHS.items())})

# (year, vote id, table name); every vote with a tally sheet, 2006-2026 (checked 2026-10-15).
MANIFEST = [
    ("2006", "vote_001", "debian_2006_gr_gfdl"), ("2006", "vote_002", "debian_2006_dpl"),
    ("2006", "vote_003", "debian_2006_gr_assets"), ("2006", "vote_004", "debian_2006_gr_dfsg2"),
    ("2006", "vote_005", "debian_2006_gr_recall_dpl"), ("2006", "vote_006", "debian_2006_gr_reaffirm_dpl"),
    ("2006", "vote_007", "debian_2006_gr_firmware"), ("2007", "vote_001", "debian_2007_dpl"),
    ("2007", "vote_002", "debian_2007_gr_upload_rules"), ("2007", "vote_003", "debian_2007_gr_maintainers"),
    ("2007", "vote_004", "debian_2007_gr_election_length"), ("2008", "vote_001", "debian_2008_dpl"),
    ("2008", "vote_002", "debian_2008_gr_membership"), ("2008", "vote_003", "debian_2008_gr_lenny_dfsg"),
    ("2009", "vote_001", "debian_2009_dpl"), ("2010", "vote_001", "debian_2010_dpl"),
    ("2010", "vote_002", "debian_2010_gr_members"), ("2011", "vote_001", "debian_2011_dpl"),
    ("2012", "vote_001", "debian_2012_dpl"), ("2012", "vote_002", "debian_2012_gr_diversity"),
    ("2013", "vote_001", "debian_2013_dpl"), ("2014", "vote_001", "debian_2014_dpl"),
    ("2014", "vote_002", "debian_2014_gr_coc"), ("2014", "vote_003", "debian_2014_gr_init_coupling"),
    ("2014", "vote_004", "debian_2014_gr_tc_terms"), ("2015", "vote_001", "debian_2015_dpl"),
    ("2015", "vote_003", "debian_2015_gr_resolution_proc"), ("2016", "vote_001", "debian_2016_dpl"),
    ("2016", "vote_002", "debian_2016_gr_declassify"), ("2016", "vote_003", "debian_2016_gr_chair"),
    ("2016", "vote_004", "debian_2016_gr_declassify2"), ("2017", "vote_001", "debian_2017_dpl"),
    ("2018", "vote_001", "debian_2018_dpl"), ("2019", "vote_001", "debian_2019_dpl"),
    ("2019", "vote_002", "debian_2019_gr_init_systems"), ("2020", "vote_001", "debian_2020_dpl"),
    ("2021", "vote_001", "debian_2021_dpl"), ("2021", "vote_002", "debian_2021_gr_fsf_statement"),
    ("2021", "vote_003", "debian_2021_gr_resolution_proc"), ("2022", "vote_001", "debian_2022_gr_voting_secrecy"),
    ("2022", "vote_002", "debian_2022_dpl"), ("2022", "vote_003", "debian_2022_gr_nonfree_firmware"),
    ("2023", "vote_001", "debian_2023_dpl"), ("2023", "vote_002", "debian_2023_gr_cra_pld"),
    ("2024", "vote_001", "debian_2024_dpl"), ("2025", "vote_001", "debian_2025_dpl"),
    ("2026", "vote_001", "debian_2026_dpl"), ("2026", "vote_002", "debian_2026_gr_llm_usage"),
]


def page_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))), raw


def parse_options(raw: str) -> list[str]:
    """The option list the results page prints as <li>Option N "label"</li> (quotes, <q>..</q> or bare,
    depending on the year). The longest consecutive run starting at Option 1 wins; a leading
    'Choice N:' is dropped because some years print it inside the label."""
    best: list[str] = []
    items = [(int(n), re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip().strip('"').strip())
             for n, body in re.findall(r"<li>\s*Option\s*(\d+)\s(.*?)</li>", raw, re.S)]
    for start in [i for i, (n, _) in enumerate(items) if n == 1]:
        run = []
        for n, label in items[start:]:
            if n != len(run) + 1 or not label or re.fullmatch(r"[\d ]+", label):
                break
            run.append(re.sub(r"^Choice \d+:\s*", "", label))
        if len(run) > len(best):
            best = run
    if len(best) < 2:
        raise ValueError("could not read the option list from the results page")
    return best


def parse_title(raw: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else "unknown"


SEP = r"[\s,]*(?:\d\d:\d\d:\d\d UTC)?[\s,]*(?:on\s+)?"
DATE_PATTERNS = [
    re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})"),
    re.compile(r"(?P<d>\d{1,2})\s?(?:st|nd|rd|th)?" + SEP + r"(?P<mon>[A-Z][a-z]+)" + SEP + r"(?P<y>\d{4})"),
    re.compile(r"(?P<mon>[A-Z][a-z]+)\s+(?P<d>\d{1,2})\s?(?:st|nd|rd|th)?" + SEP + r"(?P<y>\d{4})"),
]


def parse_end_date(raw: str) -> tuple[str, str]:
    """(ISO date of the last day of the voting period or 'unknown', the period text as printed).
    The page's time line prints 'Voting period:' with a start and an end in several styles over
    the years (the first 'voting period' on a page is often boilerplate prose); the last date in
    the time-line entry is the end."""
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))
    for m in re.finditer(r"Voting [Pp]eriod:?", txt):
        seg = txt[m.end():m.end() + 260]
        if not re.search(r"\b(?:19|20)\d\d\b", seg[:200]):
            continue
        period = re.split(r" (?:Proposer|The voting period has|Seconds|Campaigning|Nomination|Discussion)", seg)[0].strip()[:160]
        found = []
        for pat in DATE_PATTERNS:
            for d in pat.finditer(period):
                g = d.groupdict()
                mon = int(g["m"]) if g.get("m") else MONTHS.get(g["mon"].lower()) or MONTHS.get(g["mon"].lower()[:3])
                if mon:
                    found.append((d.end(), f"{g['y']}-{mon:02d}-{int(g['d']):02d}"))
        return (max(found)[1] if found else "unknown"), period
    return "unknown", ""


def read_ballots(path: Path) -> list[str]:
    return [m.group(1) for m in re.finditer(r"^V:\s*(\S+)", path.read_text(encoding="utf-8", errors="replace"), re.M)]


def convert(year: str, vote: str, table: str, raw_dir: Path) -> tuple[list[dict], dict]:
    page = fetch(f"{BASE}/{year}/{vote}", raw_dir / f"{year}_{vote}.html")
    tally = fetch(f"{BASE}/{year}/{vote}_tally.txt", raw_dir / f"{year}_{vote}_tally.txt")
    txt, raw = page_text(page)
    title = parse_title(raw)
    options = parse_options(raw)
    ballots = read_ballots(tally)
    is_dpl = "Leader Election" in title
    if len(options) == 2:
        return [], {"table": table, "skip": f"two options ({options[0]!r} vs {options[1]!r}): a two-object choice belongs to "
                                       "the competitions family, not rankings (family decision list, Ben 2026-10-15)"}
    bad = [b for b in ballots if len(b) != len(options)]
    if bad:
        raise ValueError(f"{table}: {len(bad)} ballots whose length is not {len(options)}")
    if is_dpl:
        people = [o for o in options if o.casefold() not in NOTA]
        codes = code_candidates(people)
        labels = [codes[o] if o in codes else o.casefold() for o in options]
    else:
        labels = [o.casefold() if o.casefold() in NOTA else o for o in options]
    if len(set(labels)) != len(labels):
        raise ValueError(f"{table}: option labels are not distinct: {labels}")
    rows, tied, with_marks = [], 0, 0
    for i, b in enumerate(ballots, start=1):
        ranks = [(labels[k], int(ch)) for k, ch in enumerate(b) if ch != "-"]
        if not ranks:
            continue
        with_marks += 1
        if max(Counter(r for _, r in ranks).values()) > 1:
            tied += 1
        rows.extend({"id": i, "task": 1, "item": item, "resp": r} for item, r in ranks)
    date, period = parse_end_date(raw)
    design = {"table": table, "source_file": f"{year}/{vote}_tally.txt", "collection": "debian.org/vote",
              "jurisdiction": "Debian Project (developers' vote)", "date": date, "office": title,
              "method": "condorcet", "seats": 1 if is_dpl else "na",
              "n_positions": max(r["resp"] for r in rows),
              "n_candidates": sum(1 for o in labels if o not in NOTA),
              "n_ballots_cast": len(ballots), "n_ballots_eligible_est": len(ballots), "n_ballots_with_marks": with_marks,
              "n_duplicate_marks": 0, "n_overvotes": 0, "n_writeins": 0,
              "write_in_allowed": "no", "candidate_order": "fixed",
              "evidence": f"{BASE}/{year}/{vote} and {vote}_tally.txt (one V: line per ballot, read 2026-10-15); "
                          f"voting period as printed: '{period}'; options in ballot order as listed on the page; "
                          f"n_candidates excludes the default option ({[o for o in labels if o in NOTA][0]!r}), which is an item "
                          f"in the table; equal ranks allowed: "
                          f"n_tied_ballots={tied}; n_ballots_eligible_est equals n_ballots_cast (no precinct column); "
                          f"the number of developers, which sets the quorum, is in counting_values.csv; counts computed by "
                          f"debian_votes.py"}
    return rows, design


def build(raw_dir: Path, out_dir: Path, tables: list[str] | None) -> int:
    wanted = {t: (y, v) for y, v, t in MANIFEST}
    for t in tables or list(wanted):
        if t not in wanted:
            print(f"{t}: not in the manifest", file=sys.stderr)
            return 1
        y, v = wanted[t]
        rows, design = convert(y, v, t, raw_dir)
        if "skip" in design:
            print(f"{t}: skipped, {design['skip']}")
            continue
        write_table(out_dir / f"{t}.csv", rows)
        upsert_design(design)
        print(f"{t}: {design['n_ballots_cast']} ballots, {design['n_ballots_with_marks']} with marks, "
              f"{design['n_candidates']} options, {len(rows)} rows, date {design['date']}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) >= 4:
        raw_dir, out_dir = Path(argv[1]), Path(argv[2])
        tables = None if argv[3] == "--all" else argv[3:]
        return build(raw_dir, out_dir, tables)
    print(__doc__ or "usage: debian_votes.py build <raw dir> <out dir> --all|<table>...", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
