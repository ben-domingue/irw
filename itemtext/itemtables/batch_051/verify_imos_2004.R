# verify_imos_2004.R -- Step 5b evidence for imos_2004 (45th IMO, Athens, Greece).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2004 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2004/2004_eng.pdf,
# which numbers all six problems 1-6 continuously and prints no Day I/Day II
# headers).
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes every contestant's marks for the same
# competition under the column headings P1..P6
# (https://www.imo-official.org/results/individual/year/2004/, embedded JSON
# "scores":[P1..P6]). If IRW's problem1..problem6 are that same P1..P6, each
# IRW item's mark distribution must reproduce the official column cell for
# cell. A permutation of the item text across items would show up as a
# permutation of these 48 cells -- provided the six distributions are pairwise
# distinct, which the script also checks, so the assignment is unique rather
# than merely consistent.
#
# Hard-coded below: the official 2004 individual-results page, scraped
# 2026-09-07, 486 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2004"

OFFICIAL <- matrix(c(
  94,  29,  21,  19,   9,   2, 121, 191,   # P1
  79, 158,  57,  32,  23,  23,  31,  83,   # P2
 249, 100,  80,  30,  15,   1,   0,  11,   # P3
 140,  33,  27,  16,   8,   6,   6, 250,   # P4
 157,  57,  18, 124,  35,  18,  13,  64,   # P5
 289,  85,  33,  14,   7,   6,   4,  48),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 486 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2004') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2004 contestants: 486\n")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint: P3 is the only 2004 column with zero
# marks of 6, so problem3 must be the only IRW item with 7 used mark levels.
cat("items with an unused mark level (live):",
    paste(rownames(live)[apply(live, 1, function(r) any(r == 0))], collapse = ", "),
    "| official columns with a zero cell:",
    paste(rownames(OFFICIAL)[apply(OFFICIAL, 1, function(r) any(r == 0))], collapse = ", "),
    "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official 2004 problem paper's own printed 'Problem 1'..'Problem 6' headings\n",
    "for the same competition -- a documentary fact, not something this script\n",
    "can test (2004 is easier than most years here: the paper numbers all six\n",
    "continuously, so no Day I/Day II convention is being relied on). It also\n",
    "says nothing about the English-vs-administered-language caveat, nor about\n",
    "the figure that Problem 3's statement refers to.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
