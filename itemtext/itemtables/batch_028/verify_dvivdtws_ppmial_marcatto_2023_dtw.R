# verify_dvivdtws_ppmial_marcatto_2023_dtw.R
#
# CLAIM UNDER TEST: the Italian item wording transcribed from S1 Table of
# Marcatto et al. (2024), PLOS ONE 10.1371/journal.pone.0298880, is attached to
# the right dtw1..dtw22 codes.
#
# S1 Table prints, for each Italian item, M (SD), skewness and kurtosis computed
# on the Italian-speaking sample (N = 300). The live IRW table carries
# cov_language (1 = Italian, 2 = English), so the same statistics can be
# recomputed per item on the Italian subsample and matched row-for-row against
# the published table in the order the items appear in it. A swap of any two
# items' text would show up as two mismatched M/SD pairs.

suppressMessages(library(irw))

TABLE <- "dvivdtws_ppmial_marcatto_2023_dtw"

# S1 Table, in printed order (6 narcissism, 4 Machiavellianism, 6 psychopathy,
# 6 sadism) -> claimed to be dtw1..dtw22.
PUB_M  <- c(2.61, 1.80, 3.80, 3.18, 2.91, 2.05,
            2.40, 2.05, 2.75, 3.03,
            1.60, 1.58, 1.47, 1.45, 1.66, 1.34,
            1.23, 1.16, 1.30, 1.37, 1.11, 1.13)
PUB_SD <- c(0.99, 0.94, 1.05, 0.91, 0.98, 1.09,
            1.08, 1.04, 1.21, 1.09,
            0.87, 0.95, 0.79, 0.78, 0.92, 0.68,
            0.66, 0.47, 0.71, 0.75, 0.48, 0.48)
TOL_M  <- 0.015
TOL_SD <- 0.015

d <- irw::irw_fetch(TABLE)
d <- d[d$cov_language == 1 & !is.na(d$resp), ]           # Italian sample only
items <- paste0("dtw", 1:22)
obs_m  <- sapply(items, function(i) mean(d$resp[d$item == i]))
obs_sd <- sapply(items, function(i) sd(d$resp[d$item == i]))
obs_n  <- sapply(items, function(i) sum(d$item == i))

cat(sprintf("Italian subsample (cov_language==1): %d respondents\n\n",
            max(obs_n)))
cat(sprintf("%-7s %4s %12s %12s %8s %8s\n",
            "item", "n", "pub M (SD)", "obs M (SD)", "dM", "dSD"))
for (k in seq_along(items))
    cat(sprintf("%-7s %4d  %4.2f (%4.2f) %5.2f (%4.2f) %8.3f %8.3f\n",
                items[k], obs_n[k], PUB_M[k], PUB_SD[k], obs_m[k], obs_sd[k],
                obs_m[k] - PUB_M[k], obs_sd[k] - PUB_SD[k]))

worst_m  <- max(abs(obs_m  - PUB_M))
worst_sd <- max(abs(obs_sd - PUB_SD))
cat(sprintf("\nlargest |dM| = %.3f (tol %.3f); largest |dSD| = %.3f (tol %.3f)\n",
            worst_m, TOL_M, worst_sd, TOL_SD))

# Uniqueness: is each published (M, SD) pair closest to the item it was assigned
# to? This is what rules out a swap rather than merely tolerating one.
D <- outer(seq_along(items), seq_along(items),
           Vectorize(function(a, b)
               abs(obs_m[a] - PUB_M[b]) + abs(obs_sd[a] - PUB_SD[b])))
best <- apply(D, 1, which.min)
cat("nearest published row for each item:",
    paste(sprintf("%s->%d", items, best), collapse = " "), "\n")
unique_ok <- all(best == seq_along(items))
cat(sprintf("every item's nearest published row is its own: %s\n", unique_ok))

# What this does NOT establish:
cat("Note: this pins each ITALIAN item string (S1 Table) to its code. The English\n",
    "wording shipped in item_text_translated is the original DTW wording (Thibault\n",
    "2016 thesis, Table 1) aligned to the Italian by subscale and content, not by an\n",
    "independent statistic; and the response-anchor mapping (1=strongly disagree ..\n",
    "5=strongly agree) is taken from the paper's stated scale, not verified here.\n",
    sep = "")

cat(if (worst_m <= TOL_M && worst_sd <= TOL_SD && unique_ok)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
