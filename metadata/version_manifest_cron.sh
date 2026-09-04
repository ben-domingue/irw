#!/usr/bin/env bash
# Daily cron entry point for the IRW version manifest (roadmap item 3.0, #1705).
#
# Refreshes metadata/version_manifest.tsv from Redivis' version history and
# commits it, so that the record of "which release of every dataset was live
# when" stays current without anyone remembering to run anything. The R and
# Python packages read the committed file from raw.githubusercontent, so a
# commit that never lands is a manifest no user ever sees.
#
# Daily rather than weekly, and separate from weekly_pipeline_cron.sh, because
# the two answer to different clocks: the metadata pipeline is reviewed by a
# human before anything is published, whereas this only records what has
# *already* been published. Lag here is the whole failure mode -- a version
# released today and recorded next Monday is a version nobody could cite for a
# week. It is also read-only against Redivis and cannot publish anything, so it
# needs no review gate.
#
# Unlike weekly_pipeline_cron.sh this stays quiet when nothing changed: it runs
# every day and most days there is nothing to say. It opens a GitHub issue only
# on failure, when the append is refused, or when it has been unable to run for
# STALL_AFTER days running -- see below.
#
# Why an append can be refused, and why that is an alert rather than a retry:
# an IRW version number is a citation, so red_up.manifest recomputes the whole
# history and stops if any number already committed would come to mean
# something else. That should never happen. If it does, something changed on
# Redivis that the model did not anticipate -- a deleted version, an unreleased
# release -- and a human has to look before the file moves.
#
# Why this runs in its own worktree, on a detached HEAD:
# it used to run in the live `src` checkout and refuse unless that checkout
# happened to be sitting on `main`. In practice it never is -- Ben works on
# feature branches -- so between the first install and 2026-09-04 the job
# skipped every single day and refreshed the manifest exactly zero times. The
# guard was right and its assumption was wrong. A private worktree owned by
# this script depends on nobody's branch. It is detached rather than on `main`
# so that holding it here never stops a human from checking `main` out
# somewhere else: git allows one checkout of a branch across all worktrees.
set -uo pipefail

export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

REPO_DIR="$HOME/Dropbox/projects/irw/src"      # the live checkout; source of the worktree only
WORK_DIR="$HOME/irw-wt/version-manifest-cron"  # this script's own, detached at origin/main
MANIFEST="metadata/version_manifest.tsv"
LOG_DIR="$REPO_DIR/metadata/pipeline_logs"
STATE_FILE="$LOG_DIR/.version_manifest_skips"
DATE="$(date +%F)"
LOG_FILE="$LOG_DIR/version_manifest_${DATE}.log"
GH_REPO="ben-domingue/irw"
GH_MENTION="@ben-domingue"
BRANCH="main"
STALL_AFTER=2   # consecutive days unable to run before this stops being quiet

mkdir -p "$LOG_DIR"

alert() {
  # $1 = title suffix, $2 = body preamble. The log is always on disk either
  # way; the issue exists so GitHub sends mail.
  local body
  body="$(mktemp)"
  {
    echo "$GH_MENTION $2"
    echo
    echo "Log: \`$LOG_FILE\`"
    echo
    echo '```'
    tail -c 50000 "$LOG_FILE"
    echo '```'
  } > "$body"
  gh issue create --repo "$GH_REPO" \
    --title "IRW version manifest -- $DATE [$1]" \
    --body-file "$body" --assignee ben-domingue >> "$LOG_FILE" 2>&1
  rm -f "$body"
}

