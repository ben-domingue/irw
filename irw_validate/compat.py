"""Backwards-compatible `run_qc` for the fifty callers in `data/`.

Fifty conversion scripts do `from irw_triage_updated import run_qc` and read
`c.name` / `c.status` / `c.detail`. None of them imports `Check` or anything
else, so this is the entire compatibility surface -- but fifty files break at
someone else's runtime if it moves, which is why the checks were *moved*
verbatim rather than rewritten, and why the golden test pins their emission
order.

`run_qc` here is the moved implementation itself, not a translation of it: the
severity profiles in `irw_validate.model` are layered on top by
`irw_validate.core`, never underneath. So a caller of `run_qc` sees exactly what
it saw before this package existed.
"""
from ._checks import Check, irw_metadata, run_qc

__all__ = ["Check", "run_qc", "irw_metadata"]
