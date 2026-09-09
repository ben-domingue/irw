# verify_imos_1993.R -- Step 5b evidence for imos_1993 (34th IMO, Istanbul, 1993).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1993 problem paper
# (https://www.imo-official.org/assets/documents/problems/1993/1993_eng.pdf;
# day 1 prints problems 1-3, day 2 prints the problems universally numbered 4-6).
#
# WHY THIS IS FALSIFIABLE: the same organisation publishes the per-contestant
# marks for 1993 under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/1993/, 413 contestants).
# If IRW's problem1..problem6 are that same P1..P6, the mark distribution of each
# IRW item must reproduce the official column cell for cell. Any permutation of
# item text across items shows up as a permutation of these 48 cells -- provided
# the six distributions are pairwise distinct, which the script also checks, so
# the assignment is unique rather than merely consistent.
#
# Hard-coded below: the official 1993 individual-results page, scraped
# 2026-09-07, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1993"

OFFICIAL <- matrix(c(
 208,  91,   6,   1,   1,   1,  13,  92,   # P1
 183,  32,  98,  19,  12,   6,   6,  57,   # P2
 293,  33,   6,  15,  21,   7,   8,  30,   # P3
 145,  43,  55,  55,  35,  26,  15,  39,   # P4
  43,  92,  44,  65,  32,  19,  27,  91,   # P5
 186,  38,  81,  22,  20,  26,   6,  34),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 413 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1993') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed numbering for the same competition,\n",
    "which is a documentary fact rather than something this script can test.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
