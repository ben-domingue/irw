# Step 5b evidence for qi_2025_self_concept_clarity, re-runnable.
#
# CLAIM UNDER TEST: SCC_1..SCC_12 carry, in order, items 1..12 of Campbell et al.
# (1996) Self-Concept Clarity Scale, stored RAW (not reverse-scored), where items
# 1,2,3,4,5,7,8,9,10,12 are reverse-keyed and 6 and 11 are positively keyed.
#
# Two independent falsifiable predictions:
#   (A) Route 6, keying polarity. Item-rest correlations computed on the RAW
#       responses must be NEGATIVE for exactly SCC_6 and SCC_11 and positive for
#       the other ten. A different assignment of the positive pair breaks this.
#   (B) Route 3, published statistic. Qi et al. (2025, Sci Data 12:1755) report
#       Cronbach's alpha = 0.82 for this scale in THIS sample. Alpha computed
#       after reversing exactly the ten canonical reverse items must reproduce it;
#       rival reversal sets must not.
#
# What this does NOT establish: the order of items WITHIN the ten-item reverse
# block, and it does not separate SCC_6 from SCC_11. Swapping the item_text of
# SCC_2 and SCC_3, or of SCC_6 and SCC_11, leaves every number below unchanged.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "qi_2025_self_concept_clarity"
ITEMS <- paste0("SCC_", 1:12)
REVERSE <- paste0("SCC_", c(1, 2, 3, 4, 5, 7, 8, 9, 10, 12))
POSITIVE <- setdiff(ITEMS, REVERSE)          # SCC_6, SCC_11
PUBLISHED_ALPHA <- 0.82                      # Qi et al. 2025, Sci Data 12:1755
TOL <- 0.02

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
X <- as.matrix(w[, ITEMS])
X <- X[complete.cases(X), , drop = FALSE]
cat(sprintf("live data: %d complete respondents x %d items\n\n", nrow(X), ncol(X)))

alpha <- function(M) {
    k <- ncol(M)
    k / (k - 1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
}
rev_cols <- function(M, which_rev) {
    M[, which_rev] <- 6 - M[, which_rev]
    M
}

# --- (A) keying polarity on the RAW data -------------------------------------
cat("(A) item-rest correlation, RAW responses (negative => positively keyed item)\n")
ok_polarity <- TRUE
for (it in ITEMS) {
    r <- cor(X[, it], rowSums(X[, setdiff(ITEMS, it), drop = FALSE]))
    expect <- if (it %in% POSITIVE) "neg" else "pos"
    got <- if (r < 0) "neg" else "pos"
    if (expect != got) ok_polarity <- FALSE
    cat(sprintf("  %-7s r = %+0.3f   expected %s  %s\n", it, r, expect,
                if (expect == got) "ok" else "MISMATCH"))
}
cat(sprintf("  polarity pattern as claimed: %s\n\n", ok_polarity))

# --- (B) published alpha ------------------------------------------------------
a_claim <- alpha(rev_cols(X, REVERSE))
a_raw   <- alpha(X)
a_flip  <- alpha(rev_cols(X, POSITIVE))      # the opposite reversal set
cat("(B) Cronbach's alpha vs the paper's published 0.82 for this sample\n")
cat(sprintf("  claimed reversal set (10 items reversed): %.3f  (published %.2f, diff %+0.3f)\n",
            a_claim, PUBLISHED_ALPHA, a_claim - PUBLISHED_ALPHA))
cat(sprintf("  no items reversed:                        %.3f\n", a_raw))
cat(sprintf("  opposite set (only SCC_6, SCC_11 rev):    %.3f  (alpha is reversal-direction\n", a_flip))
cat("                                                   invariant, so this ties by construction)\n")
set.seed(1)
rival_vals <- c()
for (i in 1:200) {                            # random 10-of-12 reversal sets
    rs <- sample(ITEMS, 10)
    if (setequal(rs, REVERSE)) next
    rival_vals <- c(rival_vals, alpha(rev_cols(X, rs)))
}
cat(sprintf("  200 random rival 10-of-12 reversal sets: alpha range %.3f to %.3f\n",
            min(rival_vals), max(rival_vals)))
cat(sprintf("  rival sets within %.2f of published: %d of %d\n\n", TOL,
            sum(abs(rival_vals - PUBLISHED_ALPHA) <= TOL), length(rival_vals)))

cat("Establishes: which two of the twelve codes are the positively keyed items,\n")
cat("and that the table stores responses raw. Does NOT establish the order within\n")
cat("the ten-item reverse block, nor SCC_6 vs SCC_11. => PARTIAL.\n")

pass <- ok_polarity && abs(a_claim - PUBLISHED_ALPHA) <= TOL
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
