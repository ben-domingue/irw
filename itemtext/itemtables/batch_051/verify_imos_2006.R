# verify_imos_2006.R -- Step 5b evidence for imos_2006 (47th IMO, Ljubljana, Slovenia).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2006 problem paper
# (https://www.imo-official.org/assets/documents/problems/2006/2006_eng.pdf).
# For 2006 the paper prints the numbers 1-6 outright (day 1 carries Problems
# 1-3, day 2 carries Problems 4-6), so no day-convention inference is needed.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 2006 under the
# column headings P1..P6 (https://www.imo-official.org/results/individual/year/2006/,
# embedded JSON "scores":[P1..P6], 498 contestants). If IRW's problem1..problem6
# are that same P1..P6, the mark distribution of each IRW item must reproduce the
# official column cell for cell. A permutation of item text across items would
# show up as a permutation of these 48 cells -- provided the six distributions are
# pairwise distinct, which the script also checks, so the assignment is unique
# rather than merely consistent.
#
# Hard-coded below: the official 2006 individual-results page, scraped
# 2026-09-07, 498 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2006"

OFFICIAL <- matrix(c(
  61,   9,  14,  12,  10,  27,   7, 358,   # P1
 176, 210,   0,   3,  15,   8,   8,  78,   # P2
 365,  95,   4,   1,   1,   2,   2,  28,   # P3
  18,  54,  59,  38,   6,   7,  68, 248,   # P4
 303, 101,   8,  25,   6,   5,   2,  48,   # P5
 471,  11,   3,   3,   0,   1,   1,   8),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 498 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2006') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2006 contestants: 498\n")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint: exactly two columns have an unused mark,
# and they are different marks -- P2 has zero 2s, P6 has zero 4s.
zero_cells <- which(OFFICIAL == 0, arr.ind = TRUE)
cat("official zero cells (problem, mark):",
    paste(sprintf("P%d@%d", zero_cells[, 1], zero_cells[, 2] - 1), collapse = " "), "\n")
zero_live <- which(live == 0, arr.ind = TRUE)
cat("live     zero cells (problem, mark):",
    paste(sprintf("P%d@%d", zero_live[, 1], zero_live[, 2] - 1), collapse = " "), "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed 'Problem 1'..'Problem 6' headings for the\n",
    "same competition -- a documentary fact, not something this script can test.\n",
    "It also says nothing about the English-vs-administered-language caveat: the\n",
    "IMO paper is sat in each contestant's own language.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
