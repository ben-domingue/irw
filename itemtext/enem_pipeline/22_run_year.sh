#!/bin/bash
# Run one LEDOR year end to end on the CURRENT pin.
#
#   22_run_year.sh <year> <acc_day1_glob> <acc_day2_glob> <std_day1_glob> <std_day2_glob> <colour>
#
# Deliberately takes explicit globs rather than guessing filenames: naming
# differs every year (Caderno1_Azul_Sab.pdf, CAD_ENEM_2016_DIA_1_01_AZUL.pdf,
# ENEM_2019_P1_CAD_01_DIA_1_AZUL.pdf) and 2015 even has _2.pdf.pdf duplicates
# that are the SECOND application. Guessing is how you parse the wrong exam.
#
# The colour matters too: item positions differ between colours, so filling from
# the wrong one attaches real text to the wrong item with every count still
# correct. 2024/2025 CD5 is AMARELO, not AZUL.
set -eu
cd "$(dirname "$0")"
Y=${1:?year}; A1=${2:?acc day1 glob}; A2=${3:?acc day2 glob}
S1=${4:?std day1 glob}; S2=${5:?std day2 glob}; COL=${6:?colour}
W=/scratch/users/mazzafe/itemtext_years/$Y
mkdir -p "$W/parsed"

./cut_pin.sh --check   # refuse to run a year against a stale pin
PIN=$(ls -1 12_parse_booklet_pdf.v*.py | sort -V | tail -1)
echo "  parser: $PIN"

one() {  # glob expected label
  local f; f=$(eval ls $1 2>/dev/null | head -1)
  [ -n "$f" ] || { echo "  MISSING: $1"; return 1; }
  echo "  $(basename "$f")"
  python3 "$PIN" "$f" --year "$Y" --out "$W/parsed/$3.csv" ${2:+--expect $2} 2>&1 | sed -n '2p;5,9p'
}
one "$A1" 95 acc_d1
one "$A2" 90 acc_d2
one "$S1" ""  std_d1
one "$S2" ""  std_d2

python3 13_join.py --year "$Y" --parsed "$W/parsed/acc_d1.csv" "$W/parsed/acc_d2.csv" --out-dir "$W"
python3 14_fill_gaps.py --year "$Y" --colour "$COL" --parsed "$W/parsed/std_d1.csv" "$W/parsed/std_d2.csv" --items-dir "$W"

# QC that the R10 gate cannot see (STATUS.md's trap list)
python3 - "$Y" "$W" <<'PY'
import csv, glob, re, sys
y, W = sys.argv[1], sys.argv[2]
T = re.compile(r"Descri[çc][ãa]o\s+d[oaes]\b[^\n:]{0,40}\s*:", re.I)
BAD = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]|/g\d+")
print("  --- QC the gate cannot see ---")
for f in sorted(glob.glob(f"{W}/enem_{y}_1mil_*__items.csv")):
    rows = list(csv.DictReader(open(f, encoding="utf-8")))
    per = {}
    for r in rows: per.setdefault(r["item"], {})[r["resp_raw"]] = r["option_text"] or ""
    orphan = sum(1 for i, o in per.items()
                 if T.search(o.get("E", "")) and not all(T.search(o.get(L, "")) for L in "ABCDE"))
    txt = "".join((r["item_text"] or "") + (r["option_text"] or "") for r in rows)
    print(f"    {f.split('/')[-1]:34} items={len(per):>3} "
          f"bad_rowcount={sum(1 for o in per.values() if len(o)!=5)} "
          f"orphan_desc={orphan} garbled={len(BAD.findall(txt))} "
          f"blank_instr={sum(1 for r in rows if not (r['instructions'] or '').strip())}")
PY
sbatch --export=ALL,YEAR="$Y",ITEMS_DIR="$W" -J "it_val$Y" 15_validate_year.sbatch
