"""Checks that `datastandard.md` states in prose and nothing has ever run.

`ARCHITECTURE.md`'s Rule 2 says: "Where a rule can be made executable, make it
executable instead of writing it down." The standard is 348 lines of rules, and
until now not one of them was enforced by anything. These are the mechanical
ones. Each names the line of the standard it comes from, so the two cannot drift
apart without the citation becoming visibly wrong.

They run under the `upload` profile only. Triage sees a machine's guess at a
conversion, where a table name may not exist yet and a sample floor is not the
question being asked.
"""
from __future__ import annotations

import re

import pandas as pd

from .model import Finding

#: datastandard.md line 66: "Table names must be 40 characters or fewer".
MAX_NAME = 40
#: datastandard.md line 13: "The floor is 100 unique `id` values, flat".
MIN_IDS = 100
#: The plausible interval for a human age in years. `cov_age` outside it is not
#: an age -- see #1779, which found 81 live tables shipping a sentinel (999,
#: 1999), a birth year, or a days-since-epoch offset (-18090).
AGE_RANGE = (0, 120)

_NAME_OK = re.compile(r"^[a-z0-9_.]+$")


def check_name(table: str) -> list:
    """Table-name rules from datastandard.md lines 62-66."""
    out = []
    if not table:
        return out
    stem = table[:-4] if table.endswith(".csv") else table
    if len(stem) > MAX_NAME:
        out.append(Finding(
            "name_length", "error",
            f"table name is {len(stem)} characters; datastandard.md caps it at "
            f"{MAX_NAME}. Shorten the construct label, never the author or year.",
            table=table, group="name"))
    if not _NAME_OK.match(stem):
        out.append(Finding(
            "name_charset", "warn",
            f"table name {stem!r} is not lowercase [a-z0-9_.] -- Redivis keeps "
            "the case but every client lowercases when joining, so a "
            "capitalised name silently drops out of case-sensitive joins.",
            table=table, group="name"))
    return out


def check_shape(df: pd.DataFrame, table: str = "") -> list:
    """Sample floor and column order -- both prose rules in the standard today."""
    out = []
    if "id" in df.columns:
        n = df["id"].nunique()
        if n < MIN_IDS:
            out.append(Finding(
                "sample_floor", "warn",
                f"{n} unique ids; datastandard.md sets a flat floor of {MIN_IDS} "
                "with no judgment call in between. Warn rather than block: the "
                "floor governs what to accept, not what is already published.",
                table=table, group="core"))
    lead = [c for c in df.columns[:3]]
    if len(df.columns) >= 3 and lead != ["id", "item", "resp"]:
        out.append(Finding(
            "column_order", "warn",
            f"columns start {lead}; datastandard.md step 7 writes "
            "[id, item, resp] + covariates.",
            table=table, group="core"))
    return out


def check_cov_range(df: pd.DataFrame, table: str = "") -> list:
    """`cov_age` must actually hold ages (#1779).

    Severity is deliberately `warn`, not `error`. 81 tables are already live
    with this defect; blocking would fail them all on their next re-upload
    before anyone has decided what the repair is. Promote it once #1779 is
    closed.
    """
    out = []
    if "cov_age" not in df.columns:
        return out
    age = pd.to_numeric(df["cov_age"], errors="coerce").dropna()
    if age.empty:
        return out
    lo, hi = float(age.min()), float(age.max())
    if lo < AGE_RANGE[0] or hi > AGE_RANGE[1]:
        if hi >= 999:
            why = ("a sentinel no-answer code (999/9999) or a birth year that "
                   "was never converted")
        elif lo < 0:
            why = "a date or days-since-epoch offset stored as an age"
        else:
            why = "out of range for a human age in years"
        out.append(Finding(
            "cov_range", "warn",
            f"cov_age spans {lo:g}-{hi:g}, outside "
            f"[{AGE_RANGE[0]}, {AGE_RANGE[1]}] -- looks like {why}. "
            "irw_filter() treats every value here as an age (#1779).",
            table=table, group="covariate"))
    return out


def check_resp_dtype(df: pd.DataFrame, table: str = "") -> list:
    """What R's `is.numeric()` was actually catching, which Python dropped.

    A `resp` whose every value parses as a number but whose storage type is
    text uploads to Redivis as a string column, and every IRT model downstream
    breaks. Only meaningful for typed inputs (.RData/.sav/.dta/in-memory) --
    pandas already infers int64 from a CSV of "1","2".
    """
    if "resp" not in df.columns:
        return []
    if pd.api.types.is_numeric_dtype(df["resp"]):
        return []
    parsed = pd.to_numeric(df["resp"], errors="coerce")
    if parsed.notna().all() and len(df):
        return [Finding(
            "resp_dtype", "error",
            f"resp parses as numeric but is stored as {df['resp'].dtype}; it "
            "would upload as a string column. Coerce before writing.",
            table=table, group="core")]
    return []