# A subshell, not a brace group: the steps below use `exit` to stop early, and
# in a brace group that would exit the whole script and skip the alerting.
# Exit codes: 0 = ran (committed, or nothing to commit), 2 = could not run
# (counts toward the stall alert), anything else = failed.
(
  echo "# IRW version manifest refresh -- $DATE"
  echo

  cd "$REPO_DIR" || { echo "ERROR: no checkout at $REPO_DIR."; exit 1; }

  # Create the worktree on first run, so installing this needs no manual step.
  if [[ ! -d "$WORK_DIR" ]]; then
    echo "Creating worktree $WORK_DIR (detached at origin/$BRANCH)."
    git fetch --quiet origin "$BRANCH" 2>&1 || { echo "ERROR: fetch failed."; exit 1; }
    git worktree add --detach "$WORK_DIR" "origin/$BRANCH" 2>&1 || {
      echo "ERROR: could not create worktree $WORK_DIR."
      exit 1
    }
  fi

  cd "$WORK_DIR" || { echo "ERROR: cannot enter $WORK_DIR."; exit 2; }

  # Nothing but this script ever writes here, so a dirty tree means a previous
  # run left something behind. Stop and let a human look rather than discarding
  # work whose provenance is unknown.
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "CANNOT RUN: $WORK_DIR has uncommitted changes. Nothing done."
    git status --short 2>&1
    exit 2
  fi

  git fetch --quiet origin "$BRANCH" 2>&1 || { echo "ERROR: fetch failed."; exit 1; }
  git checkout --quiet --detach "origin/$BRANCH" 2>&1 || {
    echo "ERROR: could not move worktree to origin/$BRANCH."
    exit 1
  }
  echo "At $(git rev-parse --short HEAD) (origin/$BRANCH)."

  python3 -m red_up.manifest 2>&1
  rc=$?
  if [[ "$rc" -ne 0 ]]; then
    echo "ERROR: red_up.manifest exited $rc."
    exit "$rc"
  fi

  if [[ -z "$(git status --porcelain -- "$MANIFEST")" ]]; then
    echo "No new releases; $MANIFEST unchanged."
    exit 0
  fi

  added="$(git diff --numstat -- "$MANIFEST" | awk '{print $1}')"
  git add "$MANIFEST"
  git commit -m "Version manifest: refresh for $DATE (${added:-?} new row(s))" \
    -m "Automated daily run of metadata/version_manifest_cron.sh (#1705)." 2>&1 || {
    echo "ERROR: commit failed."
    exit 1
  }
  # HEAD is detached, so name the destination branch explicitly. If the push
  # loses a race with a human push it fails here and the commit is discarded by
  # the next run's checkout -- which is harmless, because the manifest is
  # recomputed from Redivis every time rather than accumulated.
  git push origin "HEAD:$BRANCH" 2>&1 || {
    echo "ERROR: push failed. The commit is local; the packages read the "
    echo "pushed copy, so this must be resolved by hand."
    exit 1
  }
  echo "Committed and pushed ${added:-?} new row(s)."
  exit 0
) > "$LOG_FILE" 2>&1

rc=$?

# Consecutive days unable to run. A single skip is not worth waking anyone;
# a run of them means the manifest is quietly going stale, which is the exact
# failure this job exists to prevent, so it has to become loud on its own.
skips=0
[[ -f "$STATE_FILE" ]] && skips="$(cat "$STATE_FILE" 2>/dev/null || echo 0)"
[[ "$skips" =~ ^[0-9]+$ ]] || skips=0

if [[ "$rc" -eq 2 ]]; then
  skips=$((skips + 1))
  echo "$skips" > "$STATE_FILE"
  echo "Consecutive days unable to run: $skips." >> "$LOG_FILE"
  if [[ "$skips" -ge "$STALL_AFTER" ]]; then
    alert "STALLED" \
      "the daily version-manifest refresh has been unable to run for $skips days \
running, so the manifest is going stale. The packages serve whatever was last \
pushed, so users are citing an increasingly out-of-date version record. The log \
below says why it could not run."
  fi
else
  echo 0 > "$STATE_FILE"
fi

if [[ "$rc" -ne 0 && "$rc" -ne 2 ]]; then
  if grep -q "refusing to write" "$LOG_FILE"; then
    alert "RENUMBER REFUSED" \
      "the daily version-manifest refresh refused to write, because rebuilding \
the history would change an IRW version number that is already committed. That \
should not happen: a version number is a citation. Something changed on Redivis \
-- most likely a version was deleted or unreleased. Do not run with --rebuild \
until you know which."
  else
    alert "FAILED" "the daily version-manifest refresh failed."
  fi
fi

exit 0
