#!/usr/bin/env Rscript
# Usage: Rscript check_issues_page.R [<site_qmd_path>]
#
# Run from itemtext/. Reconciles every batch's provenance.csv against the live
# public issues page and reports which tables owe it an entry.
#
# A note is DUE once the table is live, not when the batch is triaged: the page
# describes the data a reader can actually fetch, so an entry written before
# upload would describe a table that does not exist yet. That gap is exactly how
# emidy2024_fevs, mohammed_2021_job_satisfaction and
# himmelstein-impossible_question-2025 were uploaded with a written public_note
# that never reached the page -- each was uploaded in a commit separate from the
# one that triaged its batch, and nothing re-checked afterwards.
#
# A note you deliberately dropped as below the issues-page bar goes in
# fixes/issues_page_dropped.csv (table,reason) so it stops being reported.
#
# Exit status 1 if anything is DUE, so it can gate an upload wrap-up.

args <- commandArgs(trailingOnly = TRUE)
qmd <- if (length(args)) args[1] else "../../irw_site/itemtext_issues.qmd"

# Liveness comes from Redivis, not from the provenance CSV (#1828).
#
# `uploaded` is a hand-maintained mirror of a fact Redivis already holds, and it
# has been wrong in both directions: himmelstein-admc_raw-2025 read as PENDING
# while it was live, and 16 rows named a live table with the column left blank.
# So whether a table is live is read from `live_tables.csv`, a committed
# snapshot of the published shards written by itemtext/refresh_live_tables.py.
#
# It is a snapshot rather than an API call because this script runs with no
# credentials and no network, and that is worth keeping -- it gates an upload
# wrap-up on a machine with no token. The cost is that the snapshot ages, so its
# date is printed and a stale one is loud. With no snapshot at all the script
# still runs, falling back to `uploaded`, and says that it did.
#
# `uploaded` keeps its other job: recording WHEN. Redivis cannot reconstruct
# that -- opening a draft copies the dataset and resets every per-table
# timestamp -- which is why the #1828 rows were left blank rather than stamped
# with a date known to be wrong.
snap_file <- "live_tables.csv"
snap <- NULL          # published: what a reader can fetch today
snap_draft <- character(0)   # uploaded, not released yet
snap_asof <- NA_character_
if (file.exists(snap_file)) {
  .raw <- readLines(snap_file, warn = FALSE)
  .hdr <- grep("^#.* as of ", .raw, value = TRUE)
  if (length(.hdr)) snap_asof <- trimws(sub(".* as of ", "", .hdr[1]))
  .snap <- read.csv(text = paste(grep("^#", .raw, invert = TRUE, value = TRUE),
                                 collapse = "\n"), stringsAsFactors = FALSE)
  snap <- .snap$table[.snap$status == "published"]
  snap_draft <- .snap$table[.snap$status == "draft"]
}

if (!file.exists(qmd)) {
  stop("issues page not found at ", qmd,
       " -- pass the path explicitly; the site checkout is a sibling of src/")
}
page <- paste(readLines(qmd, warn = FALSE), collapse = "\n")

# Say which copy of the page this read. The default sibling checkout is often
# parked on another branch -- on 2026-09-02 it sat 60 entries behind main, and a
# sibling checker reported a gap that had already been closed. Silence about the
# source is how a stale answer passes for a real one.
cat(sprintf("issues page: %s (%d entries)\n", qmd,
            sum(grepl("^- table:", strsplit(page, "\n")[[1]]))))
.br <- suppressWarnings(system2("git", c("-C", shQuote(dirname(normalizePath(qmd))),
                                         "rev-parse", "--abbrev-ref", "HEAD"),
                                stdout = TRUE, stderr = FALSE))
if (length(.br) && !is.na(.br[1]) && nzchar(.br[1]) && .br[1] != "main")
  cat(sprintf("  NOTE: that checkout is on branch '%s', not main -- it may be stale.\n", .br[1]))

# Every provenance record, not only the batches. The language backfill's 78
# tables live outside itemtables/, and while this glob was batch-only they were
# invisible here -- which is how 60 tables shipping project-generated English
# came to owe an issues-page entry with nothing reporting it (#1777, 2026-09-02).
# A reconciler that silently does not see half the corpus is worse than none.
provs <- c(Sys.glob("itemtables/batch_*/provenance.csv"),
           Sys.glob("language_backfill/*provenance.csv"))
