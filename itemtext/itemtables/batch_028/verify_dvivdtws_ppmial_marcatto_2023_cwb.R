# Step 5b verification for dvivdtws_ppmial_marcatto_2023_cwb.
#
# CLAIM UNDER TEST: the 22 Italian item strings of S1 Table of Marcatto (2024),
# PLOS ONE 10.1371/journal.pone.0298880, correspond to live item codes dtw1..dtw22
# IN THE ORDER S1 PRINTS THEM (Narcissism 1-6, Machiavellianism 7-10,
# Psychopathy 11-16, Sadism 17-22).
#
# ROUTE 1 (per-item descriptive statistics). S1 publishes M (SD) for each item in
# the ITALIAN sample (N = 300). The live table pools the Italian and English
# samples, so the comparison is restricted to cov_language == 1 (n = 300; the
# English half is cov_language == 2, n = 253).
#
# WHY THIS IS DECISIVE: no two of the 22 published (M, SD) pairs are equal, so the
# pair identifies each item uniquely. Means alone would NOT: items 6 and 8 both
# read 2.05, and 7 further pairs sit within 0.05 of each other. The SD column is
# what separates those, and it is checked here alongside the mean.
#
# WHAT THIS DOES NOT ESTABLISH: it verifies item_text (Italian, base field) only.
# item_text_translated holds the ORIGINAL English DTW wording (Thibault, 2016,
# Appendix A, Saint Mary's University thesis) matched to the Italian by meaning,
# 1:1 within each subscale and in ascending pool order; four of the 22 are
# corroborated verbatim by the PLOS paper's own English example quotes (dtw2,
# dtw9, dtw11, dtw17). The remaining 18 English strings rest on a semantic match,
# not on a number checked here.

suppressMessages(library(irw))

TABLE <- "dvivdtws_ppmial_marcatto_2023_cwb"
TOL_M  <- 0.02
TOL_SD <- 0.02

# S1 Table, in printed order = claimed dtw1..dtw22.
PUB_M  <- c(2.61, 1.80, 3.80, 3.18, 2.91, 2.05, 2.40, 2.05, 2.75, 3.03, 1.60,
            1.58, 1.47, 1.45, 1.66, 1.34, 1.23, 1.16, 1.30, 1.37, 1.11, 1.13)
PUB_SD <- c(0.99, 0.94, 1.05, 0.91, 0.98, 1.09, 1.08, 1.04, 1.21, 1.09, 0.87,
            0.95, 0.79, 0.78, 0.92, 0.68, 0.66, 0.47, 0.71, 0.75, 0.48, 0.48)

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$cov_language) & d$cov_language == 1, ]   # Italian sample only
cat(sprintf("Italian subsample rows: %d (respondents: %d)\n\n",
            nrow(d), length(unique(d$id))))

items <- paste0("dtw", 1:22)
obs_m  <- sapply(items, function(i) mean(d$resp[d$item == i], na.rm = TRUE))
obs_sd <- sapply(items, function(i) sd(d$resp[d$item == i], na.rm = TRUE))

cat(sprintf("%-7s %9s %9s %8s %9s %9s %8s\n",
            "item", "pub_M", "obs_M", "dM", "pub_SD", "obs_SD", "dSD"))
for (i in 1:22)
    cat(sprintf("%-7s %9.2f %9.3f %8.3f %9.2f %9.3f %8.3f\n",
                items[i], PUB_M[i], obs_m[i], obs_m[i] - PUB_M[i],
                PUB_SD[i], obs_sd[i], obs_sd[i] - PUB_SD[i]))

worst_m  <- max(abs(obs_m  - PUB_M))
worst_sd <- max(abs(obs_sd - PUB_SD))
cat(sprintf("\nlargest |dM| = %.3f (tol %.2f);  largest |dSD| = %.3f (tol %.2f)\n",
            worst_m, TOL_M, worst_sd, TOL_SD))

# Uniqueness of the published (M, SD) pair -- this is what makes the match
# item-by-item rather than merely consistent.
key <- paste(PUB_M, PUB_SD)
cat(sprintf("distinct published (M,SD) pairs: %d of 22\n", length(unique(key))))
mties <- sum(outer(PUB_M, PUB_M, function(a, b) abs(a - b) < 0.05)) - 22
cat(sprintf("ordered pairs of items within 0.05 on the MEAN alone: %d",
            mties), "-- SD is what separates these\n")

ok <- worst_m <= TOL_M && worst_sd <= TOL_SD && length(unique(key)) == 22
cat("\nEstablishes: item_text (Italian) for all 22 items.",
    "Does NOT establish: the English item_text_translated strings,",
    "18 of which rest on a semantic 1:1 match to the DTW original rather than",
    "on any number checked here.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
