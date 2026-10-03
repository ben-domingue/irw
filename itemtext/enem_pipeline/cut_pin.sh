#!/bin/bash
# Cut a pinned copy of the parser and PROVE it matches the working file.
#
# Two pins in a row (v2, v3) were snapshotted before the fixes they were
# supposed to contain, and both times an agent ran the pin, got the old
# behaviour, and had to diagnose a checksum instead of a year. The md5
# comparison below is the whole point of this script: cutting a pin without it
# is how that happened twice.
set -eu
cd "$(dirname "$0")"
# --check: is the NEWEST pin still identical to the working file? A pin proves
# it matched when cut, not that it still does -- v5 went stale within 8 minutes
# and "use the pin" and "use the current parser" silently diverged again.
if [ "${1:-}" = "--check" ]; then
  W=${2:-12_parse_booklet_pdf.py}
  B=${W%.py}
  newest=$(ls -1 pins/$(basename "$B").v*.py 2>/dev/null | sort -V | tail -1)
  [ -n "$newest" ] || { echo "no pin exists"; exit 1; }
  a=$(md5sum < "$W" | cut -d" " -f1); b=$(md5sum < "$newest" | cut -d" " -f1)
  if [ "$a" = "$b" ]; then
    echo "  current: $newest is up to date (md5 $a)"
  else
    echo "  STALE: $newest ($b) != working file ($a)"
    echo "         cut a new pin before running a year, or a year gets old behaviour"
    exit 1
  fi
  exit 0
fi
V=${1:?usage: cut_pin.sh <version> [script.py], e.g. v9   |   cut_pin.sh --check [script.py]}
# A version tag that looks like a filename means the caller passed the script
# as $1 and the pin would be cut from the DEFAULT script under a misleading
# name. That happened once; refuse instead of pinning the wrong file.
# A version tag that is not literally vN means the caller passed something
# else as $1 -- a bare script stem slips past a *.py test and the pin is cut
# from the DEFAULT script under that stem's name, which looks exactly like a
# real pin. Happened twice: once with a filename, once with
# "58_verified_patches", which produced pins/12_parse_booklet_pdf.58_verified_patches.py.
# Whitelist the shape instead of blacklisting the ways it can be wrong.
case "$V" in v[0-9]*) ;; *) echo "ERROR: '$V' is not a version tag (expected vN)."
  echo "       usage: cut_pin.sh <version> [script.py]   e.g. cut_pin.sh v2 58_verified_patches.py"
  exit 2;; esac
SRC=${2:-12_parse_booklet_pdf.py}
[ -f "$SRC" ] || { echo "ERROR: no such script: $SRC"; exit 2; }
# Pins live in pins/, which is what is committed. They used to be cut beside
# the working scripts; every consumer still globbed the top level after they
# were tidied in here, so from a clean checkout the pin lookup found nothing
# and 31_assemble_batch.py wrote an EMPTY build record. One home, read by all.
mkdir -p pins
DST=pins/$(basename "${SRC%.py}").$V.py
rm -f "$DST"
cp "$SRC" "$DST"
a=$(md5sum < "$SRC" | cut -d' ' -f1)
b=$(md5sum < "$DST" | cut -d' ' -f1)
if [ "$a" != "$b" ]; then echo "PIN FAILED: $a != $b"; rm -f "$DST"; exit 1; fi
chmod 444 "$DST"
python3 -c "import ast,sys;ast.parse(open('$DST').read())" || { echo "PIN FAILED: does not parse"; exit 1; }
echo "  pinned $DST"
echo "  md5    $b   (verified identical to $SRC)"
