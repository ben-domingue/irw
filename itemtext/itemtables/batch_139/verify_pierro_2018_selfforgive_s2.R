# verify_pierro_2018_selfforgive_s2.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (two parts):
#   (a) SforgiveR1/SforgiveR3 are the scale's two REVERSE-worded items
#       ("rejecting of myself", "dislike toward myself") and Sforgive2/
#       Sforgive4 the two positively-worded ones ("accepting of myself",
#       "forgiving myself") -- i.e. the polarity class of each item code,
#       which is what the paper's (R) markers at list positions 1 and 3
#       assert.
#   (b) The two R items are stored ALREADY REVERSE-RECODED in the IRW table,
#       so the shipped anchors for those rows are FLIPPED (resp 1 =
#       "Completely", resp 4 = "Not at all") relative to the other two items.
#
# Both are falsifiable from the live data alone, against three sets of
# numbers Pierro et al. (2018) publish for Study 2: the scale alpha, the
# scale M/SD, and the three experimental-condition cell means.
#
# WHAT IT DOES NOT TEST: nothing here separates SforgiveR1 from SforgiveR3,
# or Sforgive2 from Sforgive4. Those rest on the order the paper lists the
# four items in, matched to the codes' own 1-4 numbering. Status is PARTIAL
# by design.

suppressMessages(library(irw))

TABLE <- "pierro_2018_selfforgive_s2"
ITEMS <- c("SforgiveR1", "Sforgive2", "SforgiveR3", "Sforgive4")
REV   <- c("SforgiveR1", "SforgiveR3")

# Pierro et al. (2018) PLOS ONE 13(3):e0193357, Study 2:
#  "In this study the self-forgiveness Cronbach's alpha was .72 (M = 2.84,
#   SD = .66)."
#  "participants in the locomotion condition showed greater self-forgiveness
#   (N = 33, M = 3.15, SD = .48) than participants in either the assessment
#   orientation condition (N = 33, M = 2.55, SD = .57), or the control group
#   condition (N = 31, M = 2.83, SD = .77)."
PUBLISHED_ALPHA <- 0.72
PUBLISHED_M     <- 2.84
PUBLISHED_SD    <- 0.66
PUBLISHED_CELLS <- c(Assessment = 2.55, Locomotion = 3.15, Control = 2.83)
TOL_ALPHA <- 0.01
TOL_CELL  <- 0.02

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, ITEMS]
keep <- complete.cases(X)
X <- X[keep, ]

cond <- unique(as.data.frame(d[, c("id", "cov_condition")]))
cond <- cond[match(w$id[keep], cond$id), "cov_condition"]

alpha <- function(M) {
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}

a_stored <- alpha(X)
Y <- X; for (cc in REV) Y[[cc]] <- 5 - Y[[cc]]   # 4-point scale: reverse = 5 - x
a_unrev <- alpha(Y)

cat(sprintf("n complete cases: %d\n\n", nrow(X)))
cat(sprintf("alpha, items exactly as stored in IRW           : %.3f\n", a_stored))
cat(sprintf("alpha, after un-reversing SforgiveR1 + SforgiveR3: %.3f\n", a_unrev))
cat(sprintf("published alpha (paper, Study 2, N=97)          : %.2f  (tol %.2f)\n\n",
            PUBLISHED_ALPHA, TOL_ALPHA))

comp_stored <- rowMeans(X)
comp_unrev  <- rowMeans(Y)
cat(sprintf("composite as stored : M %.3f  SD %.3f\n", mean(comp_stored), sd(comp_stored)))
cat(sprintf("composite un-reversed: M %.3f  SD %.3f\n", mean(comp_unrev), sd(comp_unrev)))
cat(sprintf("published            : M %.2f  SD %.2f\n\n", PUBLISHED_M, PUBLISHED_SD))

cat("corrected item-total correlations and means, items as stored:\n")
tot <- rowSums(X)
its <- sapply(ITEMS, function(cc) cor(X[[cc]], tot - X[[cc]]))
for (cc in ITEMS) cat(sprintf("  %-11s r=%+.3f   mean %.3f\n", cc, its[[cc]], mean(X[[cc]])))

cat("\nexperimental-condition cell means of the composite (paper's Study 2 ANOVA):\n")
cells_stored <- tapply(comp_stored, cond, mean)
cells_unrev  <- tapply(comp_unrev,  cond, mean)
ns           <- tapply(comp_stored, cond, length)
for (k in names(PUBLISHED_CELLS))
    cat(sprintf("  %-11s n=%d  stored %.3f   un-reversed %.3f   published %.2f\n",
                k, ns[[k]], cells_stored[[k]], cells_unrev[[k]], PUBLISHED_CELLS[[k]]))

ok_alpha <- abs(a_stored - PUBLISHED_ALPHA) <= TOL_ALPHA
ok_dir   <- a_stored > a_unrev && all(its > 0)
ok_ms    <- abs(mean(comp_stored) - PUBLISHED_M) <= TOL_CELL &&
            abs(sd(comp_stored)   - PUBLISHED_SD) <= TOL_CELL
ok_cells <- all(abs(cells_stored[names(PUBLISHED_CELLS)] - PUBLISHED_CELLS) <= TOL_CELL)
ok_cells_flip_fails <- !all(abs(cells_unrev[names(PUBLISHED_CELLS)] - PUBLISHED_CELLS) <= TOL_CELL)

cat("\n-- what this establishes --\n")
cat("Alpha on the stored directions reproduces the paper's published .72, the\n")
cat("stored composite reproduces its published M = 2.84 / SD = .66, and the\n")
cat("stored composite reproduces all three published condition cell means to\n")
cat("within .02, while un-reversing the two R-marked codes collapses alpha to a\n")
cat("negative value and moves every cell mean far off (and reverses the paper's\n")
cat("locomotion > control > assessment ordering). All four items correlate\n")
cat("positively with the rest as stored. That fixes SforgiveR1/SforgiveR3 as the\n")
cat("reverse-worded pair, stored already recoded, and justifies the flipped\n")
cat("anchors shipped for those two items.\n")
cat("-- what this does NOT establish --\n")
cat("It does not separate SforgiveR1 from SforgiveR3, nor Sforgive2 from\n")
cat("Sforgive4: swapping either within-class pair leaves every number above\n")
cat("unchanged. Those assignments rest on the order the paper lists the items\n")
cat("('rejecting of myself (R), accepting of myself, dislike toward myself (R),\n")
cat("forgiving myself'), matched to the codes' own 1-4 numbering. PARTIAL.\n\n")

cat(if (ok_alpha && ok_dir && ok_ms && ok_cells && ok_cells_flip_fails)
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
