"""Annual Computer Poker Competition, heads-up events 2010-2017 (#2689).

Licence: CC BY. Michael Bowling, who ran the competition at the University of
Alberta, replied to IRW's ask on 2026-10-23: "The logs are not owned by the
entrants. And the ACPC intended the logs to advance research. Consider them
released under a CC-BY license (derivative works such as match-level records
included)." That parenthesis pre-clears exactly this transformation, and it was
the only way to settle the question: computerpokercompetition.org is now a parked
page, so there is nothing left at the source to read.

**Source: the competition's own results pages, from the Wayback Machine.** There is
a 20 GB third-party repack of 620M hands on Zenodo (17136841), and this script does
not use it. A crosstable cell already IS the match-level record -- one bot against
one bot over thousands of duplicate hands -- and it ships a 95% confidence interval
that summing the logs would have had to compute. Ben ruled 2026-10-26 to take the
aggregates, on the grounds that match-level results are what the rest of the sports
tables hold anyway. The archived pages also cover 2010 and 2016, which the Zenodo
repack does not.

Files read (all via https://web.archive.org/web/<stamp>id_/..., stamps in SOURCES):

    2010  rokdownloads PDFs, heads-up limit and heads-up no-limit
    2013  downloads/competitions/2013/results/results_2p{l,n}_uncapped.pdf
    2014  results_2pl_tbr.pdf and results_2pn_uncapped.pdf
    2016  downloads/competitions/2016/results/crosstable.html
    2017  downloads/competitions/2017/xtable/output/xtable.json

**Three-player events are deliberately excluded**, and they are a third of the
archived files. A three-handed crosstable is not pairwise: its 2010 columns are
indexed by *pairs* of opponents (a two-level header, "row agent against Arnold3 and
Bender"), so a cell has three contestants and cannot be written as agent_a against
agent_b. Bending it into this schema would invent a contest that was never played.
So 3pl and 3pk are left out rather than mangled, and the table is named for the
heads-up events it holds.

**tbr, iro and uncapped are not three rankings of one competition.** Entrants could
submit a different bot per winner-determination rule, which is why rosters carry the
suffix ("feste tbr" and "feste iro" are two programs). Where a year published an
`uncapped` table it is used, because that is the union: it holds every bot from both
divisions in one crosstable, with values identical to the division tables. Where
there is no uncapped file (2014 heads-up limit) the tbr table is used and the iro
entrants are simply absent.

Some PDFs carry a second crosstable below the first, captioned "Crosstable using
additional post-AAAI data" -- a re-estimate on more hands, with tighter intervals.
This script takes the FIRST crosstable, captioned "Crosstable of all matches", since
that is the competition as it was decided; the script records each table's caption so
the choice is checkable rather than implicit.

Columns beyond the standard: year, game ("heads-up limit" or "heads-up no-limit"),
mbb_per_hand (the result from agent_a's perspective, in milli big blinds per hand)
and ci95 (the half-width of its 95% confidence interval). score_a is mbb_per_hand and
score_b its negation, so the two scores sum to zero as they do in the source.

Choices:
- `winner` is "agent_a"/"agent_b"/"draw" from the sign of mbb_per_hand. A draw means
  an exactly zero result, not a tie rule.
- No `homefield` column, and here that is a property of the competition rather than a
  null finding. The ACPC plays duplicate poker: every match is replayed with the
  hands swapped between the two seats, specifically so that card luck and position
  cancel. There is no side to have an advantage.
- No `date`. The results carry a year, not a date, and `year` is its own column.
- An agent name is kept exactly as the results page prints it, including the division
  suffix. The same entrant across years is not reconciled: "Hyperborean.tbr" in 2010
  and "Hyperborean" in 2013 are left as written, because a bot is rewritten between
  years and treating them as one competitor would be a claim this table cannot
  support.
- 2017's source is JSON of pair -> result with no interval, so ci95 is blank on those
  rows. Every other row has one.

Checks the script makes rather than assumes: each crosstable is square (as many cell
columns as agent rows); the matrix is antisymmetric to within rounding, since cell
(i,j) and (j,i) are the same match reported from two sides; and a pair is written
once, from the row player's perspective.

Counts, 2026-10-27 run: 683 matches, 91 distinct agent names.

    2010  heads-up limit      15 agents, 103 matches
    2010  heads-up no-limit    8 agents,  23
    2013  heads-up limit      16 agents, 105
    2013  heads-up no-limit   14 agents,  90
    2014  heads-up limit      14 agents,  91
    2014  heads-up no-limit   16 agents, 116
    2016  heads-up no-limit   11 agents,  54
    2017  heads-up no-limit   15 agents, 101

Every shortfall against the full round robin is a blank in the source, not a parse
gap: the 2010 no-limit table has 23 of a possible 28 because an entrant's own two
bots never met (c4tw.iro against c4tw.tbr, and the same for Hyperborean and
Tartanian4) and two cross-division pairs were not played.

**Do not read the `winner` marginal.** agent_a wins 479 of 683, and that is an
artefact of orientation, not of play: a pair is written in the order the crosstable
lists its agents, and crosstables are ordered by finishing rank, so agent_a is
usually the stronger bot. Nothing here is randomised the way a seat assignment is.

Agent names are not reconciled across years; 91 names cover fewer real entrants.

Usage: python3 acpc_poker.py <dir holding the fetched files> <output dir>
The fetcher is not part of this script -- the inputs are Wayback captures, and
re-fetching them on every run would make the table depend on archive.org's uptime.
SOURCES below records the exact capture of every file.
"""
import csv
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

