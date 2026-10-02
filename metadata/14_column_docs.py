#!/usr/bin/env python3
"""Build metadata/column_docs.csv: what each column of each table is, and where that is written (#2763).

A user asked where the codebook for gilbert_meta_10 was, wanting to know what
`cluster_id` and `block_id` meant (#2755). The source deposit's codebook could
not have told them: it describes `school_grade` and `stratum`, the source's own
names, and the rename between the two lives only in our build scripts. This
file is the reconstruction the table pages render as a Codebook section, one
row per (table, column):

  defined_by     `standard` when datastandard.md's schema table defines the
                 column itself (id, treat, cluster_id, ...), `standard_family`
                 when it defines only the family (cov_*, trial_*, qmatrix*).
  basis          how the build script produced the column:
                   renamed    `cluster_id = teacher_name` -- source_column holds
                              the source's name for it
                   built      named in the code but not by a simple rename (a
                              pivot, a mutate, a recode), or built from its
                              prefix (`paste0("cov_", x)`): script_line points
                              at the first such line
                 blank when the script never names the column, or no script
                 was found, or the match was ambiguous. A column the code never
                 names is NOT taken to have kept its source name: a sample of
                 those (2026-10-02) was about half wrong -- names rewritten by a
                 helper, `.` turned into `_`, columns made in another file.
  documented     true when the standard defines the column or the script
                 renames it from a named source column. False is the honest
                 answer for everything else: the meaning is in the source's
                 codebook, and the page must not guess it from the name.

These rows are a best reconstruction, not the source's codebook, and the page
says so (#2763). The definition text is NOT copied here: the page joins it from
datastandard.md at render time, so this file cannot hold a stale copy.

Scripts are found the way the irw MCP server's get_processing_notes finds them
(Python-pkg src/irw/mcp.py `_match_scripts`): an exact stem, then
table_scripts.csv (stage 13), then a name prefix that must end at a separator.
Keep the three in step.

Only tables with a column list are covered: metadata.csv's `variables`. The
nominal, simsyn and comps catalogues carry none. No credentials, no network.

Run as stage 14 of run_pipeline.sh, after 13 (it reads table_scripts.csv).
Standalone:
    python3 metadata/14_column_docs.py [--repo DIR] [--out FILE]
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("script_index", HERE / "13_script_index.py")
script_index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script_index)

COMMENT_PREFIXES = script_index.COMMENT_PREFIXES
FIELDS = ["table", "column", "defined_by", "basis", "source_column",
          "script", "script_line", "match", "documented"]
# R values that look like identifiers but are not source columns.
NOT_A_COLUMN = {"TRUE", "FALSE", "NA", "NULL", "T", "F", "Inf", "NaN"}


# ------------------------------------------------------------------ standard

def parse_standard(text: str) -> Tuple[set, set]:
    """Exact names and family prefixes from datastandard.md's schema table.

    Same rules as the MCP's _parse_data_standard: a backticked name ending in
    `*`, or a numbered run (`qmatrix1`...`qmatrixN`), is a family.
    """
    exact, prefix = set(), set()
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        first = line.strip().strip("|").split("|")[0]
        for name in re.findall(r"`([^`]+)`", first):
            if name.endswith("*") or re.fullmatch(r"[A-Za-z_]+N", name):
                prefix.add(name[:-1])
            elif not re.fullmatch(r"[A-Za-z_]+1", name):
                exact.add(name)
    return exact, prefix


def defined_by(column: str, exact: set, prefix: set) -> str:
    if column in exact:
        return "standard"
    if any(column.startswith(p) for p in prefix):
        return "standard_family"
    return ""


# ------------------------------------------------------------------ scripts

def match_scripts(table: str, paths: List[str], index: Dict[str, List[str]]) -> Tuple[List[str], str]:
    """The MCP's _match_scripts, on local paths: exact, index, prefix, or none."""
    stem = script_index.stem
    wanted = table.casefold()
    stems: Dict[str, List[str]] = {}
    for p in paths:
        stems.setdefault(stem(p), []).append(p)
    if wanted in stems:
        found = sorted(stems[wanted])
        return found, "exact" if len(found) == 1 else "ambiguous"
    indexed = sorted(p for p in index.get(wanted, []) if p in set(paths))
    if indexed:
        return indexed, "index" if len(indexed) == 1 else "ambiguous"
    if not wanted.endswith("_nom"):
        stems = {s: kept for s, found in stems.items()
                 if (kept := [p for p in found if not p.startswith("data/nominal/")])}
    candidates = [s for s in stems if len(s) >= 8 and any(
        wanted.startswith(s + sep) or s.startswith(wanted + sep) for sep in ("_", "-", "."))]
    if candidates:
        found = sorted(p for s in candidates for p in stems[s])
        return found, "prefix" if len(candidates) == 1 else "ambiguous"
    return [], "none"


def read_index(path: Path) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    if path.exists():
        with path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                table = (row.get("table") or "").strip()
                scripts = [p for p in (row.get("scripts") or "").split("|") if p]
                if table and scripts:
                    index[table.casefold()] = scripts
    return index


def code_lines(text: str) -> List[Tuple[int, str]]:
    return [(n, line) for n, line in enumerate(text.splitlines(), start=1)
            if line.strip() and not line.lstrip().startswith(COMMENT_PREFIXES)]


