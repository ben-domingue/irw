#!/usr/bin/env bash
# Orchestrates the metadata/*.R pipeline for the "generate metadata CSVs"
# workflow. Runs the actual numbered scripts in metadata/ (never
# reimplements their logic) and wraps each with a before/after snapshot so
# diff_csv.py can report what changed -- never a silent overwrite.
#
# Default order (2026-08-02):
#   01 (metadata.csv) -> 02 (biblio.csv + comps/nominal/simsyn biblio, one
#   script) -> 03 (tags.csv + nominal_tags.csv) -> 05 (comps_metadata.csv) -> 06
#   (nominal_metadata.csv) -> 07 (simsyn_metadata.csv) -> 08
#   (itemtext_metadata.csv) -> 09 (hero_stats.json, must run LAST since it
#   reads metadata.csv written by 01)
#
# 05 and 06 were dropped from the default order 2026-07-28 (three confirmed
# bugs in 05_comps.R, 06_nominal.R never verified standalone) and restored
# 2026-08-02 after both were fixed/verified -- see TODO.md for the full
# history if either regresses.
#
# 10_collections.R (issue #1633) runs BETWEEN 08 and 09 -- numeric order is
# deliberately not run order here, as it already isn't for 04. It must follow
# 01 and 03 (it reads metadata.csv and tags.csv off disk) and precede 09, which
# stays last. It needs no credentials and no Redivis access at all, so it is
# the one stage that is fully reviewable offline.
#
# 11_status.R (issue #1940, added 2026-09-08) runs BETWEEN 10 and 09. It was
# written for #1765/2.5c and then never wired in at all -- it was absent from
# STAGE_SCRIPT, so `run_pipeline.sh 11` answered `warn: unknown stage` and the
# only way to refresh status.json was to remember to run the script by hand.
# Nobody did: by 2026-09-08 status.json on main reported n_tables 4134 in a
# commit whose metadata.csv held 4,238 rows, so every percentage in it was
# computed on a denominator 104 tables short. That is precisely the failure the
# file exists to prevent, which is the argument for running it HERE rather than
# on a clock of its own: computed in the same run that writes its inputs, it
# cannot disagree with the metadata.csv it ships beside.
#
# It must follow 01, 03 and 08 (it reads metadata.csv, tags.csv and
# itemtext_metadata.csv off disk) and it needs no credentials and no Redivis
# access -- the second stage after 10 that is fully reviewable offline.
#
# The reason its outputs are committed while the rest of metadata/**/*.csv is
# gitignored is in 11_status.R's own header: status_history.tsv is append-only
# and the TREND is the deliverable. Note that it appends one row per run, so a
# workflow_dispatch on the same day as the scheduled run adds a second row for
# that date -- deliberate, and why the file is a history rather than a table
# keyed on date.
#
# 12_stragglers.R (issue #1940, added 2026-09-08) runs after 11 and before 09.
# It names tables that are live on Redivis and have had no metadata.csv row for
# several runs. A table missing for one run is NORMAL -- 01 carries a
# refresh.per.run throttle, and #1704 established that a snapshot count of
# missing metadata measures throttle position, not pipeline health. So it alerts
# on a NAMED table that has PERSISTED, never on a count, which is why it needs
# cross-run memory: straggler_watch.tsv (table, first_seen, last_seen, cycles),
# git-tracked for the same .tsv reason 11_status.R documents.
#
# Two things make it unlike 11:
#
#   * it MUST call Redivis (irw::irw_list_tables) -- the question is which live
#     tables are absent from metadata.csv, so metadata.csv cannot be its own
#     catalog. `--live-from FILE` is the offline escape hatch.
#   * it EXITS 1 when a table is stuck. Under `set -e` that would abort the run
#     and take 09 with it, turning a report into an outage. Hence ADVISORY_STAGE
#     above: the exit is caught, recorded and surfaced, never fatal.
#
# Its --min-live guard (default 1000) refuses to touch the watch file when the
# live fetch comes back short, so a truncated Redivis read cannot erase the
# history that makes "persisted" meaningful. Leave it on.
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
#   scripts/run_pipeline.sh                 # full default sequence (01 02 03 05 06 07 08 10 11 12 09)
#   scripts/run_pipeline.sh 01 03           # only metadata.csv + tags.csv
#   scripts/run_pipeline.sh 08              # just the itemtext metadata stage
#   scripts/run_pipeline.sh 10              # just the collections tables
#   scripts/run_pipeline.sh 11              # just the corpus status numbers
#   scripts/run_pipeline.sh 12              # just the straggler watch
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
                          [08]=08_itemtext.R [10]=10_collections.R
                          [11]=11_status.R [12]=12_stragglers.R
                          [09]=09_hero_status.R )

