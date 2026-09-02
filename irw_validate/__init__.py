"""One IRW format validator, with an exit code (ben-domingue/irw#1703, 1.3).

    from irw_validate import validate_file, validate_frame, exit_code

    report = validate_file("out/mytable.csv")
    print(report.ok, [f.check for f in report.errors])

Command line:

    irw-validate out/*.csv                 # exit 1 if anything blocks
    irw-validate out/x.csv --profile core  # the validate_irw.R subset
    irw-validate out/x.csv --strict        # warnings block too

Why this exists: the checks were forked between `misc/validate_irw.R` (5 checks,
called by nothing) and `automated_finding/irw_triage_updated.py::run_qc` (~20
checks, called by fifty scripts but only ever advisorily -- its __main__ exits 0
however many fail). Neither had an exit code, so neither could gate anything.
"""
from .core import (MAX_BYTES, format_report, validate_file, validate_frame,
                   validate_paths)
from .model import (CORE_CHECKS, GATE_ERRORS, PROFILES, Finding, Report,
                    exit_code, severity_for)

__all__ = [
    "validate_file", "validate_frame", "validate_paths", "format_report",
    "Finding", "Report", "exit_code", "severity_for",
    "CORE_CHECKS", "GATE_ERRORS", "PROFILES", "MAX_BYTES",
]