#: file -> (year, game, Wayback stamp, original path)
SOURCES = {
    "y2010_2pl.pdf": (2010, "heads-up limit", "20120529193428",
                      "/index.php?option=com_rokdownloads&view=file&task=download&id=98:2010-heads-up-limit-results&Itemid=58"),
    "y2010_2pn.pdf": (2010, "heads-up no-limit", "20120529200555",
                      "/index.php?option=com_rokdownloads&view=file&task=download&id=100:2010-heads-up-no-limit-results&Itemid=58"),
    "y2013_2pl.pdf": (2013, "heads-up limit", "20131012031859",
                      "/downloads/competitions/2013/results/results_2pl_uncapped.pdf"),
    "y2013_2pn.pdf": (2013, "heads-up no-limit", "20131012032430",
                      "/downloads/competitions/2013/results/results_2pn_uncapped.pdf"),
    "y2014_2pl_tbr.pdf": (2014, "heads-up limit", "20150207020221",
                          "/downloads/competitions/2014/results/results_2pl_tbr.pdf"),
    "y2014_2pn.pdf": (2014, "heads-up no-limit", "20160510061916",
                      "/downloads/competitions/2014/results/results_2pn_uncapped.pdf"),
    "y2016.html": (2016, "heads-up no-limit", "20160308063625",
                   "/downloads/competitions/2016/results/crosstable.html"),
    "y2017.json": (2017, "heads-up no-limit", "20200205160007",
                   "/downloads/competitions/2017/xtable/output/xtable.json"),
}

COLUMNS = ["agent_a", "agent_b", "winner", "score_a", "score_b", "year", "game",
           "mbb_per_hand", "ci95"]

CELL = re.compile(r"(?P<v>[-−]?\d+(?:\.\d+)?)\s*±\s*(?P<e>\d+(?:\.\d+)?)")
#: pdftotext writes the minus sign as U+2212
NUM = lambda s: float(str(s).replace("−", "-"))
#: a label can trail the en-dash that marks the diagonal
LABEL = re.compile(r"[\s–—-]+$")


def pdf_lines(path):
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                         capture_output=True, text=True, check=True)
    return out.stdout.splitlines()


def first_crosstable(lines):
    """Rows of the first block of consecutive lines carrying >= 2 cells, + caption."""
    runs, cur = [], []
    for i, line in enumerate(lines):
        if len(CELL.findall(line)) >= 2:
            cur.append(i)
        else:
            if len(cur) >= 3:
                runs.append(cur)
            cur = []
    if len(cur) >= 3:
        runs.append(cur)
    assert runs, "no crosstable found"
    run = runs[0]
    caption = ""
    for line in lines[run[-1] + 1:]:
        if line.strip():
            caption = line.strip()
            break
    return [lines[i] for i in run], caption


