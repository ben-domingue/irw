"""The published rounds: data/rankings/published_rounds/<table>.csv (#3606).

One CSV per table, in the format of the Minneapolis rounds files (#3166): the rounds a
jurisdiction published, copied as printed, that `data/rankings/recount.py` compares a recount
with. CI cannot recount: the test job is offline by design, and an edit to `counting_rules.csv`
can touch hundreds of tables (Ben, 2026-11-19, #3606). What it can check is that each file is
well formed and that its table joins a design row and a rule set, so that a recount run by hand
finds what it needs. This file does that, and nothing else.

A file is well formed when:
  * its header is `round,item,votes`;
  * it has at least one `(source)` row, whose votes cell is an http(s) URL;
  * every other item is a candidate code (`c01`), `(write-in)`, `(exhausted)`, `(threshold)`,
    `(elected:c01)`, `(lot:c01)`, `(first_marks)` or `(seat:2)`;
  * the rounds of a count (of a seat, after a `(seat:k)` row) are numbered 1..n without a gap,
    each candidate at most once per round, each tally a number that is not negative;
  * every elected candidate is a candidate of the file, and there are as many as the design row's
    `seats`; a `(lot:...)` row names a candidate of its round.
Its table joins a design row, and exactly one rule set, that `recount.py` can count: a ranked one.
The recount's own reader must also read it.

Like the join test, the one failure worth guarding against is passing because nothing was
compared: `test_the_check_bites` feeds the check files that are broken one way each, and
PUBLISHED pins how many files each rule set has, so a file that is dropped or renamed fails here.

Offline: it reads files of this repository only. Add a step for this file to
.github/workflows/tests.yml if you move it.

Run: python metadata/tests/test_rank_published_rounds.py -v
"""
import csv
import importlib.util
import io
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RANKINGS = ROOT / "data" / "rankings"
PUBLISHED = RANKINGS / "published_rounds"
DESIGN = RANKINGS / "design_tables.csv"
RULES = RANKINGS / "counting_rules.csv"
REASONS = RANKINGS / "recount_reasons.csv"

#: Published files per rule set, in the order of counting_rules.csv. A table that moves to
#: another rule set, or a file that is added or dropped, fails here although the total holds.
PUBLISHED_FILES = {
    "mpls_2009": 22, "mpls_2013": 8, "mpls_2015plus": 58, "nyc_2019plus": 127, "oakland_2006plus": 63,
    "berkeley_2004plus": 31, "sanleandro_2010plus": 18, "maine_2016": 10, "maine_2023plus": 1, "sf_2002": 7,
    "sf_2008": 15, "sf_2015": 3, "sf_2016plus": 40, "burlington_2005": 2, "burlington_2021plus": 6,
    "stlouispark_2018plus": 4, "minnetonka_2020plus": 7, "bloomington_2023plus": 2, "takoma_2019plus": 7,
    "redondo_2023plus": 5, "pierce_2007": 4, "westbrook_2021plus": 1, "boulder_2020plus": 1,
    "easthampton_2019plus": 1, "corvallis_2022plus": 2, "santafe_2008plus": 3,
    "portlandor_council_2022plus": 4, "portlandor_exec_2022plus": 2, "eastpointe_2019plus": 2,
    "eastpointe_single_2019plus": 1, "utah_2018plus": 13, "portlandme_2020": 2, "portlandme_2022plus": 3,
}

CANDIDATE = re.compile(r"c\d+")
MARKER = re.compile(r"\((?:(elected|lot):(c\d+)|(seat):(\d+))\)")
CLASSES = {"same_outcome_source_differs", "writein_pooling", "official_page_error", "rule_question", "unexplained",
           "seats_unknown"}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rules_key(row):
    return (row.get("rules_jurisdiction") or "").strip() or row["jurisdiction"]


def matching(rule_rows, row):
    """The join of test_rank_rules_join.py: exact key, valid_from <= date < valid_to."""
    key, date = rules_key(row), row["date"]
    return [r for r in rule_rows
            if r["jurisdiction"] == key and r["valid_from"] <= date and (not r["valid_to"] or date < r["valid_to"])]


