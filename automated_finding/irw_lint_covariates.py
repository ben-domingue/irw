"""
irw_lint_covariates.py
======================
Covariate linter for finished IRW output tables.

This runs *after* a `data/<author>_<year>_<construct>.py` script has written
its CSV -- it does not convert anything and never rewrites a file. It answers
one question: **did this script handle the person-level covariates the way
1,200+ earlier scripts in `data/` handled theirs?**

The recurring failure it exists to catch is covariate *under*-extraction: a
demographic column that was silently dropped, or melted into `item`/`resp` as
though it were a scale item. Both produce a table that passes every structural
check in `irw_triage_updated.py` -- id/item/resp are all present and numeric --
while quietly losing the covariates.

The vocabulary is mined from the `data/` corpus itself (`--mine`), so it knows
the terms this project actually uses, including non-English source columns
(`Alter`, `Sexo`, `Sexe`, `性别`) and question-text columns
(`"12. What is your gender?"`). It is not a hand-typed list.

Usage
-----
    # lint one or more finished output tables
    python irw_lint_covariates.py irw_output/frikha_2023_motivation.csv
    python irw_lint_covariates.py irw_output/*.csv

    # also compare against the raw source file the script read, which is what
    # enables the "raw file had a covariate the output doesn't" check
    python irw_lint_covariates.py irw_output/hao_2025_anxiety.csv --raw raw/hao.xlsx

    # regenerate cov_vocabulary.json from ../data (run when new scripts land)
    python irw_lint_covariates.py --mine

Exit status is 1 if any `error`-severity finding was reported, else 0, so this
can gate a batch before upload:

    python irw_lint_covariates.py irw_output/*.csv || echo "fix before upload"

Provenance: the idea and the mining approach come from the covariate
vocabulary in AryanSudhirDev/automated-finding-v2 (`v2/knowledge/`,
`v2/stages/precoerce.py`), re-implemented here as a check on output rather
than as a step in an automatic converter.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"
VOCAB_PATH = HERE / "cov_vocabulary.json"

# Reserved IRW column names -- see datastandard.md. Never covariate candidates.
RESERVED = frozenset({
    "id", "item", "resp", "wave", "treat", "rt", "date", "rater",
    "item_family", "qmatrix",
})

# Terms that appear as `cov_<term>` in scripts but are Python/R *variable*
# names, not column names (`cov_cols`, `cov_map`, ...). Pair-based mining
# mostly avoids these; this is the backstop.
_NOT_A_TERM = frozenset({
    "cols", "names", "name", "map", "df", "rename", "present", "vars",
    "columns", "list", "dict", "col", "data", "keys", "values", "prefix",
})

# A short letter+digit label (`q12`, `AS3`) is far more likely an item than a
# covariate, even when the corpus once mined it as one.
_ITEM_NAME_RE = re.compile(r"^[a-z]{1,8}[_\- ]?\d{1,3}[a-z]?$", re.IGNORECASE)

# A mined term must look like a column name, not a stray token.
_TERM_OK_RE = re.compile(r"^[a-z][a-z0-9_]{1,60}$")

# Aliases seen exactly once are only trusted when they read as a real word --
# that is what lets a single-occurrence `Alter`/`Sexo`/`Idade`/`性别` in for
# free while keeping the corpus's opaque one-offs (`A`, `PID`, `D5`, `.`) out.
_ID_LIKE = frozenset({
    "pid", "sid", "uid", "subj", "subject", "respondent", "participant",
    "case", "record", "index", "no", "num", "number", "row",
})

# Leftovers from matching bare R symbols in a pipe (`cov_x = .`) and from
# generic Python locals. None of these is ever a real source column name.
_CODE_JUNK = frozenset({
    "df", "dfs", "raw", "out", "src", "idx", "tmp", "temp", "dat", "data",
    "val", "vals", "res", "obj", "win", "pos", "x", "y", "z", "d", "n",
    "i", "j", "k", "cols", "col", "names", "vec", "lst", "new", "old",
})

# `q1_1`, `v03`, `12_3`, `18.1` -- opaque codes far likelier to be items.
_CODE_LIKE_RE = re.compile(r"^[a-z]{0,4}\d{1,3}(?:[._]\d{1,3})*$")


def _alias_is_usable(alias: str, count: int) -> bool:
    """Should this mined name be trusted as a covariate lookup key?

    Applied to terms as well as aliases: both come out of the same regex
    sweep over 1,200 heterogeneous scripts, and both pick up junk.
    """
    key = normalize(alias)
    if not key or key in _ID_LIKE or key in _CODE_JUNK:
        return False
    if _CODE_LIKE_RE.match(key) or _ITEM_NAME_RE.match(key):
        return False
    # Non-ASCII source columns are short by nature (性别 = 2 chars).
    if any(ord(ch) > 127 for ch in key):
        return len(key) >= 2
    if len(key) < 4:
        # Three-letter abbreviations (ses, edu, bmi, gpa, dob) are real, but
        # only once the corpus has used them more than once.
        return len(key) == 3 and count >= 2
    return True


_NORMALIZE = re.compile(r"[\s_\-]+")
# Leading numbering/lettering on question-text columns: "12. ", "Q3) ", "a. "
_LEADING_PREFIX_RE = re.compile(r"^\s*(?:[Qq]?\d{1,3}|[A-Za-z])\s*[.):\-]\s*")
_PUNCT_TAIL_RE = re.compile(r"[?:;.,\s]+$")


def normalize(s: str) -> str:
    return _NORMALIZE.sub("_", str(s).strip().lower()).strip("_")


def strip_question_prefix(name: str) -> str:
    """`"11. What is your gender?"` -> `"what is your gender"`."""
    s = _LEADING_PREFIX_RE.sub("", str(name))
    return _PUNCT_TAIL_RE.sub("", s).strip()


# ---------------------------------------------------------------------------
# Mining -- extract (source column -> cov_term) pairs from data/ scripts
# ---------------------------------------------------------------------------

# Python: {"AGE": "cov_age"}
_PY_DICT = re.compile(r"""['"]([^'"]{1,80}?)['"]\s*:\s*['"]cov_([A-Za-z0-9_]+)['"]""")
# Python: df["cov_age"] = raw["A1"]   /   df['cov_x'] = pd.to_numeric(raw['Y']
_PY_ASSIGN = re.compile(
    r"""\[\s*['"]cov_([A-Za-z0-9_]+)['"]\s*\]\s*=[^=\n]*?\[\s*['"]([^'"]{1,80}?)['"]\s*\]"""
)
# R/tidyverse: rename(cov_age = age) / select(cov_gender=sex) / mutate(...)
_R_PAIR = re.compile(r"""\bcov_([A-Za-z0-9_]+)\s*=\s*(?:['"]([^'"]{1,80}?)['"]|([A-Za-z_.][A-Za-z0-9_.]*))""")
# R: final$cov_age <- final$age
_R_DOLLAR = re.compile(r"""\$cov_([A-Za-z0-9_]+)\s*<-\s*\w+\$([A-Za-z0-9_.]{1,80})""")
# Stata: rename age cov_age
_DO_RENAME = re.compile(r"""^\s*rename\s+(\S{1,80})\s+cov_([A-Za-z0-9_]+)""", re.MULTILINE)


