#!/usr/bin/env python3
"""Stage 2 of the covariate_labels generator (irw#1775): harvest logs ->
``metadata/covariate_labels.csv`` (the irw_meta table) and
``metadata/covariate_labels/coverage.csv`` (the record of every pairing it
considered, and why each was kept, withheld or left out).

``covariate_labels.csv`` has one row per table x covariate x code:

    table      IRW table name (live: present in metadata/metadata.csv)
    covariate  the shipped cov_* column
    code       the value as it appears in the shipped column, as text ("1", "-9", "2.5")
    label      the source file's own value label for that code, verbatim
               (only leading/trailing whitespace trimmed), or WITHHELD_LABEL
               for a covariate whose codes name institutions

Rules (all ruled on #1775, 2026-10-01):
* **Verbatim.** A label is the source's wording (hombre/mujer, 1 = "female"
  in one table and 1 = "male" in another). Nothing is harmonised here.
* **Only what ships.** A row exists only for a code observed in the shipped
  column, and a table x covariate pair is kept only if
  (a) the shipped column is numeric codes, not label strings;
  (b) at least half its distinct codes carry a source label (coverage.csv
      lists any unlabelled codes); and
  (c) the shipped codes are the source's codes, not a recode: for every code,
      the number of distinct ids carrying it in the shipped table is at most
      the number of source rows carrying it. A 1/2 swap, a 0/1 recode or a
      collapse fails this and the pair is left out (reason in coverage.csv).
* **Institution names are withheld.** A pair listed as ``withhold`` in
  ``institutions.csv`` gets one row per code with ``label`` =
  WITHHELD_LABEL instead of the names. Any other pair that *looks* like an
  institution list (name or labels; see ``institution_flag``) and is not
  reviewed in ``institutions.csv`` is withheld too, and reported, until
  someone adds a ``publish`` or ``withhold`` line for it.
* **Live tables only**: tables not in metadata/metadata.csv are skipped.

    python3 metadata/covariate_labels/build.py               # logs from ~/.cache/irw/covariate_labels/logs
    python3 metadata/covariate_labels/build.py --logs DIR
"""
import argparse
import csv
import fnmatch
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_LOGS = Path.home() / ".cache" / "irw" / "covariate_labels" / "logs"
COLUMNS = ["table", "covariate", "code", "label"]
WITHHELD_LABEL = "[institution name withheld]"
MIN_COVERAGE = 0.5

MISSING_RX = re.compile(
    r"^(missing|no answer|n/?a|na|refused|don'?t know|sin respuesta|sysmis|not asked|-?9+)$", re.I)
# Covariate names that usually hold one institution per code.
INSTITUTION_NAME_RX = re.compile(
    r"school|universit|college|institut|hospital|clinic|campus|centre|center|compan|employer|"
    r"organi[sz]ation|firm|facility|kindergarten|classroom|^cov_class$|^cov_site$|^cov_ward$", re.I)
# Words that, inside a label, suggest the label names one institution.
INSTITUTION_LABEL_RX = re.compile(
    r"\b(universit\w*|universidad|college|hospital|klinik|clinic|CEIP|CPR|IES|"
    r"colegio|escuela|liceo|lycée|gymnasium|school|schule|institute|instituto)\b|大学|学院|医院|学校", re.I)


def norm(v):
    s = str(v).strip()
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return s
    except (ValueError, OverflowError):
        return s


def is_num(vals):
    try:
        [float(v) for v in vals]
        return True
    except ValueError:
        return False


def code_key(c):
    try:
        return (0, float(c), "")
    except ValueError:
        return (1, 0.0, c)


def meaningful(labels):
    """Labels that say more than the code itself."""
    return {k: str(v).strip() for k, v in labels.items()
            if str(v).strip() not in ("", k) and norm(v) != k}


def read_live(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["table"] for r in csv.DictReader(f)}


