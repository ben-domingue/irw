#!/usr/bin/env bash
# Orchestrates the metadata/*.R pipeline for the "generate metadata CSVs"
# workflow. Runs the actual numbered scripts in metadata/ (never
# reimplements their logic) and wraps each with a before/after snapshot so
# diff_csv.py can report what changed -- never a silent overwrite.
#
# Default order (2026-08-02):
#   01 (metadata.csv) -> 02 (biblio.csv + comps/nominal/simsyn biblio, one
#   script) -> 03 (tags.csv) -> 05 (comps_metadata.csv) -> 06
#   (nominal_metadata.csv) -> 07 (simsyn_metadata.csv) -> 08
#   (itemtext_metadata.csv) -> 09 (hero_stats.json, must run LAST since it
#   reads metadata.csv written by 01)
#
# 05 and 06 were dropped from the default order 2026-07-28 (three confirmed
# bugs in 05_comps.R, 06_nominal.R never verified standalone) and restored
# 2026-08-02 after both were fixed/verified -- see TODO.md for the full
# history if either regresses.
#
# 08_itemtext.R (readability-stats metadata for item text) joined the
# default order 2026-08-02. Split of responsibility, confirmed with Ben:
# this skill produces metadata FOR item text that's already been procured;
# the separate `irw-auto-itemtext` skill is what procures/extracts that item
# text in the first place ({table}__items.csv from source papers) -- no code
# overlap between the two. Only the incremental script is wired in here (it
# already skips tables already in itemtext_metadata); the full-recompute
# variant (`hotfixes/08_itemtext_recompute.R`) stays a deliberate, rare,
# manual operation, not a routine pipeline stage.
#
# 04 (QC) is intentionally excluded here: superseded by audit_tables.R for
# this skill (see SKILL.md workflow 2). hotfixes/ (other than 08's recompute
# variant, see above) are out of scope per Ben (2026-07-27) -- ignored.
#
# Usage:
#   scripts/run_pipeline.sh                 # full default sequence (01 02 03 05 06 07 08 09)
#   scripts/run_pipeline.sh 01 03           # only metadata.csv + tags.csv
#   scripts/run_pipeline.sh 08              # just the itemtext metadata stage
#   scripts/run_pipeline.sh --no-09         # everything except the hero JSON
#
# Requires: Redivis credentials configured externally (per root CLAUDE.md;
# see ~/.redivis_api_token handling below -- 2026-07-28: REDIVIS_API_TOKEN
# deliberately no longer lives in ~/.Renviron, since that also leaks into
# Ben's plain interactive `R` sessions and triggers the redivis package's
# "deprecated and highly discouraged" interactive-token warning). Also
# needs ANTHROPIC_API_KEY set for 02_biblio.R's BibTeX-generation fallback
# (it calls Claude Haiku 4.5 and will prompt interactively if unset -- fine
# for a foreground run, not for unattended use). Stage 08 additionally needs
# the `quanteda`/`quanteda.textstats` R packages installed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
METADATA_DIR="$REPO_ROOT/metadata"
SNAPSHOT_DIR="$(mktemp -d)"
trap 'rm -rf "$SNAPSHOT_DIR"' EXIT

# Load REDIVIS_API_TOKEN for this script's own child Rscript processes only
# -- never written to .Renviron, so it never reaches an interactive R
# session. If the token's already in the environment (someone exported it
# themselves) that wins; otherwise read it from a dedicated file. Missing
# file is not fatal here -- the redivis package falls back to cached OAuth
# credentials at ~/.redivis/r_credentials, which may already be valid.
REDIVIS_TOKEN_FILE="${REDIVIS_TOKEN_FILE:-$HOME/.redivis_api_token}"
if [[ -z "${REDIVIS_API_TOKEN:-}" && -f "$REDIVIS_TOKEN_FILE" ]]; then
  export REDIVIS_API_TOKEN
  REDIVIS_API_TOKEN="$(tr -d '[:space:]' < "$REDIVIS_TOKEN_FILE")"
fi

if [[ ! -f "$METADATA_DIR/01_metadata.R" ]]; then
  echo "error: expected $METADATA_DIR/01_metadata.R -- is REPO_ROOT resolution wrong?" >&2
  exit 1
fi

declare -A STAGE_SCRIPT=( [01]=01_metadata.R [02]=02_biblio.R [03]=03_tags.R
                          [05]=05_comps.R [06]=06_nominal.R [07]=07_simsyn.R
                          [08]=08_itemtext.R [09]=09_hero_status.R )
# CSVs each stage is expected to touch (space-separated), for snapshot/diff.
declare -A STAGE_OUTPUTS=(
  [01]="metadata.csv"
  [02]="biblio.csv comps_biblio.csv nominal_biblio.csv simsyn_biblio.csv"
  [03]="tags.csv"
  [05]="comps_metadata.csv"
  [06]="nominal_metadata.csv"
  [07]="simsyn_metadata.csv"
  [08]="itemtext_metadata.csv"
  [09]=""   # writes JSON, not a keyed CSV -- reported separately below
)
DEFAULT_ORDER=(01 02 03 05 06 07 08 09)

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

  # Diff THIS stage's outputs immediately, not batched at the end -- if a
  # later stage fails, set -e aborts the script, and a batched-at-the-end
  # diff loop would mean every already-succeeded stage's output got
  # overwritten on disk with no diff ever printed. That defeats the whole
  # point of this script (silent overwrite is exactly what it exists to
  # prevent) -- confirmed happening in practice 2026-07-28: stage 05 failed
  # and stages 02/03's real changes to biblio.csv/tags.csv were never
  # diffed or reported.
  echo ""
  echo "-- Stage $stage diff --"
  for f in ${STAGE_OUTPUTS[$stage]:-}; do
    [[ -z "$f" ]] && continue
    python3 "$SCRIPT_DIR/diff_csv.py" "$SNAPSHOT_DIR/$f" "$METADATA_DIR/$f"
  done
  if [[ "$stage" == "09" ]]; then
    echo "hero_stats.json written -- not a keyed CSV, review the file directly"
    echo "(default path: $REPO_ROOT/../irw_site/data/hero_stats.json, or check 09's stdout above)."
  fi
done

echo ""
echo "Done. Nothing here uploads to Redivis or touches irw_site -- review the"
echo ".diff.csv files above, then merge into Redivis / commit by hand."
