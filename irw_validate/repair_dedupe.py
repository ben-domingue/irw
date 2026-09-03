"""Rebuild a table with its byte-identical duplicate rows dropped, for `red_up`.

    python3 -m irw_validate.repair_dedupe --from-file tables.txt -o /some/dir

For the #1842 tables whose verdict is `dedupe` **and** whose `excess_exact`
equals `excess_pair` -- every excess row is byte-identical to one already
present, so `SELECT DISTINCT *` is exactly the fix and nothing has to be chosen.
That equality is checked here, not assumed: a table whose verdict is `dedupe`
for some other reason is refused rather than silently collapsed.

Prefer fixing the processing script and regenerating from the raw source; this
is for the tables where the raw source is no longer obtainable (a dead DOI, an
OSF node whose files were replaced). It leaves the script wrong, so say so in
the handover.

**The dedupe happens in the SELECT.** What comes back is already the fixed
table. Afterwards the row count must equal `n_rows - excess_pair`, no `id`+`item` pair
may repeat, **and the id count must be unchanged** -- a drop there would mean
the dedupe keyed on the wrong columns, which is how block A got reversed once
already. A table failing any of the three is not written.

Nothing here uploads, and `live_dup.py` can only prove the fix once Ben has.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import sys
import time


def _fetch(redivis, sql: str):
    for attempt in range(5):
        try:
            return redivis.query(sql).to_arrow_table(progress=False), attempt + 1
        except OSError as exc:
            if attempt == 4 or "message body" not in str(exc):
                raise
            time.sleep(2 * (attempt + 1))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("tables", nargs="*")
    p.add_argument("--from-file", help="file of table names, one per line")
    p.add_argument("-o", "--out-dir", required=True)
    p.add_argument("--verdicts",
                   default="irw_validate/results/dup_id_item_verdicts_2026-09-02.csv")
    a = p.parse_args(argv)

    tables = list(a.tables)
    if a.from_file:
        tables += [ln.strip() for ln in open(a.from_file) if ln.strip()]
    if not tables:
        p.error("give table names, or --from-file")

    import pyarrow.compute as pc
    import pyarrow.csv as pacsv

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))
    import redivis_shim
    redivis_shim.install()
    from irw_validate.live_dup import _authenticate, shard_index

    out_dir = pathlib.Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "repair_log.jsonl"
    verdicts = {r["table"]: r for r in csv.DictReader(open(src_root / a.verdicts))}

    redivis = _authenticate(src_root)
    idx = shard_index(redivis, src_root / "irw_validate/results/.shard_index.json")
    done = ({json.loads(ln)["table"] for ln in log_path.open()}
            if log_path.exists() else set())

    failures = 0
    with log_path.open("a") as log:
        for i, t in enumerate(tables, 1):
            if t in done:
                print(f"[{i}/{len(tables)}] {t} (done)")
                continue
            rec = {"table": t}
            try:
                v = verdicts[t]
                excess, exact = int(v["excess_pair"]), int(v["excess_exact"])
                if excess != exact:
                    raise ValueError(
                        f"excess_pair {excess} != excess_exact {exact}; not a plain "
                        "dedupe -- see the worklist for which block it belongs to")
                ref = idx[t][0]
                # The id count before, because block A was reversed once on
                # exactly this question. A dedupe always leaves one copy of
                # every row, so it cannot drop an id -- but "cannot" is not
                # evidence, and a drop would mean the dedupe keyed on the
                # wrong columns.
                rec["ids_before"] = redivis.query(
                    f"SELECT COUNT(DISTINCT CAST(`id` AS STRING)) n FROM `{ref}`"
                ).to_arrow_table(progress=False).to_pylist()[0]["n"]
                tb, rec["attempts"] = _fetch(redivis, f"SELECT DISTINCT * FROM `{ref}`")
                rec["ref"] = ref
                rec["n_rows"] = tb.num_rows
                rec["expected_rows"] = int(v["n_rows"]) - excess
                # id+item must now be unique: the point of the exercise, and the
                # one thing SELECT DISTINCT does not guarantee on its own.
                pairs = tb.select(["id", "item"])
                rec["excess_pair"] = pairs.num_rows - pairs.group_by(
                    ["id", "item"]).aggregate([]).num_rows
                rec["ids_after"] = len(set(map(str, tb.column("id").to_pylist())))
                rec["ok"] = (rec["n_rows"] == rec["expected_rows"]
                             and rec["excess_pair"] == 0
                             and rec["ids_after"] == rec["ids_before"])
                if rec["ok"]:
                    pacsv.write_csv(tb, out_dir / f"{t}.csv")
            except Exception as exc:
                rec["error"] = str(exc)[:300]
            failures += not rec.get("ok")
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"[{i}/{len(tables)}] {t} rows={rec.get('n_rows')}/"
                  f"{rec.get('expected_rows')} excess_pair={rec.get('excess_pair')} "
                  f"ids={rec.get('ids_before')}->{rec.get('ids_after')} "
                  f"ok={rec.get('ok')} {rec.get('error', '')[:70]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
