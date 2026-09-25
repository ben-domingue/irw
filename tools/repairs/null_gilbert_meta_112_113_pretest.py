"""Null 1,505 fabricated pretest zeros in gilbert_meta_112 and _113 (irw#2313 item 3).

The source workbook (`Data_MainStudy.xlsx`, OSF osf.io/detfc, De Weerdt et al. 2026,
Teaching and Teacher Education 172) holds self-referencing formulas in the pretest
cells for Item_1, Item_7 and Item_8 -- e.g. `=MIN(O143:O143)` in O143. Excel caches a
circular reference as 0, so every pretest response to those three items reached IRW
as 0. The post-test and delayed cells are plain values.

Ruled 2026-09-25 (Ben): store them as missing, not 0, pending the authors' reply.

  gilbert_meta_112 (Forces)  wave 0, item_1/7/8, resp 0  ->  NULL   (250 + 251 + 251)
  gilbert_meta_113 (DNA)     wave 0, item_1/7/8, resp 0  ->  NULL   (251 + 251 + 251)

`resp == 0` rather than every wave-0 row: `gilbert_meta_112` has one wave-0 item_1 row
holding a 1, which is a typed value, not a formula.

`data/gilbertmeta.R` builds these from an external `datasets_list.Rdata`, so the fix is
made here on the published table, in a server-side `SELECT * REPLACE` that touches no
other column, and mirrored in gilbertmeta.R so a re-run keeps it. Checked before any
file is written: rows unchanged, nulls up by exactly the expected count, every other
resp value's count unchanged.

    python3 tools/repairs/null_gilbert_meta_112_113_pretest.py -o /some/dir
    cd /some/dir && python3 -m red_up . --dataset item_response_warehouse_2 --yes
"""
import argparse
import pathlib
import sys

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
import redivis_shim

OWNER, SHARD = "datapages", "item_response_warehouse_2"
ITEMS = ("item_1", "item_7", "item_8")
EXPECTED = {"gilbert_meta_112": 752, "gilbert_meta_113": 753}
COND = f"`wave` = 0 AND `item` IN {ITEMS} AND `resp` = 0"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("-o", "--out-dir", required=True)
    out = pathlib.Path(p.parse_args().out_dir)
    out.mkdir(parents=True, exist_ok=True)

    irw_secrets.load_write_token("null_gilbert_meta_112_113_pretest")
    redivis_shim.install()
    import redivis
    import pyarrow.csv as pacsv
    import pyarrow.compute as pc

    bad = 0
    for name, want in EXPECTED.items():
        ref = redivis.organization(OWNER).dataset(SHARD, version="current").table(
            name).get().properties["qualifiedReference"]
        before = redivis.query(
            f"SELECT COUNT(*) n, COUNTIF(resp IS NULL) nul, COUNTIF({COND}) hit, "
            f"COUNTIF(resp = 1) ones FROM `{ref}`").to_pandas_dataframe().iloc[0]
        if int(before["hit"]) != want:
            print(f"ABORT {name}: {int(before['hit'])} rows match, expected {want}")
            bad += 1
            continue
        tb = redivis.query(
            f"SELECT * REPLACE(IF({COND}, NULL, `resp`) AS `resp`) FROM `{ref}`"
        ).to_arrow_table(progress=False)
        resp = tb.column("resp")
        ones = pc.sum(pc.equal(resp, 1)).as_py()
        ok = (tb.num_rows == int(before["n"])
              and resp.null_count == int(before["nul"]) + want
              and ones == int(before["ones"]))
        print(f"{name}: rows {tb.num_rows}, nulls {int(before['nul'])} -> {resp.null_count}, "
              f"ones {ones} (was {int(before['ones'])}) -> {'OK' if ok else 'MISMATCH'}")
        if ok:
            pacsv.write_csv(tb, out / f"{name}.csv")
        else:
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