def rename_source(column: str, path: str, line: str) -> Optional[str]:
    """The source name a line renames `column` from, or None.

    Only shapes that are unambiguous renames: R `col = src` inside select /
    rename / transmute (a bare identifier followed by `,` `)` or end of line,
    so `col = scale(x)` is not one); a pandas rename dict `"src": "col"`;
    Stata `rename src col`.
    """
    c = re.escape(column)
    suffix = path.rsplit(".", 1)[-1].lower()
    if suffix == "r":
        m = re.search(r"(?<![\w.$])`?" + c + r"`?\s*=\s*[`\"']?([A-Za-z.][\w.]*)[`\"']?\s*(?=[,)]|$)", line)
        if m and m.group(1) not in NOT_A_COLUMN:
            return m.group(1)
    elif suffix == "py":
        m = re.search(r"[\"']([^\"']+)[\"']\s*:\s*[\"']" + c + r"[\"']", line)
        if m:
            return m.group(1)
    elif suffix == "do":
        m = re.search(r"\b(?:rename|ren)\s+(\S+)\s+" + c + r"\b", line)
        if m and not m.group(1).startswith("("):
            return m.group(1)
        # Grouped: `ren (correct trial responsetime) (resp item rt)`.
        m = re.search(r"\b(?:rename|ren)\s*\(([^)]*)\)\s*\(([^)]*)\)", line)
        if m:
            olds, news = m.group(1).split(), m.group(2).split()
            if len(olds) == len(news) and column in news:
                return olds[news.index(column)]
    return None


def dynamic_prefix_line(column: str, scripts: Dict[str, str]) -> Optional[Tuple[str, int]]:
    """First line that builds names from the column's prefix as a string.

    `paste0("cov_", names)` or `f"cov_{c}"` never names `cov_gender`, so a
    column the code does not mention may still have been renamed. Such a
    column is `built` and points at that line.
    """
    if "_" not in column.strip("_"):
        return None
    prefix = column[: column.index("_", 1) + 1]
    literal = re.compile(r"""(?:f?["'`])""" + re.escape(prefix))
    for path, text in scripts.items():
        for n, line in code_lines(text):
            if literal.search(line):
                return path, n
    return None


def column_basis(column: str, scripts: Dict[str, str], match: str) -> Tuple[str, str, str, str]:
    """(basis, source_column, script, line) for one column."""
    if match in ("none", "ambiguous") or not scripts:
        return "", "", "", ""
    token = re.compile(r"(?<![\w.$])" + re.escape(column) + r"(?![\w])")
    first: Optional[Tuple[str, int]] = None
    for path, text in scripts.items():
        for n, line in code_lines(text):
            if not token.search(line):
                continue
            src = rename_source(column, path, line)
            if src and src != column:
                return "renamed", src, path, str(n)
            if first is None:
                first = (path, n)
    if first is not None:
        return "built", "", first[0], str(first[1])
    dynamic = dynamic_prefix_line(column, scripts)
    if dynamic is not None:
        return "built", "", dynamic[0], str(dynamic[1])
    return "", "", "", ""


# ------------------------------------------------------------------ build

def build(tables: Dict[str, List[str]], paths: List[str], texts: Dict[str, str],
          index: Dict[str, List[str]], exact: set, prefix: set) -> List[Dict[str, str]]:
    rows = []
    for table in sorted(tables, key=str.casefold):
        found, match = match_scripts(table, paths, index)
        scripts = {p: texts[p] for p in found if p in texts} if match != "ambiguous" else {}
        for column in tables[table]:
            d = defined_by(column, exact, prefix)
            basis, src, script, line = column_basis(column, scripts, match)
            rows.append({
                "table": table, "column": column, "defined_by": d,
                "basis": basis, "source_column": src if basis == "renamed" else "",
                "script": script, "script_line": line, "match": match,
                "documented": "true" if d == "standard" or basis == "renamed" else "false",
            })
    return rows


def catalogue_columns(path: Path) -> Dict[str, List[str]]:
    tables: Dict[str, List[str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            table = (row.get("table") or "").strip()
            cols = [c.strip() for c in (row.get("variables") or "").split("|") if c.strip()]
            if table and cols and cols != ["NA"]:
                tables[table] = cols
    return tables


def write_rows(rows: List[Dict[str, str]], out: Path) -> None:
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def coverage(rows: List[Dict[str, str]], fixed: set) -> str:
    def pct(sub):
        return f"{sum(r['documented'] == 'true' for r in sub)}/{len(sub)}"
    other = [r for r in rows if r["column"] not in fixed]
    tables = {r["table"] for r in rows}
    with_script = {r["table"] for r in rows if r["match"] in ("exact", "index", "prefix")}
    by_basis: Dict[str, int] = {}
    for r in other:
        key = r["basis"] or "(not traced)"
        by_basis[key] = by_basis.get(key, 0) + 1
    return (f"column_docs.csv: {len(rows)} columns in {len(tables)} tables "
            f"({len(with_script)} with a build script). Documented: {pct(rows)} overall, "
            f"{pct(other)} outside id/item/resp. Outside id/item/resp, by basis: "
            + ", ".join(f"{k} {v}" for k, v in sorted(by_basis.items())) + ".")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=HERE.parent)
    parser.add_argument("--out", type=Path, default=HERE / "column_docs.csv")
    args = parser.parse_args(argv)

    meta = args.repo / "metadata"
    exact, prefix = parse_standard((args.repo / "datastandard.md").read_text(encoding="utf-8"))
    tables = catalogue_columns(meta / "metadata.csv")
    paths = script_index.data_scripts(args.repo)
    texts = {p: (args.repo / p).read_text(encoding="utf-8", errors="replace") for p in paths}
    index = read_index(meta / "table_scripts.csv")
    rows = build(tables, paths, texts, index, exact, prefix)
    write_rows(rows, args.out)
    print(coverage(rows, {"id", "item", "resp"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
