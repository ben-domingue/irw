"""Class detectors for the #2401 audit, run against the LIVE corpus.

    python3 -m irw_validate.live_detectors TABLE [TABLE ...] -o out.jsonl
    python3 -m irw_validate.live_detectors --all -o out.jsonl --resume --workers 6
    python3 -m irw_validate.live_detectors --flag out.jsonl -o flags.csv

The random-30 draw for #2401 (audit/2401/random30/RESULTS.md) found wrong values
in roughly one table in six -- too many to review table by table, but nearly all
of them in a handful of *classes* a query can see. This module measures those
classes, so the audit rules once per class instead of once per table.

Two steps, kept apart on purpose:

1. **measure** -- a few aggregate queries per table, stored raw as one JSON line
   per table. Aggregates only: the export allowance (200GB/30d against a
   181.8GB corpus) never enters into it. Slow, so it resumes.
2. **flag** -- pure Python over the stored measurements. Thresholds live here,
   so tuning a rule is a re-run of seconds, never another pass over Redivis.

Not measured here because it is already swept corpus-wide: the literal "NA"
string in `resp` (results/resp_string_na_2026-09-07.csv, #2030/#2048).
Not a defect under datastandard.md: reverse-keyed items left unreversed.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import re
import os
import pathlib
import statistics
import sys
import threading

# Codes that mean "missing" in the survey software IRW's sources come from.
SENTINELS = (-999, -99, -98, -97, -96, -9, -8, -7, 97, 98, 99, 888, 777, 999, 9999)
_SENT_SQL = ",".join(str(s) for s in SENTINELS)
PLACEHOLDER_IDS = ("0", "-1", "99", "999", "9999", "-99", "-999", "NA", "nan", "")
HIST_MAX_DISTINCT = 60      # item x value histogram only when resp is this discrete
HIST_MAX_ITEMS = 3000
COV_CHUNK = 25

FLAG_FIELDS = ["table", "flag", "severity", "n_items", "n_rows", "n_ids", "detail"]


# ---------------------------------------------------------------- measure --

def _q(redivis, sql: str) -> list[dict]:
    return redivis.query(sql).to_arrow_table(progress=False).to_pylist()


def _shape_sql(ref):
    return f"""
SELECT COUNT(*) n_rows, COUNT(DISTINCT `id`) n_ids, COUNT(DISTINCT `item`) n_items,
 COUNT(DISTINCT CAST(`resp` AS STRING)) n_resp_distinct,
 COUNTIF(`resp` IS NOT NULL AND SAFE_CAST(CAST(`resp` AS STRING) AS FLOAT64) IS NULL) n_resp_nonnumeric
FROM `{ref}`"""


def _hist_sql(ref):
    return f"""
SELECT CAST(`item` AS STRING) item, SAFE_CAST(CAST(`resp` AS STRING) AS FLOAT64) v, COUNT(*) n
FROM `{ref}` WHERE `resp` IS NOT NULL
GROUP BY item, v"""


def _itemstats_sql(ref):
    return f"""
WITH v AS (SELECT CAST(`item` AS STRING) item, SAFE_CAST(CAST(`resp` AS STRING) AS FLOAT64) r FROM `{ref}`)
SELECT item, COUNT(r) n, MIN(r) mn, MAX(r) mx,
 APPROX_QUANTILES(r, 20)[OFFSET(1)] p05, APPROX_QUANTILES(r, 20)[OFFSET(19)] p95,
 COUNTIF(r IN ({_SENT_SQL})) n_sent
FROM v GROUP BY item"""


def _cov_sql(ref, cols):
    parts = []
    for i, c in enumerate(cols):
        x = f"SAFE_CAST(CAST(`{c}` AS STRING) AS FLOAT64)"
        parts.append(
            f"COUNTIF(`{c}` IS NOT NULL) c{i}_nn, COUNT({x}) c{i}_num, "
            f"MIN({x}) c{i}_mn, MAX({x}) c{i}_mx, "
            f"APPROX_QUANTILES({x}, 20)[OFFSET(1)] c{i}_p05, "
            f"APPROX_QUANTILES({x}, 20)[OFFSET(19)] c{i}_p95, "
            f"COUNT(DISTINCT IF({x} IN ({_SENT_SQL}), CAST(`id` AS STRING), NULL)) c{i}_sent_ids, "
            f"ARRAY_TO_STRING(ARRAY_AGG(DISTINCT IF({x} IN ({_SENT_SQL}), CAST({x} AS STRING), NULL) IGNORE NULLS LIMIT 8), '|') c{i}_sent_vals")
    return f"SELECT {', '.join(parts)} FROM `{ref}`"


def _ids_sql(ref, has_rt):
    rt = ""
    if has_rt:
        rt = """,
 (SELECT COUNTIF(k > 1) FROM p) ids_multi,
 (SELECT COUNTIF(k > 1 AND drt = 1) FROM p) ids_const_rt,
 (SELECT APPROX_QUANTILES(r, 2)[OFFSET(1)] FROM (SELECT SAFE_CAST(CAST(`rt` AS STRING) AS FLOAT64) r FROM t)) rt_median"""
    placeholders = ",".join(f"'{p}'" for p in PLACEHOLDER_IDS)
    return f"""
