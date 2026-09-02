"""Findings, reports, severity profiles and exit codes.

Severity is a property of the **(check, profile)** pair, never of the check
alone. That is the whole design, and it exists because the checks were written
for triage -- deciding whether a machine's guess at a conversion is worth a
human's time -- and are now being asked to gate publication, which is a
different question with a different cost of being wrong.

`resp_scale_mixed` is the worked example. It is `fail` today, and
`data/cao_2026_cdss.py` documents a table that trips it legitimately: an unused
top category on a left-skewed 1-7 scale reads as a second scale. Promoting every
heuristic to a blocking error would have rejected that correct table on the day
the gate went in. So heuristics are capped at `warn` under `upload`, and
`GATE_ERRORS` grows one documented case at a time.
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
#: this only with a case written down.
GATE_ERRORS = frozenset({"resp_variation*"})

PROFILES = ("core", "triage", "upload", "legacy")


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str          # one of SEVERITIES
    message: str
    table: str = ""
    group: str = "core"    # "core" | "heuristic" | "name" | "covariate"


@dataclass
class Report:
    label: str
    profile: str = "upload"
    findings: list = field(default_factory=list)
    checks_run: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    overridden: list = field(default_factory=list)
    override_reason: str | None = None

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

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "profile": self.profile,
            "ok": self.ok,
            "stats": self.stats,
            "checks_run": self.checks_run,
            "findings": [vars(f) for f in self.findings],
            "overridden": [vars(f) for f in self.overridden],
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
