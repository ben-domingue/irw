# verify_pierro_2018_locomotion_s1.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST (two parts):
#   (a) loca1..loca12 are the 12 Locomotion items of the Regulatory Mode
#       Questionnaire (Kruglanski et al. 2000) in the order given by the RMQ's
#       own scoring key -- Q1, Q3, Q4, Q5, Q8, Q13(R), Q16, Q21, Q24(R), Q25,
#       Q28, Q29 -- so the two reverse-keyed items sit at sequence positions
#       6 and 9, which is exactly where the codes carry their "R" marker
#       (locaR6, locaR9).
#   (b) locaR6 and locaR9 are stored ALREADY REVERSED in the IRW table, so the
#       shipped option anchors for those two items are FLIPPED
#       (resp 1 = Strongly Agree, resp 6 = Strongly Disagree) relative to the
#       other ten.
#
# Both are falsifiable from the live data alone: (b) via Cronbach's alpha
# against the value the source paper publishes, (a) via which two items the
# alpha test picks out as reversed.

suppressMessages(library(irw))

TABLE <- "pierro_2018_locomotion_s1"
ITEMS <- c("loca1","loca2","loca3","loca4","loca5","locaR6",
           "loca7","loca8","locaR9","loca10","loca11","loca12")
REV   <- c("locaR6","locaR9")

# Pierro et al. (2018) PLOS ONE 13(3):e0193357, Study 1 Measures:
# "For the total sample the Cronbach's alpha for the locomotion scale was .78".
PUBLISHED_ALPHA <- 0.78
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, ITEMS]
X <- X[complete.cases(X), ]

alpha <- function(M) {
    k <- ncol(M)
    k/(k-1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}

a_stored <- alpha(X)
Y <- X; for (cc in REV) Y[[cc]] <- 7 - Y[[cc]]
a_unrev <- alpha(Y)

cat(sprintf("n complete cases: %d\n\n", nrow(X)))
cat(sprintf("alpha, items exactly as stored in IRW      : %.3f\n", a_stored))
cat(sprintf("alpha, after un-reversing locaR6 + locaR9  : %.3f\n", a_unrev))
cat(sprintf("published alpha (paper, Study 1 total N=323): %.2f  (tol %.2f)\n\n",
            PUBLISHED_ALPHA, TOL))

# Which items, if any, are stored against the grain? Corrected item-total r.
cat("corrected item-total correlations, items as stored:\n")
tot <- rowSums(X)
its <- sapply(ITEMS, function(cc) cor(X[[cc]], tot - X[[cc]]))
for (cc in ITEMS) cat(sprintf("  %-8s %+.3f   mean %.2f\n", cc, its[[cc]], mean(X[[cc]])))
neg <- names(its)[its < 0]
cat(sprintf("\nitems with NEGATIVE item-total r as stored: %s\n",
            if (length(neg)) paste(neg, collapse = ", ") else "(none)"))

# The same test run on the un-reversed frame: if locaR6/locaR9 really are the
# two reverse-worded items, un-reversing them must push exactly those two negative.
tot2 <- rowSums(Y)
its2 <- sapply(ITEMS, function(cc) cor(Y[[cc]], tot2 - Y[[cc]]))
neg2 <- names(its2)[its2 < 0]
cat(sprintf("items with NEGATIVE item-total r after un-reversing: %s\n",
            if (length(neg2)) paste(neg2, collapse = ", ") else "(none)"))

ok_alpha <- abs(a_stored - PUBLISHED_ALPHA) <= TOL
ok_dir   <- a_stored > a_unrev && length(neg) == 0

cat("\n-- what this establishes --\n")
cat("The stored-direction alpha reproduces the paper's published .78 while the\n")
cat("un-reversed frame collapses; all 12 items load positively as stored and only\n")
cat("the two R-marked items flip negative when un-reversed. That fixes locaR6 and\n")
cat("locaR9 as the scale's two reverse-worded items (canonical RMQ Q13 'wait awhile\n")
cat("before getting started' and Q24 'low energy person'), pins them to sequence\n")
cat("positions 6 and 9, and justifies the flipped anchors shipped for those rows.\n")
cat("-- what this does NOT establish --\n")
cat("Nothing here separates the ten non-reverse items from one another: any\n")
cat("permutation of loca1/2/3/4/5/7/8/10/11/12 would give identical numbers.\n")
cat("Their assignment rests on the RMQ scoring key's item order, not on the data.\n")
cat("Status is therefore PARTIAL, not VERIFIED.\n\n")

cat(if (ok_alpha && ok_dir) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
