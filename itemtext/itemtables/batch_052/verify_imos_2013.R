# verify_imos_2013.R -- Step 5b evidence for imos_2013 (54th IMO, Santa Marta, Colombia).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2013 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2013/2013_eng.pdf).
# The 2013 paper prints the numbers outright -- Day 1 carries Problems 1-3 and
# Day 2 carries Problems 4-6 -- so no day-numbering convention is inferred.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for the same
# competition under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/2013/, embedded JSON
# "scores":[P1..P6], 527 contestants). If IRW's problem1..problem6 are that same
# P1..P6, each IRW item's distribution of marks 0..7 must reproduce the official
# column cell for cell. A permutation of item text across items would show up as
# a permutation of these 48 cells -- provided the six distributions are pairwise
# distinct, which the script also checks, so the assignment is unique rather than
# merely consistent.
#
# Hard-coded below: the official 2013 individual-results page, scraped
# 2026-09-07, 527 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2013"

OFFICIAL <- matrix(c(
 118,  96,   9,   6,  14,   3,   5, 276,   # P1
 229,  32,  65,  33,  22,  12,  16, 118,   # P2
 438,  10,  15,  16,   0,   3,   4,  41,   # P3
  82,  16,  14,  14,   2,   5,   9, 385,   # P4
 235,  84,  33,  11,   0,  10,  19, 135,   # P5
 481,  15,   6,   6,   2,   6,   4,   7),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 527 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2013') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2013 contestants: 527\n")

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
# and it is the same mark (4) in both -- P3 and P5. Everything else is occupied.
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
    "It also says nothing about the verbatim accuracy of the transcription, nor\n",
    "about the English-vs-administered-language caveat: the IMO paper is sat in\n",
    "each contestant's own language.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