WITH t AS (SELECT * FROM `{ref}`),
p AS (SELECT CAST(`id` AS STRING) id, COUNT(*) k
      {", COUNT(DISTINCT CAST(`rt` AS STRING)) drt" if has_rt else ""}
      FROM t GROUP BY id)
SELECT (SELECT APPROX_QUANTILES(k, 2)[OFFSET(1)] FROM p) rows_per_id_median,
 (SELECT MAX(k) FROM p) rows_per_id_max,
 (SELECT ARRAY_TO_STRING(ARRAY_AGG(CONCAT(id, ':', CAST(k AS STRING)) ORDER BY k DESC LIMIT 5), '|')
    FROM p WHERE id IN ({placeholders})) placeholder_ids{rt}"""


def _is_occ(col: str) -> bool:
    """live_dup's occasion columns, plus their spelled-out variants (trial_number,
    trial_index, session_id, run) -- robison_2026_* keys trials by `trial_number`,
    which the exact-name list misses, reporting 16k 'duplicates' that are trials."""
    from irw_validate.live_dup import OCCASION
    c = col.lower()
    return c in OCCASION or bool(re.match(r"^(trial|session|block|run|wave|occasion|time)(_?(num|number|index|id|no))?$", c))


def _dup_sql(ref, cols):
    occ = [c for c in cols if _is_occ(c)]
    key = "`id`,`item`"
    occ_key = key + "".join(f",`{c}`" for c in occ)
    r = "IFNULL(CAST(`resp` AS STRING),'<<NULL>>')"
    allc = ",".join(f"`{c}`" for c in cols)
    return f"""
WITH ga AS (SELECT {key}, COUNT(*) c, COUNT(DISTINCT {r}) dr FROM `{ref}` GROUP BY {key}),
     gc AS (SELECT {allc}, COUNT(*) c FROM `{ref}` GROUP BY {allc}),
     go AS (SELECT {occ_key}, COUNT(*) c, COUNT(DISTINCT {r}) dr FROM `{ref}` GROUP BY {occ_key})
