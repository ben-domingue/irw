"""The counting-rules join: data/rankings/design_tables.csv -> counting_rules.csv.

A table's counting rules are the row of `counting_rules.csv` whose `jurisdiction`
is the table's `rules_jurisdiction`, or its own `jurisdiction` where that cell is
empty, and whose date window holds the table's `date` (Ben, 2026-10-29, #3024;
the window convention is 2026-10-22, #3165). The key is matched exactly. New
South Wales is why the column exists: 279 tables under 98 district keys, because
the Electoral Commission deposits one file per district, against counting rules
written once for the chamber.

Nothing in the pipeline reads `counting_rules.csv` yet, so nothing else would
notice if the join stopped working. The two ways it breaks silently are a key
that matches no rule set (a table whose rules cannot be found) and two rows that
both match (a table with two answers, from overlapping date windows or a rule set
entered twice). Both are cheap to check and neither is visible in a diff.

A table matching NO rule set is normal and is not checked here: some rows are
jurisdictions whose rules nobody has written down, and that is the
file's own stated condition ("Other jurisdictions get rows when their rules are
written down").

The failure mode worth guarding against is the one every cross-file check has:
passing because it compared nothing. `test_both_files_are_whole` and
`test_the_resolver_matches_keys_exactly` are there for that -- the second pins
the behaviour the ruling turned on, so a reader who reimplements the join as a
prefix match fails here rather than in a count.

Offline. Add a step for this file to .github/workflows/tests.yml if you move it.

Run: python metadata/tests/test_rank_rules_join.py -v
"""
import csv
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "data" / "rankings" / "design_tables.csv"
RULES = ROOT / "data" / "rankings" / "counting_rules.csv"

#: Rule sets written before the tables they govern were ingested, so their
#: `jurisdiction` matches no table's key yet. Empty today: every rule set in the
#: file was written after its tables. Name one here rather than dropping
#: test_no_rule_set_is_unreachable, so the exception stays visible.
RULES_AHEAD_OF_DATA = ()

#: Tables joined, per rule set, in the order of counting_rules.csv. A date or key edit
#: that moves a table from one rule set to another fails here although the total holds.
JOINED = {
    "mpls_2009": 22, "mpls_2013": 8, "mpls_2015plus": 58, "ak_2020plus": 115,
    "debian_2003": 18, "debian_2015": 8, "debian_2022plus": 7, "nsw_la_1979plus": 279,
    "nyc_2019plus": 127, "oakland_2006plus": 73, "berkeley_2004plus": 36, "sanleandro_2010plus": 21,
    "maine_2016": 10, "maine_2023plus": 1,
    "sf_2002": 15, "sf_2008": 17, "sf_2015": 3, "sf_2016plus": 47,
    "burlington_2005": 2, "burlington_2021plus": 6,
    "stlouispark_2018plus": 4, "minnetonka_2020plus": 7, "bloomington_2023plus": 2,
    "takoma_2019plus": 7, "redondo_2023plus": 5, "pierce_2007": 4, "westbrook_2021plus": 1,
    "boulder_2020plus": 1, "easthampton_2019plus": 1, "corvallis_2022plus": 2,
    "lascruces_2019plus": 3, "santafe_2008plus": 3,
    "portlandor_council_2022plus": 4, "portlandor_exec_2022plus": 2,
    "eastpointe_2019plus": 2, "eastpointe_single_2019plus": 1,
    "utah_2018plus": 13, "portlandme_2020": 4, "portlandme_2022plus": 3,
}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def rules_key(row):
    """The key this table's rules are under: the override, else its own jurisdiction."""
    return (row.get("rules_jurisdiction") or "").strip() or row["jurisdiction"]


def matching(rule_rows, row):
    """Every rule set that claims this table. More than one is a defect."""
    key, date = rules_key(row), row["date"]
    return [r for r in rule_rows
            if r["jurisdiction"] == key
            and r["valid_from"] <= date
            and (not r["valid_to"] or date < r["valid_to"])]


