# 12_stragglers.R
#
# Names the tables that are stuck (issue #1765, sub-action 2.5b).
#
# A table live on Redivis with no row in metadata.csv is NORMAL. 01_metadata.R
# carries a `refresh.per.run` throttle, so at any moment some live tables have
# not been described yet; #1704 established that a snapshot count of missing
# metadata measures throttle position, not pipeline health. Alerting on that
# count trains everyone to ignore the alert.
#
# What is NOT normal is the same table still missing several runs later. That
# means it is stuck -- an unreleased warehouse, or 01_metadata.R failing on
# that specific table -- and it will stay stuck indefinitely because nothing
# distinguishes it from the throttle backlog.
#
# So this script alerts on a NAMED TABLE that has persisted, never on a count.
# Doing that requires memory across runs, which is the whole reason the watch
# file exists:
#
#   straggler_watch.tsv   table, first_seen, last_seen, cycles
#
# A table appears when it is first seen live-without-metadata, accumulates a
# cycle per run, and is removed the moment it gets a metadata row. Anything
# that survives more than --cycles runs (default 2, i.e. flagged on the third)
# is reported by name.
#
# Unlike 09/11 this DOES call Redivis, unavoidably: the question is which live
# tables are absent from metadata.csv, so metadata.csv cannot be the catalog.
#
# Usage (from metadata/, like the rest of the numbered scripts):
#   Rscript 12_stragglers.R
#   Rscript 12_stragglers.R --cycles 3 --watch straggler_watch.tsv
#   Rscript 12_stragglers.R --live-from live.txt    # offline: one table per line

suppressPackageStartupMessages({
    library(readr)
})

args <- commandArgs(trailingOnly = TRUE)
arg <- function(flag, default) {
    i <- match(flag, args)
    if (is.na(i) || i == length(args)) default else args[[i + 1L]]
}
dir       <- arg("--dir", ".")
watch_out <- arg("--watch", file.path(dir, "straggler_watch.tsv"))
live_from <- arg("--live-from", NA_character_)
max_ok    <- as.integer(arg("--cycles", "2"))
##Below this, a live-catalog fetch is assumed broken rather than believed. An
##empty or truncated fetch would otherwise read as "every table is missing
##metadata", flag the entire corpus, and destroy the watch file's history.
min_live  <- as.integer(arg("--min-live", "1000"))

key <- function(x) tolower(trimws(as.character(x)))

meta_path <- file.path(dir, "metadata.csv")
if (!file.exists(meta_path)) {
    stop("metadata.csv not found in ", normalizePath(dir, mustWork = FALSE),
         ". Run 01_metadata.R first.", call. = FALSE)
}
described <- key(read_csv(meta_path, show_col_types = FALSE)$table)

live <- if (!is.na(live_from)) {
    key(readLines(live_from, warn = FALSE))
} else {
    key(irw::irw_list_tables(source = "core")$name)
}
live <- live[nzchar(live)]

if (length(live) < min_live) {
    stop("live catalog returned ", length(live), " table(s); expected at least ",
         min_live, ". Refusing to update the watch file -- a truncated fetch ",
         "would flag the whole corpus and erase the history that makes this ",
         "script work.", call. = FALSE)
}

missing <- sort(setdiff(live, described))
today   <- format(Sys.Date())

prev <- if (file.exists(watch_out)) {
    read_tsv(watch_out, show_col_types = FALSE,
             col_types = cols(.default = col_character()))
} else {
    data.frame(table = character(), first_seen = character(),
               last_seen = character(), cycles = character())
}

##Resolved: on the watch last run, has a metadata row now. Dropped silently --
##that is the system working, and reporting it would recreate the noisy count.
resolved <- setdiff(prev$table, missing)

carried <- prev[prev$table %in% missing, , drop = FALSE]
##Built explicitly rather than with a recycled scalar for last_seen: when
##nothing is missing -- the healthy state, and the state on the day this was
##written -- `today` is length 1 against zero-length columns and data.frame()
##errors on the mismatch. The empty case is the one this script spends most of
##its life in, so it is the one that has to work.
seen <- match(missing, carried$table)
watch <- data.frame(
    table      = missing,
    first_seen = ifelse(is.na(seen), today, carried$first_seen[seen]),
    last_seen  = rep(today, length(missing)),
    cycles     = ifelse(is.na(seen), 1L,
                        as.integer(carried$cycles[seen]) + 1L),
    stringsAsFactors = FALSE
)

write_tsv(watch, watch_out)

stuck <- watch[watch$cycles > max_ok, , drop = FALSE]
stuck <- stuck[order(-stuck$cycles, stuck$table), , drop = FALSE]

cat(sprintf("%s: %d live | %d described | %d awaiting metadata | %d resolved since last run\n",
            today, length(live), length(described), length(missing), length(resolved)))

if (nrow(stuck) == 0L) {
    cat("no stragglers: nothing has been waiting more than ", max_ok,
        " run(s)\n", sep = "")
    quit(status = 0L)
}

##Named, with how long, because "3 tables are stuck" is not actionable and
##"these 3 tables have been stuck since 2026-07-04" is.
cat("\nSTRAGGLERS -- live for more than ", max_ok,
    " run(s) with no metadata row:\n", sep = "")
for (i in seq_len(nrow(stuck))) {
    cat(sprintf("  %-52s %2s cycles, first seen %s\n",
                stuck$table[i], stuck$cycles[i], stuck$first_seen[i]))
}
cat("\nEach is stuck for a reason -- an unreleased warehouse, or 01_metadata.R\n",
    "failing on that table. Check 01 before assuming the throttle.\n", sep = "")
quit(status = 1L)
