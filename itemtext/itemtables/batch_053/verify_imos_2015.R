# verify_imos_2015.R -- Step 5b evidence for imos_2015 (56th IMO, Chiang Mai, Thailand).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2015 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2015/2015_eng.pdf,
# day 1 = Problems 1-3, Friday 10 July; day 2 = Problems 4-6, Saturday 11 July).
# The 2015 paper prints the numbers 1-6 outright, so no day-convention inference
# is needed; the numbering is read directly off the page.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes every contestant's per-problem mark for 2015
# under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/2015/, embedded JSON
# "scores":[P1..P6], 577 contestants). If IRW's problem1..problem6 are that same
# P1..P6, each IRW item's mark distribution must reproduce the official column
# cell for cell. Any permutation of item text across items shows up as a
# permutation of these 48 cells -- provided the six distributions are pairwise
# distinct, which the script also checks, so the assignment is unique rather than
# merely consistent.
#
# Hard-coded below: the official 2015 individual-results page, scraped 2026-09-07,
# 577 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2015"

OFFICIAL <- matrix(c(
  93,  89,   5,  21,  72,  12,  20, 265,   # P1
 256, 151,  77,  27,   8,  13,  14,  31,   # P2
 408, 122,  12,   1,   3,   0,   1,  30,   # P3
  91,  36,  61,  18,  11,   1,   8, 351,   # P4
 153, 255,  34,  90,   8,   4,   3,  30,   # P5
 521,  11,  15,   6,   3,   3,   7,  11),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 577 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2015') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2015 contestants: 577 (imo-official.org/editions/, 56th IMO,\n",
    "  Chiang Mai, July 4-16 2015, 104 countries); neighbouring editions 2014 = 560\n",
    "  and 2016 = 602, so the edition identification is not ambiguous.\n", sep = " ")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint: exactly one cell is empty in the official
# table -- P3 has zero marks of 5. That is why problem3 shows 7 observed resp
# levels while the other five problems show all 8.
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
