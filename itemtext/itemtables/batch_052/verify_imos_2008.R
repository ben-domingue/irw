# verify_imos_2008.R -- Step 5b evidence for imos_2008 (49th IMO, Madrid, Spain).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2008 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2008/2008_eng.pdf,
# day 1 = Problems 1-3, Wednesday 16 July; day 2 = Problems 4-6, Thursday 17 July).
# The 2008 paper prints the numbers 1-6 outright, so no day-convention inference
# is needed; the numbering is read directly off the page.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes every contestant's per-problem mark for 2008
# under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/2008/, embedded JSON
# "scores":[P1..P6], 535 contestants). If IRW's problem1..problem6 are that same
# P1..P6, each IRW item's mark distribution must reproduce the official column
# cell for cell. Any permutation of item text across items shows up as a
# permutation of these 48 cells -- provided the six distributions are pairwise
# distinct, which the script also checks, so the assignment is unique rather than
# merely consistent.
#
# Hard-coded below: the official 2008 individual-results page, scraped 2026-09-07,
# 535 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2008"

OFFICIAL <- matrix(c(
  59,  74,  17,   5,   8,  44,   7, 321,   # P1
 110, 209,  24,   3,  35,  53,   7,  94,   # P2
 438,  27,   8,   8,   3,   1,   4,  46,   # P3
  69,  80,   0,   4, 128,   0,  27, 227,   # P4
 295,  58,  33,  11,   1,   4,   1, 132,   # P5
 482,  31,   9,   0,   0,   0,   1,  12),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 535 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2008') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2008 contestants: 535 (imo-official.org/editions/, 49th IMO,\n",
    "  Madrid, July 10-22 2008, 97 countries); neighbouring editions 2007 = 520\n",
    "  and 2009 = 565, so the edition identification is not ambiguous.\n", sep = " ")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint: exactly five cells are empty, all in P4 and
# P6 -- P4 has zero marks of 2 and 5, P6 zero marks of 3, 4 and 5. That is why
# problem4 shows 6 and problem6 shows 5 observed resp levels while the other four
# problems show all 8.
zero_cells <- which(OFFICIAL == 0, arr.ind = TRUE)
cat("official zero cells (problem@mark):",
    paste(sprintf("P%d@%d", zero_cells[, 1], zero_cells[, 2] - 1), collapse = " "), "\n")
zero_live <- which(live == 0, arr.ind = TRUE)
cat("live     zero cells (problem@mark):",
    paste(sprintf("P%d@%d", zero_live[, 1], zero_live[, 2] - 1), collapse = " "), "\n")
cat("observed resp levels per item, live:",
    paste(sprintf("problem%d=%d", 1:6, rowSums(live > 0)), collapse = " "), "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed 'Problem 1'..'Problem 6' headings for the\n",
    "same competition -- a documentary fact, not something this script can test.\n",
    "It also says nothing about the English-vs-administered-language caveat: the\n",
    "IMO paper is sat in each contestant's own language.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
