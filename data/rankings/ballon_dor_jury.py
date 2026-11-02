#!/usr/bin/env python3
##Ballon d'Or jury rankings -> IRW rankings tables (source = "rank", method = "jury").
##Source: the men's Ballon d'Or is decided by a jury of one journalist per country (100 countries,
##those highest in the FIFA ranking), each ranking players from the 30-name shortlist; France Football
##(Groupe Amaury) publishes the complete per-country votes after each ceremony. The per-country tables
##are taken from the English Wikipedia article of each year ("Ballon D'Or Detailed Votes by Country",
##CC BY-SA 4.0), admitted on Ben's ruling of 2026-11-01 (#3024): the votes are facts France Football
##publishes, and Wikipedia's CC BY-SA compilation is the licensed text we read. France Football is the
##originating publisher and is named in the dictionary row ("Source via" Wikipedia).
##  2023: top 5 per juror, points 6-4-3-2-1 (92 countries in the published table; players with no points are
##        not listed, so n_candidates is the players who received points, 25 of the 30 shortlisted)
##  2024: top 10 per juror, points 15-12-10-8-7-5-4-3-2-1 (99 countries)
##  2025: top 10 per juror, same points (100 countries)
##Earlier years' articles carry only the 30-player standings, so they are not built; the 2026 article
##had no per-country table on 1 November 2026.
##
##Usage:
##  python3 ballon_dor_jury.py build <raw dir> <out dir> --all        # fetches wikitext into <raw dir>
##  python3 ballon_dor_jury.py build <raw dir> <out dir> 2024 2025
##
##Layout (data/rankings/README.md): one row per juror x ranked player.
##  id          the country's juror, re-keyed 1..n in the table's order (journalists are not named)
##  task        1
##  item        player code c01, c02, ... in case-insensitive alphabetical order of the names as the
##              table's column headers print them (surnames, e.g. "E. Martinez"); names are not stored
##  resp        the position, 1 = first, recovered from the points: the year's scale maps points to ranks
##  cov_country the juror's country as the table prints it
##A juror's points are checked against the year's scale (every juror used every place once), and each
##player's point total against the article's standings table; the build stops on any mismatch.
from __future__ import annotations

import csv
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE / "design_tables.csv"
API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "irw-rankings/1.0 (https://github.com/ben-domingue/irw; itemresponsewarehouse@stanford.edu)"}
YEARS = {2023: (6, 4, 3, 2, 1), 2024: (15, 12, 10, 8, 7, 5, 4, 3, 2, 1), 2025: (15, 12, 10, 8, 7, 5, 4, 3, 2, 1)}
CEREMONY = {2023: "2023-10-30", 2024: "2024-10-28", 2025: "2025-09-22"}


def fetch(year: int, raw_dir: Path) -> dict:
    dest = raw_dir / f"wikipedia_{year}_Ballon_dOr.json"
    if not dest.exists():
        q = urllib.parse.urlencode({"action": "parse", "page": f"{year}_Ballon_d'Or", "prop": "wikitext|revid",
                                    "format": "json", "formatversion": "2"})
        with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers=UA)) as r:
            dest.write_bytes(r.read())
    return json.loads(dest.read_text())["parse"]


def tables(wikitext: str) -> list[str]:
    return re.findall(r"\{\|.*?\n\|\}", wikitext, re.S)


def clean(cell: str) -> str:
    cell = re.sub(r"\{\{vert header\|\s*([^}]*?)\s*\}\}", r"\1", cell)
    cell = re.sub(r"\{\{flag(?:u|icon|country)?\|([^}|]+)[^}]*\}\}", r"\1", cell)
    cell = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", cell)
    cell = re.sub(r"<[^>]+>", "", cell).replace("'''", "")
    cell = re.sub(r'scope="col"\s*', "", cell)
    if "|" in cell:  # style="..." | value
        cell = cell.rsplit("|", 1)[1]
    return cell.strip()


def votes_table(wikitext: str) -> tuple[list[str], list[list[str]]]:
    tb = next(t for t in tables(wikitext) if "Detailed Votes by Country" in t)
    header, rows = None, []
    for block in re.split(r"^\|-.*$", tb, flags=re.M):
        block = block.strip()
        if not block or block.startswith("{|") or block == "|}":
            if block.startswith("{|") and "!" in block:  # header in the first block
                pass
            else:
                continue
        if block.startswith("!") or "!!" in block:
            cells = [clean(c) for c in re.split(r"!!|\n!", block.lstrip("!"))]
            header = [c for c in cells if c]
            continue
        cells = [clean(c) for c in re.split(r"\|\||\n\|", "\n" + block)[1:]]
        if header and len(cells) >= len(header):
            rows.append(cells[:len(header)])
    assert header and header[0].lower() == "country", header[:3]
    return header, rows


