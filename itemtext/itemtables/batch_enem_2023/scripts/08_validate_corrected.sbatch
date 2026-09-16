#!/bin/bash
#SBATCH --job-name=itemtext_val2
#SBATCH --array=0-3
#SBATCH --partition=normal
#SBATCH --mem=64G
#SBATCH --cpus-per-task=2
#SBATCH --time=02:00:00
#SBATCH --output=/home/users/mazzafe/enem/itemtext_run/logs/val2_%a.out
#SBATCH --error=/home/users/mazzafe/enem/itemtext_run/logs/val2_%a.err
#
# Re-run of the non-negotiable join gate against the #1942-CORRECTED response
# tables, which are what Redivis now serves. 04_validate.sbatch is kept as the
# record of the earlier run against the pre-fix CSVs; this is the stricter check.
#
# Two differences from that run:
#   - RESP points at the corrected build, not /scratch/.../enem_output/regular
#   - the items CSVs are read from the REPO (post-rebase, post-14887-removal),
#     not from the run dir, so what is gated is exactly what the PR ships.
#
# Never on a login node: read.csv on a 45M-row / 1.35GB CSV needs tens of GB.

set -u
ITEMS=/home/users/mazzafe/irw/itemtext/itemtables
VAL=/home/users/mazzafe/irw/itemtext/.claude/skills/irw-auto-itemtext/scripts/validate_items.R
RESP=/scratch/users/mazzafe/fix1942_run/work/2023

AREAS=(lc ch cn mt)
A=${AREAS[$SLURM_ARRAY_TASK_ID]}
TABLE=enem_2023_1mil_${A}

echo "=== $TABLE ==="
echo "host=$(hostname)  started=$(date -Is)"
echo "items csv: $ITEMS/${TABLE}__items.csv"
echo "resp  csv: $RESP/${TABLE}.csv"
echo

Rscript "$VAL" "$TABLE" "$ITEMS/${TABLE}__items.csv" --resp-csv "$RESP/${TABLE}.csv"
rc=$?
echo
echo "Rscript exit=$rc  finished=$(date -Is)"
[ $rc -eq 0 ] && echo "VALIDATE_RAN_$TABLE" || echo "VALIDATE_ERROR_$TABLE"
