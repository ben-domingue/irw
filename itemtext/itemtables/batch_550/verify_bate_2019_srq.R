# verify_bate_2019_srq.R -- Step 5b mapping check for bate_2019_srq (batch_550).
#
# Claim: SRQ01..SRQ20 (the deposit's own column codes, which the processing
# script keeps unchanged) are the 20 statements of Bate & Dudfield (2019) PeerJ
# 7:e6330 Table 1 in the order printed. The paper never says Table 1 is in
# questionnaire order and the deposit (.xlsx) has no labels, so the mapping is
# paper_order and has to be tested against the data.
#
# Three checks, all on the live IRW table:
#  A. Totals: summed items reproduce Table 2's SRQ mean (SD) per experiment
#     (Exp1 89.64 (8.11), Exp2 78.91 (9.94)). Establishes that the stored items
#     are ALREADY reverse-coded (higher = better face recognition), which is
#     what the per-item anchor direction in option_text rests on.
#  B. PCA/varimax on Exp1 (the paper's calibration sample): variance explained
#     must reproduce 27.35 / 8.23 / 6.81 %, and, under the claimed order, the
#     six highest loaders on one component must be the paper's six highest
#     Factor-1 (memory) loaders {13,14,15,16,18,20}, and the three highest on
#     another must be its three highest Factor-2 (spotting) loaders {6,7,9}.
#     Chance of each under a random permutation: 1/38760 and 1/1140.
#  C. Wording-method component: every item loading >= .25 on the remaining
#     component must be one of the 10 negatively-worded statements in Table 1
#     order {1,3,4,5,8,10,11,12,17,19}.
#
# NOT established: the order WITHIN each cluster (e.g. 13 vs 14 vs 15, or
# which negative item is which). The published loading values themselves do
# not reproduce cell-for-cell from the deposit (e.g. Table 1 prints no loading
# at all for items 1, 5 and 11, which load .62/.66/.52 here), so this is a
# pattern match, not a value match -> PARTIAL.

suppressMessages({ library(irw); library(psych) })

TABLE <- "bate_2019_srq"
d <- as.data.frame(irw::irw_fetch(TABLE))
I <- sprintf("SRQ%02d", 1:20)

wide <- function(x) {
  w <- reshape(x[, c("id", "item", "resp")], idvar = "id", timevar = "item",
               direction = "wide")
  names(w) <- sub("^resp\\.", "", names(w))
  w[, I]
}

ok <- TRUE

# ---- A. totals vs Table 2 ---------------------------------------------------
PUB <- list(exp1_civilian = c(89.64, 8.11), exp2_police = c(78.91, 9.94))
cat("A. SRQ total vs Table 2\n")
for (s in names(PUB)) {
  tot <- rowSums(wide(d[d$cov_study == s, ]))
  cat(sprintf("  %-14s published %.2f (%.2f)  observed %.2f (%.2f)\n",
              s, PUB[[s]][1], PUB[[s]][2], mean(tot), sd(tot)))
  ok <- ok && abs(mean(tot) - PUB[[s]][1]) < 0.02 && abs(sd(tot) - PUB[[s]][2]) < 0.02
}

# ---- B. PCA on Exp1 ---------------------------------------------------------
X <- wide(d[d$cov_study == "exp1_civilian", ])
ev <- eigen(cor(X))$values
vexp <- 100 * ev[1:3] / 20
cat(sprintf("\nB. variance explained: published 27.35 8.23 6.81  observed %s\n",
            paste(sprintf("%.2f", vexp), collapse = " ")))
ok <- ok && all(abs(vexp - c(27.35, 8.23, 6.81)) < 0.02)

L <- unclass(principal(X, 3, rotate = "varimax")$loadings)
rownames(L) <- 1:20
top <- function(k, n) sort(as.integer(names(sort(abs(L[, k]), decreasing = TRUE))[1:n]))
F1 <- c(13, 14, 15, 16, 18, 20); F2 <- c(6, 7, 9)
k1 <- which(sapply(1:3, function(k) setequal(top(k, 6), F1)))
k2 <- which(sapply(1:3, function(k) setequal(top(k, 3), F2)))
for (k in 1:3) cat(sprintf("  component %d top-6: %s\n", k, paste(top(k, 6), collapse = ",")))
cat(sprintf("  published F1 top-6 {%s}: matched by component %s\n",
            paste(F1, collapse = ","), if (length(k1)) k1 else "NONE"))
cat(sprintf("  published F2 top-3 {%s}: matched by component %s\n",
            paste(F2, collapse = ","), if (length(k2)) k2 else "NONE"))
ok <- ok && length(k1) == 1 && length(k2) == 1 && k1 != k2

# ---- C. negative-wording component ------------------------------------------
NEG <- c(1, 3, 4, 5, 8, 10, 11, 12, 17, 19)
if (length(k1) == 1 && length(k2) == 1 && k1 != k2) {
  k3 <- setdiff(1:3, c(k1, k2))
  hi <- which(abs(L[, k3]) >= 0.25)
  cat(sprintf("\nC. items loading >= .25 on component %d: %s\n", k3, paste(hi, collapse = ",")))
  cat(sprintf("   of these, negatively worded under the claimed order: %d / %d\n",
              sum(hi %in% NEG), length(hi)))
  ok <- ok && length(hi) >= 6 && all(hi %in% NEG)
}

cat("\nNot established: order within each cluster; published loading VALUES do not\n",
    "reproduce cell for cell (Table 1 leaves items 1, 5, 11 blank). Status PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
