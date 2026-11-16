"""The rankings README defines every value counting_rules.csv uses, and no other.

data/rankings/README.md has a table of the columns of `counting_rules.csv` and one of
`counting_values.csv`, and their rows are where a value such as `pass_over` or
`test1_next_higher_total_surpass` is defined. Nothing in the pipeline reads
`counting_rules.csv` yet, so two mistakes would show up nowhere: a rule set that uses a
value the README never defines (a reader, or a count written from the README, cannot tell
what the cell means), and a definition no rule set uses (most often the old spelling left
behind when a value is renamed in the CSV). Neither is visible in a diff of one file
(Ben, 2026-11-11, #3461).

A row that holds values is read as the backticked words of its description, less the words
that are not values: column names, file names, reserved items such as `(overvote)`, the
joiners `+` and `;`, `yes`, `no` and `S:1`, and, in a rule row, the quantities of
`counting_values.csv`. `quantity` is checked against the rows of `counting_values.csv`,
every other row against the rule sets. A row of several columns (`overvote`, `skipped`,
`duplicate`) is one set, so a value defined for one of them and used only in another
passes. `default_option` is not read: its values are each vote's own `item` strings.
`max_consecutive_skips` and `surplus_decimals` may also hold a number, as the README says.

The failure worth guarding against is passing because nothing was compared:
`test_the_files_are_read_whole` pins the 11 rows that hold values, needs a row for every
column of `counting_rules.csv` that holds values, and needs each row to define a value that
is in use; `test_the_check_finds_both_gaps` runs the check on a made-up README with gaps
of both kinds, in a rule row and in `quantity`.

Offline. Add a step for this file to .github/workflows/tests.yml if you move it.

Run: python metadata/tests/test_rank_readme_values.py -v
"""
import csv
import re
import unittest
from pathlib import Path

RANKINGS = Path(__file__).resolve().parents[2] / "data" / "rankings"
README = RANKINGS / "README.md"
RULES = RANKINGS / "counting_rules.csv"
VALUES = RANKINGS / "counting_values.csv"
DESIGN = RANKINGS / "design_tables.csv"

#: Columns of counting_rules.csv that hold text rather than values from a list.
#: `default_option` holds each vote's own `item` strings.
FREE_TEXT = {"jurisdiction", "rule_set", "valid_from", "valid_to", "ordinance", "sections",
             "source_url", "evidence", "default_option"}
#: Backticked words in a definition that are not values of its columns.
MENTIONS = {"+", ";", "yes", "no", "S:1"}
#: How a cell that holds several values joins them.
JOINERS = {"batch_elimination": "+", "threshold": "; "}
#: Columns the README lets hold a number besides the values it lists.
NUMBERS = {"max_consecutive_skips", "surplus_decimals"}
#: The README rows that hold values, by their columns. A new one fails
#: test_the_files_are_read_whole until it is named here.
VALUE_ROWS = {
    ("overvote", "skipped", "duplicate"), ("max_consecutive_skips",), ("batch_elimination",),
    ("threshold",), ("surplus_transfer", "surplus_decimals"), ("last_defeat_transfer",),
    ("one_seat_stop",), ("quorum",), ("majority_test",), ("condorcet_method",), ("quantity",),
}

ROW = re.compile(r"\| ((?:`[^`]+`(?:, )?)+) \| (.*) \|$")
TICKED = re.compile(r"`([^`]+)`")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def defined_values(readme, rule_cols, other_cols):
    """{the columns of a README row: the values it defines}, for every row that holds values."""
    rows = {}
    for line in readme.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        cols = tuple(TICKED.findall(m.group(1)))
        if cols == ("quantity",) or set(cols) <= set(rule_cols) - FREE_TEXT:
            rows[cols] = {w.removeprefix("; ") for w in TICKED.findall(m.group(2))}
    quantities = rows.get(("quantity",), set())
    skip = set(rule_cols) | set(other_cols) | MENTIONS
    return {cols: {w for w in words if w not in skip and not w.startswith("(") and ".csv" not in w
                   and (cols == ("quantity",) or w not in quantities)}
            for cols, words in rows.items()}


