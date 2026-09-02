"""Static checks on a `data/` conversion script (#1703, sub-item 1.4).

    python3 -m irw_validate.contract data/foo_2026_bar.py
    python3 -m irw_validate.contract --added data/new.py --modified data/old.py

**Why static.** Sub-item 1.4 asks for a gate on pull requests touching `data/`,
and the obvious reading -- validate the table -- is impossible there: a PR to
`data/` contains a *conversion script*, and `automated_finding/irw_output/` is
gitignored, so no table is ever in the diff. Running the script in CI would mean
fetching from Mendeley, OSF, Zenodo and Dryad, which 404, rate-limit and expire
tokens; making corpus admission depend on a third party's uptime is a worse
failure than the one it prevents. So CI checks the script's *contract* and
leaves the data to `irw-validate` at processing time.

**Why added files block and modified files do not.** 843 scripts live in
`data/` and 50 of them call the validator. A rule applied to every file touched
would fail 793 scripts for sins they were written with, and a one-line fix to a
2019 script would be blocked by a check about something else entirely. That
makes the contributor queue worse, which is the opposite of what 1.4 is for.
New files carry the standard; old files get an annotation and no more.
"""
from __future__ import annotations

import argparse
import ast
import csv
import pathlib
import re
import sys

from .extra import MAX_NAME, _NAME_OK
from .model import Finding

#: A local path baked into a script means nobody else can re-run it.
#: `data/AAQ-II.R` reads and writes `D:/Desktop/...`.
LOCAL_PATH = re.compile(r"""['"](?:[A-Za-z]:[\\/]|/Users/|/home/|/mnt/[a-z]/)""")

#: What counts as "the validator was called".
VALIDATOR_NAMES = ("run_qc", "irw_validate", "validate_frame", "validate_file")


def _corpus_names(root: pathlib.Path) -> set:
    path = root / "metadata" / "metadata.csv"
    if not path.exists():
        return set()
    with path.open() as fh:
        return {r["table"] for r in csv.DictReader(fh) if r.get("table")}


def _string_constants(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node


def check_script(path: pathlib.Path, *, corpus: set | None = None) -> list:
    """Findings for one conversion script. Severity is assigned by the caller."""
    out: list = []
    name = path.name
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding("unreadable", "error", str(exc), table=name, group="contract")]

    # --- text-level: works for .R and .do too
    for i, line in enumerate(source.splitlines(), 1):
        if LOCAL_PATH.search(line) and not line.lstrip().startswith("#"):
            out.append(Finding(
                "local_path", "error",
                f"line {i} hardcodes a path on one person's machine, so nobody else "
                f"can re-run this script: {line.strip()[:90]}",
                table=name, group="contract"))
            break

    if path.suffix.lower() != ".py":
        return out          # no R parser here; the text checks are what we have

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return out + [Finding("syntax", "error", f"does not parse: {exc}",
                              table=name, group="contract")]

    # --- the validator must run before anything is written
    writes = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr in ("to_csv", "write_csv")]
    validated = [n.lineno for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and ((isinstance(n.func, ast.Name) and n.func.id in VALIDATOR_NAMES)
                      or (isinstance(n.func, ast.Attribute) and n.func.attr in VALIDATOR_NAMES))]
    if writes and not validated:
        out.append(Finding(
            "no_validator", "error",
            f"writes a table (line {min(writes)}) without calling the validator. "
            f"Import `run_qc` and assert no check fails before `to_csv`, or run "
            f"`irw-validate` on the output -- SKILL.md asks for this and nothing "
            f"has ever enforced it.",
            table=name, group="contract"))
    elif writes and min(validated) > min(writes):
        out.append(Finding(
            "validator_after_write", "warn",
            f"calls the validator at line {min(validated)} but writes at line "
            f"{min(writes)} -- a table checked after it is written is not a gate.",
            table=name, group="contract"))

    # --- literal output table names
    #
    # Only names the script actually WRITES. An earlier version checked every
    # string constant ending in .csv and flagged 94 scripts for the length of an
    # *input* filename -- `raw_data_export_2019.csv` is not a table name and the
    # 40-character cap does not apply to it. So: resolve the first argument of
    # each to_csv call, following a simple variable assignment once, and check
    # nothing else.
    assigned: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    assigned[t.id] = node.value.value

    def written_names():
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("to_csv", "write_csv") and node.args):
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                yield node.lineno, arg.value
            elif isinstance(arg, ast.Name) and arg.id in assigned:
                yield node.lineno, assigned[arg.id]

    seen = set()
    for lineno, v in written_names():
        v = v.rsplit("/", 1)[-1]
        if not v.endswith(".csv") or "{" in v:
            continue
        stem = v[:-4]
        if not stem or stem in seen:
            continue
        seen.add(stem)
        node = type("N", (), {"lineno": lineno})
        if len(stem) > MAX_NAME:
            out.append(Finding(
                "name_length", "error",
                f"line {node.lineno}: table name `{stem}` is {len(stem)} characters; "
                f"datastandard.md caps it at {MAX_NAME}.",
                table=name, group="contract"))
        elif not _NAME_OK.match(stem):
            out.append(Finding(
                "name_charset", "warn",
                f"line {node.lineno}: table name `{stem}` is not lowercase "
                f"[a-z0-9_.]; every client lowercases when joining.",
                table=name, group="contract"))
        if corpus and stem in corpus:
            out.append(Finding(
                "name_taken", "warn",
                f"line {node.lineno}: `{stem}` is already a table in the corpus. "
                f"Uploading under this name replaces it rather than adding.",
                table=name, group="contract"))
    return out


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="irw_validate.contract",
        description="Static contract checks on data/ conversion scripts.")
    ap.add_argument("paths", nargs="*", help="scripts to check (treated as added)")
    ap.add_argument("--added", action="append", default=[],
                    help="a file added by this PR: findings block")
    ap.add_argument("--modified", action="append", default=[],
                    help="a file this PR only edits: findings are reported, never fatal")
    ap.add_argument("--annotate", action="store_true",
                    help="emit GitHub Actions ::error/::warning annotations")
    args = ap.parse_args(argv)

    added = [pathlib.Path(p) for p in (args.added + args.paths)]
    modified = [pathlib.Path(p) for p in args.modified]
    if not added and not modified:
        print("nothing to check")
        return 0

    root = pathlib.Path(__file__).resolve().parent.parent
    corpus = _corpus_names(root)
    blocking = 0

    for group, paths, fatal in (("added", added, True), ("modified", modified, False)):
        for path in paths:
            if not path.exists():
                continue
            findings = check_script(path, corpus=corpus)
            if not findings:
                print(f"ok   {path}")
                continue
            for f in findings:
                level = f.severity if fatal else "warn"
                if fatal and f.severity == "error":
                    blocking += 1
                print(f"{level.upper():5s} {path}: {f.check} -- {f.message}")
                if args.annotate:
                    kind = "error" if (fatal and f.severity == "error") else "warning"
                    msg = f.message.replace("\n", " ")
                    print(f"::{kind} file={path}::{f.check}: {msg}")

    if blocking:
        print(f"\n{blocking} blocking finding(s) in files this PR adds. Files it only "
              f"edits are reported but never fail -- see irw_validate/contract.py.",
              file=sys.stderr)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
