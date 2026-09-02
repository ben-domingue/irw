# Usage: Rscript normalize_nulls.R <batch_dir_or_csv> [--dry-run]
#
# Normalizes how "no value" is written on disk in {table}__items.csv files so
# batch output matches the convention already published on Redivis.
#
# The convention, established empirically (2026-08-17) by sampling 20 of the
# 422 curated tables via irw::irw_itemtext(): 19/20 represent an absent
# section_prompt / instructions / option_text / correct_response as the
# literal token NA, and only one contains empty strings at all (1,664 NA
# cells vs 109 empty across the sample). That is exactly what R's write.csv()
# emits for a true NA by default (na = "NA"), which is how the older join.R +
# upload path produced it -- so it is arguably an artifact rather than a
# deliberate choice. It is nonetheless the corpus-wide state, and a corpus
# split between two conventions is worse than either one, so new batch output
# is normalized to match rather than diverge.
#
# WHY THIS COMPARES BYTES, NOT PARSED VALUES: read.csv() maps all three
# on-disk forms -- unquoted empty (,,), quoted empty (,""), and the NA token
# -- to the same in-memory NA. So inspecting the parsed data frame cannot
# tell you which form a file actually uses, and a check written that way
# silently passes files that are on-disk inconsistent. Instead this renders
# the canonical form with write.csv() and diffs it against the file as it
# stands, rewriting only on a real difference. As a side effect this also
# makes quoting style consistent (write.csv quotes character columns and
# leaves numerics bare), which is likewise what the corpus already looks like.
#
# Idempotent: a file already in canonical form is left byte-identical.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) stop("Usage: Rscript normalize_nulls.R <batch_dir_or_csv> [--dry-run]")
target <- sub("/$", "", args[1])
dry_run <- "--dry-run" %in% args

files <- if (dir.exists(target)) {
    list.files(target, pattern = "__items\\.csv$", full.names = TRUE)
} else if (file.exists(target)) {
    target
} else {
    stop("No such file or directory: ", target)
}
if (length(files) == 0) stop("No *__items.csv files found in ", target)

# Render the canonical on-disk form of a parsed frame, as a character vector
# of lines, without touching the filesystem.
canonical_lines <- function(items) {
    for (cn in names(items)) {
        if (!is.character(items[[cn]])) next
        blank <- !is.na(items[[cn]]) & trimws(items[[cn]]) == ""
        items[[cn]][blank] <- NA_character_
    }
    tc <- textConnection(NULL, "w")
    on.exit(close(tc), add = TRUE)
    utils::capture.output(write.csv(items, row.names = FALSE))
}

changed <- 0L
for (path in files) {
    items <- read.csv(path, stringsAsFactors = FALSE)
    want <- canonical_lines(items)
    have <- readLines(path, warn = FALSE)

    if (identical(want, have)) {
        cat(sprintf("  ok        %s\n", basename(path)))
        next
    }

    # Report what is actually differing, so the change is reviewable rather
    # than a black-box rewrite.
    n_diff <- sum(want != have[seq_along(want)], na.rm = TRUE)
    changed <- changed + 1L
    cat(sprintf("  %s %s (%d line%s differ)\n",
                if (dry_run) "would fix" else "fixed    ",
                basename(path), n_diff, if (n_diff == 1L) "" else "s"))
    if (!dry_run) writeLines(want, path)
}

cat(sprintf("\n%d of %d file%s %s.\n", changed, length(files),
            if (length(files) == 1L) "" else "s",
            if (dry_run) "would be normalized" else "normalized"))
