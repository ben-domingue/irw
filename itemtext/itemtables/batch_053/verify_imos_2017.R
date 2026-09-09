# verify_imos_2017.R -- Step 5b evidence for imos_2017 (58th IMO, Rio de Janeiro, Brazil).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2017 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2017/2017_eng.pdf,
# day 1 = Problems 1-3, Tuesday 18 July; day 2 = Problems 4-6, Wednesday 19 July).
# The 2017 paper prints the numbers 1-6 outright, so no day-convention inference
# is needed; the numbering is read directly off the page.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes every contestant's per-problem mark for 2017
# under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/2017/, embedded JSON
# "scores":[P1..P6], 615 contestants). If IRW's problem1..problem6 are that same
# P1..P6, each IRW item's mark distribution must reproduce the official column
# cell for cell. Any permutation of item text across items shows up as a
# permutation of these 48 cells -- provided the six distributions are pairwise
# distinct, which the script also checks, so the assignment is unique rather than
# merely consistent.
#
# Hard-coded below: the official 2017 individual-results page, scraped 2026-09-07,
# 615 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2017"

OFFICIAL <- matrix(c(
  40,  16,  17,   5,  12,  54,  25, 446,   # P1
 183, 110,  26, 138,  79,  10,   8,  61,   # P2
 608,   3,   0,   0,   1,   1,   0,   2,   # P3
  47,  93,  42,  14,  15,   4,   6, 394,   # P4
 451,  46,  47,   9,   0,   2,   1,  59,   # P5
 557,  24,   9,   5,   4,   2,   0,  14),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 615 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2017') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2017 contestants: 615 (imo-official.org/editions/, 58th IMO,\n",
    "  Rio de Janeiro, July 12-23 2017, 111 countries); neighbouring editions\n",
    "  2016 = 602 and 2018 = 594, so the edition identification is not ambiguous.\n", sep = " ")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint: exactly five cells are empty -- P3 has zero
# marks of 2, 3 and 6, P5 zero marks of 4, P6 zero marks of 6. That is why
# problem3 shows 5 and problem5/problem6 show 7 observed resp levels while
# problem1, problem2 and problem4 show all 8.
zero_cells <- which(OFFICIAL == 0, arr.ind = TRUE)
zero_cells <- zero_cells[order(zero_cells[, 1], zero_cells[, 2]), , drop = FALSE]
cat("official zero cells (problem@mark):",
    paste(sprintf("P%d@%d", zero_cells[, 1], zero_cells[, 2] - 1), collapse = " "), "\n")
zero_live <- which(live == 0, arr.ind = TRUE)
zero_live <- zero_live[order(zero_live[, 1], zero_live[, 2]), , drop = FALSE]
cat("live     zero cells (problem@mark):",
    paste(sprintf("P%d@%d", zero_live[, 1], zero_live[, 2] - 1), collapse = " "), "\n")
cat("observed resp levels per item, live:",
    paste(sprintf("problem%d=%d", 1:6, rowSums(live > 0)), collapse = " "), "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed 'Problem 1'..'Problem 6' headings for the\n",
    "same competition -- a documentary fact, not something this script can test.\n",
    "It also says nothing about the English-vs-administered-language caveat (the\n",
    "IMO paper is sat in each contestant's own language), nor about the ASCII\n",
    "rendering of the typeset mathematics.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
