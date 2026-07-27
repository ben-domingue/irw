#!/usr/bin/env bash
# Orchestrates the metadata/*.R pipeline for the "generate metadata CSVs"
# workflow. Runs the actual numbered scripts in metadata/ (never
# reimplements their logic) and wraps each with a before/after snapshot so
# diff_csv.py can report what changed -- never a silent overwrite.
#
# Default order matches Ben's sequencing (2026-07-27):
#   01 (metadata.csv) -> 02 (biblio.csv + comps/nominal/simsyn biblio, one
#   script) -> 03 (tags.csv) -> 05 (comps_metadata.csv) -> 06
#   (nominal_metadata.csv) -> 07 (simsyn_metadata.csv) -> 09 (hero_stats.json,
#   must run LAST since it reads metadata.csv written by 01)
#
# 04 (QC) and 08 (itemtext metadata) are intentionally excluded here: 04 is
# superseded by audit_tables.R for this skill (see SKILL.md workflow 2); 08
# belongs to the separate itemtext pipeline. hotfixes/ are out of scope per
# Ben (2026-07-27) -- ignored.
#
# Usage:
#   scripts/run_pipeline.sh                 # full default sequence
#   scripts/run_pipeline.sh 01 03           # only metadata.csv + tags.csv
#   scripts/run_pipeline.sh --no-09         # everything except the hero JSON
#
# Requires: Redivis credentials configured externally (per root CLAUDE.md),
# and ANTHROPIC_API_KEY set for 02_biblio.R's BibTeX-generation fallback (it
# calls Claude Haiku 4.5 and will prompt interactively if unset -- fine for
# a foreground run, not for unattended use).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
METADATA_DIR="$REPO_ROOT/metadata"
SNAPSHOT_DIR="$(mktemp -d)"
trap 'rm -rf "$SNAPSHOT_DIR"' EXIT

if [[ ! -f "$METADATA_DIR/01_metadata.R" ]]; then
  echo "error: expected $METADATA_DIR/01_metadata.R -- is REPO_ROOT resolution wrong?" >&2
  exit 1
fi

declare -A STAGE_SCRIPT=( [01]=01_metadata.R [02]=02_biblio.R [03]=03_tags.R
                          [05]=05_comps.R [06]=06_nominal.R [07]=07_simsyn.R
                          [09]=09_hero_status.R )
# CSVs each stage is expected to touch (space-separated), for snapshot/diff.
declare -A STAGE_OUTPUTS=(
  [01]="metadata.csv"
  [02]="biblio.csv comps_biblio.csv nominal_biblio.csv simsyn_biblio.csv"
  [03]="tags.csv"
  [05]="comps_metadata.csv"
  [06]="nominal_metadata.csv"
  [07]="simsyn_metadata.csv"
  [09]=""   # writes JSON, not a keyed CSV -- reported separately below
)
DEFAULT_ORDER=(01 02 03 05 06 07 09)

stages=()
for a in "$@"; do
  case "$a" in
    --no-09) SKIP_09=1 ;;
    *) stages+=("$a") ;;
  esac
done
if [[ ${#stages[@]} -eq 0 ]]; then stages=("${DEFAULT_ORDER[@]}"); fi
if [[ "${SKIP_09:-0}" == "1" ]]; then
  stages=("${stages[@]/09}")
fi

echo "== Snapshotting current CSVs before running anything =="
for stage in "${stages[@]}"; do
  for f in ${STAGE_OUTPUTS[$stage]:-}; do
    [[ -z "$f" ]] && continue
    if [[ -f "$METADATA_DIR/$f" ]]; then
      cp "$METADATA_DIR/$f" "$SNAPSHOT_DIR/$f"
    fi
  done
done

cd "$METADATA_DIR"
for stage in "${stages[@]}"; do
  [[ -z "$stage" ]] && continue
  script="${STAGE_SCRIPT[$stage]:-}"
  if [[ -z "$script" ]]; then
    echo "warn: unknown stage '$stage', skipping" >&2
    continue
  fi
  echo ""
  echo "== Stage $stage: Rscript $script =="
  Rscript "$script"
done

echo ""
echo "== Diffing outputs against pre-run snapshots =="
for stage in "${stages[@]}"; do
  for f in ${STAGE_OUTPUTS[$stage]:-}; do
    [[ -z "$f" ]] && continue
    python3 "$SCRIPT_DIR/diff_csv.py" "$SNAPSHOT_DIR/$f" "$METADATA_DIR/$f"
  done
done

if [[ " ${stages[*]} " == *" 09 "* ]]; then
  echo ""
  echo "== Stage 09 output =="
  echo "hero_stats.json written -- not a keyed CSV, review the file directly"
  echo "(default path: $REPO_ROOT/../irw_site/data/hero_stats.json, or check 09's stdout above)."
fi

echo ""
echo "Done. Nothing here uploads to Redivis or touches irw_site -- review the"
echo ".diff.csv files above, then merge into Redivis / commit by hand."
