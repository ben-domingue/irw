"""Findings, reports, severity profiles and exit codes.

Severity is a property of the **(check, profile)** pair, never of the check
alone. That is the whole design, and it exists because the checks were written
for triage -- deciding whether a machine's guess at a conversion is worth a
human's time -- and are now being asked to gate publication, which is a
different question with a different cost of being wrong.

Response widths illustrate the distinction: an unused endpoint or a weighted
item can change an observed range without changing the construct. Width-only
findings warn in every profile. Explicit source-supported inputs can establish
an out-of-codebook response or different construct groups with different
ranges; only those evidence paths produce response-scale failures (#1697).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

SEVERITIES = ("error", "warn", "info")

#: The five checks ported from `misc/validate_irw.R`. This list is the R/Python
#: contract: `tests/test_validate.py` parses the R file and asserts set-equality
#: against it, so the fork cannot silently reopen.
CORE_CHECKS = frozenset({
    "required_columns", "id_na", "item_na", "resp_na", "resp_numeric",
    "dup_id_item", "cov_prefix",
})

#: Heuristics that block at the gate anyway. A `resp` with one distinct value is
#: unusable at any altitude -- it carries no information for any model. Add to
#: this only with a case written down. The two response checks fail only with
#: explicit external documentation (#1697): an observed code outside its
#: permitted set, or documented constructs with different observed ranges.
#: Their width-only counterparts are raw WARN and are never promoted here.
GATE_ERRORS = frozenset({"resp_variation*", "resp_outside_permitted", "resp_scale_constructs"})

PROFILES = ("core", "triage", "upload", "legacy")

#: The published version of the format these checks enforce, the IRW Data
#: Standard at https://itemresponsewarehouse.org/standard.html (#1716). Bump it
#: only when that page's changelog does -- a new check is not a new standard.
STANDARD_VERSION = "1.0"
STANDARD_URL = "https://itemresponsewarehouse.org/standard.html"

#: Check -> the numbered clause of the standard it tests. Only these checks bear
#: on conformance; everything else the validator runs is IRW intake policy (the
#: sample floor, table names) or a heuristic, and a table can conform to the
#: standard while failing every one of them. `tests/test_validate.py` asserts
#: that each of CORE_CHECKS has a clause, so a new core check cannot ship
#: without one.
CLAUSES = {
    "required_columns": "C1",
    "id_na": "C2",
    "item_na": "C3",
    "resp_na": "C4",
    "resp_numeric": "C4",
    "dup_id_item": "C5",
    "cov_prefix": "C6",
    "column_order": "C7",
}


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str          # one of SEVERITIES
    message: str
    table: str = ""
    group: str = "core"    # "core" | "heuristic" | "name" | "covariate"

    @property
    def clause(self) -> str:
        """The standard's clause this finding tests, or "" for intake/heuristics."""
        return CLAUSES.get(self.check, "")

    def to_dict(self) -> dict:
        return {**vars(self), "clause": self.clause}


@dataclass
class Report:
    label: str
    profile: str = "upload"
    findings: list = field(default_factory=list)
    checks_run: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    overridden: list = field(default_factory=list)
    override_reason: str | None = None
    #: "responses" or "item_text". Standard 1.0 defines the response table only;
    #: item text has its own schema, so conformance is not asked of it.
    kind: str = "responses"

    @property
    def errors(self) -> list:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list:
        return [f for f in self.findings if f.severity == "warn"]

    @property
    def ok(self) -> bool:
        """Mirrors red_up.checks.FileReport.ok, so the two compose directly."""
        return not self.errors

    @property
    def nonconforming(self) -> list:
        """Clauses of the standard this table breaks, in clause order.

        Overridden errors count. A waiver lets a table through IRW's gate; it
        does not make the table conform to the standard.
        """
        broken = [f for f in self.errors + self.overridden
                  if f.severity == "error" and f.clause]
        return sorted({f.clause for f in broken})

    @property
    def conforms(self) -> bool | None:
        """Does the table meet the IRW Data Standard, as distinct from `ok`?

        `ok` asks whether IRW would accept the table under this profile, which
        includes intake policy. `conforms` asks only whether it is a valid IRW
        table: no error on a check the standard's clauses define.

        None for item text, which Standard 1.0 does not cover, and under the
        `core` and `triage` profiles. Those keep the inherited readings of C4
        (99% of values numeric) and C5 (only wave/timepoint/date explain a
        repeat) for their callers, and the standard is the gate's reading: a
        rater design would be called nonconforming there and conforming here.
        """
        if self.kind != "responses" or self.profile not in ("upload", "legacy"):
            return None
        return not self.nonconforming

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "profile": self.profile,
            "standard_version": STANDARD_VERSION,
            "conforms": self.conforms,
            "nonconforming": self.nonconforming,
            "ok": self.ok,
            "stats": self.stats,
            "checks_run": self.checks_run,
            "findings": [f.to_dict() for f in self.findings],
            "overridden": [f.to_dict() for f in self.overridden],
            "override_reason": self.override_reason,
        }


def severity_for(name: str, status: str, profile: str) -> str | None:
    """Map one raw check result onto a severity, or None to drop it.

    `status` is the raw `pass|warn|fail` the moved checks emit.
    """
    if status == "pass":
        return None
    is_core = name in CORE_CHECKS or name.endswith("_na")
    if profile == "core" and not is_core:
        return None                       # the R-parity subset only
    if profile == "triage":
        return "error" if status == "fail" else "warn"
    if profile == "legacy" and name == "cov_prefix":
        return None                       # legacy tables predate the prefix rule
    if status == "warn":
        return "warn"
    # status == "fail"
    if is_core or name in GATE_ERRORS:
        return "error"
    return "warn"                         # a heuristic never blocks by default


def exit_code(reports: Iterable[Report], *, strict: bool = False) -> int:
    """0 clean - 1 something blocks. Matches red_up's contract (2 is bad input)."""
    reports = list(reports)
    if any(r.errors for r in reports):
        return 1
    if strict and any(r.warnings for r in reports):
        return 1
    return 0
