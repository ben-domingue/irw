# verify_whodas_BrummerHoffman_2021.R
#
# This table is BLOCKED on instrument rights (irw#1945 reserve-a-right test). The
# instrument is the WHO Disability Assessment Schedule 2.0, 12-item version (WHODAS-12);
# the rights holder is the World Health Organization. WHO's own WHODAS 2.0 page states
# "To license WHODAS 2.0, such as for including WHODAS 2.0 in an electronic records or
# data capture system or reproducing it in any way, please go to Licensing WHO
# Classifications."
# (https://www.who.int/standards/classifications/international-classification-of-functioning-disability-and-health/who-disability-assessment-schedule,
#  sha256:f48caeaad1654e7a5e009e412e1983bd0623fa47817e003b12674ae836f28d68, fetched 2026-09-16),
# and the page it routes to places all WHO publications under CC BY-NC-SA 3.0 IGO, with
# any other use "subject to permission being granted by WHO"
# (https://www.who.int/about/policies/publishing/copyright,
#  sha256:ca58b25d4653139d8a04ac9ab6cf6a0e285972c1541cb42d4b77616e44a957a2, fetched 2026-09-16).
#
# There is therefore NO item_text<->item mapping to verify -- none was ever formed.
# What this script verifies instead is the only falsifiable claim the round makes:
# that the block HELD, i.e. that no WHODAS 2.0 wording was shipped for any of the live
# items. It prints the numbers it compares. It does NOT establish anything about
# item-to-text correspondence.

suppressMessages(library(irw))

TABLE <- "whodas_BrummerHoffman_2021"
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

## 3. No WHODAS 2.0 wording anywhere in the batch's text-bearing outputs.
#    Distinctive WHODAS-12 stem fragments; any hit means wording leaked into a shipped file.
STEMS <- c("standing for long periods",
           "taking care of your household responsibilities",
           "learning a new task",
           "joining in community activities",
           "how much have you been emotionally affected",
           "concentrating on doing something for ten minutes",
           "walking a long distance",
           "washing your whole body",
           "getting dressed",
           "dealing with people you do not know",
           "maintaining a friendship",
           "your day-to-day work")
csvs <- list.files(BATCH, pattern = "__items\\.csv$", full.names = TRUE)
hits <- 0L
for (p in csvs) {
    txt <- tolower(paste(readLines(p, warn = FALSE), collapse = "\n"))
    for (s in STEMS) if (grepl(tolower(s), txt, fixed = TRUE)) {
        hits <- hits + 1L
        cat(sprintf("  LEAK: %s contains %s\n", basename(p), dQuote(s)))
    }
}
cat(sprintf("WHODAS 2.0 stem strings found across %d shipped __items.csv file(s): %d (expected 0)\n",
            length(csvs), hits))

cat(sprintf("\ncoverage: %d of %d live items carry shipped wording; %d of %d live resp levels carry option_text\n",
            0L, length(live_items), 0L, length(live_resp)))
cat("This verifies only that the rights block held. It establishes NOTHING about any\n",
    "item-to-text mapping, because no item text was extracted for this table.\n", sep = "")

cat(if (shipped == 0L && hits == 0L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
