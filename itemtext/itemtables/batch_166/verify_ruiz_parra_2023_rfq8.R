# verify_ruiz_parra_2023_rfq8.R -- Step 5b mapping check for ruiz_parra_2023_rfq8 (batch_166).
#
# CLAIM: live codes RFQ8_1..RFQ8_8 are the RFQ-8 items numbered 1..8 in Ruiz-Parra et al.
# (2023) S2 Appendix (Spanish) / S1 Appendix (English). The code IS the S9 workbook column
# name, but that name carries only a number, so the number->wording tie is an inference from
# the paper's numbering (mapping_basis = paper_explicit). This script tests it against
# per-item numbers the paper prints for the SAME non-clinical sample:
#
#   A. Fig 1 (doi:10.1371/journal.pone.0274378.g001): one-factor CFA, WLSMV, item 7 reversed,
#      error covariance item3~~item4. Standardised loadings 1..8 and the 3~~4 covariance.
#   B. Fig 3 (.g003): two-factor EFA, Promax. Salient (>=.30) loadings:
#      F1 = item2 .74, item5 .38, item6 .77, item7 .44, item8 .44; F2 = item3 .81, item4 .82;
#      item1 below .30 on both (greyed out, value not printed).
#   C. Text: alpha .763 (Table 2); "removing the item 1 ... alpha improved to 0.779".
#   D. Polarity: item 7 ("I always know what I feel") is the only positively-worded item and
#      is reverse-scored by the paper, so RAW it must be the only item correlating
#      negatively with the rest.
#
# Uniqueness test: holding the observed per-item vectors fixed, reassign them to the
# published item slots under all 8! = 40320 permutations and score the misfit against
# A+B. PASS requires the claimed (identity) assignment to be the unique minimum; the
# per-transposition margins printed below are what decide VERIFIED vs PARTIAL.

suppressMessages({library(irw); library(lavaan); library(psych)})

TABLE <- "ruiz_parra_2023_rfq8"
PUB_CFA  <- c(0.25, 0.68, 0.56, 0.52, 0.46, 0.84, 0.36, 0.53)
PUB_COV34 <- 0.59
# EFA pattern: NA = greyed out (|loading| < .30, value not printed)
PUB_EFA <- rbind(c(NA, 0.74, NA, NA, 0.38, 0.77, 0.44, 0.44),   # F1
                 c(NA, NA, 0.81, 0.82, NA, NA, NA, NA))          # F2
PUB_ALPHA <- 0.763; PUB_ALPHA_DROP1 <- 0.779
TOL <- 0.07

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, paste0("RFQ8_", 1:8)]
cat("respondents:", nrow(X), " (paper: 602 non-clinical; live table 605)\n\n")

# D. raw polarity
R <- cor(X, use = "pairwise")
negcount <- sapply(1:8, function(i) sum(R[i, -i] < 0))
cat("D. raw polarity: number of negative correlations with the other 7 items\n")
print(setNames(negcount, names(X)))
polarity_ok <- negcount[7] == 7 && all(negcount[-7] == 1)

names(X) <- paste0("i", 1:8)
X$i7 <- 8 - X$i7

# C. alpha
a <- psych::alpha(X, warnings = FALSE)
alpha <- a$total$raw_alpha; drop1 <- a$alpha.drop$raw_alpha
cat(sprintf("\nC. alpha observed %.3f vs published %.3f\n", alpha, PUB_ALPHA))
cat("   alpha-if-dropped:", sprintf("%.3f", drop1), "\n")
# The paper (N=602) says only removing item 1 improves alpha, to 0.779. In the live 605-row
# table item 1 is still the largest alpha-if-dropped and reproduces 0.779 to 0.001, but
# item 7's also edges above the full alpha (0.770 vs 0.767) -- a within-sampling departure
# from the paper's rounded "only item 1", printed rather than hidden. The test is therefore
# the argmax and the value, not the count.
cat(sprintf("   argmax alpha-if-dropped = item %d (%.3f vs published item 1 = %.3f); items whose drop exceeds full alpha: %s\n",
            which.max(drop1), max(drop1), PUB_ALPHA_DROP1, paste(which(drop1 > alpha), collapse = ",")))
alpha_ok <- abs(alpha - PUB_ALPHA) < 0.02 && which.max(drop1) == 1 && abs(drop1[1] - PUB_ALPHA_DROP1) < 0.01

