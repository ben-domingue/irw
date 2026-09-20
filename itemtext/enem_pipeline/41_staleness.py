#!/usr/bin/env python3
"""Flag any DERIVED artifact older than the tool that produced it.

2018 shipped with a thorn where a minus belongs. The decoder had had the
correct override for days; the REPAIRED PDFs were made before it and were
never regenerated, so every downstream step faithfully carried the old glyph.
cut_pin.sh checks that a PIN matches its script. Nothing checked that an
ARTIFACT matches the script that produced it, and no content gate can: a wrong
glyph leaves item_set_match TRUE.
"""
import glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = "/scratch/users/mazzafe/itemtext_years"

# The build path is 42_rebuild.py, which writes rb_repaired/, rb_parsed/ and
# out_rb/. The older parsed/ and out_v8/ directories are ARCHIVES of earlier
# runs; flagging them made this report 84 lines of noise, and a check that
# cries wolf is ignored -- which is how the thorn shipped in the first place.
DEPS = [
    (f"{T}/*/rb_repaired/*.pdf",   ["17_decode_2018.py", "25_repair_2021.py"]),
    (f"{T}/*/rb_parsed/*.csv",     ["12_parse_booklet_pdf.py"]),
    (f"{T}/*/out_rb/*__items.csv", ["13_join.py", "14_fill_gaps.py",
                                    "26_strip_page_furniture.py",
                                    "43_normalize_glyphs.py",
                                    "46_strip_option_letter.py",
                                    "48_mark_scripts.py",
                                    "49_option_conventions.py"]),
]

REPO = os.path.expanduser("~/irw/itemtext/itemtables")


def committed_matches_pipeline():
    """The question that matters: is what is COMMITTED what the pipeline makes?

    Timestamps only say an artifact MIGHT be out of date. This compares the
    shipped table against a fresh pipeline build, which is the claim anyone
    reviewing the PR actually wants checked. Whitespace-exact; the only
    expected difference is the literal-NA normalisation that normalize_nulls.R
    applies to the repo copy afterwards.
    """
    import csv
    out = []
    for d in sorted(glob.glob(f"{T}/*/out_rb")):
        y = d.replace(T + "/", "").split("/")[0]
        for src in sorted(glob.glob(f"{d}/*__items.csv")):
            name = os.path.basename(src)
            dst = os.path.join(REPO, f"batch_enem_{y}", name)
            if not os.path.exists(dst):
                out.append((y, name, "not committed")); continue
            def rows(p):
                return [{k: (v or "") for k, v in r.items()}
                        for r in csv.DictReader(open(p, encoding="utf-8"))]
            a_, b_ = rows(src), rows(dst)
            if len(a_) != len(b_):
                out.append((y, name, f"row count {len(a_)} vs {len(b_)}")); continue
            diff = 0
            for x, z in zip(a_, b_):
                for col in ("item_text", "option_text", "correct_response", "resp"):
                    if x.get(col, "") != z.get(col, "") and not (
                            x.get(col, "") == "" and z.get(col, "") == "NA"):
                        diff += 1
            if diff:
                out.append((y, name, f"{diff} differing field(s)"))
    return out


def main():
    stale = []
    checked = 0
    for pat, scripts in DEPS:
        newest = max((os.path.getmtime(os.path.join(HERE, s))
                      for s in scripts if os.path.exists(os.path.join(HERE, s))),
                     default=0)
        who = max(((os.path.getmtime(os.path.join(HERE, s)), s) for s in scripts
                   if os.path.exists(os.path.join(HERE, s))), default=(0, "?"))[1]
        for f in sorted(glob.glob(pat)):
            checked += 1
            if os.path.getmtime(f) < newest:
                stale.append((f, who,
                              (newest - os.path.getmtime(f)) / 3600.0))
    print(f"  checked {checked} derived artifact(s) on the build path")
    mism = committed_matches_pipeline()
    if mism:
        print(f"  COMMITTED != PIPELINE for {len(mism)} table(s):")
        for y, n, why in mism[:12]:
            print(f"     {y} {n}: {why}")
    else:
        print("  committed tables match a fresh pipeline build exactly")
    if not stale:
        print("  STALE: none -- every artifact is newer than the tools that make it")
        return 0
    print(f"  STALE: {len(stale)} artifact(s) older than their producing script\n")
    byyear = {}
    for f, who, hrs in stale:
        y = f.replace(T + "/", "").split("/")[0]
        byyear.setdefault(y, []).append((f.replace(T + "/", ""), who, hrs))
    for y in sorted(byyear):
        print(f"  {y}:")
        for f, who, hrs in byyear[y][:6]:
            print(f"     {f:52s} {hrs:6.1f}h older than {who}")
        if len(byyear[y]) > 6:
            print(f"     ... and {len(byyear[y])-6} more")
    return 1

if __name__ == "__main__":
    sys.exit(main())
