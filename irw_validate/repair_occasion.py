"""Give a table back the column that says *which* measurement a row is, for `red_up`.

    python3 -m irw_validate.repair_occasion --spec spec.json -o /some/dir

For #1842's third class -- the repeats are real, and what was lost is the column
recording which occasion, trial or node each one belongs to. **Deduping these
destroys data**; the whole fix is to make the occasion visible again.

Two things a table in this class needs, and they are often both:

* a **rename**, where the column is present under a name nothing recognises.
  `KTEEM_Schoen_2019-2022` carries its four years of data collection as
  `group`, which `datastandard.md` reserves for the sample and the #1835 gate
  list therefore refuses to accept as an occasion. Renaming it to `wave` takes
  the table from 49,357 unexplained repeats to none, with no data change at
  all.
* a **re-derivation**, where the column has to come back from the source --
  `IRTrees.R` deleting the `sub` column that already held `item:node`.

Only the rename half runs here; a re-derivation needs the raw file and belongs
in the processing script.

Success is not `excess_pair == 0` for these tables. The repeat is the design, so
`excess_pair` stays high and correctly so; what must reach zero is the excess
once `id`, `item` and the occasion columns are taken together. The spec states
both expectations in advance and a table missing either is not written.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

from irw_validate.live_dup import OCCASION


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
    p.add_argument("--spec", required=True,
                   help='JSON: {table: {"rename": {old: new}, "expect_rows": n, '
                        '"expect_excess_occ": 0}}')
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args(argv)

    import pyarrow.csv as pacsv

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))
    import redivis_shim
    redivis_shim.install()
    from irw_validate.live_dup import _authenticate, shard_index

    spec = json.load(open(a.spec))
    out_dir = pathlib.Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "repair_log.jsonl"
    done = ({json.loads(ln)["table"] for ln in log_path.open()}
            if log_path.exists() else set())

    redivis = _authenticate(src_root)
    idx = shard_index(redivis, src_root / "irw_validate/results/.shard_index.json")

    failures = 0
    with log_path.open("a") as log:
        for i, (t, sp) in enumerate(spec.items(), 1):
            if t in done:
                print(f"[{i}/{len(spec)}] {t} (done)")
                continue
            rec = {"table": t, "spec": sp}
            try:
                ref = idx[t][0]
                rec["ref"] = ref
                ren = sp["rename"]
                # A rename that produces a name the gate still does not treat as
                # an occasion fixes nothing, so refuse it here rather than
                # discover it at upload.
                unknown = [n for n in ren.values() if n.lower() not in OCCASION]
                if unknown:
                    raise ValueError(
                        f"{unknown} is not an occasion column name the gate "
                        f"recognises; it accepts {', '.join(OCCASION)}")
                drop = "".join(f", `{o}`" for o in ren)
                add = "".join(f", `{o}` AS `{n}`" for o, n in ren.items())
                tb, rec["attempts"] = _fetch(
                    redivis, f"SELECT * EXCEPT(_x{drop}){add} FROM "
                             f"(SELECT *, 0 AS _x FROM `{ref}`)")
                rec["n_rows"] = tb.num_rows
                cols = tb.column_names
                occ = [c for c in cols if c.lower() in OCCASION]
                rec["occ_cols"] = occ
                key = ["id", "item"] + occ
                seen = set(zip(*[map(str, tb.column(c).to_pylist()) for c in key]))
                rec["excess_occ"] = tb.num_rows - len(seen)
                rec["ok"] = (rec["n_rows"] == sp["expect_rows"]
                             and rec["excess_occ"] == sp.get("expect_excess_occ", 0))
                if rec["ok"]:
                    pacsv.write_csv(tb, out_dir / f"{t}.csv")
            except Exception as exc:
                rec["error"] = str(exc)[:300]
            failures += not rec.get("ok")
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"[{i}/{len(spec)}] {t} rows={rec.get('n_rows')}/{sp.get('expect_rows')} "
                  f"occ={rec.get('occ_cols')} excess_occ={rec.get('excess_occ')} "
                  f"ok={rec.get('ok')} {rec.get('error', '')[:70]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
