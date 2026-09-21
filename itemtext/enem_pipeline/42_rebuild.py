#!/usr/bin/env python3
"""Rebuild a year END TO END from the source PDFs, with the CURRENT tools.

WHY THIS EXISTS. 2018 shipped a thorn where a minus belongs. The decoder had
been correct for days; its REPAIRED PDFs predated the fix and were never
regenerated. Every later step -- parse, join, fill, strip, gate -- faithfully
carried the wrong glyph, and no content gate could see it, because a wrong
glyph leaves item_set_match TRUE. 41_staleness.py then found 100 of 132
derived artifacts older than the tool that makes them.

The fix is not to chase timestamps. It is to make a full rebuild cheap enough
that it is the normal thing to do, so "is this artifact current?" stops being
a question anybody has to answer.

Each year is one recipe: which booklets, whether they need font repair, which
colour fills the gaps, and which post-passes apply. Run it, then diff the
output against what is committed.

Usage:
  python3 42_rebuild.py --year 2018 [--year 2016 ...] [--all] [--out-suffix _rb]
"""
import argparse, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENEM = os.path.expanduser("~/enem")
T = "/scratch/users/mazzafe/itemtext_years"

def pin(stem):
    import glob, re
    c = sorted(glob.glob(os.path.join(HERE, f"{stem}.v*.py")),
               key=lambda p: int(re.search(r"\.v(\d+)\.py$", p).group(1)))
    if not c:
        return os.path.join(HERE, f"{stem}.py")
    return c[-1]

# day1 and day2 booklets, by role. "acc" = accessibility, "std" = the standard
# colour used to fill gaps and, before 2017, as the primary source.
RECIPE = {
 "2013": dict(repair=False, primary="std", colour="AZUL", fill=None,
   files={"std_d1": "extracted_2013/PROVAS e GABARITOS/Caderno1_Azul_Sab.pdf",
          "std_d2": "extracted_2013/PROVAS e GABARITOS/Caderno7_Azul_Dom.pdf"},
   figopts=["2013_CN_72"]),
 "2015": dict(repair=True, primary="std", colour="AZUL", fill=None,
   files={"std_d1": "extracted_2015/PROVAS e GABARITOS/PRIMEIRA APLICAÇÃO/Caderno1_Azul_Sab.pdf",
          "std_d2": "extracted_2015/PROVAS e GABARITOS/PRIMEIRA APLICAÇÃO/Caderno7_Azul_Dom.pdf"},
   figopts=[]),
 "2016": dict(repair=True, primary="std", colour="AZUL", fill=None,
   files={"std_d1": "extracted_2016/PROVAS E GABARITOS/PRIMEIRA APLICAÇÃO/CAD_ENEM_2016_DIA_1_01_AZUL.pdf",
          "std_d2": "extracted_2016/PROVAS E GABARITOS/PRIMEIRA APLICAÇÃO/CAD_ENEM_2016_DIA_2_07_AZUL.pdf"},
   figopts=["2016_CN_49"]),
 "2018": dict(repair=True, primary="acc", colour="AZUL", fill="std",
   files={"acc_d1": "extracted_2018/**/ENEM_2018_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf",
          "acc_d2": "extracted_2018/**/ENEM_2018_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf",
          "std_d1": "extracted_2018/**/ENEM_2018_P1_CAD_01_DIA_1_AZUL.pdf",
          "std_d2": "extracted_2018/**/ENEM_2018_P1_CAD_07_DIA_2_AZUL.pdf"},
   figopts=["2018_CN_126"]),
 "2017": dict(repair=False, primary="acc", colour="AZUL", fill="std",
   files={"acc_d1": "extracted_2017/**/ENEM_2017_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf",
          "acc_d2": "extracted_2017/**/ENEM_2017_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf",
          "std_d1": "extracted_2017/**/ENEM_2017_P1_CAD_01_DIA_1_AZUL.pdf",
          "std_d2": "extracted_2017/**/ENEM_2017_P1_CAD_07_DIA_2_AZUL.pdf"},
   figopts=[]),
 "2019": dict(repair=False, primary="acc", colour="AZUL", fill="std",
   files={"acc_d1": "extracted_2019/**/ENEM_2019_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf",
          "acc_d2": "extracted_2019/**/ENEM_2019_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf",
          "std_d1": "extracted_2019/**/ENEM_2019_P1_CAD_01_DIA_1_AZUL.pdf",
          "std_d2": "extracted_2019/**/ENEM_2019_P1_CAD_07_DIA_2_AZUL.pdf"},
   figopts=[]),
 "2020": dict(repair=False, primary="acc", colour="AZUL", fill="std",
   files={"acc_d1": "extracted_2020/**/ENEM_2020_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf",
          "acc_d2": "extracted_2020/**/ENEM_2020_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf",
          "std_d1": "extracted_2020/**/ENEM_2020_P1_CAD_01_DIA_1_AZUL.pdf",
          "std_d2": "extracted_2020/**/ENEM_2020_P1_CAD_07_DIA_2_AZUL.pdf"},
   figopts=[]),
 "2022": dict(repair=False, primary="acc", colour="AZUL", fill="std",
   files={"acc_d1": "extracted_2022/**/ENEM_2022_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf",
          "acc_d2": "extracted_2022/**/ENEM_2022_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf",
          "std_d1": "extracted_2022/**/ENEM_2022_P1_CAD_01_DIA_1_AZUL.pdf",
          "std_d2": "extracted_2022/**/ENEM_2022_P1_CAD_07_DIA_2_AZUL.pdf"},
   figopts=[], symbolmt=True),
 "2021": dict(repair="2021", primary="acc", colour="AZUL", fill="std",
   files={"acc_d1": "extracted_2021/**/ENEM_2021_P1_CAD_09_DIA_1_LARANJA_LEDOR.pdf",
          "acc_d2": "extracted_2021/**/ENEM_2021_P1_CAD_11_DIA_2_LARANJA_LEDOR.pdf",
          "std_d1": "extracted_2021/**/ENEM_2021_P1_CAD_01_DIA_1_AZUL.pdf",
          "std_d2": "extracted_2021/**/ENEM_2021_P1_CAD_07_DIA_2_AZUL.pdf"},
   figopts=["2021_CN_102"], notation=True),
}