class RulesJoin(unittest.TestCase):
    def setUp(self):
        self.design_cols, self.design = read(DESIGN)
        self.rule_cols, self.rules = read(RULES)

    def test_both_files_are_whole(self):
        """Neither side may be empty or missing a column the join reads."""
        for col in ("table", "jurisdiction", "rules_jurisdiction", "date"):
            self.assertIn(col, self.design_cols)
        for col in ("jurisdiction", "rule_set", "valid_from", "valid_to"):
            self.assertIn(col, self.rule_cols)
        self.assertGreater(len(self.design), 500)
        self.assertGreater(len(self.rules), 5)

    def test_the_resolver_matches_keys_exactly(self):
        """The ruling: an exact key, never a prefix of one.

        `New South Wales` prefixes the Legislative Council's district keys too,
        and that chamber counts by STV under other clauses, so a prefix match
        would hand those tables the Assembly's rules.
        """
        own = {"jurisdiction": "Minneapolis", "rules_jurisdiction": ""}
        keyed = {"jurisdiction": "New South Wales, district of Albury",
                 "rules_jurisdiction": "New South Wales (Legislative Assembly)"}
        self.assertEqual(rules_key(own), "Minneapolis")
        self.assertEqual(rules_key(keyed), "New South Wales (Legislative Assembly)")
        self.assertEqual(rules_key({"jurisdiction": "Alaska", "rules_jurisdiction": "  "}), "Alaska")
        statewide = [{"jurisdiction": "New South Wales", "valid_from": "2017-01-01", "valid_to": ""}]
        self.assertEqual(matching(statewide, dict(keyed, date="2023-03-25")), [])

    def test_every_table_joins_at_most_one_rule_set(self):
        """Two matching rows mean two answers: overlapping windows, or a repeat."""
        twice = [(r["table"], [m["rule_set"] for m in matching(self.rules, r)])
                 for r in self.design if len(matching(self.rules, r)) > 1]
        self.assertFalse(twice, f"{len(twice)} tables match more than one rule set: {twice[:4]}")

    def test_the_join_reaches_the_tables_it_should(self):
        """A count, so a key that stops matching is a failure and not a quiet zero, and a
        count per rule set, JOINED, so that a table moving between rule sets fails too.

        The jurisdictions whose rules are written down, with the sums of JOINED by jurisdiction: Minneapolis (88),
        Alaska (115: 63 of 2022 and 52 of 2024), the Debian Project (33) and New South Wales (279), whose
        tables are also counted on the key below. From the FairVote pool: New York City (127), Oakland (73), Berkeley (36), San Leandro (21), Maine (11), San Francisco (82), Burlington (8), St. Louis Park (4), Minnetonka (7), Bloomington (2), Takoma Park (7), Redondo Beach (5), Pierce County (4), Westbrook (1), Boulder (1), Easthampton (1), Corvallis (2), Las Cruces (3), Santa Fe (3), Portland, Oregon (6), Eastpointe (3), the Utah pilot cities (13), Portland, Maine (7).
        """
        joined = [m[0]["rule_set"] for m in (matching(self.rules, r) for r in self.design) if m]
        self.assertEqual(len(joined), 942)
        self.assertEqual(sum(JOINED.values()), 942)
        self.assertEqual(dict(Counter(joined)), JOINED)
        self.assertEqual(list(JOINED), [r["rule_set"] for r in self.rules],
                         "JOINED names every rule set once, in the file's order")
        keyed = [r for r in self.design if (r["rules_jurisdiction"] or "").strip()]
        self.assertEqual(len(keyed), 301)
        self.assertEqual({rules_key(r) for r in keyed}, {"New South Wales (Legislative Assembly)", "Eastpointe (one seat)", "Eastpointe (two seats)", "PortlandOR (Council)", "PortlandOR (Mayor and Auditor)", "Utah (municipal pilot)"})

    def test_an_override_is_never_redundant(self):
        """A key that duplicates an exact match on the table's own jurisdiction
        would give two readings of the same row depending on which the reader
        used. Where `rules_jurisdiction` is set, its own `jurisdiction` must not
        name a rule set."""
        under_rules = {r["jurisdiction"] for r in self.rules}
        bad = sorted(r["table"] for r in self.design
                     if (r["rules_jurisdiction"] or "").strip() and r["jurisdiction"] in under_rules)
        self.assertFalse(bad, f"{len(bad)} tables carry a key although their own "
                              f"jurisdiction names a rule set: {bad[:4]}")

    def test_no_rule_set_is_unreachable(self):
        """Every rule set's `jurisdiction` is some table's key -- the other half
        of a typo, which otherwise sits in the file matching nothing."""
        keys = {rules_key(r) for r in self.design}
        orphan = sorted({r["jurisdiction"] for r in self.rules}
                        - keys - set(RULES_AHEAD_OF_DATA))
        self.assertFalse(orphan, f"rule sets no table can reach: {orphan}; add the "
                                 f"tables, fix the spelling, or name the jurisdiction "
                                 f"in RULES_AHEAD_OF_DATA")


if __name__ == "__main__":
    unittest.main()
