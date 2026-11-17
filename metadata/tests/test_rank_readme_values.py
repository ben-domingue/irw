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
`counting_values.csv`. A consequence, known and accepted (Ben, 2026-11-16, #3461): a value
spelled like a column name of `counting_rules.csv`, `design_tables.csv` or
`counting_values.csv` (`seats`, `value`), or in a rule row like a quantity (`majority`), is
dropped from the definitions. A rule set that uses such a value still fails, as a value
used and not defined; a definition of one that nothing uses goes unreported. No value in
use is spelled so today. `quantity` is checked against the rows of `counting_values.csv`, every
other row against the rule sets. `default_option` is not read: its values are each vote's
own `item` strings. `max_consecutive_skips` and `surplus_decimals` may also hold a number,
as the README says.

A row of several columns is checked column by column. A value the row restricts to one of
its columns, in the README's words "for `<column>` also `<value>`" (`skipped_ranking` for
`duplicate`, `exhaust_unless_one_continuing` for `overvote`), is defined for that column
only, and must be used there; any other value of the row is defined for each of its
columns and needs a use in one of them. So `skipped_ranking` in `overvote` fails. A row
that restricts nothing (`surplus_transfer`, `surplus_decimals`) gives each of its values to
both columns. No two rows may define the same column, since the second would replace the
first unseen.

The failure worth guarding against is passing because nothing was compared:
`test_the_files_are_read_whole` pins the rows that hold values (`VALUE_ROWS`), needs a row
for every column of `counting_rules.csv` that holds values, needs each row to define a value
that is in use, and needs the README's two restrictions to be read as restrictions;
`test_the_check_finds_both_gaps` runs the check on a made-up README with gaps of both kinds,
in a rule row, in a restricted value and in `quantity`, and
`test_two_rows_for_one_column_fail` on one that defines a column twice.

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
#: "for `duplicate` also `skipped_ranking`": a value the row defines for one of its columns only.
RESTRICTED = re.compile(r"for `([^`]+)` also `([^`]+)`")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def defined_values(readme, rule_cols, other_cols):
    """{the columns of a README row: {column: the values the row defines for it}}, for every
    row that holds values. Two rows that define the same column raise ValueError."""
    rows, row_of = {}, {}
    for line in readme.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        cols = tuple(TICKED.findall(m.group(1)))
        if not (cols == ("quantity",) or set(cols) <= set(rule_cols) - FREE_TEXT):
            continue
        for c in cols:
            if c in row_of:
                raise ValueError(f"two README rows define `{c}`: {row_of[c]} and {cols}")
            row_of[c] = cols
        rows[cols] = ({w.removeprefix("; ") for w in TICKED.findall(m.group(2))},
                      {(c, v) for c, v in RESTRICTED.findall(m.group(2)) if c in cols})
    quantities = rows[("quantity",)][0] if ("quantity",) in rows else set()
    skip = set(rule_cols) | set(other_cols) | MENTIONS
    defined = {}
    for cols, (words, restricted) in rows.items():
        values = {w for w in words if w not in skip and not w.startswith("(") and ".csv" not in w
                  and (cols == ("quantity",) or w not in quantities)}
        shared = values - {v for _, v in restricted}
        defined[cols] = {c: shared | {v for rc, v in restricted if rc == c and v in values}
                         for c in cols}
    return defined


def used_values(col, rules, values):
    """The values the rule sets use in this column; for `quantity`, the rows of counting_values.csv."""
    if col == "quantity":
        return {v["quantity"] for v in values}
    return {w for r in rules for w in (r[col].split(JOINERS[col]) if col in JOINERS else [r[col]])
            if not (col in NUMBERS and w.isascii() and w.isdigit())}


def gaps(defined, rules, values):
    """{row: (values defined and used nowhere, values used and never defined)}, column by column.

    A value restricted to one column must be used in it; a value of every column of the row
    needs a use in one of them; a value used in a column must be defined for that column. In a
    row of several columns a value tied to one column is named with it, as "v in `column`"."""
    found = {}
    for cols, by_col in defined.items():
        used = {c: used_values(c, rules, values) for c in cols}
        shared = set.intersection(*by_col.values())
        name = (lambda v, c: f"{v} in `{c}`") if len(cols) > 1 else (lambda v, c: v)
        unused = (shared - set().union(*used.values())) | {
            name(v, c) for c in cols for v in by_col[c] - shared - used[c]}
        undefined = {name(v, c) for c in cols for v in used[c] - by_col[c]}
        found[cols] = (sorted(unused), sorted(undefined))
    return found