def find(pat):
    import glob
    hits = glob.glob(os.path.join(ENEM, pat), recursive=True)
    if not hits:
        raise SystemExit(f"  source not found: {pat}")
    return hits[0]

def run(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 and not quiet:
        print("    !!", " ".join(str(c) for c in cmd[:3]), r.stderr[-300:])
    return r.stdout

def rebuild(y, outdir):
    rec = RECIPE[y]
    W = f"{T}/{y}"
    rp, ps = f"{W}/rb_repaired", f"{W}/rb_parsed"
    for d in (rp, ps, outdir):
        os.makedirs(d, exist_ok=True)
    parses = {}
    for role, pat in rec["files"].items():
        src = find(pat)
        if rec["repair"] == "2021":
            pdf = os.path.join(rp, role + ".pdf")   # done in one batch below
        elif rec["repair"]:
            pdf = os.path.join(rp, role + ".pdf")
            run([sys.executable, os.path.join(HERE, "17_decode_2018.py"),
                 "repair", src, pdf])
        else:
            pdf = src
        parses[role] = pdf
    if rec["repair"] == "2021":
        srcs = [find(p) for p in rec["files"].values()]
        run([sys.executable, os.path.join(HERE, "25_repair_2021.py"),
             "--out-dir", rp] + srcs)
        for role, pat in rec["files"].items():
            parses[role] = os.path.join(rp, os.path.basename(find(pat)))
    out = {}
    for role, pdf in parses.items():
        dst = os.path.join(ps, role + ".csv")
        run([sys.executable, pin("12_parse_booklet_pdf"), pdf,
             "--year", y, "--out", dst])
        out[role] = dst
    pri = [out[k] for k in sorted(out) if k.startswith(rec["primary"])]
    cmd = [sys.executable, os.path.join(HERE, "13_join.py"), "--year", y,
           "--parsed"] + pri + ["--out-dir", outdir]
    if rec["primary"] == "std":
        cmd[4:4] = ["--colour", rec["colour"]]
    run(cmd)
    if rec["fill"]:
        run([sys.executable, os.path.join(HERE, "14_fill_gaps.py"), "--year", y,
             "--colour", rec["colour"], "--parsed"]
            + [out[k] for k in sorted(out) if k.startswith("std")]
            + ["--items-dir", outdir])
    for fo in rec["figopts"]:
        f = f"{T}/figopts/{fo}.csv"
        if os.path.exists(f):
            run([sys.executable, os.path.join(HERE, "14_fill_gaps.py"), "--year", y,
                 "--colour", rec["colour"], "--parsed", f, "--items-dir", outdir])
    run([sys.executable, os.path.join(HERE, "26_strip_page_furniture.py"),
         "--items-dir", outdir, "--apply"])
    if rec.get("notation"):
        run([sys.executable, os.path.join(HERE, "29_decode_2021_notation.py"),
             "--items-dir", outdir, "--apply"])
    # These two MUST run inside the pipeline, not on the repo copies. Applying
    # them to the batch dirs by hand once meant the next 31_assemble_batch.py
    # run -- which recopies the tables out of /scratch -- silently reverted a
    # thorn-for-minus fix and 880 stripped option letters. Whatever the
    # assembler copies has to be final already.
    if rec.get("symbolmt"):
        import glob as _g
        run([sys.executable, os.path.join(HERE, "23_decode_symbolmt.py"), "--apply"]
            + sorted(_g.glob(os.path.join(outdir, "*__items.csv"))))
    # Restore superscripts/subscripts BEFORE the glyph pass, while the text
    # still matches the PDF spans the markers are anchored to. Accessibility
    # booklets spell notation out and contribute ~0 spans, so passing every
    # booklet is harmless and keeps gap-filled items covered too.
    pdfs = [p for p in parses.values()]
    run([sys.executable, os.path.join(HERE, "48_mark_scripts.py"),
         "--year", y, "--items-dir", outdir, "--apply"]
        + sum((["--pdf", p] for p in pdfs), []))
    run([sys.executable, os.path.join(HERE, "43_normalize_glyphs.py"),
         "--items-dir", outdir, "--apply"])
    run([sys.executable, os.path.join(HERE, "46_strip_option_letter.py"),
         "--items-dir", outdir, "--apply"])
    run([sys.executable, os.path.join(HERE, "49_option_conventions.py"),
         "--items-dir", outdir, "--apply"])
    # Stacked fractions and misplaced figure descriptions. Both are invisible
    # to every content gate -- the first leaves the text complete but the
    # arithmetic gone, the second makes the stem LONGER than it should be --
    # so they have to run here, where a rebuild cannot lose them, rather than
    # being applied to the batch copies by hand.
    run([sys.executable, os.path.join(HERE, "53_stacked_fractions.py"),
         "--items-dir", outdir, "--year", y, "--apply"])
    run([sys.executable, os.path.join(HERE, "54_relocate_descriptions.py"),
         "--items-dir", outdir, "--year", y, "--apply"])
    # Table contents the accessibility edition dropped. Runs last because its
    # anchors are sentences in the finished stem.
    run([sys.executable, os.path.join(HERE, "55_recover_tables.py"),
         "--items-dir", outdir, "--year", y, "--apply"])
    return outdir

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out-suffix", default="_rb")
    a = ap.parse_args()
    years = sorted(RECIPE) if a.all else a.year
    for y in years:
        od = f"{T}/{y}/out{a.out_suffix}"
        if os.path.isdir(od):
            shutil.rmtree(od)
        rebuild(y, od)
        import csv, glob
        n = {}
        for p in sorted(glob.glob(f"{od}/*__items.csv")):
            ar = p.split("_1mil_")[1][:2]
            n[ar] = len({r["item"] for r in csv.DictReader(open(p, encoding="utf-8"))})
        print(f"  {y} rebuilt -> {od}   " + " ".join(f"{k}={v}" for k, v in sorted(n.items())))
    return 0

if __name__ == "__main__":
    sys.exit(main())
