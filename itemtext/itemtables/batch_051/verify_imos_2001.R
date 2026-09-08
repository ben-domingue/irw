# verify_imos_2001.R -- Step 5b evidence for imos_2001 (42nd IMO, Washington DC, USA,
# July 8-9 2001).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as "Problem K"
# in the official IMO 2001 problem paper
# (https://www.imo-official.org/assets/documents/problems/2001/2001_eng.pdf).
# Unlike several neighbouring years, the 2001 paper numbers all six problems 1-6
# on its face and prints no Day I / Day II headers, so no day convention is
# needed to reach problems 4-6.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes each contestant's marks for 2001 under the
# column headings P1..P6 (https://www.imo-official.org/results/individual/year/2001/,
# embedded JSON "scores":[P1..P6], 473 contestants). If IRW's problem1..problem6
# are that same P1..P6, each IRW item's mark distribution must reproduce the
# official column cell for cell. A permutation of item text across items would
# show up as a permutation of these 48 cells -- provided the six distributions are
# pairwise distinct, which the script also checks, so the assignment is unique
# rather than merely consistent.
#
# Hard-coded below: the official 2001 individual-results page, scraped 2026-09-07,
# 473 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_2001"

OFFICIAL <- matrix(c(
 132,  28,  47,  45,  12,  12,  20, 177,   # P1
 311,  40,  15,   9,  11,   7,   3,  77,   # P2
 272, 127,  36,   8,   1,   6,   3,  20,   # P3
 147,  79,  34,  11,  15,   6,   8, 173,   # P4
  93,  48, 145,  67,  17,  16,   5,  82,   # P5
 380,  20,  16,   8,  10,   9,   3,  27),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 473 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_2001') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 2001 contestants: 473\n")

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
    "official 2001 problem paper's own printed headings 'Problem 1'..'Problem 6'\n",
    "for the same competition -- a documentary fact, not something this script can\n",
    "test. It also says nothing about the English-vs-administered-language caveat\n",
    "(the IMO is sat in each contestant's own language; the shipped wording is the\n",
    "organisers' official English).\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
