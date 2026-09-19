# verify_imos_1994.R -- Step 5b evidence for imos_1994 (35th IMO, Hong Kong, 13-14 July 1994).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1994 English problem paper
# (https://www.imo-official.org/assets/documents/problems/1994/1994_eng.pdf).
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements publishes the per-contestant marks for 1994 under the
# headings P1..P6 (https://www.imo-official.org/results/individual/year/1994/,
# embedded JSON, "scores":[P1..P6]). If IRW's problem1..problem6 are that same
# P1..P6, each IRW item's mark distribution must reproduce the official column
# cell for cell. Any permutation of item text across items would appear as a
# permutation of these 48 cells -- provided the six distributions are pairwise
# distinct, which the script also checks, so the assignment is unique rather
# than merely consistent.
#
# Hard-coded below: the official 1994 individual-results JSON, scraped
# 2026-09-07, 385 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1994"

OFFICIAL <- matrix(c(
 151, 60, 33, 15, 10, 13, 11, 92,   # P1
  52, 25, 12, 26, 17, 14, 12,227,   # P2
 104, 30, 18, 19, 11, 19, 36,148,   # P3
  52, 69, 70, 43, 19, 20, 11,101,   # P4
  95, 54, 40, 29, 22, 23, 38, 84,   # P5
 211, 34, 30,  7,  4,  8,  3, 88),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 385 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1994') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants official: 385 | live unique ids:", length(unique(d$id)), "\n")

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
    "official 1994 problem paper's own printed numbering 1..6 for the same\n",
    "competition, a documentary fact no statistic can test. It also says nothing\n",
    "about the English-vs-administered-language caveat.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