provs <- provs[file.exists(provs)]
if (!length(provs)) stop("no provenance.csv found -- run from itemtext/")

rows <- do.call(rbind, lapply(provs, function(f) {
  x <- read.csv(f, stringsAsFactors = FALSE)
  for (col in c("table", "public_note", "uploaded")) {
    if (!col %in% names(x)) x[[col]] <- NA_character_
  }
  # backfill_provenance.csv records the translation's origin rather than a
  # public_note, so derive the obligation from the value: a machine translation
  # is project-generated content and is disclosed (ratified 2026-09-02).
  if (!"public_note" %in% names(x) || all(is.na(x$public_note))) {
    if ("translation_source" %in% names(x)) {
      x$public_note <- ifelse(trimws(x$translation_source) == "machine_translation",
                              "English in the _translated columns was generated by IRW, not by the study.",
                              NA_character_)
    }
  }
  data.frame(batch = basename(dirname(f)), table = x$table,
             public_note = x$public_note, uploaded = x$uploaded,
             note = if ("note" %in% names(x)) x$note else NA_character_,
             stringsAsFactors = FALSE)
}))

has <- function(v) !is.na(v) & nzchar(trimws(v))

# A date, `unrecorded`, or empty. `unrecorded` means the table is live but the
# date is not recoverable -- see #1828; it is a stamp, not a gap.
stamped <- has(rows$uploaded) & !trimws(rows$uploaded) %in% c("NA", "unrecorded")
rows$dated <- stamped
rows$claims_live <- stamped | (has(rows$uploaded) & trimws(rows$uploaded) == "unrecorded")

# A table can hold more than one provenance row -- a language backfill records a
# second event for the same table, and a redone batch supersedes an earlier one
# (duboz_2021_swls, the enkavi_2019 trio). The stamp is a property of the TABLE,
# so resolve it across every row naming it; otherwise a superseded row reads as
# an unstamped upload.
tbl_stamped <- unique(rows$table[rows$claims_live])

if (!is.null(snap)) {
  rows$live <- rows$table %in% snap
} else {
  rows$live <- rows$claims_live
}
# Keep every row for the CSV-vs-Redivis reconciliation below: a stale
# `uploaded` is worth reporting whether or not that table owes a public note.
all_rows <- rows
rows <- rows[has(rows$public_note), ]
rows$on_page <- vapply(rows$table, function(t) grepl(t, page, fixed = TRUE), logical(1))

dropped <- character(0)
drop_file <- "fixes/issues_page_dropped.csv"
if (file.exists(drop_file)) {
  dropped <- read.csv(drop_file, stringsAsFactors = FALSE)$table
}
rows$dropped <- rows$table %in% dropped

rows$in_draft <- rows$table %in% snap_draft

due     <- rows[rows$live & !rows$on_page & !rows$dropped, ]
pending <- rows[!rows$live & !rows$on_page & !rows$dropped, ]
# A table in the draft is neither live nor missing: it goes live at the next
# release, so an entry written for it now is early but correct, not wrong.
early   <- rows[!rows$live & rows$on_page & !rows$in_draft, ]
staged  <- rows[!rows$live & rows$on_page & rows$in_draft, ]

if (is.null(snap)) {
  cat("liveness: NO SNAPSHOT -- falling back to the `uploaded` column, which is\n",
      "  exactly the thing #1828 found lying. Run, with credentials:\n",
      "    python3 refresh_live_tables.py\n", sep = "")
} else {
  .age <- suppressWarnings(as.integer(Sys.Date() - as.Date(snap_asof)))
  cat(sprintf("liveness: live_tables.csv, %d published tables, taken %s%s\n",
              length(snap), snap_asof,
              if (!is.na(.age) && .age > 7)
                sprintf(" -- %d DAYS OLD, refresh it", .age) else ""))
}

cat(sprintf("%d tables carry a public_note; %d live, %d on the page, %d dropped as below the bar\n",
            nrow(rows), sum(rows$live), sum(rows$on_page), sum(rows$dropped)))

