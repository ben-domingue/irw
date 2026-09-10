# verify_pickova2025_attitude.R -- Step 5b route 9 (response-frequency matching).
#
# Claim under test: item codes att_1..att_7 correspond POSITIONALLY to columns
# 6..12 (1-based) of the raw Google Forms export
# "DATA - Attitude-Behavior Gap on TEMU and SHEIN (Odpovedi).xlsx"
# (figshare 30576341, file 59422829), whose headers spell out the semantic
# differential adjectives: bad, good, harmful, unpleasant, unwise, fun,
# waste of time.
#
# Falsifiable prediction: the per-item x per-level response frequency table of
# the live IRW data must match, cell for cell, the frequency table computed
# from those raw columns. The seven raw columns have mutually distinct
# frequency vectors, so a permutation of any two items would break at least
# one cell. Numbers hard-coded from the raw file so this runs offline.

suppressMessages(library(irw))

TABLE <- "pickova2025_attitude"

# counts of raw values 1..7 in the raw xlsx, columns in header order
RAW <- rbind(
  "...bad"           = c(47, 35, 16,  8, 13,  8,  7),
  "...good"          = c( 4,  6, 10, 10, 24, 37, 42),
  "...harmful"       = c(52, 22, 20,  9, 15,  6,  9),
  "...unpleasant"    = c(52, 35, 20, 11,  8,  3,  3),
  "...unwise"        = c(48, 31, 17, 12, 12,  7,  6),
  "...fun"           = c( 1,  4,  5,  8, 22, 44, 47),
  "...waste of time" = c(58, 32, 15, 13,  8,  7,  0))
colnames(RAW) <- 1:7

d <- irw::irw_fetch(TABLE)
LIVE <- table(factor(d$item, paste0("att_", 1:7)), factor(d$resp, 1:7))

cat("shipped item_text (in att_1..att_7 order) vs raw column, counts of resp 1..7\n\n")
cat(sprintf("%-18s %-28s %-28s\n", "item / raw header", "raw counts", "live counts"))
ok <- TRUE
for (i in 1:7) {
  r <- RAW[i, ]; l <- as.integer(LIVE[i, ])
  cat(sprintf("%-6s %-11s %-28s %-28s %s\n",
              paste0("att_", i), rownames(RAW)[i],
              paste(r, collapse = " "), paste(l, collapse = " "),
              if (identical(as.integer(r), l)) "match" else "MISMATCH"))
  if (!identical(as.integer(r), l)) ok <- FALSE
}

# a permutation must be detectable: confirm no two raw rows are identical
dupe <- any(duplicated(apply(RAW, 1, paste, collapse = "-")))
cat(sprintf("\nany two raw frequency vectors identical? %s\n", if (dupe) "YES" else "no"))

cat("Note: this pins every item's TEXT to its code (all 7 vectors distinct, all 49\n",
    "cells match). It does NOT establish the response-option anchors: the Google\n",
    "Forms grid publishes no labels for scale points 1-7, so option_text is blank\n",
    "by design and nothing here verifies the resp<->option_text axis.\n", sep = "")

cat(if (ok && !dupe) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
