#!/usr/bin/env python3
"""Run the PINNED parser 12_parse_booklet_pdf.v2.py over a DECODED reader.

EXTRACTION_RULES / STATUS.md require every year to be parsed by the pinned v2
copy (md5 d345acc79464ea31c90f534bada963ae) because eight items' text
boundaries moved when a shared parser was edited mid-flight. So this does not
reimplement, fork or edit it: it imports the pinned module and rebinds the one
name that reads the file -- its module-level `PdfReader` -- to a factory that
returns a reader whose /ToUnicode CMaps have been completed by
17_decode_2021.py. Segmentation, the option-run rules (R1-R3 of
split_options), the furniture stripping and the CSV writing are the pinned
code, unmodified and unread by this file.

Usage mirrors the pinned parser exactly:
  python3 12b_parse_decoded.py <pdf> --year 2021 --out items.csv \
      --map glyphmap.json [--expect N]
"""
from __future__ import annotations
import argparse, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PINNED = os.path.join(HERE, "12_parse_booklet_pdf.v2.py")
PINNED_MD5 = "d345acc79464ea31c90f534bada963ae"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--year", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--map", required=True, help="gid->unicode map (--save-map)")
    ap.add_argument("--expect", type=int, default=None)
    a = ap.parse_args()

    import hashlib
    got = hashlib.md5(open(PINNED, "rb").read()).hexdigest()
    if got != PINNED_MD5:
        print(f"REFUSING TO RUN: pinned parser md5 is {got}, expected {PINNED_MD5}")
        return 2

    dec = _load(os.path.join(HERE, "17_decode_2021.py"), "decode2021")
    gmap = dec.load_map(a.map)
    parser = _load(PINNED, "pinned_v2")
    parser.PdfReader = lambda pdf: dec.decoded_reader(pdf, gmap)

    sys.argv = ["12_parse_booklet_pdf.v2.py", a.pdf, "--year", a.year,
                "--out", a.out] + (["--expect", str(a.expect)] if a.expect else [])
    return parser.main()


if __name__ == "__main__":
    sys.exit(main())