SELECT
 (SELECT IFNULL(SUM(c-1),0) FROM ga WHERE c>1) excess_pair,
 (SELECT IFNULL(SUM(c-1),0) FROM gc WHERE c>1) excess_exact,
 (SELECT IFNULL(SUM(c-1),0) FROM go WHERE c>1) excess_occ,
 (SELECT COUNT(*) FROM go WHERE dr>1) n_conflict_pairs"""


def measure(redivis, idx: dict, table: str) -> dict:
    rec: dict = {"table": table, "error": ""}
    try:
        refs = idx.get(table)
        if not refs:
            rec["error"] = "not found in any core shard"
            return rec
        ref = refs[0]
        rec["ref"] = ref
        cols = [v.properties["name"] for v in redivis.table(ref).list_variables()]
        rec["cols"] = cols
        if not {"id", "item", "resp"} <= set(cols):
            rec["error"] = "missing id/item/resp"
            return rec
        rec["shape"] = _q(redivis, _shape_sql(ref))[0]
        sh = rec["shape"]
        if sh["n_resp_distinct"] <= HIST_MAX_DISTINCT and sh["n_items"] <= HIST_MAX_ITEMS:
            rec["hist"] = [[r["item"], r["v"], r["n"]] for r in _q(redivis, _hist_sql(ref))]
        else:
            rec["itemstats"] = _q(redivis, _itemstats_sql(ref))
        covs = [c for c in cols if c.startswith("cov_")]
        cov = {}
        for s in range(0, len(covs), COV_CHUNK):
            chunk = covs[s:s + COV_CHUNK]
            row = _q(redivis, _cov_sql(ref, chunk))[0]
            for i, c in enumerate(chunk):
                cov[c] = {k.split("_", 1)[1]: v for k, v in row.items()
                          if k.split("_", 1)[0] == f"c{i}"}
        rec["cov"] = cov
        rec["ids"] = _q(redivis, _ids_sql(ref, "rt" in cols))[0]
        rec["dup"] = _q(redivis, _dup_sql(ref, cols))[0]
        rec["occ_cols"] = [c for c in cols if _is_occ(c)]
    except Exception as exc:
        rec["error"] = str(exc)[:300]
    return rec


# ------------------------------------------------------------------- flag --

def _item_values(rec) -> dict:
    """item -> {value: n} (hist) or None when only summary stats exist."""
    if "hist" not in rec:
        return {}
    out: dict = {}
    for item, v, n in rec["hist"]:
        if v is None:
            continue
        out.setdefault(item, {})[v] = n
    return out


def _flags(rec) -> list[dict]:
    t = rec["table"]
    out = []
    add = lambda flag, sev, detail, **kw: out.append(  # noqa: E731
        {"table": t, "flag": flag, "severity": sev, "detail": detail, **kw})
    if rec.get("error"):
        add("measure_error", "info", rec["error"])
        return out
    sh = rec["shape"]
    iv = _item_values(rec)

    # resp_sentinel: an item holding a missing-data code set apart from its other values
    hits, rows = [], 0
    if iv:
        for item, vals in iv.items():
            vs = sorted(vals)
            for s in SENTINELS:
                if s not in vals:
                    continue
                rest = [v for v in vs if v != s]
                if not rest:
                    continue
                apart = (s < 0 and min(rest) >= 0) or (s > 0 and s > 3 * max(rest) and max(rest) <= 30)
                if apart:
                    hits.append(f"{item}={s:g}")
                    rows += vals[s]
    else:
        for r in rec.get("itemstats", []):
            if r["n_sent"] and r["p95"] is not None and r["mx"] is not None and (
                    (r["mn"] < 0 <= r["p05"]) or (r["mx"] > 3 * r["p95"] and r["p95"] <= 30)):
                hits.append(f"{r['item']}(n_sent={r['n_sent']})")
                rows += r["n_sent"]
    if hits:
        add("resp_sentinel", "error", "; ".join(hits[:6]), n_items=len(hits), n_rows=rows)

    # resp_binary_plus: the survey yes/no convention (1=yes, 2=no) with a rare trailing
    # 3 -- "No sabe". Triage of the first corpus pass (audit/2401/triage/judgement.md):
    # a {0,1} core plus 2 is almost always partial credit or a 0-2 clinical scale
    # (PISA, CBCL, RPQ), and a table with short-Likert siblings is a battery of
    # 1-3 scales. Precision 20% -> 73%, at the cost of recall that an option-text
    # rule over item text recovers better than any threshold here.
    if iv and len(iv) >= 2:
        sets = {item: frozenset(v) for item, v in iv.items()}
        likert = any(4 <= max(s) <= 7 for s in sets.values())
        pair = frozenset({1.0, 2.0}) in set(sets.values())   # a pure yes/no sibling
        odd = []
        for item, s in sets.items():
            if s != frozenset({1.0, 2.0, 3.0}) or likert or not pair:
                continue
            share = iv[item][3.0] / sum(iv[item].values())
            if share < 0.05:
                odd.append((item, 3.0, iv[item][3.0]))
        if odd:
            add("resp_binary_plus", "warn",
                "; ".join(f"{i}+{x:g}({n})" for i, x, n in odd[:6]),
                n_items=len(odd), n_rows=sum(n for *_, n in odd))

    # resp_mixed_scale: a few items on a scale an order of magnitude wider than the rest
    maxes = ({i: max(v) for i, v in iv.items()} if iv else
             {r["item"]: r["mx"] for r in rec.get("itemstats", []) if r["mx"] is not None})
    if len(maxes) >= 3:
        med = statistics.median(maxes.values())
        if 0 < med <= 10:
            # 0-100 sliders in a multi-format battery are legitimate, and an item
            # already caught by resp_sentinel is not a second finding
            sent = {h.split("=")[0] for f in out if f["flag"] == "resp_sentinel"
                    for h in f["detail"].split("; ")}
            mins = ({i: min(v) for i, v in iv.items()} if iv else
                    {r["item"]: r["mn"] for r in rec.get("itemstats", []) if r["mn"] is not None})
            wide = [i for i, m in maxes.items() if m > 10 * med and i not in sent
                    and not (m == 100 and (mins.get(i) or 0) >= 0)]
            if wide and len(wide) < 0.5 * len(maxes):
                add("resp_mixed_scale", "warn",
                    f"median item max {med:g}; wide: " + ", ".join(wide[:6]), n_items=len(wide))

    # cov_sentinel / cov_range
    for c, s in rec.get("cov", {}).items():
        if s.get("nn") == 0:
            add("cov_all_null", "warn", f"{c} is NULL on every row")
            continue
        if not s.get("num"):
            continue
        name = c.lower()
        mn, mx, p05, p95 = s["mn"], s["mx"], s["p05"], s["p95"]
        if "birth" in name and "year" in name or name.endswith("_yob"):
            if mn is not None and (mn < 1900 or mx > 2026):
                add("cov_range", "error", f"{c} spans {mn:g}..{mx:g}")
            continue
        if name == "cov_age" or (name.startswith("cov_age_") and not any(
                w in name for w in ("group", "month", "week", "day", "cat"))):
            if mn is not None and (mn < 0 or mx > 120):   # #1779 bound
                add("cov_range", "error", f"{c} spans {mn:g}..{mx:g}")
            continue
        if s.get("sent_ids") and p95 is not None:
            vals = [float(v) for v in (s.get("sent_vals") or "").split("|") if v]
            apart = [v for v in vals if (v < 0 <= (p05 or 0)) or (v > 0 and v > 3 * p95 and p95 <= 30)]
            if apart:
                add("cov_sentinel", "warn",
                    f"{c}: {'/'.join(f'{v:g}' for v in apart)} (p05..p95 {p05:g}..{p95:g})",
                    n_ids=s["sent_ids"])

    ids = rec.get("ids", {})
    # rt_constant: rt that does not vary within a person is a per-person time, not per-item
    if ids.get("ids_multi"):
        share = ids["ids_const_rt"] / ids["ids_multi"]
        if share >= 0.9 and sh["n_items"] > 1:
            add("rt_constant", "error",
                f"rt constant within {ids['ids_const_rt']}/{ids['ids_multi']} multi-row ids",
                n_ids=ids["ids_const_rt"])
    if (ids.get("rt_median") is not None and ids["rt_median"] > 300
            and not any(f["flag"] == "rt_constant" for f in out)):
        add("rt_units", "warn", f"median rt {ids['rt_median']:g} -- milliseconds, not seconds?")

    # id_placeholder: a sentinel-looking id holding many times a typical person's rows
    med = ids.get("rows_per_id_median") or 0
    for tok in (ids.get("placeholder_ids") or "").split("|"):
        if ":" in tok:
            pid, k = tok.rsplit(":", 1)
            if med and int(k) > 1.4 * med:
                add("id_placeholder", "info",   # low precision (mostly person #99): info only, #2401
                    f"id {pid!r} holds {k} rows (median {med})",
                    n_rows=int(k))

    # dup_id_item beyond what occasion columns explain
    d = rec.get("dup", {})
    if d.get("excess_exact"):
        add("dup_exact", "error", f"{d['excess_exact']} rows identical in every column",
            n_rows=d["excess_exact"])
    if d.get("excess_occ") and d["excess_occ"] > (d.get("excess_exact") or 0):
        add("dup_id_item", "warn",
            f"excess_occ={d['excess_occ']} exact={d['excess_exact']} conflicts={d['n_conflict_pairs']}"
            f" occ_cols={','.join(rec.get('occ_cols', [])) or '-'}",
            n_rows=d["excess_occ"])
    return out


def flag_file(jsonl: str, out: str) -> int:
    n = 0
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FLAG_FIELDS)
        w.writeheader()
        for line in open(jsonl):
            for fl in _flags(json.loads(line)):
                w.writerow({k: fl.get(k, "") for k in FLAG_FIELDS})
                n += 1
    return n


# ------------------------------------------------------------------- main --

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("tables", nargs="*")
    p.add_argument("--all", action="store_true", help="every table in the six core shards")
    p.add_argument("--from-file")
    p.add_argument("--flag", metavar="JSONL", help="flag stored measurements; no network")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--workers", type=int, default=4)
    a = p.parse_args(argv)

    if a.flag:
        print(f"{flag_file(a.flag, a.out)} flags -> {a.out}")
        return 0

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))
    from irw_validate.live_dup import _authenticate, shard_index
    import redivis_shim
    redivis_shim.install()
    redivis = _authenticate(src_root)
    idx = shard_index(redivis, src_root / "irw_validate" / "results" / ".shard_index.json")

    tables = list(a.tables)
    if a.from_file:
        tables += [ln.strip() for ln in open(a.from_file) if ln.strip()]
    if a.all:
        tables += sorted(idx)
    if not tables:
        p.error("give table names, --from-file, or --all")

    done = set()
    if a.resume and os.path.exists(a.out):
        done = {json.loads(ln)["table"] for ln in open(a.out) if ln.strip()}
    todo = [t for t in dict.fromkeys(tables) if t not in done]
    print(f"{len(todo)} to measure ({len(done)} already done)", file=sys.stderr)

    lock = threading.Lock()
    mode = "a" if a.resume else "w"
    with open(a.out, mode) as f, cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(measure, redivis, idx, t): t for t in todo}
        for i, fut in enumerate(cf.as_completed(futs), 1):
            rec = fut.result()
            with lock:
                f.write(json.dumps(rec, default=str) + "\n")
                f.flush()
            if i % 25 == 0 or rec.get("error"):
                print(f"[{i}/{len(todo)}] {rec['table']} {rec.get('error', '')[:80]}",
                      file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
