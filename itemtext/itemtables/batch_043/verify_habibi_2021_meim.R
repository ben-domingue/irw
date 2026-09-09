# verify_habibi_2021_meim.R -- Step 5b re-runnable mapping evidence.
#
# Claim under test: the IRW item codes Q1..Q12 (which ARE the column names of the
# study's raw supplement peerj-09-10752-s001.csv) correspond to MEIM items 1..12 as
# numbered in the study's own Persian questionnaire (supplement S3) and in the paper's
# Table 2, which prints the English wording of each numbered item.
#
# Two independent routes, both against numbers the paper/supplements published:
#
#  (A) Table 2 prints, per numbered item, "Z = Z score for tests of univariate
#      normality" -- a monotone function of that item's skewness. Skewness computed
#      from the live IRW data must track it across all 12 items.
#
#  (B) Supplement S2 publishes each respondent's Commitment and Exploration subscale
#      MEANS (its rows are in a different order from S1, so only the distributions are
#      comparable). The canonical MEIM subscale membership -- Exploration = items
#      1,2,4,8,10; Commitment = items 3,5,6,7,9,11,12 -- must be the best-fitting
#      subset among ALL C(12,5) and C(12,7) subsets of the live items.
#
# What this does NOT establish: neither route separates items whose statistics are
# near-tied. Route A leaves four adjacent rank inversions -- (5,9), (6,12), (3,7)
# within commitment and (1,8) within exploration -- and route B pins subscale
# membership only, not order within a subscale.

suppressMessages(library(irw))
TABLE <- "habibi_2021_meim"

# --- published values, hard-coded ------------------------------------------------
# PeerJ 2021;9:e10752 Table 2, column Z (item number -> Z).
PUB_Z <- c(`1` = -0.76, `2` = 1.16, `3` = -1.29, `4` = -0.13, `5` = -4.04, `6` = -3.26,
           `7` = -1.48, `8` = -1.11, `9` = -4.39, `10` = -2.42, `11` = -2.64, `12` = -3.17)
# Percentiles (0,.01,...,1) of the per-respondent subscale means published in supplement S2.
PUB_EXP_Q <- c(1, 1.038, 1.2, 1.4, 1.4, 1.6, 1.6, 1.6, 1.8, 1.8, 1.8, 1.8, 1.856, 2, 2, 2, 2, 2, 2, 2.122, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.558, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.614, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 3, 3, 3, 3, 3, 3, 3, 3, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.316, 3.4, 3.4, 3.4, 3.4, 3.4, 3.4, 3.4, 3.4, 3.6, 3.6, 3.6, 3.6, 3.6, 3.6, 3.8, 3.8, 3.8, 4)
PUB_COM_Q <- c(1, 1.3, 1.6, 1.85714, 1.85714, 1.85714, 2, 2.14286, 2.14286, 2.27143, 2.28571, 2.28571, 2.31429, 2.42857, 2.42857, 2.42857, 2.42857, 2.57143, 2.57143, 2.57143, 2.57143, 2.57143, 2.57143, 2.57143, 2.57143, 2.71429, 2.71429, 2.71429, 2.71429, 2.71429, 2.71429, 2.71429, 2.71429, 2.71429, 2.77143, 2.85714, 2.85714, 2.85714, 2.85714, 2.85714, 2.85714, 3, 3, 3, 3, 3, 3, 3, 3, 3.14286, 3.14286, 3.14286, 3.14286, 3.14286, 3.14286, 3.14286, 3.28571, 3.28571, 3.28571, 3.28571, 3.28571, 3.28571, 3.31429, 3.42857, 3.42857, 3.42857, 3.42857, 3.42857, 3.42857, 3.42857, 3.57143, 3.57143, 3.57143, 3.71429, 3.71429, 3.71429, 3.71429, 3.71429, 3.71429, 3.71429, 3.71429, 3.72857, 3.85714, 3.85714, 3.85714, 3.85714, 3.85714, 3.85714, 3.85714, 3.85714, 3.85714, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
EXP <- as.integer(c(1, 2, 4, 8, 10)); COM <- as.integer(c(3, 5, 6, 7, 9, 11, 12))

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
its <- paste0("Q", 1:12)

# --- route A ---------------------------------------------------------------------
skewness <- function(x) { x <- x[!is.na(x)]; m <- mean(x)
  mean((x - m)^3) / (sqrt(mean((x - m)^2)))^3 }
obs <- sapply(its, function(i) skewness(d$resp[d$item == i]))
mn  <- sapply(its, function(i) mean(d$resp[d$item == i], na.rm = TRUE))

cat("=== Route A: published normality Z (Table 2) vs observed skewness ===\n")
cat(sprintf("%-5s %8s %10s %8s\n", "item", "pub Z", "obs skew", "mean"))
for (k in 1:12)
  cat(sprintf("%-5s %8.2f %10.3f %8.3f\n", its[k], PUB_Z[k], obs[k], mn[k]))
r  <- cor(PUB_Z, obs)
rs <- cor(rank(PUB_Z), rank(obs))
cat(sprintf("\nPearson r = %.4f   Spearman rho = %.4f\n", r, rs))
cat("published rank order:", its[order(PUB_Z)], "\n")
cat("observed  rank order:", its[order(obs)], "\n")
A <- (r >= 0.90 && rs >= 0.90)

# --- route B ---------------------------------------------------------------------
w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
qdist <- function(cols, pubq) {
  m <- rowMeans(as.data.frame(w)[, paste0("Q", cols), drop = FALSE])
  m <- m[!is.na(m)]
  mean(abs(as.numeric(quantile(m, seq(0, 1, 0.01))) - pubq))
}
rank_of <- function(k, truth, pubq) {
  cmb <- combn(1:12, k, simplify = FALSE)
  sc  <- sapply(cmb, qdist, pubq = pubq)
  o   <- order(sc)
  list(best = cmb[[o[1]]], best_sc = sc[o[1]], next_sc = sc[o[2]],
       truth_rank = which(sapply(cmb[o], function(z) setequal(z, truth))),
       n = length(cmb))
}
cat("\n=== Route B: subscale membership vs supplement S2 subscale-mean percentiles ===\n")
bE <- rank_of(5, EXP, PUB_EXP_Q); bC <- rank_of(7, COM, PUB_COM_Q)
cat(sprintf("Exploration: best of %d 5-item subsets = {%s}, mean|dq| = %.5f (runner-up %.5f); canonical {%s} ranks %d\n",
            bE$n, paste0("Q", bE$best, collapse = ","), bE$best_sc, bE$next_sc,
            paste0("Q", EXP, collapse = ","), bE$truth_rank))
cat(sprintf("Commitment : best of %d 7-item subsets = {%s}, mean|dq| = %.5f (runner-up %.5f); canonical {%s} ranks %d\n",
            bC$n, paste0("Q", bC$best, collapse = ","), bC$best_sc, bC$next_sc,
            paste0("Q", COM, collapse = ","), bC$truth_rank))
B <- (bE$truth_rank == 1 && bC$truth_rank == 1)

cat("\nNOTE: route A leaves four adjacent rank inversions -- Q5/Q9, Q6/Q12, Q3/Q7 and\n",
    "Q1/Q8 -- so these pairs are not separated from each other; route B pins subscale\n",
    "membership, not order within a subscale. Status recorded as PARTIAL.\n", sep = "")
cat(if (A && B) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
