# verify_imos_1984.R -- Step 5b evidence for imos_1984 (25th IMO, Prague 1984).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as 1984/K
# in the official IMO 1984 problem paper
# (https://www.imo-official.org/assets/documents/problems/1984/1984_eng.pdf,
# sha256 bab14c4e3dc47f43905edd1d1cb82c456470f16a8a4379518346d8986afcc86d).
#
# WHY THIS IS FALSIFIABLE: the IMO, which publishes the numbered statements, also
# publishes per-contestant marks for 1984 under columns P1..P6
# (https://www.imo-official.org/results/individual/year/1984/). If IRW's
# problem1..problem6 are that P1..P6, each item's mark distribution must reproduce
# the official column cell for cell. A permutation of the text across items would
# show as a permutation of these 48 cells -- provided the six distributions are
# pairwise distinct, which is also checked, so the assignment is unique.
#
# Hard-coded below: the official 1984 individual-results page, scraped
# 2026-09-23, 192 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1984"

OFFICIAL <- matrix(c(
  19,  3, 35, 23,  9,  7, 10, 86,   # P1
  55, 39,  8,  8,  7,  6,  3, 66,   # P2
 121, 18, 14,  0,  1,  3,  6, 29,   # P3
  38,  9, 10, 11, 15,  3, 24, 82,   # P4
  88, 17,  4, 12, 19,  4,  7, 41,   # P5
 123, 18,  9,  6,  5,  3,  3, 25),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 192 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1984') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))

dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed numbering 1984/1..1984/6, a documentary\n",
    "fact this script cannot test. Nor does it check the transcription of the\n",
    "mathematical notation (superscripts rendered with ^, fractions inline).\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
