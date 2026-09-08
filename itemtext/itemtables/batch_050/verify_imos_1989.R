# verify_imos_1989.R -- Step 5b evidence for imos_1989 (30th IMO, Braunschweig).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1989 problem paper
# (https://www.imo-official.org/assets/documents/problems/1989/1989_eng.pdf).
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 1989, scored
# as an ordered vector [P1..P6]
# (https://www.imo-official.org/results/individual/year/1989/, embedded JSON in
# the `data-results-individual-year-contestants` script block). If IRW's
# problem1..problem6 are that same P1..P6, the score distribution of each IRW
# item must reproduce the official column cell for cell. A permutation of item
# text across items would show up as a permutation of these 48 cells -- provided
# the six distributions are pairwise distinct, which the script also checks, so
# the assignment is unique rather than merely consistent.
#
# Hard-coded below: the official 1989 individual-results JSON, scraped
# 2026-09-07, 291 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1989"

OFFICIAL <- matrix(c(
 109, 31, 29,  4,  4,  8, 15, 91,   # P1
  45, 23,  9, 49, 14, 28, 15,108,   # P2
 188, 27, 19, 13,  2,  7,  3, 32,   # P3
  65, 37, 12, 23,  8,  9,  5,132,   # P4
 122,  3,  3,  3,  2,  8,  8,142,   # P5
 143, 23, 13,  6, 11, 15, 11, 69),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 291 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1989') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("contestants per item  official: %s\n",
            paste(rowSums(OFFICIAL), collapse = " ")))
cat(sprintf("contestants per item      live: %s\n",
            paste(rowSums(live), collapse = " ")))
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
    "column*, not directly to a *statement*. The column-number-to-statement tie is\n",
    "the official problem paper's own printed numbering 1..6 for the same\n",
    "competition, a documentary fact no statistic can test. It also says nothing\n",
    "about the English-vs-administered-language caveat (the IMO paper is sat in\n",
    "each contestant's own language).\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