def standings(wikitext: str) -> list[tuple[str, int]]:
    """(player, points) rows of the article's standings table (columns Rank, Player, ..., Points; one cell per line);
    a list, because two players can share a printed surname (the 2023 Martínez pair)."""
    out = []
    for tb in tables(wikitext):
        if "Detailed Votes" in tb or "Points" not in tb or "Rank" not in tb:
            continue
        for block in re.split(r"^\|-.*$", tb, flags=re.M):
            cells = [clean(re.sub(r"^[!|]\s*", "", ln)) for ln in block.strip().split("\n") if re.match(r"^[!|]", ln) and not ln.startswith("|+") and not ln.startswith("|}")]
            cells = [re.sub(r"\{\{sortname\|([^|}]+)\|([^|}]+)[^}]*\}\}", r"\1 \2", c) for c in cells]
            nums = [c for c in cells if re.fullmatch(r"\d[\d,]*", c)]
            names = [c for c in cells[1:] if re.search(r"[A-Za-z]", c) and not re.fullmatch(r"\d.*", c)]
            if len(nums) >= 2 and names:
                out.append((re.sub(r"[{}]", "", names[0]).strip(), int(nums[-1].replace(",", ""))))
        if len(out) >= 25:
            return out
    return out


def fold(name: str) -> str:
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFKD", name) if not unicodedata.combining(ch)).casefold()


def tokens(name: str) -> set[str]:
    """The name's words, folded, without initials and junior suffixes, for matching a header's short form
    ("Vinicius Jr.", "E. Martinez", "Min-jae Kim") to the standings' long form ("Vinícius Júnior",
    "Emiliano Martínez", "Kim Min-jae")."""
    return {t for t in re.split(r"[\s.]+", fold(name)) if len(t) > 2 and t not in {"jr", "junior"}}


def build(raw_dir: Path, out_dir: Path, years: list[int]) -> int:
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    for year in years:
        scale = YEARS[year]
        parsed = fetch(year, raw_dir)
        header, rows = votes_table(parsed["wikitext"])
        players = header[1:]
        code = {p: f"c{k:02d}" for k, p in enumerate(sorted(players, key=lambda s: (s.casefold(), s)), 1)}
        out, totals = [], {p: 0 for p in players}
        for jid, row in enumerate(rows, 1):
            country = row[0]
            pts = [(int(x) if re.fullmatch(r"\d+", x) else 0) for x in row[1:]]
            used = sorted((v for v in pts if v > 0), reverse=True)
            assert tuple(used) == scale, f"{year} {country}: points {used} are not the scale {scale}"
            for p, v in zip(players, pts):
                if v > 0:
                    totals[p] += v
                    out.append({"id": jid, "task": 1, "item": code[p], "resp": scale.index(v) + 1, "cov_country": country})
        st = standings(parsed["wikitext"])
        ##Names differ between the two tables (short forms, accents, sortname templates), so the check is on the
        ##numbers: the sorted per-player totals of the votes table must equal the sorted standings points of the
        ##same number of players (players with no points are absent from the votes table).
        got = sorted(totals.values(), reverse=True)
        want = sorted((v for _, v in st), reverse=True)[:len(got)]
        mism = [] if got == want else [(g, w) for g, w in zip(got, want) if g != w]
        table = f"ballondor_{year}_jury"
        with open(out_dir / f"{table}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "task", "item", "resp", "cov_country"], lineterminator="\n")
            w.writeheader()
            w.writerows(out)
        design = {"table": table, "source_file": f"wikipedia_{year}_Ballon_dOr.json (revision {parsed.get('revid')})",
                  "collection": f"https://en.wikipedia.org/wiki/{year}_Ballon_d%27Or", "jurisdiction": "Ballon d'Or",
                  "rules_jurisdiction": "", "date": CEREMONY[year], "office": f"{year} men's Ballon d'Or jury ranking",
                  "method": "jury", "seats": "na", "n_positions": len(scale), "n_candidates": len(players),
                  "n_ballots_cast": len(rows), "n_ballots_eligible_est": len(rows), "n_ballots_with_marks": len(rows),
                  "n_duplicate_marks": 0, "n_overvotes": 0, "n_writeins": 0, "write_in_allowed": "no", "candidate_order": "unknown",
                  "evidence": (f"English Wikipedia, '{year} Ballon d'Or', table 'Ballon D'Or Detailed Votes by Country', revision {parsed.get('revid')} "
                               f"(CC BY-SA 4.0; the votes as France Football published them after the ceremony); {len(rows)} countries x {len(players)} shortlisted players, "
                               f"points {'-'.join(map(str, scale))} mapped to positions 1..{len(scale)}, every juror using every place once; "
                               f"the {len(got)} per-player point totals equal the article's standings points"
                               + (f" EXCEPT {mism[:3]}" if mism else " (all {0} match, sorted)".format(len(got)))
                               + "; seats: na, a jury ranking, not an election; write_in_allowed: no, jurors choose from the published 30-name shortlist; "
                               "candidate_order: unknown, jurors submit a list and no ballot is printed; counts computed by ballon_dor_jury.py")}
        upsert(design)
        print(f"{table}: {len(rows)} jurors, {len(players)} players, {len(out)} rows, totals {'match the standings' if not mism else 'MISMATCH ' + str(mism[:3])}")
        assert not mism, mism
    return 0


def upsert(record: dict) -> None:
    rows = []
    with open(DESIGN, newline="") as f:
        for r in csv.DictReader(f):
            if r["table"] != record["table"]:
                rows.append(r)
    rows.append(record)
    rows.sort(key=lambda r: r["table"])
    with open(DESIGN, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(record), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["build"] and len(a) >= 4:
        years = sorted(YEARS) if a[3] == "--all" else [int(x) for x in a[3:]]
        sys.exit(build(Path(a[1]), Path(a[2]), years))
    print(__doc__, file=sys.stderr)
    sys.exit(2)
