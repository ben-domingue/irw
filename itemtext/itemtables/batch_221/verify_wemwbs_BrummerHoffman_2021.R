# verify_wemwbs_BrummerHoffman_2021.R
#
# This table is BLOCKED on instrument rights (irw#1945 reserve-a-right test): the
# University of Warwick's WEMWBS non-commercial licence states it "does not give you
# permission to publicly share WEMWBS or for you to provide WEMWBS to other parties for
# their use under your licence"
# (https://warwick.ac.uk/fac/sci/med/research/platform/wemwbs/using/register/,
#  sha256:74ec29283e230ddc6eb325323f382e03c29efb232ea0d6e58ef8890bdfb9e900, fetched 2026-09-16).
#
# There is therefore NO item_text<->item mapping to verify -- none was ever formed.
# What this script verifies instead is the only falsifiable claim the round makes:
# that the block HELD, i.e. that no WEMWBS/SWEMWBS wording was shipped for any of the
# live items. It prints the numbers it compares. It does NOT establish anything about
# item-to-text correspondence.

suppressMessages(library(irw))

TABLE <- "wemwbs_BrummerHoffman_2021"
BATCH <- dirname(normalizePath(sub("^--file=", "",
           grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)[1])))
if (is.na(BATCH) || !nzchar(BATCH)) BATCH <- "."

## 1. Live ground truth -- set fetch only, no full-table export.
ts <- irw::irw_table_sets(TABLE)
live_items <- sort(unique(as.character(unlist(ts$item))))
live_resp  <- sort(unique(as.numeric(unlist(ts$resp))))
cat(sprintf("live items (n=%d): %s\n", length(live_items), paste(live_items, collapse = ", ")))
cat(sprintf("live resp  (n=%d): %s\n", length(live_resp),  paste(live_resp,  collapse = ", ")))

## 2. Shipped item text for this table, if any.
f <- file.path(BATCH, paste0(TABLE, "__items.csv"))
shipped <- if (file.exists(f)) nrow(read.csv(f, stringsAsFactors = FALSE)) else 0L
cat(sprintf("rows in %s: %d (expected 0 -- rights block)\n", basename(f), shipped))

## 3. No WEMWBS wording anywhere in the batch's text-bearing outputs.
#    Distinctive SWEMWBS stems; any hit means wording leaked into a shipped file.
STEMS <- c("feeling optimistic about the future", "been feeling useful",
           "been feeling relaxed", "dealing with problems well",
           "been thinking clearly", "feeling close to other people",
           "make up my own mind about things")
csvs <- list.files(BATCH, pattern = "__items\\.csv$", full.names = TRUE)
hits <- 0L
for (p in csvs) {
    txt <- tolower(paste(readLines(p, warn = FALSE), collapse = "\n"))
    for (s in STEMS) if (grepl(tolower(s), txt, fixed = TRUE)) {
        hits <- hits + 1L
        cat(sprintf("  LEAK: %s contains %s\n", basename(p), dQuote(s)))
    }
}
cat(sprintf("SWEMWBS stem strings found across %d shipped __items.csv file(s): %d (expected 0)\n",
            length(csvs), hits))

cat(sprintf("\ncoverage: %d of %d live items carry shipped wording; %d of %d live resp levels carry option_text\n",
            0L, length(live_items), 0L, length(live_resp)))
cat("This verifies only that the rights block held. It establishes NOTHING about any\n",
    "item-to-text mapping, because no item text was extracted for this table.\n", sep = "")

cat(if (shipped == 0L && hits == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