# Stages whose non-zero exit is a FINDING, not a failure. 12 exits 1 when a
# table has been stuck for several runs -- that is the report doing its job, and
# under `set -e` it would otherwise abort the run and take 09 down with it. The
# run loop tolerates the exit and records it; the workflow turns it into a line
# in the pull request body. Nothing else may be added here without the same
# argument: a stage that can fail silently is worse than one that stops the run.
declare -A ADVISORY_STAGE=( [12]=1 )
# CSVs each stage is expected to touch (space-separated), for snapshot/diff.
declare -A STAGE_OUTPUTS=(
  [01]="metadata.csv"
  [02]="biblio.csv comps_biblio.csv nominal_biblio.csv simsyn_biblio.csv"
  [03]="tags.csv nominal_tags.csv"
  [05]="comps_metadata.csv"
  [06]="nominal_metadata.csv"
  [07]="simsyn_metadata.csv"
  [08]="itemtext_metadata.csv"
  [10]="collections.csv collection_members.csv"
  [11]=""   # writes status.json + status_history.tsv -- reported separately below
  [12]=""   # writes straggler_watch.tsv -- reported separately below
  [09]=""   # writes JSON, not a keyed CSV -- reported separately below
)
DEFAULT_ORDER=(01 02 03 05 06 07 08 10 11 12 09)

# Join key for the diff, per output file. Everything is keyed on `table` except
# the two collections outputs (issue #1633): the registry is one row per
# collection, and collection_members is LONG -- `table` repeats there, so it
# needs a composite key or the differ de-duplicates it into a meaningless diff.
declare -A DIFF_KEY=(
  [collections.csv]="collection"
  [collection_members.csv]="table,collection"
)

stages=()
for a in "$@"; do
  case "$a" in
    --no-09) SKIP_09=1 ;;
    *) stages+=("$a") ;;
  esac