def from_pdf(path):
    """{(row, col): (value, ci)} plus the agent names, read off a layout dump."""
    rows, caption = first_crosstable(pdf_lines(path))
    names, cells = [], []
    for line in rows:
        first = CELL.search(line)
        names.append(LABEL.sub("", line[:first.start()]).strip())
        cells.append([(m.group("v"), m.group("e"), (m.start() + m.end()) // 2)
                      for m in CELL.finditer(line)])
    ##Cells are placed by the horizontal position of their +/- sign, not by
    ##counting: a blank cell (two bots from one entrant never played) would
    ##otherwise shift every later cell in that row into the wrong column.
    anchors = sorted(p for row in cells for (_, _, p) in row)
    cols = []
    for a in anchors:
        if not cols or a - cols[-1][-1] > 6:
            cols.append([a])
        else:
            cols[-1].append(a)
    centres = [sum(c) / len(c) for c in cols]
    ##The average column carries a bare number, no interval, so it never
    ##matched CELL and is not among the centres. Squareness is the check that
    ##nothing else crept in.
    assert len(centres) == len(names), (path.name, len(centres), len(names))
    matrix = {}
    for i, row in enumerate(cells):
        for (v, e, pos) in row:
            j = min(range(len(centres)), key=lambda k: abs(centres[k] - pos))
            assert i != j, (path.name, i)
            matrix[(i, j)] = (NUM(v), float(e))
    return names, matrix, caption


class _Table(HTMLParser):
    """Rows of the FIRST <table> only.

    The 2016 page carries the crosstable and then several ranking tables. An
    earlier version fed every <tr> on the page into one matrix, which produced
    51 "agents" for an 11-bot competition and a row that beat itself.
    """

    def __init__(self):
        super().__init__()
        self.rows, self.cur, self.cell = [], None, ""
        self.in_cell = False
        self.depth, self.done = 0, False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
        elif tag == "tr" and self.depth == 1 and not self.done:
            self.cur = []
        elif tag == "td" and self.cur is not None:
            self.in_cell, self.cell = True, ""

    def handle_endtag(self, tag):
        if tag == "table":
            self.depth -= 1
            if self.depth == 0:
                self.done = True
        elif tag == "td" and self.cur is not None:
            self.cur.append(self.cell.strip())
            self.in_cell = False
        elif tag == "tr" and self.cur is not None:
            if self.cur:
                self.rows.append(self.cur)
            self.cur = None

    def handle_data(self, data):
        if self.in_cell:
            self.cell += data

    def handle_entityref(self, name):
        if self.in_cell:
            self.cell += "\u00b1" if name == "plusmn" else ""


def from_html(path):
    p = _Table()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    body = [r for r in p.rows if r and CELL.search(" ".join(r))]
    names = [re.sub(r"^\(\d+\)\s*", "", r[0]).strip() for r in body]
    matrix = {}
    for i, row in enumerate(body):
        ##row[0] is the label; the next len(names) cells are the agents in the
        ##same order as the labels, and the one after them is the average.
        assert len(row) >= len(names) + 1, (path.name, i, len(row))
        for j, text in enumerate(row[1:1 + len(names)]):
            m = CELL.search(text)
            if m and i != j:
                matrix[(i, j)] = (NUM(m.group("v")), float(m.group("e")))
    return names, matrix, "2016 competition crosstable"


def from_json(path):
    """{agent: {"overall": x, "<pair key>": v, ...}}.

    The value is from the perspective of the dict it sits in, NOT of the name
    that comes first in the key: RobotShark_tbr's dict gives
    "RobotShark_tbr-Slumbot" as +45.45 and Slumbot's gives the same key as
    -45.45. Keying on the pair name alone would therefore keep whichever side
    happened to be read last. So each entry is stored against its owner, and
    the antisymmetry check in main() is what confirms the reading.
    """
    raw = json.loads(path.read_text())
    names = list(raw)
    index = {n: i for i, n in enumerate(names)}
    matrix = {}
    for owner, row in raw.items():
        for key, value in row.items():
            if key == "overall":
                continue
            ##Split only where both sides are known agents and one of them is
            ##the owner: a name could itself contain the separator.
            hit = [(key[:k], key[k + 1:]) for k, ch in enumerate(key) if ch == "-"]
            hit = [(a, b) for a, b in hit if a in index and b in index
                   and owner in (a, b)]
            assert len(hit) == 1, (key, owner, hit)
            a, b = hit[0]
            other = b if owner == a else a
            matrix[(index[owner], index[other])] = (float(value), None)
    return names, matrix, "2017 competition crosstable"


def main(raw, out):
    raw, rows = Path(raw), []
    report = []
    for name, (year, game, _stamp, _path) in sorted(SOURCES.items()):
        path = raw / name
        if path.suffix == ".pdf":
            agents, matrix, caption = from_pdf(path)
        elif path.suffix == ".html":
            agents, matrix, caption = from_html(path)
        else:
            agents, matrix, caption = from_json(path)
        ##(i,j) and (j,i) are one match seen from two sides: the values must
        ##negate. Checked, not assumed -- it is the only thing standing between
        ##a column-alignment slip and a silently wrong table.
        pairs, mism = {}, 0
        for (i, j), (v, e) in matrix.items():
            ##Orient every pair the same way so a match reported only as (j,i)
            ##is still written once, flipped. Skipping i > j outright dropped
            ##47 of 2017's 105 matches, because that file states each pair once.
            key = (i, j) if i < j else (j, i)
            if i > j:
                v = -v
            back = matrix.get((j, i))
            if back is not None:
                if abs(back[0] + (v if i < j else -v)) > 0.051 + abs(v) * 1e-6:
                    mism += 1
                    continue
                if e is None:
                    e = back[1]
            pairs[key] = (v, e)
        assert mism == 0, (name, mism)
        for (i, j), (v, e) in sorted(pairs.items()):
            rows.append([agents[i], agents[j],
                         "agent_a" if v > 0 else "agent_b" if v < 0 else "draw",
                         v, -v, year, game, v, "" if e is None else e])
        report.append(f"  {name}: {len(agents)} agents, {len(pairs)} matches "
                      f"| {caption[:60]}")
    with open(Path(out) / "acpc_poker_2010_2017.csv", "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(COLUMNS)
        w.writerows(rows)
    print("\n".join(report), file=sys.stderr)
    print(f"wrote {len(rows)} matches", file=sys.stderr)
    assert rows


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
