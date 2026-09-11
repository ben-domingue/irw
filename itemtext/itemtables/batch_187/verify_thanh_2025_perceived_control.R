# verify_thanh_2025_perceived_control.R
#
# Claim: live items PBC1..PBC5 are "Perceived behavioral control 1".."5" of the study's
# S1 Appendix (journal.pone.0320053.s001 docx), in that order.
#
# The IRW code IS the S1 File (.s002 xlsx) column name (data/thanh_2025_green_behavior.py
# melts columns matching ^PBC\d+$ unrenamed), so there is no positional step. The
# number tie PBCn <-> "Perceived behavioral control n" is a label-number match, not a
# data label, so it is checked here against the paper's Table 2 (journal.pone.0320053.t002,
# image): PLS-SEM factor loadings for the five PBC statements, printed in appendix order,
# and Cronbach's alpha for the block.
#
# Published (Table 2, "Perceived Behavior Control", alpha 0.919, N=407):
#   1 "I may control the performance ..."          0.831
#   2 "I support environmental practice ..."       0.901
#   3 "I can perform pro-environmentally ..."      0.888
#   4 "It is convenient for me ..."                0.900
#   5 "I have my own decision ..."                 0.826
# SmartPLS mode-A loadings are item-composite correlations; the unit-weight item-total
# correlation and the first-principal-component loading are used as close proxies.

suppressMessages(library(irw))

TABLE <- "thanh_2025_perceived_control"
PUB <- c(0.831, 0.901, 0.888, 0.900, 0.826)
PUB_ALPHA <- 0.919
TOL <- 0.015
items <- paste0("PBC", 1:5)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, items])
X <- X[complete.cases(X), ]
cat("complete cases:", nrow(X), "\n")

k <- ncol(X)
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
cat(sprintf("Cronbach alpha: observed %.3f, published %.3f\n", alpha, PUB_ALPHA))

itot <- as.numeric(cor(X, rowSums(X)))
e <- eigen(cor(X))
pc1 <- abs(e$vectors[, 1]) * sqrt(e$values[1])
obs <- (itot + pc1) / 2

cat(sprintf("\n%-5s %9s %10s %8s %8s %8s\n", "item", "published", "item-total", "PC1", "mean", "diff"))
for (i in 1:5) cat(sprintf("%-5s %9.3f %10.3f %8.3f %8.3f %8.3f\n",
                           items[i], PUB[i], itot[i], pc1[i], obs[i], obs[i] - PUB[i]))
own_dev <- max(abs(obs - PUB))
cat(sprintf("\nidentity mapping: max |obs - published| = %.3f (tol %.3f)\n", own_dev, TOL))

# All 120 assignments of the five published rows to the five codes.
perm <- function(v) if (length(v) == 1) matrix(v, 1) else
  do.call(rbind, lapply(seq_along(v), function(i) cbind(v[i], perm(v[-i]))))
P <- perm(1:5)
devs <- apply(P, 1, function(p) max(abs(obs - PUB[p])))
within <- P[devs <= TOL, , drop = FALSE]
cat(sprintf("assignments within tolerance: %d of %d\n", nrow(within), nrow(P)))
for (r in seq_len(nrow(within)))
  cat("  published row order for PBC1..5:", paste(within[r, ], collapse = " "),
      sprintf("(max dev %.3f)\n", max(abs(obs - PUB[within[r, ]]))))

# Structural claim the route CAN make: the two weakest-loading codes are PBC1 and PBC5,
# as published rows 1 and 5 are the two weakest.
low2 <- sort(items[order(obs)][1:2])
cat("two lowest-loading codes in data:", paste(low2, collapse = ", "),
    "(published: rows 1 and 5)\n")

ok <- abs(alpha - PUB_ALPHA) <= 0.005 && own_dev <= TOL &&
  identical(low2, c("PBC1", "PBC5")) &&
  all(apply(within, 1, function(p) setequal(p[c(1, 5)], c(1, 5))))

cat("\nEstablishes: every assignment within tolerance puts published rows {1,5} (the two\n",
    "weak loadings, 0.831/0.826) on codes {PBC1,PBC5} and rows {2,3,4} (0.901/0.888/0.900)\n",
    "on {PBC2,PBC3,PBC4}; alpha matches the PBC block.\n",
    "Does NOT establish: order within {PBC1,PBC5} (the 1<->5 swap fits BETTER, max dev\n",
    "0.003 vs 0.007 for identity) or within {PBC2,PBC3,PBC4} (all six orders within\n",
    "0.014). Those orders rest on the S1 Appendix numbering matching the column numbers.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
