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
# on failure, or when the append is refused -- see below.
#
# Why an append can be refused, and why that is an alert rather than a retry:
# an IRW version number is a citation, so red_up.manifest recomputes the whole
# history and stops if any number already committed would come to mean
# something else. That should never happen. If it does, something changed on
# Redivis that the model did not anticipate -- a deleted version, an unreleased
# release -- and a human has to look before the file moves.
set -uo pipefail

export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

REPO_DIR="$HOME/Dropbox/projects/irw/src"
MANIFEST="metadata/version_manifest.tsv"
LOG_DIR="$REPO_DIR/metadata/pipeline_logs"
DATE="$(date +%F)"
LOG_FILE="$LOG_DIR/version_manifest_${DATE}.log"
GH_REPO="ben-domingue/irw"
GH_MENTION="@ben-domingue"
BRANCH="main"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR" || exit 1

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
(
  echo "# IRW version manifest refresh -- $DATE"
  echo

  # Only ever touch main, and only from a clean tree. The working copy is a
  # live checkout Ben edits: committing from whatever branch happened to be
  # checked out, or sweeping up unrelated staged work, would be worse than
  # skipping a day.
  branch="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$branch" != "$BRANCH" ]]; then
    echo "SKIP: on branch '$branch', not '$BRANCH'. Nothing done."
    exit 0
  fi
  if [[ -n "$(git status --porcelain -- "$MANIFEST")" ]]; then
    echo "SKIP: $MANIFEST has uncommitted local changes. Nothing done."
    exit 0
  fi

  git pull --ff-only origin "$BRANCH" 2>&1 || {
    echo "ERROR: could not fast-forward $BRANCH."
    exit 1
  }

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
  git push origin "$BRANCH" 2>&1 || {
    echo "ERROR: push failed. The commit is local; the packages read the "
    echo "pushed copy, so this must be resolved by hand."
    exit 1
  }
  echo "Committed and pushed ${added:-?} new row(s)."
  exit 0
) > "$LOG_FILE" 2>&1

rc=$?
if [[ "$rc" -ne 0 ]]; then
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
