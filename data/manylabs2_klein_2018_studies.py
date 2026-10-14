"""Many Labs 2 (Klein et al. 2018, AMPPS 1(4), 10.1177/2515245918810225): multi-item dependent
measures of six replicated studies. Companion to data/manylabs2_klein_2018.py (TIPI, MFQ), which also
documents the base-R export; this script reads a second export with the study columns:

    Rscript -e 'for (s in c("S1","S2")) { e<-new.env(); load(paste0("ML2_",s,".rda"),envir=e);
      x<-get(ls(e)[1],envir=e); keep<-grep("^(ResponseID|Source\\\\.Global|Country|and[12]\\\\.[34]_|zhon\\\\.dv\\\\.1_|zhon[12]\\\\.1$|geis\\\\.dv_|geis[12]\\\\.1$|baudv\\\\.[2-6]$|bau[12]\\\\.1$|alt[12]\\\\.([3-9]|1[01])$)",
      names(x), value=TRUE); write.csv(x[,keep], paste0("ML2_",s,"_dv.csv"), row.names=FALSE, na="") }'

Source OSF 8cd4r / fanre (CC0). id = s1_/s2_ + ResponseID, cluster_id = Source.Global, cov_country.
Each study ran two between-subject conditions; the condition a participant saw is the block whose
columns are filled (ML2 Codebook for Primary Analyses.xlsx names them). treat is coded as:

  manylabs2_klein_2018_swls      Anderson et al. 2012: Satisfaction With Life Scale, 5 items (1-7);
                                 treat = 1 high sociometric status (and2), 0 low (and1). Slate 1.
  manylabs2_klein_2018_panas     Anderson et al. 2012: PANAS, 20 items (1-5), positive 1,4,5,8,9,12,14,17,18,19,
                                 negative the rest, stored as given; same treat. Slate 1.
  manylabs2_klein_2018_bauer     Bauer et al. 2012: five water-crisis items (1-7: responsible, obligated,
                                 trust, partners, others-should-use-less); treat = 1 consumer framing (bau1),
                                 0 individual framing (bau2). Slate 1.
  manylabs2_klein_2018_alter     Alter et al. 2007: six syllogisms scored 0/1 against the codebook key
                                 (alt*.3 = 7, .4 = 8, .5 in {5,6,7,8}, .6 = 8, .7 = 3, .8 = 8; .9 has no key
                                 and is dropped); treat = 1 difficult-to-read font (alt2), 0 easy (alt1). Slate 1.
  manylabs2_klein_2018_zhong     Zhong & Liljenquist 2006: desirability of ten products (1-7);
                                 treat = 1 unethical-deed recall (zhon1), 0 ethical (zhon2). Slate 2.
  manylabs2_klein_2018_giessner  Giessner & Schubert 2007: five leader-power ratings (1-7: dominant,
                                 strong, self-confident, control, status); treat = 1 long organisational-chart
                                 line (geis1), 0 short (geis2). Slate 2.

    python3 data/manylabs2_klein_2018_studies.py --s1 ML2_S1_dv.csv --s2 ML2_S2_dv.csv -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in

KEY = {3: {"7"}, 4: {"8"}, 5: {"5", "6", "7", "8"}, 6: {"8"}, 7: {"3"}, 8: {"8"}}
COLS = ["id", "item", "resp", "treat", "cluster_id", "cov_country"]


def load(path, prefix):
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["_id"] = prefix + r["ResponseID"]
    return rows


def base(r):
    return {"id": r["_id"], "cluster_id": r["Source.Global"], "cov_country": r["Country"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--s1", required=True)
    p.add_argument("--s2", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    s1, s2 = load(a.s1, "s1_"), load(a.s2, "s2_")
    # Anderson: block 1 = low status (treat 0), block 2 = high status (treat 1)
    swls, panas = [], []
    for r in s1:
        for blk, treat in (("and1", "0"), ("and2", "1")):
            if not any(r[f"{blk}.3_{i}"].strip() for i in range(1, 6)) and \
               not any(r[f"{blk}.4_{i}"].strip() for i in range(1, 21)):
                continue
            swls += [{**base(r), "item": f"swls_{i}", "resp": int_in(r[f"{blk}.3_{i}"], 1, 7), "treat": treat}
                     for i in range(1, 6)]
            panas += [{**base(r), "item": f"panas_{i}", "resp": int_in(r[f"{blk}.4_{i}"], 1, 5), "treat": treat}
                      for i in range(1, 21)]
    write_long(a.out_dir, "manylabs2_klein_2018_swls", swls, COLS)
    write_long(a.out_dir, "manylabs2_klein_2018_panas", panas, COLS)
    # Bauer: shared DV columns, condition from bau1.1 / bau2.1
    names = {2: "responsible", 3: "obligated", 4: "trust", 5: "partners", 6: "others_less"}
    bauer = []
    for r in s1:
        c1, c2 = r["bau1.1"].strip() != "", r["bau2.1"].strip() != ""
        if c1 == c2:
            continue
        bauer += [{**base(r), "item": f"bauer_{names[i]}", "resp": int_in(r[f"baudv.{i}"], 1, 7),
                   "treat": "1" if c1 else "0"} for i in range(2, 7)]
    write_long(a.out_dir, "manylabs2_klein_2018_bauer", bauer, COLS)
    # Alter: scored syllogisms
    alter = []
    for r in s1:
        for blk, treat in (("alt1", "0"), ("alt2", "1")):
            if not any(r[f"{blk}.{i}"].strip() for i in KEY):
                continue
            for i, ok in KEY.items():
                v = r[f"{blk}.{i}"].strip()
                alter.append({**base(r), "item": f"syllogism_{i - 2}", "treat": treat,
                              "resp": "" if v == "" else ("1" if v in ok else "0")})
    write_long(a.out_dir, "manylabs2_klein_2018_alter", alter, COLS)
    # Zhong: products, condition from zhon1.1 / zhon2.1
    products = ["postit", "dove_soap", "crest", "nantucket_juice", "energizer", "sony_cd_cases",
                "windex", "lysol", "snickers", "tide"]
    zhong, giess = [], []
    for r in s2:
        z1, z2 = r["zhon1.1t_1"].strip() != "", r["zhon2.1t_1"].strip() != ""  # page-timing columns mark the block seen
        if z1 != z2:
            zhong += [{**base(r), "item": f"product_{products[i - 1]}", "resp": int_in(r[f"zhon.dv.1_{i}"], 1, 7),
                       "treat": "1" if z1 else "0"} for i in range(1, 11)]
        g1, g2 = r["geis1.1"].strip() != "", r["geis2.1"].strip() != ""
        if g1 != g2:
            giess += [{**base(r), "item": f"leader_{n}", "resp": int_in(r[f"geis.dv_{i}"], 1, 7),
                       "treat": "1" if g1 else "0"}
                      for i, n in enumerate(["dominant", "strong", "self_confident", "control", "status"], 1)]
    write_long(a.out_dir, "manylabs2_klein_2018_zhong", zhong, COLS)
    write_long(a.out_dir, "manylabs2_klein_2018_giessner", giess, COLS)


if __name__ == "__main__":
    main()
