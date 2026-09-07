# verify_imos_1996.R -- Step 5b evidence for imos_1996 (37th IMO, Mumbai, India).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1996 problem paper
# (https://www.imo-official.org/assets/documents/problems/1996/1996_eng.pdf),
# under the standard IMO convention that the Day I paper's printed problems 1-3
# are problems 1-3 and the Day II paper's printed problems 1-3 are problems 4-6.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 1996 under the
# column headings P1..P6 (https://www.imo-official.org/results/individual/year/1996/,
# embedded JSON "scores":[P1..P6]). If IRW's problem1..problem6 are that same
# P1..P6, the score distribution of each IRW item must reproduce the official
# column cell for cell. A permutation of the item text across items would show up
# as a permutation of these 48 cells -- provided the six distributions are
# pairwise distinct, which the script also checks, so the assignment is unique
# rather than merely consistent.
#
# Hard-coded below: the official 1996 individual-results page, scraped
# 2026-09-07, 424 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1996"

OFFICIAL <- matrix(c(
  67,  30,  98,  26, 111,  17,  12,  63,   # P1
 178, 124,  10,   5,  11,   6,   2,  88,   # P2
  49, 176,  73,  22,  14,  19,  19,  52,   # P3
 177, 109,  11,  17,  11,   7,   6,  86,   # P4
 311,  74,  18,   7,   4,   4,   0,   6,   # P5
 196,  79,  16,  15,   3,   6,  10,  99),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 424 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1996') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 1996 contestants: 424\n")

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
    "official problem paper's own printed numbering for the same competition --\n",
    "direct for problems 1-3, and for 4-6 by the standard convention that the\n",
    "Day II paper's printed 1-3 are problems 4-6. That is a documentary fact, not\n",
    "something this script can test. Note also that problem5/P5 is the only column\n",
    "with zero marks of 6, an independent structural fingerprint of that column,\n",
    "and it says nothing about the English-vs-administered-language caveat.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