def _pairs_from_text(text: str) -> list[tuple[str, str]]:
    """Return (source_column, cov_term) pairs found in one script's source."""
    pairs: list[tuple[str, str]] = []
    for m in _PY_DICT.finditer(text):
        pairs.append((m.group(1), m.group(2)))
    for m in _PY_ASSIGN.finditer(text):
        pairs.append((m.group(2), m.group(1)))
    for m in _R_PAIR.finditer(text):
        src = m.group(2) or m.group(3) or ""
        pairs.append((src, m.group(1)))
    for m in _R_DOLLAR.finditer(text):
        pairs.append((m.group(2), m.group(1)))
    for m in _DO_RENAME.finditer(text):
        pairs.append((m.group(1), m.group(2)))
    return pairs


def mine(data_dir: Path = DATA_DIR) -> dict:
    """Walk data/ and build {term: {count, aliases}} from human renames."""
    scripts = sorted(
        p for ext in ("*.py", "*.R", "*.r", "*.do") for p in data_dir.glob(ext)
    )
    counts: dict[str, int] = defaultdict(int)
    aliases: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for path in scripts:
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for src, term in _pairs_from_text(text):
            term = term.lower().strip("_")
            if not term or term in _NOT_A_TERM or not _TERM_OK_RE.match(term):
                continue
            counts[term] += 1
            src = src.strip()
            # A rename whose source *is* the target carries no alias
            # information, but still counts toward the term.
            if src and normalize(src) != f"cov_{term}":
                aliases[term][src] += 1
    terms = {
        term: {
            "count": counts[term],
            "aliases": dict(sorted(aliases.get(term, {}).items(),
                                   key=lambda kv: (-kv[1], kv[0]))[:80]),
        }
        for term in sorted(counts, key=lambda t: (-counts[t], t))
    }
    return {
        "generated": date.today().isoformat(),
        "scripts_scanned": len(scripts),
        "n_terms": len(terms),
        "terms": terms,
    }


# ---------------------------------------------------------------------------
# Vocabulary lookup
# ---------------------------------------------------------------------------

