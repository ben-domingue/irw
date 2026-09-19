# verify_sun_2016_risky_choice_graph.R -- Step 5b, route 1 (per-item published statistics).
#
# Claim: resulta..resultd are choice Pairs 1..4 of Sun et al. (2016) PLOS ONE
# 10.1371/journal.pone.0146914, Experiment 1, Table 1, and resp 1 = option A
# (the probability bet), resp 0 = option B (the money bet).
#
# The paper publishes, per pair, (i) the % choosing the probability bet in each
# graph-scale condition (Table 1) and (ii) a Pearson chi-square (1, N=189) for
# condition x choice (Results). The four chi-squares are all distinct (closest two
# differ by 1.7), so matching them pins every item code to exactly one pair; the
# chi-square is invariant to flipping resp, so the Table 1 percentages are what
# pin the resp direction. The live table's cov_graph_condition carries the .sav's
# `condition` (1 = N 95 = probability-distance-compressed, 2 = N 94).

suppressMessages(library(irw))
TABLE <- "sun_2016_risky_choice_graph"

PUB_CHI  <- c(2.760, 6.484, 4.825, 9.029)           # pairs 1..4
PUB_PCT1 <- c(62, 41, 55, 44)                        # prob-distance compressed (N=95)
PUB_PCT2 <- c(73, 60, 70, 68)                        # money-distance compressed (N=94)
ITEMS    <- c("resulta", "resultb", "resultc", "resultd")

d <- as.data.frame(irw::irw_fetch(TABLE))
d$cond <- as.character(d$cov_graph_condition)
cat("rows:", nrow(d), " ids:", length(unique(d$id)), "\n")
cat("persons per condition:\n"); print(tapply(d$id, d$cond, function(x) length(unique(x))))

chi <- function(tab) suppressWarnings(unname(chisq.test(tab, correct = FALSE)$statistic))

obs_chi <- obs1 <- obs2 <- numeric(4)
for (i in 1:4) {
    s <- d[d$item == ITEMS[i], ]
    obs_chi[i] <- chi(table(s$cond, s$resp))
    obs1[i] <- 100 * mean(s$resp[s$cond == "1"] == 1)
    obs2[i] <- 100 * mean(s$resp[s$cond == "2"] == 1)
}

cat(sprintf("\n%-8s %6s | %9s %9s | %7s %7s | %7s %7s\n",
            "item", "pair", "chi2 pub", "chi2 obs", "c1 pub", "c1 obs", "c2 pub", "c2 obs"))
for (i in 1:4)
    cat(sprintf("%-8s %6d | %9.3f %9.3f | %7.0f %7.1f | %7.0f %7.1f\n",
                ITEMS[i], i, PUB_CHI[i], obs_chi[i], PUB_PCT1[i], obs1[i], PUB_PCT2[i], obs2[i]))

# Identity: does each item's observed chi-square match ITS pair and no other?
M <- abs(outer(obs_chi, PUB_CHI, "-"))
dimnames(M) <- list(ITEMS, paste0("pair", 1:4))
cat("\n|chi2 obs - chi2 pub| matrix (rows = item, cols = published pair):\n"); print(round(M, 3))
best <- apply(M, 1, which.min)
id_ok <- all(best == 1:4) && all(diag(M) < 0.0015)
cat("best-matching pair per item:", paste(ITEMS, best, sep = "->", collapse = " "), "\n")
cat("diagonal max |diff|:", round(max(diag(M)), 4), " smallest off-diagonal:", round(min(M[row(M) != col(M)]), 3), "\n")

# Direction: percentages of resp==1 must match the % choosing the probability bet
# (a flipped coding would give 100 - these, e.g. 38/27 for pair 1).
dev1 <- abs(obs1 - PUB_PCT1); dev2 <- abs(obs2 - PUB_PCT2)
dev1f <- abs((100 - obs1) - PUB_PCT1); dev2f <- abs((100 - obs2) - PUB_PCT2)
cat("\nmean |% dev| as coded:", round(mean(c(dev1, dev2)), 2),
    "  if resp were flipped:", round(mean(c(dev1f, dev2f)), 2), "\n")
# Known misprint: pair 4, condition 2 printed 68%; the data give 62/94 = 66.0%,
# and the published chi2 9.029 is reproduced exactly only by 62/94 (64/94 would not).
alt <- matrix(c(42, 53, 64, 30), 2, byrow = TRUE)
cat("pair 4 chi2 if cond-2 were 64/94 A (=68%):", round(chi(alt), 3), " vs published 9.029\n")
dir_ok <- all(dev1[1:4] < 0.6) && all(dev2[1:3] < 0.6) && abs(dev2[4] - 2.0) < 0.1 &&
          mean(c(dev1f, dev2f)) > 20

cat("\nNOT established: nothing about the graph rendering each respondent saw (condition is\n",
    "a covariate), and the pair-4 condition-2 printed 68% is treated as a misprint because the\n",
    "published chi-square reproduces exactly from 66.0%.\n", sep = "")
cat(if (id_ok && dir_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
