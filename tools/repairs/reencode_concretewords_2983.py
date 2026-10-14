"""Re-encode concretewords: the rater moves from `item` to `rater` (irw#2983, ruling 3).

concretewords (Muraki, Sidhu & Pexman 2022, concreteness ratings for 66,404 multiword
expressions, CC BY) was built with id = expression and item = the Qualtrics respondent,
on the argument that a single rating dimension would otherwise leave one item (#1876).
Ben ruled on 2026-10-13 that a norms study with one dimension keeps the stimulus-norms
shape anyway: id = stimulus, item = the dimension, rater = participant. The rater is
never placed on `item`.

The raw file `Ratings_RawData.csv` that data/concretewords.R read is no longer held
(irw_validate/results/dup_id_item_worklist.md), so the change is made on the published
table: every row is kept, `item` becomes `rater`, and `item` is set to `concreteness`.
Checked after the read: row count and distinct (id, rater) pairs equal the live counts.

    python3 tools/repairs/reencode_concretewords_2983.py -o /some/dir
    cd /some/dir && python3 -m red_up . --dataset item_response_warehouse --yes
"""
import argparse
import pathlib
import sys

sys.path.insert(0, "/home/ben/Dropbox/projects/irw/src")
import irw_secrets
import redivis_shim

OWNER, SHARD, TABLE = "datapages", "item_response_warehouse", "concretewords"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("-o", "--out-dir", required=True)
    out = pathlib.Path(p.parse_args().out_dir)
    out.mkdir(parents=True, exist_ok=True)

    irw_secrets.load_write_token("reencode_concretewords_2983")
    redivis_shim.install()
    import redivis
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.csv as pacsv

    ref = redivis.organization(OWNER).dataset(SHARD, version="current").table(
        TABLE).get().properties["qualifiedReference"]
    live = redivis.query(
        f"SELECT COUNT(*) n, COUNT(DISTINCT id) ids, COUNT(DISTINCT item) raters, "
        f"COUNT(DISTINCT CONCAT(id, '|', item)) pairs FROM `{ref}`").to_pandas_dataframe().iloc[0]
    print("live:", dict(live))

    tbl = redivis.query(f"SELECT id, item, resp FROM `{ref}`").to_arrow_table()
    if tbl.num_rows != int(live["n"]):
        print(f"ABORT: read {tbl.num_rows} rows, live has {int(live['n'])}")
        return 1
    n_pairs = pa.table({"k": pc.binary_join_element_wise(
        pc.cast(tbl["id"], pa.string()), pc.cast(tbl["item"], pa.string()), "|")}
    ).group_by("k").aggregate([]).num_rows
    if n_pairs != int(live["pairs"]):
        print(f"ABORT: {n_pairs} distinct (id, rater) pairs, live has {int(live['pairs'])}")
        return 1
    new = pa.table({
        "id": tbl["id"],
        "item": pa.array(["concreteness"] * tbl.num_rows),
        "resp": tbl["resp"],
        "rater": tbl["item"],
    })
    path = out / f"{TABLE}.csv"
    pacsv.write_csv(new, path)
    print(f"wrote {path}: {new.num_rows} rows, {int(live['ids'])} ids, "
          f"{int(live['raters'])} raters, 1 item")
    return 0


if __name__ == "__main__":
    sys.exit(main())