def used_values(cols, rules, values):
    """The values the rule sets use in these columns; for `quantity`, the rows of counting_values.csv."""
    if cols == ("quantity",):
        return {v["quantity"] for v in values}
    return {w for r in rules for c in cols
            for w in (r[c].split(JOINERS[c]) if c in JOINERS else [r[c]])
            if not (c in NUMBERS and w.isascii() and w.isdigit())}


def gaps(defined, rules, values):
    """{row: (values defined and used nowhere, values used and never defined)}."""
    return {cols: (sorted(d - used_values(cols, rules, values)), sorted(used_values(cols, rules, values) - d))
            for cols, d in defined.items()}


class ReadmeValues(unittest.TestCase):
    def setUp(self):
        self.rule_cols, self.rules = read(RULES)
        value_cols, self.values = read(VALUES)
        other_cols = set(read(DESIGN)[0]) | set(value_cols)
        self.defined = defined_values(README.read_text(encoding="utf-8"), self.rule_cols, other_cols)
        self.gaps = gaps(self.defined, self.rules, self.values)

    def test_the_files_are_read_whole(self):
        """The 11 rows are found, every column that holds values has one, and each row
        defines a value that is in use."""
        self.assertEqual(len(VALUE_ROWS), 11)
        self.assertEqual(set(self.defined), VALUE_ROWS, "the README rows that hold values changed; update VALUE_ROWS")
        self.assertGreater(len(self.rules), 5)
        self.assertGreater(len(self.values), 5)
        in_rows = {c for cols in self.defined for c in cols}
        self.assertFalse(set(self.rule_cols) - FREE_TEXT - in_rows,
                         "columns of counting_rules.csv that no README row defines")
        for cols in VALUE_ROWS:
            self.assertTrue(self.defined[cols] & used_values(cols, self.rules, self.values),
                            f"{cols}: no value the README row defines is in use")

    def test_every_value_defined_is_used(self):
        unused = {", ".join(c): g[0] for c, g in self.gaps.items() if g[0]}
        self.assertFalse(unused, f"the README defines values that nothing uses: {unused}; "
                                 f"drop them or fix the spelling")

    def test_every_value_used_is_defined(self):
        undefined = {", ".join(c): g[1] for c, g in self.gaps.items() if g[1]}
        self.assertFalse(undefined, f"values in use that the README does not define: {undefined}; "
                                    f"define them in the column's row")

    def test_the_check_finds_both_gaps(self):
        """Unused and undefined values are found, in a rule row and in `quantity`; numbers,
        joiners, reserved items, file names, quantities and the free-text rows are not read
        as values."""
        readme = "\n".join([
            "| `jurisdiction` | as in `design_tables.csv` |",
            "| `default_option` | the `item` of the default option; `na` in a ranked-choice count |",
            "| `overvote`, `skipped` | `pass_over` or `exhaust`; the `(overvote)` item |",
            "| `max_consecutive_skips` | `none` or a number |",
            "| `batch_elimination` | joined by `+`: `test_a`, `test_b` or `writein_test` "
            "(reads `writein_filed` in `counting_values.csv`, `yes` or `no`) |",
            "| `quantity` | `developers` or `writein_filed` |",
        ])
        rule_cols = ["jurisdiction", "rule_set", "default_option", "overvote", "skipped",
                     "max_consecutive_skips", "batch_elimination"]
        rules = [
            {"rule_set": "r1", "overvote": "exhaust", "skipped": "exhaust",
             "max_consecutive_skips": "none", "batch_elimination": "test_a+test_c"},
            {"rule_set": "r2", "overvote": "pass_over", "skipped": "pass_over",
             "max_consecutive_skips": "2", "batch_elimination": "writein_test"},
        ]
        values = [{"table": "t1", "quantity": "writein_filed"}]
        found = gaps(defined_values(readme, rule_cols, {"table", "item", "quantity", "value"}), rules, values)
        self.assertEqual(found, {
            ("overvote", "skipped"): ([], []),
            ("max_consecutive_skips",): ([], []),
            ("batch_elimination",): (["test_b"], ["test_c"]),
            ("quantity",): (["developers"], []),
        })


if __name__ == "__main__":
    unittest.main()
