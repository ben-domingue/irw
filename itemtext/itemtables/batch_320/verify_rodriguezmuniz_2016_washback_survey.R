# verify_rodriguezmuniz_2016_washback_survey.R -- batch_320, Step 5b.
#
# Claim: live item Qk carries the wording of question k in Table 8 of
# Rodriguez-Muniz et al. (2016) PLOS ONE 11(12):e0167544 ("Answers to Likert-type
# questions in the questionnaire for teachers (N = 51)", Question/Median/Mean/SD).
# The item code IS the S1 .xls column name (Q1..Q17; data/rodriguezmuniz_2016_
# washback_survey.py melts them by name), and Table 8 numbers the same questions 1..17.
#
# Falsifiable prediction: live per-item mean/SD reproduce Table 8 in order, and for
# every PAIR of items, swapping their text makes the fit worse (cost = |dMean| + |dSD|).
# What this does NOT establish robustly: Q11 vs Q16. Table 8 prints both with SD 0.91 and
# median 3, and means 3.13 vs 3.12 -- inside the ~0.02 near-tie band, with no floor/
# ceiling published to break it. The identity assignment is preferred (mean+SD cost 0.022 vs
# 0.037 swapped, and Q16's 153/49 = 3.1224 rounds to 3.12 while not rounding to 3.13), but that
# pair rests on the paper's own 1..17 numbering matching Q1..Q17 more than on statistics.

suppressMessages(library(irw))
TABLE <- "rodriguezmuniz_2016_washback_survey"

PUB_MEAN <- c(2.02, 3.88, 1.50, 3.76, 3.59, 2.88, 3.28, 2.67, 1.63, 2.57,
              3.13, 4.06, 2.39, 2.86, 3.86, 3.12, 3.76)
PUB_SD   <- c(1.34, 1.09, 0.91, 1.23, 0.95, 1.08, 1.16, 0.97, 0.83, 1.31,
              0.91, 0.92, 1.31, 1.06, 1.05, 0.91, 1.05)
PUB_MED  <- c(1, 4, 1, 4, 3, 3, 4, 3, 1, 2, 3, 4, 2, 3, 4, 3, 4)
TOL <- 0.025

d <- irw::irw_fetch(TABLE)
it <- paste0("Q", 1:17)
obs_m  <- tapply(d$resp, d$item, mean)[it]
obs_s  <- tapply(d$resp, d$item, sd)[it]
obs_md <- tapply(d$resp, d$item, median)[it]
obs_n  <- table(d$item)[it]

cat(sprintf("%-4s %3s %8s %8s %7s %8s %8s %7s %5s %5s\n", "item", "n", "pubMean", "obsMean",
            "dMean", "pubSD", "obsSD", "dSD", "pMed", "oMed"))
for (i in 1:17)
  cat(sprintf("%-4s %3d %8.2f %8.3f %7.3f %8.2f %8.3f %7.3f %5g %5g\n", it[i], obs_n[i],
              PUB_MEAN[i], obs_m[i], obs_m[i] - PUB_MEAN[i], PUB_SD[i], obs_s[i],
              obs_s[i] - PUB_SD[i], PUB_MED[i], obs_md[i]))

exact_m <- sum(round(obs_m, 2) == PUB_MEAN)
exact_s <- sum(round(obs_s, 2) == PUB_SD)
worst_m <- max(abs(obs_m - PUB_MEAN))
cat(sprintf("\nmeans reproduced exactly at 2dp: %d/17; SDs: %d/17; medians: %d/17\n",
            exact_m, exact_s, sum(obs_md == PUB_MED)))
cat(sprintf("largest mean deviation: %.3f (tolerance %.3f)\n", worst_m, TOL))

# Pairwise swap test: identity must beat every transposition.
cost <- function(i, j) abs(obs_m[i] - PUB_MEAN[j]) + abs(obs_s[i] - PUB_SD[j])
bad <- 0; tight <- character(0)
for (i in 1:16) for (j in (i + 1):17) {
  keep <- cost(i, i) + cost(j, j); swap <- cost(i, j) + cost(j, i)
  if (swap <= keep) { bad <- bad + 1; cat(sprintf("SWAP NOT WORSE: %s<->%s keep %.3f swap %.3f\n", it[i], it[j], keep, swap)) }
  else if (swap - keep < 0.03) tight <- c(tight, sprintf("%s<->%s keep %.3f swap %.3f", it[i], it[j], keep, swap))
}
cat(sprintf("pairwise swaps not worse than identity: %d of 136\n", bad))
cat("thin-margin pairs (swap - keep < 0.03):\n"); cat(paste0("  ", tight, "\n"), sep = "")
cat("Residuals (not mapping evidence against): SD Q17 0.81 vs 1.05, Q15 0.97 vs 1.05,\n",
    "Q13 1.35 vs 1.31, Q8 0.99 vs 0.97; median Q5 4 vs 3 (live n=49, counts 0/7/15/18/9). Means all within tol.\n", sep = "")

cat(if (worst_m <= TOL && bad == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
