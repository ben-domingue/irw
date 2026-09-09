#!/usr/bin/env python3
"""Check that the three Redivis config files declare the same datasets (#1733).

The set of Redivis datasets IRW reads is declared once per language:

  | file                          | repo         | carries                |
  |-------------------------------|--------------|------------------------|
  | metadata/redivis_config.R     | irw          | dataset names only     |
  | R/redivis-config.R            | Rpkg         | names + version hashes |
  | src/irw/config.py             | Python-pkg   | names + version hashes |

Each of the three describes itself as a single source of truth, and nothing
compared them. They had already drifted: Python-pkg carried no reference to
irw_nominal at all, so the nominal source was reachable from R and not from
Python, and that went unnoticed until someone wrote ARCHITECTURE.md by hand.

De-duplicating them is not on the table -- three languages, three runtimes, no
shared build, and any scheme that "removes" the duplication just generates the
copies, which can still go ungenerated. Publishing the registry as a Redivis
table was considered and rejected: it puts a network round-trip and a bootstrap
dependency in every client's cold start, so a client that cannot reach Redivis
could no longer learn its own configuration. So: detect the drift instead.

WHAT IS COMPARED, AND WHAT IS NOT
Dataset *names*, with any `:refid` version hash stripped. The three files
legitimately differ in content -- redivis_config.R carries no hashes by design
-- so byte or line equality would false-alarm on every run. Whether the two
packages pin the same version hash is a real but separate question, and not
always a defect: one package may pin an older dataset version deliberately.

Order is compared for the sharded sources (`core`, `text`). It is not
decoration: all three files declare shards oldest-to-newest and every client
searches them newest-first so a table resolves to its most recent copy. A file
that listed them in a different order would resolve some tables to a stale copy
while every name still matched.

PARSE, DO NOT IMPORT
Nothing here imports irw, sources R, or touches the network, so it runs on any
runner in about a second. The R files are read with regexes and the Python file
with `ast`; a config file is a literal declaration in all three, which is what
makes that safe.

Usage:
    python metadata/check_config_parity.py                  # sibling checkouts
    python metadata/check_config_parity.py --rpkg P --pypkg P

Run it against checkouts that are up to date. It reads the working tree it is
pointed at, so a sibling repo sitting behind its remote reports drift that is
not actually on main -- which is exactly how the `nom` gap read as still open
after it had been fixed and released. `git -C ../Python-pkg pull` first, or
trust the CI run, which always checks out both packages fresh.

Exits 0 when the three agree, 1 when they do not, 2 when a file could not be
found or parsed (which is itself a failure -- see _require below).
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

# Sources that are shards -- ordered lists, oldest to newest. Everything else
# is a single dataset. Order is compared for these and only these.
SHARDED = ("core", "text")

# A floor on what a healthy parse returns, per source. The failure this guards
# against is a parser that silently matches nothing -- if a file is reformatted
# past our regexes and every extraction comes back empty, the sets all compare
# equal and the check passes green while checking nothing at all. These are
# deliberately floors, not exact counts: adding a seventh warehouse is a normal
# Tuesday and must not have to edit this file.
MIN_DATASETS = {"core": 6, "text": 2, "meta": 1, "sim": 1, "comp": 1, "nom": 1}


class ParseError(RuntimeError):
    """A config file could not be read or did not contain what we expected."""


def _strip_hash(ref: str) -> str:
    """`item_response_warehouse:as2e` -> `item_response_warehouse`."""
    return ref.split(":", 1)[0].strip()


def _require(name: str, source: str, values: Sequence[str]) -> List[str]:
    """Fail loudly when an extraction comes back implausibly short."""
    floor = MIN_DATASETS.get(source, 1)
    if len(values) < floor:
        raise ParseError(
            f"{name}: extracted {len(values)} dataset(s) for source '{source}' "
            f"but expected at least {floor}. The file's shape has probably "
            f"changed; fix the parser in metadata/check_config_parity.py "
            f"rather than lowering this floor."
        )
    return [_strip_hash(v) for v in values]


# --------------------------------------------------------------------------
# R parsing
#
# Both R files declare their datasets as literal c(...) / list(...) calls, so
# the extraction is: find the assignment, take the balanced parenthetical that
# follows it, and pull the quoted strings out of that. Balancing the parens
# rather than reading to the next blank line is what makes the nested
# list(list(...), list(...)) in Rpkg work.
# --------------------------------------------------------------------------

def _balanced_block(text: str, start: int) -> str:
    """Return the parenthetical beginning at the first `(` at or after start."""
    open_at = text.index("(", start)
    depth = 0
    for i in range(open_at, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[open_at : i + 1]
    raise ParseError("unbalanced parentheses")


def _r_assignment(text: str, var: str) -> str:
    """The right-hand side of `var <- c(...)` or `var <- list(...)`."""
    m = re.search(rf"^\s*{re.escape(var)}\s*<-\s*", text, re.MULTILINE)
    if m is None:
        raise ParseError(f"no assignment to `{var}`")
    return _balanced_block(text, m.end())


def _quoted(block: str) -> List[str]:
    """Every double-quoted string in a block, in order."""
    return re.findall(r'"([^"]*)"', block)


def _r_datasets(block: str) -> List[str]:
    """Dataset names from a block of Rpkg-style `dataset = "name:hash"` specs.

    Reads the `dataset =` values only. The `user =` values in the same block
    are the Redivis owner, not a dataset, and would otherwise be picked up as
    six copies of "datapages".
    """
    return re.findall(r'dataset\s*=\s*"([^"]*)"', block)


def parse_pipeline_config(path: Path) -> Dict[str, List[str]]:
    """metadata/redivis_config.R -- bare names, no version hashes."""
    text = path.read_text()
    out: Dict[str, List[str]] = {}

    out["core"] = _require(
        path.name, "core", _quoted(_r_assignment(text, "IRW_CORE_DATASETS"))
    )
    out["text"] = _require(
        path.name, "text", _quoted(_r_assignment(text, "IRW_TEXT_DATASETS"))
    )

    # IRW_AUX_DATASETS is a *named* vector -- c(meta = "irw_meta", ...) -- so
    # the key is the source name the irw package uses and the value is the
    # dataset. Item text is deliberately absent from it (it is a shard list,
    # handled above); anything else that appears here must be matched.
    aux_block = _r_assignment(text, "IRW_AUX_DATASETS")
    for key, value in re.findall(r'(\w+)\s*=\s*"([^"]*)"', aux_block):
        out[key] = _require(path.name, key, [value])

    return out


def parse_rpkg_config(path: Path) -> Dict[str, List[str]]:
    """Rpkg/R/redivis-config.R -- names with version hashes."""
    text = path.read_text()
    out: Dict[str, List[str]] = {}

    # .irw_datasource_specs is one nested list per source keyed by source name.
    # Split the outer block on the `key = list(` headers so each source's
    # datasets stay with their own key.
    specs = _r_assignment(text, ".irw_datasource_specs")
    keys = list(re.finditer(r"(\w+)\s*=\s*list\(", specs))
    if not keys:
        raise ParseError(f"{path.name}: no sources found in .irw_datasource_specs")
    for i, m in enumerate(keys):
        end = keys[i + 1].start() if i + 1 < len(keys) else len(specs)
        key = m.group(1)
        out[key] = _require(path.name, key, _r_datasets(specs[m.end() : end]))

    out["meta"] = _require(
        path.name, "meta", _r_datasets(_r_assignment(text, ".irw_meta_spec"))
    )
    out["text"] = _require(
        path.name, "text", _r_datasets(_r_assignment(text, ".irw_itemtext_specs"))
    )
    return out


# --------------------------------------------------------------------------
# Python parsing
#
# config.py is literal module-level assignments, so `ast` reads it exactly and
# without importing it -- importing would pull in the redivis client and its
# dependencies, which a config check has no business requiring.
# --------------------------------------------------------------------------

# Module-level name in config.py -> the source key it stands for.
PY_NAMES = {
    "MAIN_REFS": "core",
    "ITEMTEXT_REFS": "text",
    "META_REF": "meta",
    "SIM_REF": "sim",
    "COMP_REF": "comp",
    "NOM_REF": "nom",
}


def parse_python_config(path: Path) -> Dict[str, List[str]]:
    """Python-pkg/src/irw/config.py -- names with version hashes.

    Each value is either a (user, ref) pair or a tuple of them; both shapes
    reduce to a list of refs the same way.
    """
    tree = ast.parse(path.read_text())

    literals: Dict[str, object] = {}
    for node in tree.body:
        # Plain `X = ...` is Assign; the annotated `X: ClassVar[...] = ...`
        # this file uses throughout is AnnAssign. Both appear here.
        if isinstance(node, ast.AnnAssign):
            targets, value = [node.target], node.value
        elif isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        else:
            continue
        if value is None:
            continue
        for t in targets:
            if isinstance(t, ast.Name) and t.id in PY_NAMES:
                try:
                    literals[t.id] = ast.literal_eval(value)
                except ValueError as e:
                    raise ParseError(f"{path.name}: {t.id} is not a literal ({e})")

    out: Dict[str, List[str]] = {}
    for name, source in PY_NAMES.items():
        if name not in literals:
            # A missing name is the exact defect this check exists to catch --
            # NOM_REF was absent here for months -- so it is reported as a
            # divergence below, not raised as a parse failure.
            continue
        value = literals[name]
        if value and isinstance(value[0], (tuple, list)):
            refs = [ref for _user, ref in value]   # tuple of (user, ref)
        else:
            refs = [value[1]]                      # a single (user, ref)
        out[source] = _require(path.name, source, refs)
    return out


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

def compare(configs: Dict[str, Dict[str, List[str]]]) -> List[str]:
    """Return one problem line per divergence; empty when the three agree."""
    problems: List[str] = []
    files = list(configs)
    all_sources = sorted({s for c in configs.values() for s in c})

    for source in all_sources:
        present = {f: configs[f].get(source) for f in files}

        missing = [f for f, v in present.items() if v is None]
        if missing:
            has = [f for f, v in present.items() if v is not None]
            names = ", ".join(sorted({n for f in has for n in present[f]}))
            problems.append(
                f"source '{source}' ({names}) is declared in "
                f"{', '.join(has)} but MISSING from {', '.join(missing)}"
            )
            continue

        if source in SHARDED:
            # Ordered comparison: shard order decides which copy of a table wins.
            if len({tuple(v) for v in present.values()}) > 1:
                detail = "; ".join(f"{f}={present[f]}" for f in files)
                problems.append(
                    f"source '{source}' shards differ in membership or ORDER "
                    f"(all three declare oldest-to-newest): {detail}"
                )
        else:
            if len({tuple(sorted(v)) for v in present.values()}) > 1:
                detail = "; ".join(f"{f}={present[f]}" for f in files)
                problems.append(f"source '{source}' differs: {detail}")

    return problems


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    here = Path(__file__).resolve().parent          # src/metadata
    siblings = here.parent.parent                   # the projects/irw checkout
    ap.add_argument(
        "--pipeline", type=Path, default=here / "redivis_config.R",
        help="path to metadata/redivis_config.R",
    )
    ap.add_argument(
        "--rpkg", type=Path, default=siblings / "Rpkg" / "R" / "redivis-config.R",
        help="path to Rpkg's R/redivis-config.R",
    )
    ap.add_argument(
        "--pypkg", type=Path,
        default=siblings / "Python-pkg" / "src" / "irw" / "config.py",
        help="path to Python-pkg's src/irw/config.py",
    )
    args = ap.parse_args(argv)

    wanted: List[Tuple[str, Path, object]] = [
        ("irw/metadata/redivis_config.R", args.pipeline, parse_pipeline_config),
        ("Rpkg/R/redivis-config.R", args.rpkg, parse_rpkg_config),
        ("Python-pkg/src/irw/config.py", args.pypkg, parse_python_config),
    ]

    configs: Dict[str, Dict[str, List[str]]] = {}
    for label, path, parser in wanted:
        if not path.exists():
            print(
                f"ERROR: {label} not found at {path}\n"
                f"       Pass --rpkg/--pypkg, or check the two package repos "
                f"out as siblings of this one.",
                file=sys.stderr,
            )
            return 2
        try:
            configs[label] = parser(path)
        except ParseError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

    problems = compare(configs)
    if problems:
        print("Redivis config files DISAGREE (see irw#1733):\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(
            "\nAdding or moving a dataset means editing all three files:\n"
            "  irw          metadata/redivis_config.R\n"
            "  Rpkg         R/redivis-config.R\n"
            "  Python-pkg   src/irw/config.py\n"
            "\n"
            "Land the two package pull requests BEFORE the irw one: this reads\n"
            "Rpkg and Python-pkg at their default branch, so an irw change that\n"
            "arrives first is a real disagreement and stays red until they land.\n"
            "\n"
            'Runbook: Rpkg/inst/developer/warehouses.md, "Adding a warehouse\n'
            'everywhere else". Overview: ARCHITECTURE.md section 2.',
            file=sys.stderr,
        )
        return 1

    for label, cfg in configs.items():
        summary = ", ".join(f"{k}={len(v)}" for k, v in sorted(cfg.items()))
        print(f"ok  {label}: {summary}")
    print("\nAll three Redivis config files declare the same datasets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
