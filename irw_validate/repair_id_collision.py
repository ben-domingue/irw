"""Give the same-id-different-person tables one id per person, for `red_up`.

    python3 -m irw_validate.repair_id_collision --spec spec.json -o /some/dir

For #1842's class 1a: a processing script numbered each of its input files from
1 and then stacked them, so respondent 1 of the English sample and respondent 1
of the German sample became one person holding two ages and two sexes. **Not a
duplicate** -- every excess row is a real response, and deduping destroys data.

The fix approved 2026-09-02 is to prefix `id` with the label identifying the
sample and keep that label as its own `cov_` column, because folding it into the
id and dropping it loses a real covariate.

Two modes, chosen per table in the spec:

* `label` -- the table carries the sample label (`group`, `study`, `cov_sample`).
  `id` becomes `<label>_<id>` and the column is renamed to `cov_<label>` unless
  it is already prefixed.
* `person_columns` -- it does not, and the only thing separating the people is
  their demographics. The id gains a suffix from a dense rank over those
  columns, **applied only to ids that actually hold more than one person**, so
  every other id in the table is left alone. Ranking on the demographic tuple
  rather than on row order is what makes the same person get the same suffix
  across a study's sibling tables.

Nothing is invented and nothing is dropped: the row count must come back
unchanged.

## What is checked before a file is written

* the separator does not occur in any source `id` -- otherwise the prefix is
  not injective and two people could still merge;
* the row count is unchanged;
* `id`+`item` no longer repeats, except for a residual the spec declares in
  advance (`expect_excess`), which is how a table that needs the source for the
  *rest* of its collisions can still have this part fixed;
* the id count equals the spec's `expect_ids`, measured beforehand. Checking
  against a number decided in advance is the point -- a fix that merely reports
  its own output proves nothing.

Nothing here uploads.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

SEP = "_"


def _fetch(redivis, sql: str):
    for attempt in range(5):
        try:
            return redivis.query(sql).to_arrow_table(progress=False), attempt + 1
        except OSError as exc:
            if attempt == 4 or "message body" not in str(exc):
                raise
            time.sleep(2 * (attempt + 1))


def _sql(ref: str, spec: dict) -> str:
    if "label" in spec:
        lab = spec["label"]
        new = spec.get("rename") or (lab if lab.startswith(("cov_", "itemcov_"))
                                     else f"cov_{lab.lower()}")
        prefixed = (f"CONCAT(CAST(`{lab}` AS STRING), '{SEP}', CAST(`id` AS STRING))")
        if new == lab:
            return f"SELECT * REPLACE({prefixed} AS `id`) FROM `{ref}`"
        return (f"SELECT * EXCEPT(`{lab}`) REPLACE({prefixed} AS `id`), "
                f"CAST(`{lab}` AS STRING) AS `{new}` FROM `{ref}`")

    cols = spec["person_columns"]
    tuple_expr = ", ".join(f"CAST(`{c}` AS STRING)" for c in cols)
    # An unprefixed person column is a covariate that was never renamed
    # (`deception_game` ships a bare `age`), so fix that in the same pass
    # rather than leaving a second defect behind in a table being rewritten.
    ren = spec.get("rename_columns", {})
    extra = ("".join(f", `{old}` AS `{new}`" for old, new in ren.items())
             if ren else "")
    drop = ("".join(f", `{old}`" for old in ren) if ren else "")
    # DENSE_RANK over the demographic tuple, not over row order: the same person
    # must get the same suffix in every sibling table of the study.
    return f"""
WITH ranked AS (
  SELECT *,
    DENSE_RANK() OVER (PARTITION BY `id` ORDER BY {tuple_expr}) AS _rk,
    COUNT(DISTINCT FORMAT('%T', ({tuple_expr}))) OVER (PARTITION BY `id`) AS _n
  FROM `{ref}`)
SELECT * EXCEPT(_rk, _n{drop}) REPLACE(
  IF(_n > 1, CONCAT(CAST(`id` AS STRING), '{SEP}', CAST(_rk AS STRING)),
             CAST(`id` AS STRING)) AS `id`){extra}
FROM ranked
"""


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--spec", required=True,
                   help="JSON: {table: {label|person_columns, expect_ids, "
                        "expect_rows, expect_excess}}")
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
                # A prefix is only injective if the separator cannot appear in
                # the thing it is prefixed onto.
                clash = redivis.query(
                    f"SELECT COUNTIF(REGEXP_CONTAINS(CAST(`id` AS STRING), r'{SEP}')) n "
                    f"FROM `{ref}`").to_arrow_table(progress=False).to_pylist()[0]["n"]
                rec["sep_in_id"] = clash
                if clash:
                    raise ValueError(
                        f"{clash} ids already contain {SEP!r}; the prefix would "
                        "not be injective -- pick another separator")
                tb, rec["attempts"] = _fetch(redivis, _sql(ref, sp))
                rec["n_rows"] = tb.num_rows
                ids = list(map(str, tb.column("id").to_pylist()))
                items = list(map(str, tb.column("item").to_pylist()))
                rec["n_ids"] = len(set(ids))
                rec["excess_pair"] = len(ids) - len(set(zip(ids, items)))
                rec["ok"] = (rec["n_rows"] == sp["expect_rows"]
                             and rec["n_ids"] == sp["expect_ids"]
                             and rec["excess_pair"] == sp.get("expect_excess", 0))
                if rec["ok"]:
                    pacsv.write_csv(tb, out_dir / f"{t}.csv")
            except Exception as exc:
                rec["error"] = str(exc)[:300]
            failures += not rec.get("ok")
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"[{i}/{len(spec)}] {t} rows={rec.get('n_rows')}/{sp.get('expect_rows')} "
                  f"ids={rec.get('n_ids')}/{sp.get('expect_ids')} "
                  f"excess={rec.get('excess_pair')}/{sp.get('expect_excess', 0)} "
                  f"ok={rec.get('ok')} {rec.get('error', '')[:70]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
