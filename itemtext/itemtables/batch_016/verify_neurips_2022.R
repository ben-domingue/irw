# verify_neurips_2022.R
#
# NOTE ON SCOPE. No item text was shipped for neurips_2022 (see
# notes_neurips_2022.csv): the NeurIPS 2022 Eedi starter kit distributes
# QuestionId as a bare identifier and ships NO question content -- no text and,
# unlike the 2020 release, no images either. So there is no item_text->item
# mapping to verify, and verification_neurips_2022.csv records NO_ROUTE.
#
# What this script DOES verify is the fact a later pass has to stand on: what
# the IRW `item` integer actually refers to. The IRW codes are bare 1..5730,
# assigned by a processing script (data/eedi.R in the repo root is a one-line
# comment and carries no code), so the referent of `item` is not self-evident.
# The claim under test:
#
#     item = the 1-based rank of QuestionId in ascending numeric order over the
#            5730 distinct QuestionId values in
#            Task_3_dataset/checkins_lessons_checkouts_training.csv
#
# The falsifiable prediction is the per-item response count. This script
# compares, for all 5730 items, the live per-item n (server-side aggregate --
# irw_table_sets(), NOT irw_fetch(); the table is 509,957 rows and exporting it
# spends export quota for nothing) against the count of non-missing IsCorrect
# rows for the QuestionId the claim assigns to that item.
#
# It also prints the rival hypothesis (first-appearance order) so the reader can
# see the check has teeth rather than passing by construction.
#
# Source download: ~307MB, cached under itemtext/.cache/neurips_2022/kit.zip and
# reused if present.

suppressMessages(library(irw))

TABLE <- "neurips_2022"
URL   <- "https://dqanonymousdata.blob.core.windows.net/neurips-public/neurips-2022-starter-kit.zip"

## ---- locate / populate the cache -------------------------------------------
this_file <- (function() {
    a <- commandArgs(trailingOnly = FALSE)
    f <- sub("^--file=", "", a[grepl("^--file=", a)])
    if (length(f)) normalizePath(f) else NA_character_
})()
cache <- if (!is.na(this_file))
    file.path(dirname(dirname(dirname(this_file))), ".cache", TABLE) else
    file.path(".cache", TABLE)
dir.create(cache, recursive = TRUE, showWarnings = FALSE)

kit <- file.path(cache, "kit.zip")
csv <- file.path(cache, "t3", "Task_3_dataset",
                 "checkins_lessons_checkouts_training.csv")

if (!file.exists(csv)) {
    if (!file.exists(kit)) {
        cat("downloading starter kit (~307MB) to", kit, "...\n")
        utils::download.file(URL, kit, mode = "wb", quiet = TRUE)
    }
    tmpd <- tempfile(); dir.create(tmpd)
    utils::unzip(kit, files = "Task_3_dataset.zip", exdir = tmpd)
    utils::unzip(file.path(tmpd, "Task_3_dataset.zip"),
                 exdir = file.path(cache, "t3"))
}
stopifnot(file.exists(csv))

## ---- source-side counts ----------------------------------------------------
src <- utils::read.csv(csv, colClasses = "character")
qid <- as.integer(src$QuestionId)
has <- nzchar(src$IsCorrect)

qs   <- sort(unique(qid))                       # ascending QuestionId
n_src <- table(factor(qid[has], levels = qs))   # non-missing-resp rows per QuestionId

## rival hypothesis: order of first appearance
first <- qid[!duplicated(qid)]

## ---- live-side counts (server-side aggregate, no export) -------------------
s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
pi$item <- as.integer(as.character(pi$item))
pi <- pi[order(pi$item), ]

cat(sprintf("live items: %d (range %d..%d)   source QuestionIds: %d (range %d..%d)\n",
            nrow(pi), min(pi$item), max(pi$item),
            length(qs), min(qs), max(qs)))

n_live <- pi$n[match(seq_along(qs), pi$item)]

cat("\nclaimed mapping, first 8 and last 3 items:\n")
cat(sprintf("%-6s %-12s %10s %10s\n", "item", "QuestionId", "n_source", "n_live"))
for (i in c(1:8, (length(qs) - 2):length(qs)))
    cat(sprintf("%-6d %-12d %10d %10d\n", i, qs[i], as.integer(n_src[i]), n_live[i]))

mismatch <- sum(as.integer(n_src) != n_live)
cat(sprintf("\nclaimed mapping (ascending QuestionId): %d of %d items mismatch on n\n",
            mismatch, length(qs)))

## rival
n_rival <- as.integer(table(factor(qid[has], levels = first)))
mis_rival <- sum(n_rival != n_live)
cat(sprintf("rival mapping (first-appearance order): %d of %d items mismatch on n\n",
            mis_rival, length(first)))

## ---- what this does NOT establish ------------------------------------------
tab <- table(as.integer(n_src))
uniq <- sum(as.integer(n_src) %in% as.integer(names(tab))[tab == 1])
cat(sprintf("\nOnly %d of %d items have an n that no other item shares, so the n-vector\n",
            uniq, length(qs)))
cat("cannot by itself separate two items inside an equal-n class: the check rules out\n")
cat("wholesale re-orderings (the rival above), not a swap of two same-n neighbours.\n")
cat("It establishes what `item` REFERS TO; it verifies no item_text mapping, because\n")
cat("this table ships none -- the 2022 Eedi release publishes no question content.\n")

cat(if (mismatch == 0 && mis_rival > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