def problems(text, design_row, rule_rows):
    """Everything wrong with one published-rounds file, as sentences; [] is a well-formed file whose table joins."""
    out = []
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ["round", "item", "votes"]:
        return [f"header is {reader.fieldnames}, not round,item,votes"]
    sources, elected, lots, seen = 0, [], [], {}
    seat, seats_seen = 1, 0
    for line, r in enumerate(reader, 2):
        item, votes = r["item"], r["votes"]
        try:
            rnd = int(r["round"])
        except ValueError:
            out.append(f"line {line}: round {r['round']!r} is not a whole number")
            continue
        if item == "(source)":
            if re.fullmatch(r"https?://\S+", votes):
                sources += 1
            else:
                out.append(f"line {line}: a (source) row needs an http(s) URL in votes, not {votes!r}")
        elif item == "(first_marks)":
            pass
        elif (m := MARKER.fullmatch(item)):
            if m.group(3):
                seat, seats_seen = int(m.group(4)), seats_seen + 1
            elif m.group(1) == "elected":
                elected.append(m.group(2))
            else:
                lots.append((seat, rnd, m.group(2)))
        elif CANDIDATE.fullmatch(item) or item in ("(write-in)", "(exhausted)", "(threshold)"):
            if (seat, rnd, item) in seen:
                out.append(f"line {line}: round {rnd} lists {item} twice")
            if not re.fullmatch(r"\d+(\.\d+)?", votes):
                out.append(f"line {line}: votes {votes!r} is not a number that is not negative")
            seen[seat, rnd, item] = True
        else:
            out.append(f"line {line}: item {item!r} is not a candidate code or a known (...) row")
    if not sources:
        out.append("no (source) row with a URL")
    rounds = {}
    for s, k, _ in seen:
        rounds.setdefault(s, set()).add(k)
    for s, ks in sorted(rounds.items()):
        if ks != set(range(1, max(ks) + 1)):
            out.append(f"seat {s}: rounds are {sorted(ks)}, not 1..{max(ks)}")
    if not rounds:
        out.append("no round has a tally")
    if not elected:
        out.append("no (elected:...) row")
    candidates = {i for _, _, i in seen}
    for e in elected:
        if e not in candidates:
            out.append(f"{e} is elected and is in no round")
    for s, k, c in lots:
        if (s, k, c) not in seen:
            out.append(f"(lot:{c}) in round {k} names a candidate that is not in that round")
    if design_row is None:
        out.append("the table has no design row")
        return out
    if design_row["seats"].isdigit() and len(elected) != int(design_row["seats"]):
        out.append(f"{len(elected)} elected, the design row has {design_row['seats']} seats")
    if seats_seen and seats_seen != len(rounds):
        out.append("(seat:k) rows and the seats with rounds disagree")
    hit = matching(rule_rows, design_row)
    if len(hit) != 1:
        out.append(f"the table joins {len(hit)} rule sets, not one")
    elif hit[0].get("condorcet_method", "na") != "na":
        out.append(f"rule set {hit[0]['rule_set']} is a Condorcet count, which recount.py does not count")
    elif (hit[0].get("surplus_transfer") == "seat_by_seat_restart" and design_row["seats"].isdigit()
          and int(design_row["seats"]) > 1 and seats_seen != int(design_row["seats"])):
        out.append(f"rule set {hit[0]['rule_set']} counts seat by seat, so the file needs a (seat:k) row for each of the "
                   f"{design_row['seats']} seats")
    return out


