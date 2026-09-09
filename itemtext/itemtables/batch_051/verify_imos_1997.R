# verify_imos_1997.R -- Step 5b evidence for imos_1997 (38th IMO, Mar del Plata, Argentina).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1997 English problem paper
# (https://www.imo-official.org/assets/documents/problems/1997/1997_eng.pdf).
# The 1997 paper prints its Day I problems as 1-3 and its Day II problems as
# 4-6 explicitly, so unlike 1996 no day convention has to be assumed.
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 1997 under the
# column headings P1..P6 (https://www.imo-official.org/results/individual/year/1997/,
# embedded JSON "scores":[P1..P6], 460 contestants). If IRW's problem1..problem6
# are that same P1..P6, the mark distribution of each IRW item must reproduce the
# official column cell for cell. A permutation of item text across items would
# show up as a permutation of these 48 cells -- provided the six distributions are
# pairwise distinct, which the script also checks, so the assignment is unique
# rather than merely consistent.
#
# Hard-coded below: the official 1997 individual-results page, scraped 2026-09-07,
# 460 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1997"

OFFICIAL <- matrix(c(
  91, 143,  30,  23, 102,  15,   8,  48,   # P1
 164,  24,  16,   4,   7,   9,   0, 236,   # P2
 269,  64,   5,  22,   4,   2,   6,  88,   # P3
  81,  72,  20,  34,  58,  29,  31, 135,   # P4
 136,  51,  36,  31,  21,  19,  14, 152,   # P5
 341,  40,  12,  22,   4,  27,   4,  10),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 460 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1997') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat(sprintf("means  official: %s\n",
            paste(sprintf("%.3f", OFFICIAL %*% (0:7) / rowSums(OFFICIAL)), collapse = " ")))
cat(sprintf("means      live: %s\n",
            paste(sprintf("%.3f", live %*% (0:7) / rowSums(live)), collapse = " ")))
cat("contestants (unique id) live:", length(unique(d$id)),
    "| official 1997 contestants: 460\n")

# Uniqueness: are the six distributions pairwise distinct? If two were identical,
# swapping their item text would be undetectable by this route.
dup <- 0
for (i in 1:5) for (j in (i + 1):6)
    if (identical(as.integer(OFFICIAL[i, ]), as.integer(OFFICIAL[j, ]))) {
        dup <- dup + 1
        cat(sprintf("NOT DISTINCT: P%d and P%d have identical distributions\n", i, j))
    }
cat("pairs of problems with identical mark distributions:", dup, "of 15\n")

# Independent structural fingerprint: exactly one problem has an unused mark.
cat("problems with a zero cell (unused mark) -- official:",
    paste(rownames(OFFICIAL)[apply(OFFICIAL == 0, 1, any)], collapse = ","),
    "| live:",
    paste(rownames(live)[apply(live == 0, 1, any)], collapse = ","), "\n")

cat("\nWhat this does NOT establish: it ties each IRW item to an official *score\n",
    "column*, not directly to a *statement*. The statement-to-number tie is the\n",
    "official problem paper's own printed numbering 1..6 for the same competition\n",
    "-- a documentary fact, not something this script can test. It also says\n",
    "nothing about the English-vs-administered-language caveat: the IMO paper is\n",
    "sat in each contestant's own language and the shipped wording is the\n",
    "organisers' official English version.\n", sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