# A. CFA
f <- cfa('F =~ i1+i2+i3+i4+i5+i6+i7+i8
         i3 ~~ i4', data = X, ordered = names(X), estimator = "WLSMV", std.lv = TRUE)
s <- standardizedSolution(f)
obs_cfa <- s$est.std[s$op == "=~"]
obs_cov34 <- s$est.std[s$op == "~~" & s$lhs == "i3" & s$rhs == "i4"]
cat("\nA. one-factor CFA loadings (WLSMV, item 7 reversed, 3~~4)\n")
cat(sprintf("%-6s %9s %9s %7s\n", "item", "published", "observed", "diff"))
for (i in 1:8) cat(sprintf("%-6s %9.2f %9.2f %7.2f\n", i, PUB_CFA[i], obs_cfa[i], obs_cfa[i] - PUB_CFA[i]))
cat(sprintf("3~~4   %9.2f %9.2f %7.2f\n", PUB_COV34, obs_cov34, obs_cov34 - PUB_COV34))

# B. EFA (ML on Pearson correlations, Promax -- reproduces Fig 3 closest)
e <- fa(na.omit(X), nfactors = 2, rotate = "promax", fm = "ml")
L <- unclass(e$loadings)
# align factor order to published (F1 = the factor item 2 loads on)
if (abs(L[2, 1]) < abs(L[2, 2])) L <- L[, 2:1]
obs_efa <- t(L)
cat("\nB. two-factor EFA pattern (Promax)\n")
cat(sprintf("%-6s %8s %8s %8s %8s\n", "item", "pubF1", "obsF1", "pubF2", "obsF2"))
for (i in 1:8) cat(sprintf("%-6s %8s %8.2f %8s %8.2f\n", i,
    ifelse(is.na(PUB_EFA[1, i]), "<.30", sprintf("%.2f", PUB_EFA[1, i])), obs_efa[1, i],
    ifelse(is.na(PUB_EFA[2, i]), "<.30", sprintf("%.2f", PUB_EFA[2, i])), obs_efa[2, i]))

misfit <- function(p) {   # p[k] = observed item assigned to published slot k
    sse <- sum((obs_cfa[p] - PUB_CFA)^2)
    E <- obs_efa[, p, drop = FALSE]
    shown <- !is.na(PUB_EFA)
    sse <- sse + sum((E[shown] - PUB_EFA[shown])^2)
    sse + sum(pmax(0, abs(E[!shown]) - 0.30)^2)
}
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(r) c(v[i], r))))
P <- perms(1:8)
scores <- vapply(P, misfit, numeric(1))
id_score <- misfit(1:8)
o <- order(scores)
cat(sprintf("\nUniqueness over %d permutations: identity misfit %.4f\n", length(P), id_score))
cat(sprintf("best permutation: %s (misfit %.4f)\n", paste(P[[o[1]]], collapse = ","), scores[o[1]]))
cat(sprintf("second best:      %s (misfit %.4f, %.1fx identity)\n",
            paste(P[[o[2]]], collapse = ","), scores[o[2]], scores[o[2]] / id_score))
unique_min <- all(P[[o[1]]] == 1:8) && scores[o[2]] > id_score
cat("\nall 28 single transpositions, misfit as a multiple of identity (lowest = least separated):\n")
tr <- t(combn(8, 2))
trs <- apply(tr, 1, function(ab) { p <- 1:8; p[ab] <- p[rev(ab)]; misfit(p) / id_score })
ordtr <- order(trs)
for (k in ordtr) cat(sprintf("  swap %d<->%d: %6.1fx\n", tr[k, 1], tr[k, 2], trs[k]))

max_cfa <- max(abs(c(obs_cfa - PUB_CFA, obs_cov34 - PUB_COV34)))
shown <- !is.na(PUB_EFA)
max_efa <- max(abs(obs_efa[shown] - PUB_EFA[shown]))
grey_ok <- all(abs(obs_efa[!shown]) < 0.30)
cat(sprintf("\nmax |diff| CFA %.3f, EFA salient %.3f (tol %.2f); greyed cells all < .30: %s\n",
            max_cfa, max_efa, TOL, grey_ok))
cat("polarity ok:", polarity_ok, " alpha ok:", alpha_ok, " identity unique minimum:", unique_min, "\n")
cat("Not established: (1) the ORDER WITHIN THE 3/4 PAIR is only weakly separated -- the 3<->4\n",
    "swap costs ~1.3x identity misfit, resting on a published CFA loading gap of .04 (.56/.52)\n",
    "that is about one standard error at N=605; the EFA does not separate them (.81/.82). So this\n",
    "route is PARTIAL, not VERIFIED. (2) It tests the S9 column numbering against the paper's\n",
    "numbering statistically; the data file carries no label to read.\n", sep = "")

pass <- polarity_ok && alpha_ok && unique_min && max_cfa <= TOL && max_efa <= TOL && grey_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
