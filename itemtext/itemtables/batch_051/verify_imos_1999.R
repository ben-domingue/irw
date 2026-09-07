# verify_imos_1999.R -- Step 5b evidence for imos_1999 (40th IMO, Bucharest, Romania).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1999 problem paper
# (https://www.imo-official.org/assets/documents/problems/1999/1999_eng.pdf).
# Unlike the 1996 paper, the 1999 paper numbers its Day II problems 4, 5, 6
# outright, so the statement-to-number tie is printed directly for all six.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 1999 under the
# column headings P1..P6 (https://www.imo-official.org/results/individual/year/1999/,
# embedded JSON "scores":[P1..P6]). If IRW's problem1..problem6 are that same
# P1..P6, the mark distribution of each IRW item must reproduce the official
# column cell for cell. A permutation of the item text across items would show up
# as a permutation of these 48 cells -- provided the six distributions are
# pairwise distinct, which the script also checks, so the assignment is unique
# rather than merely consistent.
#
# Hard-coded below: the official 1999 individual-results page, scraped
# 2026-09-07, 450 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1999"

OFFICIAL <- matrix(c(
  29,  52,  53,  45,  42,  41,  48, 140,   # P1
 195, 129,  37,  10,   5,   4,  11,  59,   # P2
 154, 119,  79,  44,  20,   3,   8,  23,   # P3
  40, 119, 109,  59,  24,  15,   9,  75,   # P4
 195, 103,  44,  18,   5,   7,  31,  47,   # P5
 145, 225,  28,  21,   8,   7,   5,  11),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 450 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1999') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 1999 contestants: 450 (1998: 419, 2000: 461)\n")

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
    "official problem paper's own printed numbering 1..6 for the same competition,\n",
    "a documentary fact this script cannot test (it is direct for 1999 -- the Day II\n",
    "paper prints 4, 5, 6 rather than repeating 1-3). It also says nothing about the\n",
    "English-vs-administered-language caveat, nor about the verbatim accuracy of the\n",
    "transcribed wording.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
