# verify_imos_2005.R -- Step 5b evidence for imos_2005 (46th IMO, Merida, Mexico).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 2005 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2005/2005_eng.pdf).
# Unlike most years, the 2005 paper is a single sheet that prints all six
# problems numbered "Problem 1." .. "Problem 6." outright, so there is no Day I /
# Day II renumbering convention to lean on for problems 4-6.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 2005 under the
# column headings P1..P6 (https://www.imo-official.org/results/individual/year/2005/,
# embedded JSON "scores":[P1..P6]). If IRW's problem1..problem6 are that same
# P1..P6, the score distribution of each IRW item must reproduce the official
# column cell for cell. A permutation of the item text across items would show up
# as a permutation of these 48 cells -- provided the six distributions are
# pairwise distinct, which the script also checks, so the assignment is unique
# rather than merely consistent.
#
# Hard-coded below: the official 2005 individual-results page, scraped
# 2026-09-07, 513 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2005"

OFFICIAL <- matrix(c(
 207,  59,  65,  20,   5,  11,   5, 141,   # P1
  96, 202,  13,   7,  11,   7,   2, 175,   # P2
 423,  23,   3,   0,   0,   0,   9,  55,   # P3
  90, 145,  30,   0,   0,   3,   7, 238,   # P4
 288,  36,  30,  16,   4,   6,   8, 125,   # P5
 325,  39,  57,  13,  15,   2,   6,  56),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 513 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2005') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2005 contestants: 513\n")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint that needs no counting: the number of mark
# levels actually used differs by problem (P3 uses 5 of 8, P4 uses 6 of 8, the
# rest all 8), which alone separates problem3 and problem4 from everything else.
cat("levels used, official:", paste(rowSums(OFFICIAL > 0), collapse = " "), "\n")
cat("levels used,     live:", paste(rowSums(live > 0), collapse = " "), "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The column-to-statement tie is the\n",
    "official 2005 problem paper's own printed numbering ('Problem 1.' .. 'Problem\n",
    "6.' on one sheet) -- a documentary fact, not something this script can test.\n",
    "It also says nothing about the English-vs-administered-language caveat: the\n",
    "IMO administers the paper in each contestant's own language.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