if (nrow(due)) {
  cat("\nDUE -- uploaded but absent from the page:\n")
  for (i in seq_len(nrow(due))) {
    .when <- trimws(due$uploaded[i])
    if (is.na(.when) || !nzchar(.when) || .when %in% c("NA", "unrecorded"))
      .when <- "date not recorded"
    cat(sprintf("  %-42s %s (uploaded %s)\n", due$table[i], due$batch[i], .when))
  }
  cat("\nApply the issues-page bar before pasting: concrete text-vs-table\n",
      "mismatches only, not gaps the source never published. If one of these\n",
      "does not clear the bar, record it in ", drop_file, " with a reason\n",
      "rather than leaving it to be re-reported every run.\n", sep = "")
}

if (nrow(pending)) {
  cat("\nPENDING -- note written, table not live yet (correctly absent):\n")
  cat(sprintf("  %-42s %s%s\n", pending$table, pending$batch,
              ifelse(pending$in_draft, "  [in the draft -- live at the next release]", "")),
      sep = "")
}

if (nrow(staged)) {
  cat("\nSTAGED -- on the page and in the draft. Correct once the draft is\n",
      "released; until then the page is ahead of what a reader can fetch.\n", sep = "")
  cat(sprintf("  %-42s %s\n", staged$table, staged$batch), sep = "")
}

if (nrow(early)) {
  cat("\nCHECK -- on the page but not live. The page is describing a table\n",
      "nobody can fetch: either it was never uploaded, or it was withdrawn\n",
      "and its entry should go too.\n", sep = "")
  cat(sprintf("  %-42s %s\n", early$table, early$batch), sep = "")
}

# The two ways the CSV and Redivis disagree. Neither blocks the exit status:
# they are bookkeeping, not an unwritten disclosure, and a withdrawal is a
# legitimate reason for the second. Reported every run so they cannot silently
# accumulate the way the #1828 sixteen did.
if (!is.null(snap)) {
  owed <- setdiff(unique(all_rows$table[all_rows$live]), tbl_stamped)
  if (length(owed)) {
    cat("\nSTAMP OWED -- live in Redivis, no date in any provenance row:\n")
    for (t in sort(owed))
      cat(sprintf("  %-42s %s\n", t,
                  paste(unique(all_rows$batch[all_rows$table == t]), collapse = ", ")))
    cat("Stamp the upload date if you know it. If it is not recoverable, write\n",
        "`unrecorded`: it says the same thing this check does, in the file, and\n",
        "a fabricated date is worse than a named gap (#1828).\n", sep = "")
  }

  all_rows$in_draft <- all_rows$table %in% snap_draft
  gone <- setdiff(unique(all_rows$table[all_rows$claims_live & !all_rows$in_draft]),
                  snap)
  # A withdrawal is the expected reason a stamped table is not live, and it is
  # already recorded -- in one of two places, because the two withdrawal rounds
  # wrote it differently. tools/withdraw_wording_rights.py rewrites the
  # public_note to open "IRW does not offer item text for", which is the signal
  # check_provenance.R reads (#2034); the PROMIS round instead wrote WITHDRAWN
  # at the head of the private note and left public_note empty. Both are read
  # here: a withdrawal recorded in the wrong field is still a withdrawal, and
  # treating it as a lost upload would send someone hunting for nothing.
  said <- function(v, prefix) !is.na(v) & startsWith(trimws(v), prefix)
  withdrawn <- unique(all_rows$table[
      said(all_rows$public_note, "IRW does not offer item text for") |
      said(all_rows$note, "WITHDRAWN")])
  lost <- setdiff(gone, withdrawn)
  if (length(gone)) {
    cat(sprintf("\nGONE -- stamped as uploaded, not live: %d table(s), %d of them recorded withdrawals.\n",
                length(gone), length(gone) - length(lost)))
    if (length(lost)) {
      cat("  Not recorded as withdrawn -- an upload that did not survive, a\n",
          "  rename, or a withdrawal nobody wrote down:\n", sep = "")
      for (t in sort(lost))
        cat(sprintf("    %-40s %s\n", t,
                    paste(unique(all_rows$batch[all_rows$table == t]), collapse = ", ")))
    } else {
      cat("  All of them are recorded withdrawals; nothing unexplained.\n")
    }
  }
}

if (!nrow(due)) cat("\nNothing due.\n")
quit(status = if (nrow(due)) 1L else 0L)