class Vocabulary:
    """Normalized alias -> canonical covariate term."""

    def __init__(self, raw: dict) -> None:
        self.raw = raw
        self.terms: dict[str, int] = {
            t: info.get("count", 0) for t, info in raw.get("terms", {}).items()
        }
        self.lookup: dict[str, str] = {}
        for term, info in raw.get("terms", {}).items():
            if _alias_is_usable(term, info.get("count", 0)):
                self._add(term, term)
            for alias, n in dict(info.get("aliases", {})).items():
                if _alias_is_usable(alias, n):
                    self._add(alias, term)

    def _add(self, alias: str, term: str) -> None:
        key = normalize(alias)
        if not key or key in RESERVED:
            return
        if _ITEM_NAME_RE.match(str(alias).strip()):
            return
        # First writer wins: terms are inserted in descending corpus frequency,
        # so a name shared by two terms resolves to the commoner one.
        self.lookup.setdefault(key, term)
        # Also index the question-text form, but re-run hygiene on it:
        # stripping "18." off "18.1" leaves a bare "1", which is a perfectly
        # ordinary item label and must never resolve to a covariate.
        stripped = normalize(strip_question_prefix(alias))
        if stripped and stripped != key and _alias_is_usable(stripped, 2):
            self.lookup.setdefault(stripped, term)

    def hit(self, name: str) -> str | None:
        """Canonical term for a column/item label, or None."""
        raw = str(name).strip()
        if not raw or _ITEM_NAME_RE.match(raw):
            return None
        full = normalize(raw)
        if full in RESERVED or full.startswith(("cov_", "itemcov_", "qmatrix")):
            return None
        if full in self.lookup:
            return self.lookup[full]
        stripped = normalize(strip_question_prefix(raw))
        if stripped in self.lookup:
            return self.lookup[stripped]
        # Question text: "what is your gender" -> gender. Only match whole
        # words, and only for the last/first word, to avoid "age" firing on
        # "language" or "average".
        words = [w for w in stripped.split("_") if w]
        for word in (words[-1:] + words[:1]) if words else ():
            if word in self.lookup:
                return self.lookup[word]
        return None


def load_vocabulary(path: Path = VOCAB_PATH) -> Vocabulary:
    if not path.exists():
        sys.exit(
            f"no vocabulary at {path}\n"
            f"build it first:  python {Path(__file__).name} --mine"
        )
    return Vocabulary(json.loads(path.read_text()))


# ---------------------------------------------------------------------------
# Loading tables
# ---------------------------------------------------------------------------

def load_any(path: Path) -> pd.DataFrame:
    """Read a table for linting. Reuses irw_triage_updated's reader for the
    stats formats so raw .sav/.dta sources can be compared too."""
    suffix = path.suffix.lower()
    if suffix in (".csv", ".tsv", ".txt"):
        # sep=None asks the python engine to sniff the delimiter, which is
        # what handles the semicolon-separated exports some sources publish.
        sep = "\t" if suffix == ".tsv" else None
        return pd.read_csv(path, sep=sep, engine="python")
    try:
        from irw_triage_updated import load_table
    except ImportError as exc:  # pragma: no cover - import-time environment issue
        raise SystemExit(f"cannot read {path.name}: {exc}") from exc
    return load_table(path.read_bytes(), filename=path.name)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

SEVERITY_ORDER = {"error": 0, "warn": 1, "info": 2}


def _finding(sev: str, code: str, message: str) -> dict:
    return {"severity": sev, "code": code, "message": message}


