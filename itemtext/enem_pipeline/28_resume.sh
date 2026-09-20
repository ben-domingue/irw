#!/bin/bash
# Connection-proof entry point. Every subcommand reads STATE FROM DISK, never
# from a note, so it is correct after any interruption and safe to re-run.
set -uo pipefail
cd "$(dirname "$0")"
T=/scratch/users/mazzafe/itemtext_years
L=/scratch/users/mazzafe/itemtext_logs
mkdir -p "$L"

# authoritative output dir per year -- these are NOT uniform (2025 has two)
dir_for() { case "$1" in
  2018) echo "$T/2018/out_v8";; 2021) echo "$T/2021/out_v8";;
  2024) echo "$T/2024/items";; 2025) echo "$T/2025/items_sp";;
  *) echo "$T/$1";; esac; }
YEARS="2013 2015 2016 2017 2018 2019 2020 2021 2022 2024 2025"

case "${1:-status}" in

detached)
  shift
  [ $# -gt 0 ] || { echo "usage: 28_resume.sh detached <subcommand> [args]"; exit 2; }
  stamp=$(date +%Y%m%d_%H%M%S)
  log="$L/${stamp}_$1.log"
  # setsid detaches from the controlling terminal, so a dropped connection
  # cannot take the job with it.
  setsid nohup "$0" "$@" > "$log" 2>&1 < /dev/null &
  echo "  detached pid $! -> $log"
  echo "  follow with: tail -f $log"
  ;;

logs)
  ls -1t "$L" 2>/dev/null | head -20 | sed "s|^|  $L/|"
  ;;

status)
  echo "=== pins (the working file must match the newest pin) ==="
  for f in 12_parse_booklet_pdf 13_join 14_fill_gaps 20_geom_options \
           20_verify_gabarito_microdata 23_decode_symbolmt 25_repair_2021 \
           26_strip_page_furniture 29_decode_2021_notation; do
    [ -f "$f.py" ] || continue
    ./cut_pin.sh --check "$f.py" 2>&1 | sed 's/^/  /'
  done
  echo "=== per-year output on disk ==="
  printf "  %-6s %-34s %s\n" year dir "items (ch/cn/lc/mt)"
  for y in $YEARS; do
    d=$(dir_for "$y")
    n=$(python3 - "$d" "$y" <<'PY'
import csv,sys,os
d,y=sys.argv[1],sys.argv[2]
out=[]
for a in ("ch","cn","lc","mt"):
    p=f"{d}/enem_{y}_1mil_{a}__items.csv"
    out.append(str(len({r["item"] for r in csv.DictReader(open(p,encoding="utf-8"))})) if os.path.exists(p) else "-")
print("/".join(out), sum(int(x) for x in out if x.isdigit()))
PY
)
    printf "  %-6s %-34s %s\n" "$y" "${d#$T/}" "$n"
  done
  echo "=== key strings present (needed by the gate) ==="
  ls -1 "$T"/gab_strings_*.txt 2>/dev/null | sed 's/.*gab_strings_//;s/\.txt//' | tr '\n' ' '; echo
  ;;

verify)
  fail=0
  for y in $YEARS; do
    [ -f "$T/gab_strings_$y.txt" ] || { echo "  $y  SKIP (no key strings; run: 28_resume.sh gabstrings $y)"; continue; }
    out=$(python3 20_verify_gabarito_microdata.py "$y" 2>&1)
    tot=$(echo "$out" | grep -E "^  TOTAL" | sed 's/^  //')
    # A MISMATCH is a real failure. "NOT VERIFIED" on an accessibility booklet
    # is NOT: INEP only publishes key strings for some of its areas, and the
    # standard booklets still score 4/4 -- so count the two separately rather
    # than lumping them, which would hide a real mismatch among benign lines.
    bad=$(echo "$out" | grep -cE "MISMATCH|NOT SCORABLE|FAILURE")
    part=$(echo "$out" | grep -cE "NOT VERIFIED")
    echo "  === $y ==="; echo "$out" | grep -E "^  TOTAL|NOT SCORABLE|FAILURE" | sed 's/^/    /'
    [ "$bad" -gt 0 ] && { fail=$((fail+1)); echo "    ^^ MISMATCH present"; }
    [ "$part" -gt 0 ] && echo "    (note: $part accessibility booklet(s) partly scored -- benign, standard booklets are 4/4)"
  done
  echo
  echo "  REAL failures (MISMATCH/unscored): $fail"
  echo "  known and accepted: 2017 LARANJA LC 43/45 = defect in INEP's own key string (STATUS.md trap 31)"
  ;;

gabstrings)
  shift
  for y in "$@"; do python3 21_gab_strings.py --year "$y"; done
  ;;

qc)
  python3 - <<'PY'
import csv,glob,os,re,collections
T="/scratch/users/mazzafe/itemtext_years"
D={"2018":"2018/out_v8","2021":"2021/out_v8","2024":"2024/items","2025":"2025/items_sp"}
FURN=re.compile(r"(Caderno\s*\d+\s*[-|]\s*[A-ZÇÃÕ]+|\*[A-Za-z0-9]{5,}\*|\d\s*[º°o]\s*dia\s*\||\.indb)",re.I)
print("  year  rows  ctrl  fffd  furniture  blank_item_text")
for y in ["2013","2015","2016","2017","2018","2019","2020","2021","2022","2024","2025"]:
    d=os.path.join(T,D.get(y,y)); n=c=f=fu=bl=0
    for p in glob.glob(f"{d}/*__items.csv"):
        for r in csv.DictReader(open(p,encoding="utf-8")):
            n+=1
            blob=(r["item_text"] or "")+(r["option_text"] or "")
            c+=len(re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f]",blob)); f+=blob.count("�")
            if FURN.search(blob+(r["instructions"] or "")): fu+=1
            if not (r["item_text"] or "").strip(): bl+=1
    print(f"  {y}  {n:5d} {c:5d} {f:5d} {fu:10d} {bl:15d}")
PY
  ;;

*) echo "usage: 28_resume.sh [status|verify|qc|gabstrings <y..>|logs|detached <cmd>]"; exit 2;;
esac
