"""Apply the #2401 mechanical class rulings to live tables, ready for `red_up`.

    python3 -m irw_validate.repair_classes plan  -o spec.json          # from the flags
    python3 -m irw_validate.repair_classes apply spec.json -o /stage/dir [--only T ...]

The repair half of `live_detectors.py`, for the classes Ben ruled mechanical on
2026-09-29 (audit/2401/RULES.md, "Decisions"):

    cov_all_null   a cov_* column NULL on every row          -> drop the column
    cov_sentinel   98/99/-99... set apart from its range     -> those values to NULL
    cov_range      age outside 0-110, birth year 1900-2026   -> those values to NULL
    rt_constant    rt identical across a person's rows       -> rename cov_completion_time_s
    resp_sentinel  a missing-data code in resp               -> drop those rows

Same design as `repair_cov_age`: **the fix is the SELECT**, so what comes over the
wire is already the repaired table, every untouched column keeps its type, and
there is no download-then-edit step. Column order is preserved (an explicit
select list, not SELECT * EXCEPT).

Before each export the counts the fix should change are measured server-side;
after it, the arrow table is checked against them -- row count, the NULLs each
nulled column gained, the target values gone. A table that fails is not written.
Nothing here uploads: hand the directory to Ben.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import pathlib
import sys
import time

AGE_LO, AGE_HI = 0, 120   # #1779's bound; the audit does not re-rule it
YOB_LO, YOB_HI = 1900, 2026

# Flagged, looked at, and not what the class assumes (2026-09-29).
EXCLUDE_COLS = {
    ("baudin_2024_static99r", "cov_age_at_release"),   # a Static-99R item score, -3..1
    ("saha_2026_cesd", "cov_age_z"),                    # a z-score
}
PENDING_SINCE = "2026-09-22"
MECHANICAL = ("cov_all_null", "cov_sentinel", "cov_range", "rt_constant", "resp_sentinel")


def _num(c):
    return f"SAFE_CAST(CAST(`{c}` AS STRING) AS FLOAT64)"


# ------------------------------------------------------------------- plan --

def plan(flags_csv: str, measurements: str) -> dict:
    from irw_validate.live_detectors import SENTINELS
    meas = {}
    opener = gzip.open if measurements.endswith(".gz") else open
    with opener(measurements, "rt") as f:
        for ln in f:
            r = json.loads(ln)
            meas[r["table"]] = r
    # A table with a table_changes row from the last week may have a fix sitting
    # in an unreleased draft; repairing the LIVE copy would upload over it.
    pending = {r["table"] for r in csv.DictReader(open("metadata/table_changes.csv"))
               if r["date"] >= PENDING_SINCE}
    spec: dict = {}
    for fl in csv.DictReader(open(flags_csv)):
        k, t = fl["flag"], fl["table"]
        if k not in MECHANICAL:
            continue
        if t in pending:
            spec.setdefault("_held_pending_draft", []).append(t) if t not in spec.get("_held_pending_draft", []) else None
            continue
        rec = meas[t]
        s = spec.setdefault(t, {"ref": rec["ref"], "cols": rec["cols"], "drop": [],
                                "null_values": {}, "null_range": {}, "rename": {},
                                "drop_resp_values": [], "flags": []})
        s["flags"].append(k)
        col = fl["detail"].split(" ", 1)[0].rstrip(":")
        if (t, col) in EXCLUDE_COLS:
            continue
        if k == "cov_all_null":
            s["drop"].append(col)
        elif k == "cov_sentinel":
            vals = [float(v) for v in fl["detail"].split(": ", 1)[1].split(" ", 1)[0].split("/")]
            s["null_values"][col] = vals
        elif k == "cov_range":
            yob = "birth" in col or col.endswith("_yob")
            s["null_range"][col] = [YOB_LO, YOB_HI] if yob else [AGE_LO, AGE_HI]
        elif k == "rt_constant":
            s["rename"]["rt"] = "cov_completion_time_s"
        elif k == "resp_sentinel":
            vals = sorted({float(h.split("=")[1]) for h in fl["detail"].split("; ")})
            s["drop_resp_values"] = [v for v in vals if v in SENTINELS]
    return spec


# ------------------------------------------------------------------ apply --

def _select_sql(s: dict) -> str:
    out = []
    for c in s["cols"]:
        if c in s["drop"]:
            continue
        if c in s["rename"]:
            out.append(f"`{c}` AS `{s['rename'][c]}`")
        elif c in s["null_values"]:
            vals = ",".join(repr(v) for v in s["null_values"][c])
            out.append(f"IF({_num(c)} IN ({vals}), NULL, `{c}`) AS `{c}`")
        elif c in s["null_range"]:
            lo, hi = s["null_range"][c]
            out.append(f"IF({_num(c)} < {lo} OR {_num(c)} > {hi}, NULL, `{c}`) AS `{c}`")
        else:
            out.append(f"`{c}`")
    where = ""
    if s["drop_resp_values"]:
        vals = ",".join(repr(v) for v in s["drop_resp_values"])
        where = f" WHERE {_num('resp')} IS NULL OR {_num('resp')} NOT IN ({vals})"
    return f"SELECT {', '.join(out)} FROM `{s['ref']}`{where}"


def _expect_sql(s: dict) -> str:
    parts = ["COUNT(*) n_rows"]
    for i, c in enumerate(s["null_values"]):
        vals = ",".join(repr(v) for v in s["null_values"][c])
        parts.append(f"COUNTIF(`{c}` IS NULL OR {_num(c)} IN ({vals})) nv{i}")
    for i, c in enumerate(s["null_range"]):
        lo, hi = s["null_range"][c]
        parts.append(f"COUNTIF(`{c}` IS NULL OR {_num(c)} < {lo} OR {_num(c)} > {hi}) nr{i}")
    if s["drop_resp_values"]:
        vals = ",".join(repr(v) for v in s["drop_resp_values"])
        parts.append(f"COUNTIF({_num('resp')} IN ({vals})) n_resp_drop")
    return f"SELECT {', '.join(parts)} FROM `{s['ref']}`"


def _q(redivis, sql):
    for attempt in range(5):
        try:
            return redivis.query(sql).to_arrow_table(progress=False)
        except Exception as exc:                        # stream truncation, 429s
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))


def apply_one(redivis, t: str, s: dict, out_dir: pathlib.Path) -> dict:
    import pyarrow.compute as pc
    import pyarrow.csv as pacsv
    rec = {"table": t, "flags": s["flags"]}
    e = _q(redivis, _expect_sql(s)).to_pylist()[0]
    tb = _q(redivis, _select_sql(s))
    want_rows = e["n_rows"] - e.get("n_resp_drop", 0)
    checks = {"rows": (tb.num_rows, want_rows)}
    for i, c in enumerate(s["null_values"]):
        checks[f"null:{c}"] = (tb.column(c).null_count, e[f"nv{i}"])
    for i, c in enumerate(s["null_range"]):
        checks[f"null:{c}"] = (tb.column(c).null_count, e[f"nr{i}"])
    for c in s["drop"]:
        checks[f"dropped:{c}"] = (c in tb.column_names, False)
    for old, new in s["rename"].items():
        checks[f"renamed:{old}"] = (new in tb.column_names and old not in tb.column_names, True)
    if s["drop_resp_values"]:
        left = pc.sum(pc.is_in(pc.cast(tb.column("resp"), "double", safe=False),
                               value_set=__import__("pyarrow").array(s["drop_resp_values"]))).as_py() or 0
        checks["resp_sentinels_left"] = (left, 0)
    rec["checks"] = {k: list(v) for k, v in checks.items()}
    rec["ok"] = all(a == b for a, b in checks.values())
    if rec["ok"]:
        pacsv.write_csv(tb, out_dir / f"{t}.csv")
    return rec


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("plan")
    pp.add_argument("--flags", default="audit/2401/detectors/corpus_flags.csv")
    pp.add_argument("--measurements", default=str(pathlib.Path.home() / "irw-stage/2401-audit/corpus.jsonl.gz"))
    pp.add_argument("-o", "--out", required=True)
    pa = sub.add_parser("apply")
    pa.add_argument("spec")
    pa.add_argument("-o", "--out-dir", required=True)
    pa.add_argument("--only", nargs="*")
    a = p.parse_args(argv)

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))

    if a.cmd == "plan":
        spec = plan(a.flags, a.measurements)
        pathlib.Path(a.out).write_text(json.dumps(spec, indent=1))
        print(f"{len(spec)} tables -> {a.out}")
        return 0

    import redivis_shim
    redivis_shim.install()
    from irw_validate.live_dup import _authenticate
    spec = json.loads(pathlib.Path(a.spec).read_text())
    # a table whose only flagged column was excluded has nothing to repair
    empty = lambda v: not (v["drop"] or v["null_values"] or v["null_range"]  # noqa: E731
                           or v["rename"] or v["drop_resp_values"])
    tables = a.only or sorted(t for t in spec if not t.startswith("_") and not empty(spec[t]))
    out_dir = pathlib.Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "repair_log.jsonl"
    done = ({json.loads(ln)["table"] for ln in log_path.open() if json.loads(ln).get("ok")}
            if log_path.exists() else set())
    redivis = _authenticate(src_root)
    fails = 0
    with log_path.open("a") as log:
        for i, t in enumerate(tables, 1):
            if t in done:
                continue
            try:
                rec = apply_one(redivis, t, spec[t], out_dir)
            except Exception as exc:
                rec = {"table": t, "ok": False, "error": str(exc)[:300]}
            fails += not rec["ok"]
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"[{i}/{len(tables)}] {t} ok={rec['ok']} {rec.get('error', '')[:80]}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
