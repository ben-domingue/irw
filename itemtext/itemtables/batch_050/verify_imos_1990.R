# verify_imos_1990.R -- Step 5b evidence for imos_1990 (31st IMO, Beijing, China).
#
# THE CLAIM: item `problemK` in the IRW table is the problem printed as number K
# in the official IMO 1990 English problem paper
# (https://www.imo-official.org/assets/documents/problems/1990/1990_eng.pdf).
#
# WHY THIS IS FALSIFIABLE: the same organisation that publishes the numbered
# problem statements also publishes the per-contestant marks for 1990, scored by
# problem, at https://www.imo-official.org/results/individual/year/1990/ (the page
# embeds them as a JSON array whose per-contestant `scores` field is [P1..P6]).
# If IRW's problem1..problem6 are that same P1..P6, the score distribution of
# each IRW item must reproduce the official column cell for cell. Any permutation
# of item text across items shows up as a permutation of these 48 cells --
# provided the six distributions are pairwise distinct, which the script also
# checks, so the assignment is unique rather than merely consistent.
#
# Hard-coded below: the official 1990 individual-results data, scraped
# 2026-09-07, 308 contestants, counts of each mark 0..7 per problem.

suppressMessages(library(irw))

TABLE <- "imos_1990"

OFFICIAL <- matrix(c(
  88, 54, 28, 19, 26, 14,  8, 71,   # P1
  47, 46, 37, 54, 11,  9,  8, 96,   # P2
  25,118, 79, 42, 16,  6,  6, 16,   # P3
  31, 76, 70, 46, 10,  3,  3, 69,   # P4
  21, 39, 43, 31, 22, 26, 26,100,   # P5
 115, 93, 29, 31, 18,  2,  3, 17),  # P6
 nrow = 6, byrow = TRUE,
 dimnames = list(paste0("P", 1:6), as.character(0:7)))

d <- irw::irw_fetch(TABLE)
live <- table(factor(d$item, levels = paste0("problem", 1:6)),
              factor(d$resp, levels = 0:7))
live <- matrix(as.integer(live), nrow = 6, dimnames = dimnames(OFFICIAL))

cat("Official imo-official.org P1..P6 mark counts (0..7), 308 contestants:\n")
print(OFFICIAL)
cat("\nLive irw_fetch('imos_1990') problem1..problem6 resp counts (0..7):\n")
print(live)

diffs <- OFFICIAL - live
cat("\ncells compared: 48 | cells disagreeing:", sum(diffs != 0), "\n")
cat("contestants per item -- official:", paste(rowSums(OFFICIAL), collapse = " "),
    "| live:", paste(rowSums(live), collapse = " "), "\n")
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

cat("\nWhat this does NOT establish: it ties each IRW item code to an official\n",
    "*score column*, not directly to a *statement*. The column-to-statement tie is\n",
    "the official problem paper's own printed numbering 1..6 for the same\n",
    "competition, a documentary fact no statistic can test. It also says nothing\n",
    "about the English-vs-administered-language caveat: the paper is sat in each\n",
    "contestant's own language and the shipped wording is the organisers' English.\n",
    sep = "")

cat(if (sum(diffs != 0) == 0 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
