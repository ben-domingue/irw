"""Many Labs 2 (Klein et al. 2018, AMPPS 1(4), 10.1177/2515245918810225): the individual-difference
measures given to every participant, 15,157 participants in 125 samples over two slates.

Source: OSF 8cd4r, data component fanre, `ML2_S1.rda` and `ML2_S2.rda` (CC0). Export the needed
columns with R first (readxl-free, base R):

    Rscript -e 'for (s in c("S1","S2")) { e<-new.env(); load(paste0("ML2_",s,".rda"),envir=e);
      x<-get(ls(e)[1],envir=e); keep<-grep("^(ResponseID|Source\\\\.Global|Country|Language|tipi_|grah1\\\\.)",
      names(x), value=TRUE); write.csv(x[,keep], paste0("ML2_",s,"_sel.csv"), row.names=FALSE, na="") }'

`ResponseID` (Qualtrics) is unique within a slate; ids are prefixed s1_/s2_ because the two slates
are different participants and the id spaces are not guaranteed disjoint. cluster_id = Source.Global
(the sample; 64 in slate 1, 61 in slate 2). cov_country = Country of the sample.

Tables:
  manylabs2_klein_2018_tipi  TIPI, tipi_1-10 (1-7), both slates.
  manylabs2_klein_2018_mfq   Moral Foundations Questionnaire relevance items (Graham et al. 2009
                             replication), grah1.2-grah1.16 -> mfq_r1-mfq_r15 (1-6), slate 1 only;
                             grah1.1 is the instruction stem and is dropped.

    python3 data/manylabs2_klein_2018.py --s1 ML2_S1_sel.csv --s2 ML2_S2_sel.csv -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in


def load(path, prefix):
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len({r["ResponseID"] for r in rows}) == len(rows)
    for r in rows:
        r["_id"] = prefix + r["ResponseID"]
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--s1", required=True)
    p.add_argument("--s2", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    s1, s2 = load(a.s1, "s1_"), load(a.s2, "s2_")
    cols = ["id", "item", "resp", "cluster_id", "cov_country"]
    tipi = [{"id": r["_id"], "item": f"tipi_{i}", "resp": int_in(r[f"tipi_{i}"], 1, 7),
             "cluster_id": r["Source.Global"], "cov_country": r["Country"]}
            for r in s1 + s2 for i in range(1, 11)]
    write_long(a.out_dir, "manylabs2_klein_2018_tipi", tipi, cols)
    mfq = [{"id": r["_id"], "item": f"mfq_r{i - 1}", "resp": int_in(r[f"grah1.{i}"], 1, 6),
            "cluster_id": r["Source.Global"], "cov_country": r["Country"]}
           for r in s1 for i in range(2, 17)]
    write_long(a.out_dir, "manylabs2_klein_2018_mfq", mfq, cols)


if __name__ == "__main__":
    main()