def lint_frame(df: pd.DataFrame, vocab: Vocabulary,
               raw: pd.DataFrame | None = None) -> list[dict]:
    findings: list[dict] = []
    cols = list(df.columns)
    normalized = {normalize(c) for c in cols}

    # 1. A covariate column that never got the cov_ prefix.
    for col in cols:
        term = vocab.hit(col)
        if term is not None:
            findings.append(_finding(
                "error", "unprefixed_covariate",
                f"column {col!r} looks like a covariate ({term}) but is not "
                f"prefixed -- rename to cov_{term}",
            ))

    # 2. A covariate melted into `item`, so its values sit in `resp`. This is
    #    the one that silently survives every structural check.
    if "item" in df.columns:
        item_hits: dict[str, str] = {}
        for label in df["item"].dropna().astype(str).unique():
            term = vocab.hit(label)
            if term is not None:
                item_hits[label] = term
        for label, term in sorted(item_hits.items()):
            findings.append(_finding(
                "error", "covariate_as_item",
                f"item {label!r} is a covariate ({term}), not a scale item -- "
                f"it belongs in a cov_{term} column, not in item/resp",
            ))

    # 3. A cov_ column whose suffix is an alias rather than the canonical term
    #    the rest of the corpus uses (cov_sexo -> cov_sex).
    for col in cols:
        low = normalize(col)
        if not low.startswith("cov_"):
            continue
        suffix = low[4:]
        if not suffix:
            continue
        term = vocab.lookup.get(suffix)
        if not term or term == suffix:
            continue
        # `cov_idade` is a name the corpus has itself used, so only say
        # anything when the canonical spelling is overwhelmingly more common.
        mine_n, theirs_n = vocab.terms.get(suffix, 0), vocab.terms.get(term, 0)
        if theirs_n >= 20 and theirs_n >= 10 * max(mine_n, 1):
            findings.append(_finding(
                "info", "nonstandard_cov_name",
                f"{col!r}: the corpus spells this covariate cov_{term} "
                f"({theirs_n} scripts vs {mine_n} for cov_{suffix})",
            ))

    # 4. A covariate is person-level by definition -- it must not vary across
    #    the items of one person. In a longitudinal table it may legitimately
    #    change between waves (age does), so the grouping key includes `wave`
    #    when there is one; what is still flagged is variation *within* a
    #    single person-wave, which no person-level field can have.
    if "id" in df.columns:
        key = ["id", "wave"] if "wave" in df.columns else ["id"]
        unit = "person-wave" if len(key) == 2 else "person"
        grouped = df.groupby(key, dropna=True)
        for col in cols:
            if not normalize(col).startswith("cov_"):
                continue
            nunique = grouped[col].nunique(dropna=True)
            varying = int((nunique > 1).sum())
            if varying:
                findings.append(_finding(
                    "warn", "covariate_varies_within_id",
                    f"{col!r} takes >1 value for {varying} of {len(nunique)} "
                    f"{unit} groups -- a cov_ column is person-level "
                    f"(item-level? use itemcov_; timepoint-level? use wave)",
                ))

    # 5. Against the raw source: a covariate the source published and the
    #    output dropped entirely.
    if raw is not None:
        have = {normalize(c)[4:] for c in cols if normalize(c).startswith("cov_")}
        have |= {vocab.lookup.get(t, t) for t in have}
        for col in raw.columns:
            term = vocab.hit(col)
            if term is None or term in have:
                continue
            if normalize(col) in normalized:
                continue  # present in output under some other role
            findings.append(_finding(
                "warn", "missed_covariate",
                f"raw column {col!r} is a covariate ({term}) that does not "
                f"appear in the output -- add it as cov_{term} or note why not",
            ))

    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["code"], f["message"]))
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Lint finished IRW output tables for covariate handling.",
    )
    ap.add_argument("tables", nargs="*", type=Path,
                    help="finished IRW output table(s) to lint")
    ap.add_argument("--raw", type=Path, default=None,
                    help="raw source file the script read, to check for "
                         "covariates the output dropped (single table only)")
    ap.add_argument("--mine", action="store_true",
                    help=f"regenerate {VOCAB_PATH.name} from {DATA_DIR}/ and exit")
    ap.add_argument("--vocab", type=Path, default=VOCAB_PATH,
                    help="vocabulary JSON to use (default: %(default)s)")
    ap.add_argument("--json", action="store_true",
                    help="emit findings as JSON instead of text")
    args = ap.parse_args(argv)

    if args.mine:
        if not DATA_DIR.is_dir():
            sys.exit(f"no data/ directory at {DATA_DIR}")
        built = mine()
        args.vocab.write_text(json.dumps(built, indent=1, ensure_ascii=False,
                                         sort_keys=False) + "\n")
        top = list(built["terms"])[:12]
        print(f"scanned {built['scripts_scanned']} scripts in {DATA_DIR}")
        print(f"wrote {args.vocab} -- {built['n_terms']} covariate terms")
        print("most common: " + ", ".join(top))
        return 0

    if not args.tables:
        ap.error("give at least one table to lint, or --mine")
    if args.raw is not None and len(args.tables) > 1:
        ap.error("--raw applies to a single output table")

    vocab = load_vocabulary(args.vocab)
    raw_df = load_any(args.raw) if args.raw else None

    report: dict[str, list[dict]] = {}
    for table in args.tables:
        if not table.exists():
            print(f"{table}: not found", file=sys.stderr)
            report[str(table)] = [_finding("error", "missing_file", "not found")]
            continue
        report[str(table)] = lint_frame(load_any(table), vocab, raw_df)

    if args.json:
        print(json.dumps(report, indent=1, ensure_ascii=False))
    else:
        for table, findings in report.items():
            name = Path(table).name
            if not findings:
                print(f"{name}: clean")
                continue
            print(f"{name}:")
            for f in findings:
                print(f"  [{f['severity']:5}] {f['code']}: {f['message']}")

    n_err = sum(1 for fs in report.values() for f in fs if f["severity"] == "error")
    if not args.json:
        n_warn = sum(1 for fs in report.values() for f in fs if f["severity"] == "warn")
        print(f"\n{len(report)} table(s), {n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
