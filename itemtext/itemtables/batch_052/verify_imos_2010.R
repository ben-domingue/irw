# verify_imos_2010.R -- Step 5b evidence for imos_2010 (51st IMO, Astana, Kazakhstan).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2010 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2010/2010_eng.pdf).
# The 2010 paper prints the numbers 1-6 outright (Day 1, Wednesday 7 July,
# carries Problems 1-3; Day 2, Thursday 8 July, carries Problems 4-6), so no
# day-numbering convention had to be assumed.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for the same
# competition under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/2010/, embedded JSON
# "scores":[P1..P6], 516 contestants). If IRW's problem1..problem6 are that same
# P1..P6, each IRW item's mark distribution must reproduce the official column
# cell for cell. Any permutation of item text across items shows up as a
# permutation of these 48 cells -- provided the six distributions are pairwise
# distinct, which the script also checks, so the assignment is unique rather
# than merely consistent.
#
# Hard-coded below: the official 2010 individual-results page, scraped
# 2026-09-07, 516 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2010"

OFFICIAL <- matrix(c(
  39,  17,  27,  16,  34,  35,  54, 294,   # P1
 223,  93,  23,   8,   2,   4,   2, 161,   # P2
 428,  48,  10,   4,   4,   4,   2,  16,   # P3
  84,   2,  10,  47,   2,   4,   2, 365,   # P4
 352,  85,  26,   3,   0,   2,  11,  37,   # P5
 470,  14,   4,   3,   0,   6,   4,  15),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 516 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2010') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2010 contestants: 516\n")

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
# and it is the same mark in both -- P5 and P6 each have zero 4s, and no other
# problem has any unused mark level.
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
    "IMO paper is sat in each contestant's own language, and this table ships the\n",
    "official English version.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
