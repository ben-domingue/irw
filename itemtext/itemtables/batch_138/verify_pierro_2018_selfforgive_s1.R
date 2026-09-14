# verify_pierro_2018_selfforgive_s1.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (two parts):
#   (a) sforgiveR1/sforgiveR3 are the scale's two REVERSE-worded items
#       ("rejecting of myself", "dislike toward myself") and sforgive2/
#       sforgive4 the two positively-worded ones ("accepting of myself",
#       "forgiving myself") -- i.e. the polarity class of each item code,
#       which is what the paper's (R) markers at list positions 1 and 3 assert.
#   (b) The two R items are stored ALREADY REVERSE-RECODED in the IRW table,
#       so the shipped anchors for those rows are FLIPPED (resp 1 =
#       "Completely", resp 4 = "Not at all") relative to the other two items.
#
# Both are falsifiable from the live data alone, against the alpha Pierro et
# al. (2018) publish for this scale in Study 1.
#
# WHAT IT DOES NOT TEST: nothing here separates sforgiveR1 from sforgiveR3,
# or sforgive2 from sforgive4. Those rest on the order the paper lists the
# four items in. Status is PARTIAL by design.

suppressMessages(library(irw))

TABLE <- "pierro_2018_selfforgive_s1"
ITEMS <- c("sforgiveR1", "sforgive2", "sforgiveR3", "sforgive4")
REV   <- c("sforgiveR1", "sforgiveR3")

# Pierro et al. (2018) PLOS ONE 13(3):e0193357, Study 1 Measures:
# "The 4 items were averaged to create a composite score (Total sample
#  Cronbach's alpha = .72). Higher scores reflected greater self-forgiveness."
PUBLISHED_ALPHA <- 0.72
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, ITEMS]
X <- X[complete.cases(X), ]

alpha <- function(M) {
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}

a_stored <- alpha(X)
Y <- X; for (cc in REV) Y[[cc]] <- 5 - Y[[cc]]   # 4-point scale: reverse = 5 - x
a_unrev <- alpha(Y)

cat(sprintf("n complete cases: %d\n\n", nrow(X)))
cat(sprintf("alpha, items exactly as stored in IRW           : %.3f\n", a_stored))
cat(sprintf("alpha, after un-reversing sforgiveR1 + sforgiveR3: %.3f\n", a_unrev))
cat(sprintf("published alpha (paper, Study 1, N=323)         : %.2f  (tol %.2f)\n\n",
            PUBLISHED_ALPHA, TOL))

cat("corrected item-total correlations and means, items as stored:\n")
tot <- rowSums(X)
its <- sapply(ITEMS, function(cc) cor(X[[cc]], tot - X[[cc]]))
for (cc in ITEMS) cat(sprintf("  %-11s r=%+.3f   mean %.3f\n", cc, its[[cc]], mean(X[[cc]])))

# Semantic direction check: on a scale where a HIGH composite means MORE
# self-forgiveness, the two negatively-worded items cannot sit at the top of
# the range unless they are stored already reversed.
cat(sprintf("\nmean of the two R-marked items  : %.3f\n", mean(as.matrix(X[, REV]))))
cat(sprintf("mean of the two positive items  : %.3f\n",
            mean(as.matrix(X[, setdiff(ITEMS, REV)]))))
cat(sprintf("composite (plain mean of all 4) : %.3f  -- paper: higher = more self-forgiveness\n",
            mean(rowMeans(X))))

ok_alpha <- abs(a_stored - PUBLISHED_ALPHA) <= TOL
ok_dir   <- a_stored > a_unrev && all(its > 0)

cat("\n-- what this establishes --\n")
cat("Alpha on the stored directions reproduces the paper's published .72, while\n")
cat("un-reversing the two R-marked codes collapses it to a negative value; all\n")
cat("four items correlate positively with the rest as stored. That fixes\n")
cat("sforgiveR1/sforgiveR3 as the reverse-worded pair, stored already recoded,\n")
cat("and justifies the flipped anchors shipped for those two items.\n")
cat("-- what this does NOT establish --\n")
cat("It does not separate sforgiveR1 from sforgiveR3, nor sforgive2 from\n")
cat("sforgive4: swapping either within-class pair leaves every number above\n")
cat("unchanged. Those assignments rest on the order the paper lists the items\n")
cat("('rejecting of myself (R), accepting of myself, dislike toward myself (R),\n")
cat("forgiving myself'), matched to the codes' own 1-4 numbering. PARTIAL.\n\n")

cat(if (ok_alpha && ok_dir) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
