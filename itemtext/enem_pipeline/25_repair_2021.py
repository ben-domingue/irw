#!/usr/bin/env python3
"""Write 2021's decode back into the PDF, so the PINNED parser reads it directly.

WHY THIS EXISTS. 17_decode_2021.py derives a correct, document-internal
gid->unicode map and can already apply it in memory (`patch_reader`), but it
had no way to SAVE the result. So 2021 was the only year whose text reached the
joiner through a text-level post-process rather than through the pinned parser,
which means its line and item boundaries were not produced by the same code as
every other year. That is a reproducibility hole, not a cosmetic one.

This completes the /ToUnicode CMap and saves the PDF, exactly as
17_decode_2018.py does for 2018 -- and exactly as STATUS.md trap 22 requires:
"COMPLETE the ToUnicode CMap instead and leave /Differences alone." Rewriting
/Differences corrupted every lowercase l and x when it was tried, because
pypdf follows PDF 1.7 5.9.1 and lets ToUnicode win over the encoding.

Unresolved gids are deliberately left as /gNNN so they stay COUNTABLE in the
extracted text rather than becoming a plausible wrong letter.

Usage:
  python3 25_repair_2021.py --out-dir <dir> <in1.pdf> [in2.pdf ...]
  # the map is derived from ALL the pdfs given, which is what makes it
  # family-scoped and cross-attested (trap 23)
"""
import argparse, os, sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "d2021", os.path.join(HERE, "17_decode_2021.py"))
d2021 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d2021)

from pypdf import PdfWriter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mac-ceiling", type=int, default=None)
    a = ap.parse_args()

    # Derive the map from every booklet at once: a family's glyphs are attested
    # by whichever subset happens to carry real names, which is not the same
    # subset in every file.
    gmap, meta = d2021.build_map(a.pdfs, a.mac_ceiling)
    print(f"  map derived: {len(gmap)} family(ies), "
          f"{meta['outline_attested']} outline-attested gids, "
          f"{meta['mac_fallback']} mac-order fallback")

    os.makedirs(a.out_dir, exist_ok=True)
    total_done = total_left = 0
    for p in a.pdfs:
        r = d2021.PdfReader(p)
        done, left = d2021.patch_reader(r, gmap)
        w = PdfWriter()
        w.append(r)
        dst = os.path.join(a.out_dir, os.path.basename(p))
        with open(dst, "wb") as fh:
            w.write(fh)
        total_done += done
        total_left += left
        print(f"  {os.path.basename(p):34s} {done:5d} codes decoded, "
              f"{left:4d} left as /gNNN -> {dst}")
    print(f"  TOTAL {total_done} decoded, {total_left} left visible as /gNNN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