class ReadmeValues(unittest.TestCase):
    def setUp(self):
        self.rule_cols, self.rules = read(RULES)
        value_cols, self.values = read(VALUES)
        other_cols = set(read(DESIGN)[0]) | set(value_cols)
        self.defined = defined_values(README.read_text(encoding="utf-8"), self.rule_cols, other_cols)
        self.gaps = gaps(self.defined, self.rules, self.values)

    def test_the_files_are_read_whole(self):
        """The rows of VALUE_ROWS are found, every column that holds values has one, each row
        defines a value that is in use, and the README's two restrictions are read as such."""
        self.assertEqual(set(self.defined), VALUE_ROWS, "the README rows that hold values changed; update VALUE_ROWS")
        self.assertGreater(len(self.rules), 5)
        self.assertGreater(len(self.values), 5)
        in_rows = {c for cols in self.defined for c in cols}
        self.assertFalse(set(self.rule_cols) - FREE_TEXT - in_rows,
                         "columns of counting_rules.csv that no README row defines")
        for cols in VALUE_ROWS:
            defined = set().union(*self.defined[cols].values())
            used = set().union(*(used_values(c, self.rules, self.values) for c in cols))
            self.assertTrue(defined & used, f"{cols}: no value the README row defines is in use")
        ballot = self.defined[("overvote", "skipped", "duplicate")]
        self.assertEqual({c for c in ballot if "skipped_ranking" in ballot[c]}, {"duplicate"})
        self.assertEqual({c for c in ballot if "exhaust_unless_one_continuing" in ballot[c]}, {"overvote"})
        self.assertEqual({c for c in ballot if "pass_over" in ballot[c]}, set(ballot))

    def test_every_value_defined_is_used(self):
        unused = {", ".join(c): g[0] for c, g in self.gaps.items() if g[0]}
        self.assertFalse(unused, f"the README defines values that nothing uses: {unused}; "
                                 f"drop them or fix the spelling")

    def test_every_value_used_is_defined(self):
        undefined = {", ".join(c): g[1] for c, g in self.gaps.items() if g[1]}
        self.assertFalse(undefined, f"values in use that the README does not define: {undefined}; "
                                    f"define them in the column's row")

    #: A made-up README and rule sets for the two tests below.
    MADE_UP = [
        "| `jurisdiction` | as in `design_tables.csv` |",
        "| `default_option` | the `item` of the default option; `na` in a ranked-choice count |",
        "| `overvote`, `skipped`, `duplicate` | `pass_over` or `exhaust`; for `overvote` also "
        "`exhaust_unless_one`; for `duplicate` also `skip_it` (counts toward "
        "`max_consecutive_skips`); for `skipped` also `stop_at_two`; the `(overvote)` item |",
        "| `max_consecutive_skips` | `none` or a number |",
        "| `batch_elimination` | joined by `+`: `test_a`, `test_b` or `writein_test` "
        "(reads `writein_filed` in `counting_values.csv`, `yes` or `no`) |",
        "| `quantity` | `developers` or `writein_filed` |",
    ]
    MADE_UP_COLS = ["jurisdiction", "rule_set", "default_option", "overvote", "skipped", "duplicate",
                    "max_consecutive_skips", "batch_elimination"]
    OTHER_COLS = {"table", "item", "quantity", "value"}

    def test_the_check_finds_both_gaps(self):
        """Unused and undefined values are found, in a rule row, in a value restricted to one
        column and in `quantity`; numbers, joiners, reserved items, file names, quantities and
        the free-text rows are not read as values."""
        rules = [
            {"rule_set": "r1", "overvote": "exhaust", "skipped": "exhaust", "duplicate": "skip_it",
             "max_consecutive_skips": "none", "batch_elimination": "test_a+test_c"},
            {"rule_set": "r2", "overvote": "skip_it", "skipped": "pass_over", "duplicate": "pass_over",
             "max_consecutive_skips": "2", "batch_elimination": "writein_test"},
        ]
        values = [{"table": "t1", "quantity": "writein_filed"}]
        defined = defined_values("\n".join(self.MADE_UP), self.MADE_UP_COLS, self.OTHER_COLS)
        self.assertEqual(gaps(defined, rules, values), {
            ("overvote", "skipped", "duplicate"): (
                ["exhaust_unless_one in `overvote`", "stop_at_two in `skipped`"],
                ["skip_it in `overvote`"]),
            ("max_consecutive_skips",): ([], []),
            ("batch_elimination",): (["test_b"], ["test_c"]),
            ("quantity",): (["developers"], []),
        })

    def test_two_rows_for_one_column_fail(self):
        """A second row for a column, whole or as part of a row of several, is an error, not a
        silent replacement of the first."""
        for extra in ("| `batch_elimination` | `test_d` |", "| `skipped` | `pass_over` |"):
            with self.assertRaisesRegex(ValueError, "two README rows define"):
                defined_values("\n".join(self.MADE_UP + [extra]), self.MADE_UP_COLS, self.OTHER_COLS)


if __name__ == "__main__":
    unittest.main()
