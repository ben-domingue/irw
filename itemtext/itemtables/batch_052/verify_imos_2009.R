# verify_imos_2009.R -- Step 5b evidence for imos_2009 (50th IMO, Bremen, Germany).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as
# "Problem K" in the official IMO 2009 English problem paper
# (https://www.imo-official.org/assets/documents/problems/2009/2009_eng.pdf).
# The 2009 paper prints the numbers 1-6 outright (day 1 = Problems 1-3,
# Wednesday 15 July; day 2 = Problems 4-6, Thursday 16 July), so no day-numbering
# convention had to be inferred.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 2009 under the
# column headings P1..P6 (https://www.imo-official.org/results/individual/year/2009/,
# embedded JSON "scores":[P1..P6], 565 contestants). If IRW's problem1..problem6
# are that same P1..P6, each IRW item's mark distribution must reproduce the
# official column cell for cell. A permutation of item text across items would
# show up as a permutation of these 48 cells -- provided the six distributions
# are pairwise distinct, which the script also checks, so the assignment is
# unique rather than merely consistent.
#
# Hard-coded below: the official 2009 individual-results page, scraped
# 2026-09-07, 565 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2009"

OFFICIAL <- matrix(c(
  83,  56,  28,  20,  17,  16,  21, 324,   # P1
 101, 106,  43,  51,  16,  15,  19, 214,   # P2
 357, 127,  16,   5,   2,   5,   2,  51,   # P3
 188,  79,  37,  23,  17,  69,  52, 100,   # P4
 270,  42,  50,  33,   6,   4,   7, 153,   # P5
 540,   2,   1,  10,   6,   2,   1,   3),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 565 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2009') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2009 contestants: 565 (neighbours: 2008 Madrid 535, 2010 Astana 516)\n")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Difficulty ordering is a second, weaker read on the same cells: P6 (the
# grasshopper problem, famously the hardest of the 2009 paper) must sit at the
# floor and P1 at the top.
cat("mark means in problem order:",
    paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " "),
    "| hardest item:", rownames(live)[which.min(live %*% (0:7))],
    "| easiest item:", rownames(live)[which.max(live %*% (0:7))], "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed 'Problem 1'..'Problem 6' headings for the\n",
    "same competition -- a documentary fact, not something this script can test.\n",
    "It also says nothing about the English-vs-administered-language caveat: the\n",
    "IMO paper is sat in each contestant's own language.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
