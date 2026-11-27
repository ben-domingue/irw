"""IconicITA: iconicity ratings for the Italian ANEW words (de Varda, Lamarra, Ravelli,
Saponaro, Giustolisi & Bolognesi 2025, PLOS ONE 20(12), e0337947,
10.1371/journal.pone.0337947).

Source: OSF r2tqs (CC BY-NC 4.0 on the node), https://osf.io/r2tqs/. Built from the ten
raw per-list files `all_ratings_anon/all_ratings_anon/<list>_<it|en>_ratings_all_anon.tsv`
(wide: one row per submission, `rater_id` plus one column per word, ~234 words per list).
The `it` files are native Italian speakers (L1), the `en` files highly proficient L2
speakers who read the English instructions. Ratings are 1 (not at all iconic) to 7 (very
iconic). `all_data.csv` on the node is the authors' analysis file, not the responses: it
drops every blank cell, averages a rater's repeated ratings of a word, and keeps only the
raters who passed the authors' leave-one-out agreement filter (111 of 128). It is read here
only to flag those raters.

Stimulus-norms shape (irw#2983): id = word (upper case, as presented), item = `iconicity`,
rater = the anonymised rater id (global across lists: no id appears in both an L1 and an
L2 file). A blank cell is the "I do not know the meaning or pronunciation of this word"
box (or a skip; the file does not separate the two): it is kept as resp NA with
`dontknow` = 1, and `dontknow` = 0 on every rated row. Columns:
  trial_list      the list (1-5) the submission rated
  trial_session   1, 2, 3 for a rater's repeated submissions of the same list (three
                  raters submitted a list two or three times); 1 otherwise
  cov_l2          1 = L2 speaker (`en` file), 0 = native Italian speaker (`it` file)
  cov_in_norms    1 = rater kept in the authors' published norms (in all_data.csv)
Five words appear in every list, so raters who did several lists rated them more than
once; trial_list separates those rows.

    python3 data/devarda_2025_iconicita.py --src-dir <dir with the ten tsv files> \
        --all-data <all_data.csv> -o <out dir>
"""
import argparse
import pathlib
import re
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from irw_validate import validate_frame  # noqa: E402

TABLE = "devarda_2025_iconicita"
FILE_RE = re.compile(r"^(\d)_(it|en)_ratings_all_anon\.tsv$")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src-dir", required=True)
    p.add_argument("--all-data", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    parts = []
    files = sorted(f for f in pathlib.Path(a.src_dir).iterdir() if FILE_RE.match(f.name))
    assert len(files) == 10, [f.name for f in files]
    for f in files:
        lst, lang = FILE_RE.match(f.name).groups()
        d = pd.read_csv(f, sep="\t", dtype=str, keep_default_na=False)
        assert d.columns[0] == "rater_id", f.name
        d["trial_session"] = d.groupby("rater_id").cumcount() + 1
        m = d.melt(id_vars=["rater_id", "trial_session"], var_name="id", value_name="raw")
        m["trial_list"] = int(lst)
        m["cov_l2"] = 1 if lang == "en" else 0
        parts.append(m)
    df = pd.concat(parts, ignore_index=True)
    assert df.groupby("rater_id").cov_l2.nunique().max() == 1, "rater in both L1 and L2 files"

    raw = df["raw"].str.strip()
    ok = raw.isin([f"{k}" for k in range(1, 8)] + [f"{k}.0" for k in range(1, 8)])
    assert (ok | (raw == "")).all(), raw[~ok & (raw != "")].unique()
    df["resp"] = pd.to_numeric(raw.where(raw != ""), errors="raise").astype("Int64")
    df["dontknow"] = (raw == "").astype(int)
    df["item"] = "iconicity"
    df = df.rename(columns={"rater_id": "rater"})

    kept = set(pd.read_csv(a.all_data, usecols=["participant"], dtype=str).participant)
    assert kept <= set(df.rater), "all_data.csv has raters not in the raw files"
    df["cov_in_norms"] = df.rater.isin(kept).astype(int)

    cols = ["id", "item", "resp", "dontknow", "trial_list", "trial_session",
            "cov_l2", "cov_in_norms", "rater"]
    df = df[cols].sort_values(["id", "rater", "trial_list", "trial_session"]).reset_index(drop=True)
    assert not df.duplicated(["id", "rater", "trial_list", "trial_session"]).any()

    rep = validate_frame(df, label=TABLE, profile="upload")
    for f in rep.findings:
        print(f"  {f.severity}: {f.check}: {f.message}")
    assert rep.ok, "validator errors"
    df.to_csv(out / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(df)} words={df.id.nunique()} raters={df.rater.nunique()} "
          f"(L2 {df[df.cov_l2 == 1].rater.nunique()}, in norms {df[df.cov_in_norms == 1].rater.nunique()}) "
          f"dontknow={int(df.dontknow.sum())} resp={df.resp.min()}-{df.resp.max()}")


if __name__ == "__main__":
    main()