done
if [[ ${#stages[@]} -eq 0 ]]; then stages=("${DEFAULT_ORDER[@]}"); fi
if [[ "${SKIP_09:-0}" == "1" ]]; then
  # Drop the element, do not blank it. `${stages[@]/09}` substitutes the text
  # and leaves an EMPTY element behind, and an empty key is a fatal error when
  # it reaches an associative array: "STAGE_OUTPUTS: bad array subscript",
  # which under `set -e` kills the run before a single stage has executed. The
  # run loop below guards for an empty stage; the snapshot loop above it did
  # not, so --no-09 failed every time it was used. First hit 2026-09-04, the
  # first time anything passed this flag.
  kept=()
  for s in "${stages[@]}"; do
    [[ "$s" == "09" ]] && continue
    kept+=("$s")
  done
  stages=("${kept[@]}")
fi

echo "== Snapshotting current CSVs before running anything =="
for stage in "${stages[@]}"; do
  [[ -z "$stage" ]] && continue   # parity with the run loop below
  for f in ${STAGE_OUTPUTS[$stage]:-}; do
    [[ -z "$f" ]] && continue
    if [[ -f "$METADATA_DIR/$f" ]]; then
      cp "$METADATA_DIR/$f" "$SNAPSHOT_DIR/$f"
    fi
  done
done

cd "$METADATA_DIR"
ADVISORY_HIT=()
for stage in "${stages[@]}"; do
  [[ -z "$stage" ]] && continue
  script="${STAGE_SCRIPT[$stage]:-}"
  if [[ -z "$script" ]]; then
    echo "warn: unknown stage '$stage', skipping" >&2
    continue
  fi
  echo ""
  echo "== Stage $stage: Rscript $script =="
  if [[ -n "${ADVISORY_STAGE[$stage]:-}" ]]; then
    # Markers, not just an exit code: the workflow lifts what is between them
    # into the pull request body, so the named tables travel with the review
    # rather than being buried in a 40kB log tail.
    echo "--- ADVISORY $stage BEGIN ---"
    set +e
    Rscript "$script"
    stage_rc=$?
    set -e
    echo "--- ADVISORY $stage END ---"
    if [[ $stage_rc -ne 0 ]]; then
      echo "advisory: stage $stage exited $stage_rc -- a finding, not a failed run."
      ADVISORY_HIT+=("$stage")
    fi
  else
    Rscript "$script"
  fi

  # Diff THIS stage's outputs immediately, not batched at the end -- if a
  # later stage fails, set -e aborts the script, and a batched-at-the-end
  # diff loop would mean every already-succeeded stage's output got
  # overwritten on disk with no diff ever printed. That defeats the whole
  # point of this script (silent overwrite is exactly what it exists to
  # prevent) -- confirmed happening in practice 2026-07-28: stage 05 failed
  # and stages 02/03's real changes to biblio.csv/tags.csv were never
  # diffed or reported.
  # Canonicalise before diffing. diff_csv.py joins on the key and never cared
  # about row order, but git does: the outputs are committed now, and the
  # stages emit rows in whatever order Redivis and the Sheets returned them.
  # Without this a run that changes nothing still rewrites most of a file --
  # the first full workflow run produced a 30,668-line diff on biblio.csv in
  # which not one existing row had a changed field.
  for f in ${STAGE_OUTPUTS[$stage]:-}; do
    [[ -z "$f" ]] && continue
    python3 "$SCRIPT_DIR/canonicalize_csv.py" "$METADATA_DIR/$f" \
      --key "${DIFF_KEY[$f]:-table}"
  done

  echo ""
  echo "-- Stage $stage diff --"
  for f in ${STAGE_OUTPUTS[$stage]:-}; do
    [[ -z "$f" ]] && continue
    python3 "$SCRIPT_DIR/diff_csv.py" "$SNAPSHOT_DIR/$f" "$METADATA_DIR/$f" \
      --key "${DIFF_KEY[$f]:-table}"
  done
  if [[ "$stage" == "12" ]]; then
    echo "straggler_watch.tsv rewritten -- table, first_seen, last_seen, cycles."
    echo "A row here is a table live on Redivis with no metadata.csv row. That is"
    echo "NORMAL while 01's refresh throttle works through the backlog; what is not"
    echo "normal is the same table still there several runs later, which is the only"
    echo "thing this stage reports."
  fi
  if [[ "$stage" == "11" ]]; then
    echo "status.json rewritten and one row appended to status_history.tsv --"
    echo "neither is a keyed CSV, so read them directly. The number to check is"
    echo "\`n_tables\`: it must equal the row count of the metadata.csv committed"
    echo "in the same change, which is the whole reason this stage runs here."
  fi
  if [[ "$stage" == "09" ]]; then
    echo "hero_stats.json written -- not a keyed CSV, review the file directly"
    echo "(default path: $REPO_ROOT/../irw_site/data/hero_stats.json, or check 09's stdout above)."
  fi
done

echo ""
if [[ ${#ADVISORY_HIT[@]} -gt 0 ]]; then
  echo "Advisory stage(s) reported a finding: ${ADVISORY_HIT[*]} -- see above."
  echo ""
fi
echo "Done. Nothing here uploads to Redivis or touches irw_site -- review the"
echo ".diff.csv files above, then merge into Redivis / commit by hand."
