"""Expected utility ratings for ~24,000 Dutch words (Brysbaert lab, OSF udjzq, deposited
2024; data for the manuscript "Adding volition to word recognition: Expected utility norms
for 24 thousand Dutch words", no published version found on 2026-11-27).

Source: OSF udjzq (CC BY 4.0 on the node), https://osf.io/udjzq/, `Raw data/Lijst1.xlsx`
to `Lijst5.xlsx`. Each list is a wide word x rater matrix: column 1 the word, then one
column per participant (`PP1`, `PP2`, ..., plus `PP1_2` and `PP2_2` in some lists), then
the authors' `Average` and `SD` (not read). Participants rated how useful it is for
someone to know each word, 1 (weinig nuttig, little use) to 5 (zeer nuttig, very useful),
and could mark an unknown word with a cross (`Instructies_Importance.pdf`). In the files
that cross is a 0: every rater except `PP1` uses 0, `PP1` never does and leaves blanks
instead. The authors' `Average` counts the 0s as values; here they are not ratings.

Stimulus-norms shape (irw#2983): id = word, item = `expected_utility`, rater =
`L<list>_<PP column>`. Participant codes restart in every list, so the list number is
prefixed to keep raters from different lists apart; whether any person rated two lists
is not recorded. `PP1_2` and `PP2_2` are treated as raters of their own (each is a full
column next to `PP1`/`PP2`). A 0 is kept as resp NA with `dontknow` = 1 (0 on every rated
row). A blank cell is no response and produces no row. Four cells hold 6 and one holds a
space; these isolated out-of-range entries are dropped as data-entry errors.
`trial_list` is the list and `trial_position` the word's row in it: `alliteratie` appears
twice in list 1, and trial_position separates the two. In list 4 the header cell of the
word column reads `woordenschat` instead of `Woord`; it is taken as the header.

    python3 data/brysbaert_2024_expected_utility.py --src-dir <dir with Lijst1-5.xlsx> -o <out>
"""
import argparse
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from irw_validate import validate_frame  # noqa: E402

TABLE = "brysbaert_2024_expected_utility"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src-dir", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    parts, dropped = [], 0
    for lst in range(1, 6):
        d = pd.read_excel(pathlib.Path(a.src_dir) / f"Lijst{lst}.xlsx", dtype=object)
        pp = [c for c in d.columns if str(c).startswith("PP")]
        assert list(d.columns[-2:]) == ["Average", "SD"], d.columns
        assert len(pp) == len(d.columns) - 3, d.columns
        d = d.rename(columns={d.columns[0]: "id"})
        d["trial_position"] = range(1, len(d) + 1)
        m = d.melt(id_vars=["id", "trial_position"], value_vars=pp,
                   var_name="pp", value_name="raw")
        m = m[m.raw.notna()]
        v = pd.to_numeric(m.raw, errors="coerce")
        bad = v.isna() | ~v.isin([0, 1, 2, 3, 4, 5])
        dropped += int(bad.sum())
        m = m[~bad].assign(v=v[~bad].astype(int))
        m["trial_list"] = lst
        m["rater"] = f"L{lst}_" + m.pp
        parts.append(m)
    df = pd.concat(parts, ignore_index=True)
    assert dropped == 5, dropped
    df["id"] = df["id"].astype(str).str.strip()
    df["item"] = "expected_utility"
    df["dontknow"] = (df.v == 0).astype(int)
    df["resp"] = df.v.where(df.v > 0).astype("Int64")
    cols = ["id", "item", "resp", "dontknow", "trial_list", "trial_position", "rater"]
    df = df[cols].sort_values(["id", "trial_list", "trial_position", "rater"]).reset_index(drop=True)
    assert not df.duplicated(["id", "rater", "trial_position"]).any()

    rep = validate_frame(df, label=TABLE, profile="upload")
    for f in rep.findings:
        print(f"  {f.severity}: {f.check}: {f.message}")
    assert rep.ok, "validator errors"
    df.to_csv(out / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(df)} words={df.id.nunique()} raters={df.rater.nunique()} "
          f"dontknow={int(df.dontknow.sum())} dropped={dropped} resp={df.resp.min()}-{df.resp.max()}")


if __name__ == "__main__":
    main()
