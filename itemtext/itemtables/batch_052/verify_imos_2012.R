# verify_imos_2012.R -- Step 5b evidence for imos_2012 (53rd IMO, Mar del Plata, Argentina).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2012 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2012/2012_eng.pdf).
# That paper prints the numbers 1-6 outright -- Day 1 (Tuesday, July 10, 2012)
# carries Problems 1-3, Day 2 (Wednesday, July 11, 2012) carries Problems 4-6 --
# so no day-numbering convention had to be assumed.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for the same
# competition under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/2012/, embedded JSON
# "scores":[P1..P6], scraped 2026-09-07, 547 contestants). If IRW's
# problem1..problem6 are that same P1..P6, each IRW item's mark distribution
# must reproduce the official column cell for cell. Any permutation of item
# text across items shows up as a permutation of these 48 cells -- provided the
# six distributions are pairwise distinct, which this script also checks, so the
# assignment is unique rather than merely consistent.

suppressMessages(library(irw))

TABLE <- "imos_2012"

OFFICIAL <- matrix(c(
  41,  37,  15,  24,  16,  11,   2, 401,   # P1
 263,  83,   8,   5,   8,   2,   7, 171,   # P2
 480,  11,   4,  31,   7,   6,   0,   8,   # P3
  53,  65,  95,  74,  47,  26,  44, 143,   # P4
 348,  17,  29,  45,  15,   4,   3,  86,   # P5
 473,  39,  12,   3,   9,   0,   1,  10),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 547 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2012') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2012 contestants: 547\n")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint: exactly two cells are unused, on different
# marks -- P3 has zero 6s, P6 has zero 5s -- which is why problem3 and problem6
# are the only live items with 7 rather than 8 observed resp levels.
zc <- which(OFFICIAL == 0, arr.ind = TRUE)
cat("official zero cells (problem, mark):",
    paste(sprintf("P%d@%d", zc[, 1], zc[, 2] - 1), collapse = " "), "\n")
zl <- which(live == 0, arr.ind = TRUE)
cat("live     zero cells (problem, mark):",
    paste(sprintf("P%d@%d", zl[, 1], zl[, 2] - 1), collapse = " "), "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The column-to-statement tie is the\n",
    "official problem paper's own printed 'Problem 1'..'Problem 6' headings for the\n",
    "same competition -- a documentary fact, not something this script can test.\n",
    "It also says nothing about the English-vs-administered-language caveat: the\n",
    "IMO paper is sat in each contestant's own language.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
