# verify_reyes_2022_eheals.R -- Step 5b, route 1 (per-item published means).
#
# CLAIM UNDER TEST: eheals_1..eheals_8 carry the wording of Q1..Q8 of Table 1 of
# Norman & Skinner (2006), J Med Internet Res 8(4):e27 -- i.e. the numbering the
# Reyes & Vance-Chalcraft (2022) deposit points at, NOT the 1-8 renumbering of the
# instrument's own Multimedia Appendix 1 (which orders the same 8 items 3,4,1,2,...).
# The two orderings differ, so this is a real, falsifiable mapping question.
#
# THE FALSIFIABLE PREDICTION: S3 Table of the PLOS paper
# (doi:10.1371/journal.pone.0266802.s003, "Means of each eHEALS question ...
# See Table 1 in their original publication for the items") publishes a mean for
# each Q1..Q8. Those means are on the paper's own reverse/0-based scoring, which
# is the affine map score = 5 - resp of the 1-5 integer stored in IRW (resp 1 =
# "Strongly agree" per the deposit's own Qualtrics key row, so agreement decreases
# as resp rises). Under the claimed mapping, 5 - mean(resp | eheals_n) must equal
# the published mean for Qn, for every n, to within rounding (published to 2 dp,
# so half-width 0.005).
#
# WHAT WOULD BREAK IT: all 8 published means are distinct, so any permutation of
# the item->text assignment misaligns at least two of them. The tightest pair is
# Q3 = 2.76 vs Q4 = 2.75; the script checks that pair explicitly, because a
# swap there is the only near-miss a 2 dp table could hide.

suppressMessages(library(irw))

TABLE <- "reyes_2022_eheals"

# PLOS ONE 2022, doi:10.1371/journal.pone.0266802.s003 -- S3 Table, Q1..Q8.
PUBLISHED <- c(2.83, 2.79, 2.76, 2.75, 2.72, 2.69, 2.94, 2.22)
PUBLISHED_TOTAL <- 2.71          # "Mean eHEALS score" in the same table
TOL <- 0.005                     # rounding half-width of a 2 dp figure

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs <- tapply(d$resp, d$item, mean)[paste0("eheals_", 1:8)]
recoded <- 5 - obs               # onto the paper's scoring

cat(sprintf("%-10s %10s %10s %10s %8s\n",
            "item", "mean(resp)", "5-mean", "published", "diff"))
for (i in seq_along(obs))
    cat(sprintf("%-10s %10.4f %10.4f %10.2f %8.4f\n",
                names(obs)[i], obs[i], recoded[i], PUBLISHED[i],
                recoded[i] - PUBLISHED[i]))

worst <- max(abs(recoded - PUBLISHED))
cat(sprintf("\nlargest deviation: %.4f (rounding half-width %.3f)\n", worst, TOL))
cat(sprintf("overall mean: %.4f observed vs %.2f published\n",
            mean(recoded), PUBLISHED_TOTAL))

# The one pair a 2 dp table could plausibly hide: Q3/Q4, published 0.01 apart.
swap <- recoded
swap[c(3, 4)] <- swap[c(4, 3)]
worst_swap <- max(abs(swap - PUBLISHED))
cat(sprintf("counterfactual, eheals_3 <-> eheals_4 swapped: largest deviation %.4f",
            worst_swap))
cat(if (worst_swap > TOL) "  -> excluded\n" else "  -> NOT excluded\n")

ok <- worst <= TOL &&
      abs(mean(recoded) - PUBLISHED_TOTAL) <= 0.005 &&
      worst_swap > TOL

cat("\nWhat this establishes: every one of the 8 items is separated from every\n",
    "other, because the 8 published means are distinct and each observed value\n",
    "rounds to exactly one of them. It also confirms the resp direction (5 - resp\n",
    "reproduces the paper's scoring, so resp 1 is the agreement end), which is the\n",
    "option_text axis. It does NOT independently confirm the wording itself --\n",
    "that is transcribed from Norman & Skinner (2006), which the deposit cites.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
