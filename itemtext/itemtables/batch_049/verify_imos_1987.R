# verify_imos_1987.R -- Step 5b evidence for imos_1987 (IMO 1987, Havana).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1987 problem paper
# (https://www.imo-official.org/assets/documents/problems/1987/1987_eng.pdf).
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 1987 under the
# column headings P1..P6
# (https://www.imo-official.org/results/individual/year/1987/). If IRW's
# problem1..problem6 are that same P1..P6, then the *score distribution* of each
# IRW item must reproduce the official column cell for cell. A permutation of the
# item text across items would show up as a permutation of these 48 cells --
# provided the six distributions are pairwise distinct, which the script also
# checks, so the assignment is unique rather than merely consistent.
#
# Hard-coded below: the official 1987 individual-results page, scraped
# 2026-09-07, 237 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1987"

OFFICIAL <- matrix(c(
  75, 31, 15,  7,  3,  7,  1, 98,   # P1
  54,  9,  7, 11,  7,  4,  4,141,   # P2
 125, 39,  5,  1,  0,  2,  6, 59,   # P3
  75, 20, 21, 10,  1, 12,  7, 91,   # P4
  59, 21,  7,  7,  8, 10,  6,119,   # P5
 126, 33, 12, 12,  8,  5,  4, 37),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 237 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1987') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
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
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed numbering 1..6 for the same competition,\n",
    "which is a documentary fact, not something this script can test. Also note\n",
    "P3/problem3 is the only problem with no mark of 4 (0 contestants), which is an\n",
    "independent structural fingerprint of that one column.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
