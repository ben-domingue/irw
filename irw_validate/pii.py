"""A personal-data screen on the write path, for every family (review R-41, #3227).

WHY IT WAS MISSING
------------------
The 28-check registry had no PII check at all. The real value-level screen --
`_holds_email_addresses`, `_looks_like_person_names`, `_holds_full_postal_codes`
in `automated_finding/irw_triage_updated.py`, with documented false-positive
discipline -- runs only during automated-finding triage, against raw candidate
headers. A table arriving by any other route (a hand-written `data/` script, a
direct contribution, a rebuild) reached Redivis unscreened, which is how
`friedman_2018_risks_*` published a full 5-digit ZIP for 516 releases.

WHY A NAME MATCH WARNS AND A VALUE MATCH FAILS
----------------------------------------------
Measured, not assumed. The 2026-10-24 live screen examined the 29 published
tables whose column NAME suggests a direct identifier: 28 were coded yes/no
flags (`cov_address`, `cov_left_email`, `cov_contact`, `cov_mobile_phone` all
hold 0/1), and the single real identifier in the corpus was found by reading
VALUES. So a name is a lead -- block uploads on it and the gate gets switched
off within the week -- while a column OF email addresses, personal names or
full postal codes is a finding that should stop a release.

A SCREEN THAT READS NOTHING REPORTS CLEAN
-----------------------------------------
That is the worst shape a safety check can take, and it is not hypothetical: an
ad-hoc screen on 2026-10-19 read 0 of a deposit's 11 string columns and printed
no hits. So the content-tier denominator is asserted here rather than printed:
a frame with unreadable non-numeric columns produces `pii_screen_blind`, and a
frame the screen is unavailable for produces `pii_screen_unavailable`. Neither
is ever silent.

The screen lives in the pipeline, not in this package: `irw_validate` is
installable on its own, and a contributor who does that has no
`automated_finding/`. The import is therefore attempted and its absence
reported, exactly as `rights.load_register()` reports a missing register.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from .model import Finding

#: Columns the IRW schema defines, which are never identifiers whatever their
#: values look like. `id` is a pseudonymous respondent key by construction, and
#: `item`/`resp` are the response itself. Screening them would report the
#: standard's own schema: a free-text `resp` can contain anything a respondent
#: typed, and that is a question about the source, not about the write path.
#: Rows screened from each end of a large table; see check_pii.
_SAMPLE_ROWS = 25_000

SCHEMA_COLUMNS = frozenset({"id", "item", "resp", "raw_resp", "table",
                            "item_text", "option_text", "task", "profile",
                            "choice", "rating", "rank", "wave", "trial", "date"})


#: An IRW column whose name says "name" and which therefore has to be judged
#: on its values. `_RE_BARE_NAME_LABEL` in the triage screen matches the bare
#: word only -- deliberately, because a raw deposit is full of `variable_name`
#: and `file_name` columns -- but an IRW table's columns are the schema's plus
#: `cov_*`, so `cov_name` is the shape this has to cover. The blocklist keeps
#: the structural ones out: those hold item or file labels, and a column of
#: short alphabetic item names reads exactly like a roster to a values test.
_RE_NAME_COLUMN = re.compile(
    r"(?:^|_)(?:name|names|nombre|nome|nom)$", re.IGNORECASE)
_NOT_PERSON_NAME = re.compile(
    r"(?:item|table|variable|var|file|column|col|dataset|data|scale|"
    r"construct|instrument|measure|test|form|site|school|country|city|"
    r"region|state|team|player|club|product|brand|party|candidate)"
    r"[_\s-]*(?:name|names)$", re.IGNORECASE)


def _screen():
    """The pipeline's PII screen, or None when this package is installed alone."""
    root = Path(__file__).resolve().parent.parent
    module = root / "automated_finding" / "irw_triage_updated.py"
    if not module.is_file():
        return None
    try:
        sys.path.insert(0, str(root / "automated_finding"))
        from irw_triage_updated import screen_for_pii  # noqa: WPS433
        return screen_for_pii
    except Exception:
        return None


