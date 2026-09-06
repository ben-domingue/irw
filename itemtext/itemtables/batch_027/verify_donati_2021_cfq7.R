# verify_donati_2021_cfq7.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the Italian item at row i of the paper's S1 Appendix (the only
# published Italian CFQ-7 wording) is the text of live item code CFQ<i>.
#
# The chain has two links; this script tests the one the DATA can settle:
#   (A) appendix row i == canonical CFQ-7 item number i.  Settled OUTSIDE this script,
#       by two independent CC BY sources that print the English CFQ items KEYED TO THE
#       SAME CODES: PMC11875431 Appendix A ("CFQ1 My thoughts cause me distress or
#       emotional pain", "CFQ2 I get so caught up in my thoughts...", CFQ4, CFQ5, CFQ6,
#       CFQ7) and PMC13082997 ('Item 3 ("I over-analyze situations to the point where
#       it's unhelpful")', 'item 4 ("I struggle with my thoughts")'). Together those
#       key all seven; each Italian appendix row is the translation of the English item
#       carrying that number.
#   (B) canonical item number i == live column CFQ<i>.  THIS is what runs below.
#       Donati et al. (2021) PLOS ONE 16(2):e0246434, Table 1, publishes per-item
#       skewness and kurtosis for items 1-7 in the NON-CLINICAL sample (n = 258).
#       A permutation of the item codes would break the match: the (Sk, Ku) pairs are
#       mutually distinct, so each published item is identified by exactly one column.
#
# CAUTION carried by this script: cov_population in the live IRW table is INVERTED.
# The paper's non-clinical sample is n = 258 (Donati et al., Participants); the live
# rows labelled cov_population == "clinical" number 258 * 7 = 1806, and those labelled
# "non_clinical" number 107 * 7 = 749. So the paper's non-clinical sample is the group
# the table calls "clinical". The script selects by SIZE, and asserts it, rather than
# by the (wrong) label.

suppressMessages(library(irw))

TABLE <- "donati_2021_cfq7"
ITEMS <- paste0("CFQ", 1:7)

# Donati et al. 2021, Table 1 (non-clinical sample, n = 258).
PUB_SK <- c( 0.04,  0.46, -0.04,  0.18,  0.08,  0.01,  0.01)
PUB_KU <- c(-0.61, -0.51, -0.86, -0.85, -0.81, -0.91, -1.01)
TOL    <- 0.02   # published to 2 dp

d <- irw::irw_fetch(TABLE)

# --- pick the paper's non-clinical sample by n, not by the inverted label ---
sizes <- tapply(d$id, d$cov_population, function(x) length(unique(x)))
cat("participants per cov_population level (live table):\n")
print(sizes)
grp <- names(sizes)[which.max(sizes)]
cat(sprintf("paper's non-clinical sample (n = 258) is the group the table labels '%s' (n = %d)\n\n",
            grp, sizes[[grp]]))
stopifnot(sizes[[grp]] == 258)

sub <- as.data.frame(d[d$cov_population == grp, ])
sub$resp <- as.numeric(sub$resp)

# SPSS/pandas G1, G2 (sample-adjusted) skewness and kurtosis, matching the paper's SPSS run.
skew <- function(x) { x <- x[!is.na(x)]; n <- length(x); m <- mean(x); s <- sd(x)
    n / ((n - 1) * (n - 2)) * sum(((x - m) / s)^3) }
kurt <- function(x) { x <- x[!is.na(x)]; n <- length(x); m <- mean(x); s <- sd(x)
    n * (n + 1) / ((n - 1) * (n - 2) * (n - 3)) * sum(((x - m) / s)^4) -
    3 * (n - 1)^2 / ((n - 2) * (n - 3)) }

obs_sk <- sapply(ITEMS, function(i) skew(sub$resp[sub$item == i]))
obs_ku <- sapply(ITEMS, function(i) kurt(sub$resp[sub$item == i]))

cat(sprintf("%-6s %9s %9s %8s   %9s %9s %8s\n",
            "item", "pub Sk", "obs Sk", "diff", "pub Ku", "obs Ku", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-6s %9.2f %9.2f %8.3f   %9.2f %9.2f %8.3f\n",
                ITEMS[i], PUB_SK[i], obs_sk[i], obs_sk[i] - PUB_SK[i],
                PUB_KU[i], obs_ku[i], obs_ku[i] - PUB_KU[i]))

worst <- max(c(abs(obs_sk - PUB_SK), abs(obs_ku - PUB_KU)))
cat(sprintf("\nlargest deviation: %.3f (tolerance %.2f)\n", worst, TOL))

# Falsifiability: would any OTHER assignment of the published rows to the columns fit?
best_perm_hits <- 0
for (p in list(c(2,1,3,4,5,6,7), c(1,2,4,3,5,6,7), c(1,2,3,4,5,7,6))) {
    hits <- sum(abs(obs_sk - PUB_SK[p]) <= TOL & abs(obs_ku - PUB_KU[p]) <= TOL)
    best_perm_hits <- max(best_perm_hits, hits)
}
cat(sprintf("adjacent-swap permutations match at most %d of 7 items (identity matches %d)\n",
            best_perm_hits, sum(abs(obs_sk - PUB_SK) <= TOL & abs(obs_ku - PUB_KU) <= TOL)))

cat("Note: this route settles link (B) only -- published item number to live column.\n",
    "Link (A), appendix row order to item number, rests on the code-keyed English CFQ\n",
    "items in PMC11875431 / PMC13082997, which is a text comparison, not a data check.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
