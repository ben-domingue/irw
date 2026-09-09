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

import os
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


def _cov_range_severity() -> str:
    """`error` by default since 2026-09-05; `IRW_COV_RANGE_SEVERITY` overrides.

    The override exists because promoting a gate is a judgement about a corpus
    that keeps changing, and the person who needs to reverse it may not be the
    person who can ship a release.
    """
    value = os.environ.get("IRW_COV_RANGE_SEVERITY", "error").strip().lower()
    return value if value in ("error", "warn", "info") else "error"


def check_cov_range(df: pd.DataFrame, table: str = "") -> list:
    """`cov_age` must actually hold ages (#1779).

    **Promoted from `warn` to `error` on 2026-09-05** ("let's test error for
    now" -- Ben, irw#1856). The objection to erroring was that it would fail
    all 81 known tables on their next re-upload before anyone had decided the
    repair. That objection expired: 72 of the 81 are repaired, and the only
    live tables it now refuses are the nine `wvs_panasiuk_*`, which are blocked
    on a source file and are not going to be re-uploaded by accident.

    The argument for erroring is that warning has already been tried. This check
    has warned since it was written, and 81 tables served a `cov_age` of 1999
    for as long as they were published; a warning in a scrolling upload log is
    not a notification. `irw_filter()` reads every value here as an age.

    This is a **test**, so it is reversible in one place: set
    `IRW_COV_RANGE_SEVERITY=warn` in the environment to put it back without a
    deploy, and see `_severity()` below.
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
            "cov_range", _cov_range_severity(),
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


#: Separator characters that different source workbooks use interchangeably for
#: the same item, and the digit runs that must NOT be merged across.
_SEPARATORS = re.compile(r"[\s_\-.]+")
_NON_ALNUM = re.compile(r"[^0-9A-Za-z]+")
_DIGIT_RUN = re.compile(r"\d+")


def _separator_key(item: str) -> str:
    """Treat any run of separators as one, ignore case.

    Substitutes rather than deletes, so "item_1_2" and "item_12" stay distinct:
    collapsing those would be a false positive on every table that numbers its
    items.
    """
    return _SEPARATORS.sub("\x00", item.strip()).casefold()


def _squashed_key(item: str) -> str | None:
    """Drop every non-alphanumeric character. `None` where that is unsafe.

    Needed because a workbook does not only swap one separator for another, it
    deletes them: `DART_Brysbaert_2020_3_4_5` spells "J.K. Rowling" as "JK
    Rowling", which no separator-substituting key can match.

    Guarded by the digit runs, which is what keeps "item_1_2" from merging into
    "item_12": codes whose digit sequences differ are never compared this way.
    A code carrying no digits at all -- the personal-name case this comes from
    -- is always safe.
    """
    return _NON_ALNUM.sub("", item).casefold() + "|" + ",".join(_DIGIT_RUN.findall(item))


def check_item_variants(df: pd.DataFrame, table: str = "") -> list:
    """Two item codes that are renderings of one item (#2052).

    Nothing else in the suite can see this. `dup_id_item` cannot, because the
    whole defect is that the two codes are *different* -- no id+item key ever
    repeats. The whole-row duplicate sweep cannot either. Yet the effect is that
    one real item is estimated twice, from disjoint samples, as two unrelated
    items.

    `DART_Brysbaert_2020_3_4_5` is the case this comes from: studies 3 and 4
    read author names from a workbook column ("Agatha Christie", "J.K.
    Rowling"), study 5 pivoted them out of column headers ("Agatha_Christie",
    "JK Rowling"), and nothing reconciled the two before the studies were
    pooled. 106 of its 158 authors were doubled -- 264 codes in the published
    table. That was introduced by our own ingest rather than carried in from the
    deposit, which is why it belongs in the uploader rather than in triage.

    Warn rather than error: like `dup_id_item` and `cov_range` before it, this
    describes tables that are already published, and a blocking gate would stop
    unrelated work on the strength of a defect nobody has triaged yet.
    """
    if "item" not in df.columns or df.empty:
        return []
    items = [str(v) for v in pd.Series(df["item"]).dropna().unique()]
    if not items:
        return []

    groups: dict = {}
    for keyfn in (_separator_key, _squashed_key):
        buckets: dict = {}
        for item in items:
            buckets.setdefault(keyfn(item), []).append(item)
        for members in buckets.values():
            if len(members) > 1:
                groups[tuple(sorted(members))] = sorted(members)

    # A pair caught by both keys is one finding, not two.
    merged: list = []
    for members in sorted(groups.values()):
        if not any(set(members) <= set(m) for m in merged):
            merged = [m for m in merged if not set(m) < set(members)]
            merged.append(members)
    if not merged:
        return []

    doubled = sum(len(m) - 1 for m in merged)
    examples = "; ".join(" || ".join(m) for m in merged[:3])
    return [Finding(
        "item_variants", "warn",
        f"{len(merged)} item(s) appear under more than one code differing only "
        f"in punctuation, spacing or case, so {len(items)} codes describe "
        f"{len(items) - doubled} items: {examples}"
        f"{' ...' if len(merged) > 3 else ''}. An IRT model fits each rendering "
        "as a separate item (#2052). Normalise the codes in the processing "
        "script.",
        table=table, group="core")]