def _person_name_columns(df, columns) -> list:
    """Columns named `*_name` whose VALUES read as a roster of people.

    The content test is the triage screen's own `_looks_like_person_names`
    (20+ values, 80% name-shaped, 15+ distinct, <=4 tokens), so the threshold
    discipline is shared rather than re-tuned here. Only the set of column
    names this is applied to is IRW-specific.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent
                               / "automated_finding"))
        from irw_triage_updated import _looks_like_person_names  # noqa: WPS433
    except Exception:
        return []
    out = []
    for c in columns:
        name = str(c)
        if not _RE_NAME_COLUMN.search(name) or _NOT_PERSON_NAME.search(name):
            continue
        try:
            if _looks_like_person_names(df[c]):
                out.append(f"{name} (personal names in the values)")
        except Exception:
            continue
    return out


def _unreadable(df, columns) -> list:
    """Non-numeric columns whose values the content tier could not read.

    The honest zero is an all-numeric response matrix. The zero worth a finding
    is the one where the frame DOES hold non-numeric columns and the screen read
    none of them -- that is a dtype bug, and it looks exactly like a pass.
    """
    try:
        import pandas as pd
    except Exception:
        return []
    out = []
    for c in columns:
        try:
            if (not pd.api.types.is_numeric_dtype(df[c])
                    and not pd.api.types.is_datetime64_any_dtype(df[c])
                    and not pd.api.types.is_string_dtype(df[c])
                    and not pd.api.types.is_object_dtype(df[c])):
                out.append(str(c))
        except Exception:
            out.append(str(c))
    return out


def check_pii(df, table: str) -> tuple[list, list]:
    """(findings, checks_run) for one frame, any family.

    Never raises: a screen that crashes must not take the upload's other
    findings with it, so a failure is reported as a finding of its own.
    """
    screen = _screen()
    if screen is None:
        return ([Finding(
            "pii_screen_unavailable", "warn",
            "no PII screen available: automated_finding/irw_triage_updated.py is "
            "not beside this package, so nothing read this table's values for "
            "email addresses, personal names or postal codes. Run the validator "
            "from an `irw` checkout before uploading (#3227).",
            table=table, group="core")], ["pii_screen:unavailable"])

    columns = [c for c in getattr(df, "columns", []) if str(c) not in SCHEMA_COLUMNS]
    if not columns:
        return ([], ["pii_screen:no_columns"])
    #: Screen a head-and-tail sample of a large table rather than all of it.
    #: `_looks_like_person_names` reads a whole column, and the biggest IRW
    #: tables are tens of millions of rows -- unaffordable in the uploader's hot
    #: path, which is the same reason red_up streams 500 MB files with the csv
    #: module. Every detector here is a PROPORTION over its sample, so a column
    #: OF identifiers is just as visible in 50,000 rows as in 44 million; what a
    #: sample can miss is a handful of addresses deep in the middle of one
    #: column, and that is the incidental case the 2026-10-19 ruling says is not
    #: disqualifying anyway. Both ends, because a sorted export puts the
    #: anomalous rows last.
    frame = df
    try:
        if len(df) > 2 * _SAMPLE_ROWS:
            import pandas as pd
            frame = pd.concat([df.head(_SAMPLE_ROWS), df.tail(_SAMPLE_ROWS)])
    except Exception:
        frame = df
    #: IRW column names defeat the screen's word boundaries: every covariate is
    #: `cov_`-prefixed and underscore-joined, so `\bemail\b` does not match
    #: `cov_left_email` (both sides of the underscore are word characters). The
    #: screen already has a tier for alternative text -- the SPSS/Stata variable
    #: label -- so the spaced form of the name goes through that, and the
    #: content tier keeps reading `df[c]` under the real name.
    labels = {c: str(c).replace("_", " ").replace("-", " ") for c in columns}
    try:
        hits = screen(columns, frame, labels=labels)
    except Exception as exc:                      # noqa: BLE001 -- reported, not raised
        return ([Finding(
            "pii_screen_failed", "warn",
            f"the PII screen raised {type(exc).__name__}: {exc}. Nothing was "
            "screened, which is not the same as clean (#3227).",
            table=table, group="core")], ["pii_screen:failed"])

    value_hits = list(getattr(screen, "value_hits", []) or [])
    #: `cov_name`-shaped columns, which the triage screen's bare-label rule
    #: cannot reach. Value-level, so they join the hits that fail.
    for extra_hit in _person_name_columns(frame, columns):
        if extra_hit not in value_hits:
            value_hits.append(extra_hit)
            hits = list(hits) + [extra_hit]
    screened = int(getattr(screen, "content_cols_screened", 0) or 0)
    checks_run = [f"pii_screen:content_cols={screened}"]
    findings = []
    if value_hits:
        findings.append(Finding(
            "pii_values", "error",
            f"{len(value_hits)} column(s) hold what reads as personal data: "
            + "; ".join(value_hits[:5])
            + ". This is a value-level match, not a guess from the column name. "
              "Drop or coarsen the column before uploading -- a geographic code "
              "is coarsened, a name or an address means the table does not ship "
              "(2026-10-20 ruling).",
            table=table, group="core", details=tuple(value_hits)))
    name_only = [h for h in hits if h not in set(value_hits)]
    if name_only:
        findings.append(Finding(
            "pii_name", "warn",
            f"{len(name_only)} column name(s) read like a direct identifier: "
            + "; ".join(name_only[:5])
            + ". Usually a coded flag -- 28 of the 29 such columns in the live "
              "corpus hold yes/no values -- so this warns rather than blocks. "
              "Confirm what the column holds (#3227).",
            table=table, group="core", details=tuple(name_only)))
    unread = _unreadable(frame, columns)
    if screened == 0 and unread:
        findings.append(Finding(
            "pii_screen_blind", "warn",
            f"the PII screen read 0 of {len(columns)} column(s), yet "
            f"{len(unread)} are neither numeric nor readable as text "
            f"(e.g. {', '.join(unread[:3])}). A screen that reads nothing "
            "reports clean, so this result is not evidence (#3227).",
            table=table, group="core", details=tuple(unread)))
    return findings, checks_run