class PublishedRounds(unittest.TestCase):
    def setUp(self):
        self.design = {r["table"]: r for r in read(DESIGN)}
        self.rules = read(RULES)
        self.files = sorted(PUBLISHED.glob("*.csv"))

    def test_there_are_files(self):
        """Not a quiet zero: the folder holds the Minneapolis rounds and the FairVote ones."""
        self.assertEqual(len(self.files), sum(PUBLISHED_FILES.values()))

    def test_every_file_is_well_formed_and_joins(self):
        bad = {p.stem: problems(p.read_text(encoding="utf-8"), self.design.get(p.stem), self.rules)
               for p in self.files}
        bad = {t: pr for t, pr in bad.items() if pr}
        self.assertFalse(bad, f"{len(bad)} files: " + "; ".join(f"{t}: {pr[0]}" for t, pr in list(bad.items())[:4]))

    def test_files_per_rule_set(self):
        joined = Counter(matching(self.rules, self.design[p.stem])[0]["rule_set"] for p in self.files)
        self.assertEqual(dict(joined), PUBLISHED_FILES)
        self.assertEqual(list(PUBLISHED_FILES), [r["rule_set"] for r in self.rules if r["rule_set"] in PUBLISHED_FILES],
                         "PUBLISHED_FILES lists the rule sets in the file's order")

    def test_the_recount_reads_every_file(self):
        """recount.py reads the folder it was written for; its reader and this check must agree."""
        spec = importlib.util.spec_from_file_location("rank_recount", RANKINGS / "recount.py")
        assert spec is not None and spec.loader is not None
        recount = importlib.util.module_from_spec(spec)
        sys.modules["rank_recount"] = recount  # a dataclass looks its module up here
        spec.loader.exec_module(recount)
        for p in self.files:
            pub = recount.read_published(p)
            self.assertTrue(pub.sources and pub.elected and pub.rounds, p.name)

    def test_the_reasons_name_published_tables(self):
        """recount_reasons.csv says why a table is known to differ; each row is for a table with a file."""
        stems = {p.stem for p in self.files}
        rows = read(REASONS)
        self.assertTrue(rows)
        self.assertEqual([r["table"] for r in rows], sorted(r["table"] for r in rows))
        self.assertFalse({r["table"] for r in rows} - stems, "a reason for a table without published rounds")
        self.assertFalse({r["class"] for r in rows} - CLASSES)
        self.assertTrue(all(r["reason"].strip() for r in rows))

    def test_the_check_bites(self):
        """Files broken one way each, and one good file: the check must say something about each."""
        design = {"table": "t", "jurisdiction": "J", "rules_jurisdiction": "", "date": "2020-01-01", "seats": "1"}
        rules = [{"jurisdiction": "J", "rule_set": "r", "valid_from": "2000-01-01", "valid_to": "", "condorcet_method": "na"}]
        good = ("round,item,votes\n1,(source),https://example.org/r\n1,c01,5\n1,c02,3\n1,(write-in),1\n"
                "2,c01,6\n2,c02,3\n1,(elected:c01),\n")
        self.assertEqual(problems(good, design, rules), [])
        broken = {
            "header": good.replace("votes", "n", 1),
            "no source": good.replace("1,(source),https://example.org/r\n", ""),
            "source is not a URL": good.replace("https://example.org/r", "the city's page"),
            "a gap in the rounds": good.replace("\n2,c01,6\n2,c02,3", "\n3,c01,6\n3,c02,3"),
            "a candidate twice": good.replace("1,c02,3\n", "1,c02,3\n1,c02,3\n"),
            "not a number": good.replace("1,c02,3\n", "1,c02,three\n"),
            "negative": good.replace("1,c02,3\n", "1,c02,-3\n"),
            "unknown item": good.replace("1,(write-in),1\n", "1,a name,1\n"),
            "no winner": good.replace("1,(elected:c01),\n", ""),
            "winner not in a round": good.replace("(elected:c01)", "(elected:c07)"),
            "two winners, one seat": good + "1,(elected:c02),\n",
            "lot for nobody": good + "2,(lot:c09),\n",
        }
        for what, text in broken.items():
            self.assertTrue(problems(text, design, rules), what)
        self.assertTrue(problems(good, None, rules), "no design row")
        self.assertTrue(problems(good, {**design, "jurisdiction": "K"}, rules), "no rule set")
        self.assertTrue(problems(good, design, rules + rules), "two rule sets")
        self.assertTrue(problems(good, design, [{**rules[0], "condorcet_method": "schwartz_sequential_dropping"}]),
                        "a Condorcet rule set")
        self.assertEqual(problems(good, {**design, "seats": "unknown"}, rules), [], "seats unknown is the design row's gap")
        seat_rules = [{**rules[0], "surplus_transfer": "seat_by_seat_restart"}]
        two = {**design, "seats": "2"}
        by_seat = ("round,item,votes\n1,(source),https://example.org/r\n1,(seat:1),\n1,c01,5\n1,c02,3\n"
                   "1,(seat:2),\n1,c02,4\n1,c03,2\n1,(elected:c01),\n1,(elected:c02),\n")
        self.assertEqual(problems(by_seat, two, seat_rules), [])
        no_seat_rows = ("round,item,votes\n1,(source),https://example.org/r\n1,c01,5\n1,c02,3\n2,c02,4\n2,c03,2\n"
                        "1,(elected:c01),\n1,(elected:c02),\n")
        self.assertEqual(problems(no_seat_rows, two, rules), [], "well formed without them under another rule set")
        self.assertEqual(len(problems(no_seat_rows, two, seat_rules)), 1, "a seat-by-seat rule needs a (seat:k) row per seat")


if __name__ == "__main__":
    unittest.main()