def read_institutions(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def institution_decision(table, cov, rules):
    for r in rules:
        if fnmatch.fnmatchcase(table, r["table_pattern"]) and r["covariate"] == cov:
            return r["decision"]
    return None


def institution_flag(cov, labels):
    """True when a pair looks like a list of named institutions."""
    if INSTITUTION_NAME_RX.search(cov):
        return True
    hits = sum(1 for v in labels.values() if INSTITUTION_LABEL_RX.search(v))
    # several labels each naming an institution; one "University degree" in an
    # education scale is not that
    return hits >= 3 and hits >= len(labels) / 2


def source_links(src, cov):
    """Source column names the script ties to `cov`, and quoted tokens on lines mentioning it."""
    q = r"[\"']"
    adj = set()
    for rx in (q + r"([^\"']+)" + q + r"\s*:\s*" + q + re.escape(cov) + q,
               q + re.escape(cov) + q + r"\s*:\s*" + q + r"([^\"']+)" + q,
               re.escape(cov) + r"\s*=\s*[\w.]*\[?" + q + r"([^\"']+)" + q,
               q + re.escape(cov) + q + r"\]\s*=\s*[^\n]*?\[" + q + r"([^\"']+)" + q,
               r"\(\s*" + q + re.escape(cov) + q + r"\s*,\s*" + q + r"([^\"']+)" + q + r"\s*[,)]",
               r"\(\s*" + q + r"([^\"']+)" + q + r"\s*,\s*" + q + re.escape(cov) + q + r"\s*[,)]"):
        adj |= set(re.findall(rx, src))
    toks = set()
    for ln in src.splitlines():
        if cov in ln:
            toks |= set(re.findall(r"[\"']([^\"']+)[\"']", ln))
    return adj, toks


def load_log(path):
    reads, writes = [], {}
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("ev") == "read":
            reads.append(r)
        elif r.get("ev") == "write" and r.get("has_item") and str(r["path"]).endswith(".csv"):
            writes[Path(r["path"]).name[:-4]] = r  # last write of a table wins
    return reads, writes


def source_columns(reads):
    """col -> (labels, summed counts over every read carrying that column)."""
    lab, cnt = {}, {}
    for r in reads:
        for col, lv in r.get("value_labels", {}).items():
            m = meaningful({norm(k): v for k, v in lv.items()})
            if not m:
                continue
            lab.setdefault(col, m)
            for k, n in (r.get("counts", {}).get(col) or {}).items():
                cnt.setdefault(col, {})
                cnt[col][k] = cnt[col].get(k, 0) + n
    return lab, cnt


def column_presence(reads):
    """col -> list of the meaningful labels each read carrying it had ({} = none).
    Reads logged without a column list (older hook) are returned as None."""
    pres = {}
    for r in reads:
        if "columns" not in r:
            return None
        lv = r.get("value_labels", {})
        for col in r["columns"]:
            pres.setdefault(col, []).append(meaningful({norm(k): v for k, v in (lv.get(col) or {}).items()}))
    return pres


def consistent_source(cov, col, lab, pres, src):
    """Empty string if every source column the script feeds into `cov` carries
    the same labels as `col` in every file read; else the reason it does not.
    Several files (one per study or wave) can feed one covariate, and a label
    set taken from one of them says nothing about the others."""
    if pres is None:
        return "harvest log predates the column list; re-run harvest.py --force for this script"
    adj, _ = source_links(src, cov)
    for name in {col} | adj:
        for got in pres.get(name, []):
            if got != lab[col]:
                if name == col:
                    return f"{col} is unlabelled or labelled differently in another file the script read"
                return f"the script also feeds {name} into {cov}, and it is not labelled like {col}"
    return ""


def pick_source(cov, vals, lab, src):
    """The labelled source column behind `cov`, or (None, why)."""
    adj, toks = source_links(src, cov)
    cands = []
    for col, m in lab.items():
        hit = [v for v in vals if v in m]
        if not hit:
            continue
        strength = 3 if col in adj else 2 if col.lower() == cov[4:].lower() else 1 if col in toks else 0
        frac = len(hit) / max(len(vals), 1)
        if frac < MIN_COVERAGE and strength < 3:
            continue
        cands.append((strength, frac, col))
    best = max((c[0] for c in cands), default=0)
    if adj and best < 3:
        return None, "script maps it to an unlabelled source column"
    named = [c for c in cands if c[0] == best and best > 0]
    if best == 3 and len(named) > 1:
        named = [max(named, key=lambda c: c[1])]
    if len(named) == 1:
        return named[0][2], ""
    if len(named) > 1:
        return None, "ambiguous source column: " + ",".join(sorted(c[2] for c in named)[:5])
    if len(cands) == 1 and len(vals) <= 20:
        return cands[0][2], ""
    if cands:
        return None, "ambiguous source column: " + ",".join(sorted(c[2] for c in cands)[:5])
    return None, "no labelled source column"


def assess(cov, info, labels, src_counts):
    """Decide one table x covariate pair. Returns (status, reason, unlabelled codes)."""
    vals = info.get("values")
    if vals is None:
        return "excluded", f"{info.get('n_unique')} distinct values: not a coded categorical", []
    substantive = {k: v for k, v in labels.items() if not MISSING_RX.match(v)}
    if not substantive:
        return "excluded", "source labels mark missing values only", []
    unlabelled = [v for v in vals if v not in labels]
    cov_frac = (len(vals) - len(unlabelled)) / max(len(vals), 1)
    if cov_frac < MIN_COVERAGE:
        return "excluded", f"only {cov_frac:.0%} of shipped codes are labelled", unlabelled
    shipped = info.get("counts") or {}
    if info.get("count_basis") != "ids":
        return "excluded", "shipped table has no id column to check the codes against", unlabelled
    if not src_counts:
        return "excluded", "no source counts to check the codes against", unlabelled
    over = [k for k, n in shipped.items() if n > src_counts.get(k, 0)]
    if over:
        return ("excluded", "shipped counts exceed source counts for code(s) " + ",".join(sorted(over, key=code_key))
                + ": the script recoded this column", unlabelled)
    return "included", "", unlabelled


def build(logs, live, rules, script_dir):
    rows, record, flagged = [], [], []
    for log in sorted(logs.glob("*.jsonl")):
        b = log.stem
        script = script_dir / f"{b}.py"
        if not script.exists():
            continue
        src = script.read_text(errors="replace")
        reads, writes = load_log(log)
        lab, cnt = source_columns(reads)
        pres = column_presence(reads)
        if not lab:
            continue
        for table, w in sorted(writes.items()):
            if table not in live:
                continue
            for cov, info in sorted(w["covs"].items()):
                vals = info.get("values")
                if vals is not None and (not vals or not is_num(vals)):
                    continue  # label strings or text ship already
                col, why = pick_source(cov, vals or [], lab, src) if vals is not None else (None, "")
                if col is None:
                    if why.startswith("ambiguous"):
                        record.append(dict(table=table, covariate=cov, script=f"data/{b}.py", source_column="",
                                           status="excluded", reason=why, n_codes=len(vals or []),
                                           n_labelled=0, unlabelled_codes=""))
                    continue
                labels = lab[col]
                status, reason, unl = assess(cov, info, labels, cnt.get(col))
                if status == "included":
                    why = consistent_source(cov, col, lab, pres, src)
                    if why:
                        status, reason = "excluded", why
                shipped = [v for v in vals if v in labels]
                if status == "included":
                    decision = institution_decision(table, cov, rules)
                    if decision is None and institution_flag(cov, {k: labels[k] for k in shipped}):
                        decision = "withhold"
                        reason = "looks like named institutions; not reviewed in institutions.csv, withheld until it is"
                        flagged.append((table, cov))
                    if decision == "withhold":
                        status = "withheld"
                        reason = reason or "institution names withheld (institutions.csv)"
                    for k in sorted(shipped, key=code_key):
                        rows.append(dict(table=table, covariate=cov, code=k,
                                         label=WITHHELD_LABEL if status == "withheld" else labels[k]))
                record.append(dict(table=table, covariate=cov, script=f"data/{b}.py", source_column=col,
                                   status=status, reason=reason, n_codes=len(vals),
                                   n_labelled=len(shipped), unlabelled_codes="|".join(sorted(unl, key=code_key))))
    rows.sort(key=lambda r: (r["table"], r["covariate"], code_key(r["code"])))
    record.sort(key=lambda r: (r["table"], r["covariate"]))
    return rows, record, flagged


def write_csv(path, rows, cols):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", type=Path, default=DEFAULT_LOGS)
    ap.add_argument("--out", type=Path, default=REPO / "metadata" / "covariate_labels.csv")
    ap.add_argument("--coverage", type=Path, default=HERE / "coverage.csv")
    a = ap.parse_args(argv)
    live = read_live(REPO / "metadata" / "metadata.csv")
    rules = read_institutions(HERE / "institutions.csv")
    rows, record, flagged = build(a.logs, live, rules, REPO / "data")
    write_csv(a.out, rows, COLUMNS)
    write_csv(a.coverage, record, ["table", "covariate", "script", "source_column", "status",
                                   "reason", "n_codes", "n_labelled", "unlabelled_codes"])
    pairs = {(r["table"], r["covariate"]) for r in rows}
    print(f"{len(rows)} rows, {len({t for t, _ in pairs})} tables, {len(pairs)} table x covariate pairs "
          f"-> {a.out}")
    for t, c in sorted(set(flagged)):
        print(f"REVIEW: {t} {c} looks like named institutions; withheld. Add a line to institutions.csv.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
