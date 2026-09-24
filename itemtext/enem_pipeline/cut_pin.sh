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
  newest=$(ls -1 $B.v*.py 2>/dev/null | sort -V | tail -1)
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
case "$V" in *.py|*/*) echo "ERROR: '$V' is a filename, not a version tag."
  echo "       usage: cut_pin.sh <version> [script.py]"; exit 2;; esac
SRC=${2:-12_parse_booklet_pdf.py}
[ -f "$SRC" ] || { echo "ERROR: no such script: $SRC"; exit 2; }
DST=${SRC%.py}.$V.py
rm -f "$DST"
cp "$SRC" "$DST"
a=$(md5sum < "$SRC" | cut -d' ' -f1)
b=$(md5sum < "$DST" | cut -d' ' -f1)
if [ "$a" != "$b" ]; then echo "PIN FAILED: $a != $b"; rm -f "$DST"; exit 1; fi
chmod 444 "$DST"
python3 -c "import ast,sys;ast.parse(open('$DST').read())" || { echo "PIN FAILED: does not parse"; exit 1; }
echo "  pinned $DST"
echo "  md5    $b   (verified identical to $SRC)"
