# verify_pierro_2018_assessment_s1.R
#
# CLAIM UNDER TEST
#   pierro_2018_assessment_s1 holds the 12-item Assessment scale of the Regulatory
#   Mode Questionnaire (Kruglanski et al., 2000), and the .sav column codes
#   ass1..ass12 are the assessment items in the RMQ's own within-subscale order
#   (RMQ items Q2, Q6, Q7, Q9, Q10, Q11, Q15, Q19, Q20, Q22, Q27, Q30), with the
#   "R" in assR1 / assR5 / assR11 marking the three reverse-worded items (Q2, Q10,
#   Q27) -- which the RMQ scoring key places at exactly within-subscale positions
#   1, 5 and 11.
#
# WHAT THIS SCRIPT CHECKS, against the live IRW data:
#   (a) STORAGE DIRECTION. The .sav's own `assessment` composite is the plain mean
#       of the 12 columns with no recoding, so the three R columns must already be
#       reverse-recoded. Test: Cronbach's alpha as stored should reproduce the
#       paper's published .75, and flipping the three R items should make it worse.
#       This is what decides that the shipped anchors for assR1/assR5/assR11 are
#       flipped (1 = Strongly Agree ... 6 = Strongly Disagree).
#   (b) WHICH POSITIONS ARE THE REVERSE-WORDED ONES. After recoding, reverse-worded
#       items keep a weak-item-total / mutual-correlation method signature. Test:
#       positions 1, 5 and 11 -- and only those -- should be the three lowest
#       corrected item-total correlations. That is the RMQ key's reverse pattern
#       reproduced from the data, which is what ties the code numbering to the
#       instrument's item order.
#
# WHAT IT DOES NOT ESTABLISH: nothing here separates the nine positively-worded
#   items from one another, nor the three reversed ones from one another. Alpha is
#   permutation-invariant by construction. The verification status is PARTIAL.

suppressMessages(library(irw))

TABLE <- "pierro_2018_assessment_s1"
ORDER <- c("assR1","ass2","ass3","ass4","assR5","ass6","ass7","ass8","ass9",
           "ass10","assR11","ass12")
REV   <- c("assR1","assR5","assR11")   # within-subscale positions 1, 5, 11
PUBLISHED_ALPHA <- 0.75                # Pierro et al. 2018, Study 1, total sample
TOL <- 0.01

alpha <- function(X) {
    k <- ncol(X)
    k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[complete.cases(w[, ORDER]), ORDER, drop = FALSE]
cat(sprintf("respondents with complete data: %d\n\n", nrow(X)))

a_stored <- alpha(X)
Y <- X; Y[, REV] <- 7 - Y[, REV]
a_flipped <- alpha(Y)

cat("(a) storage direction\n")
cat(sprintf("    published alpha (paper, Study 1 total sample) : %.3f\n", PUBLISHED_ALPHA))
cat(sprintf("    alpha as stored in IRW                        : %.3f  (diff %+.3f)\n",
            a_stored, a_stored - PUBLISHED_ALPHA))
cat(sprintf("    alpha if assR1/assR5/assR11 are flipped (7-x)  : %.3f\n", a_flipped))
cat("    -> the stored values already carry the reversal; flipping degrades the scale.\n\n")

tot <- rowSums(X)
itc <- sapply(ORDER, function(c) cor(X[[c]], tot - X[[c]]))
cat("(b) corrected item-total correlations (reverse-worded items keep a weak method signature)\n")
for (c in ORDER) cat(sprintf("    %-7s %s %.3f\n", c, ifelse(c %in% REV, "[R]", "   "), itc[c]))
lowest3 <- names(sort(itc))[1:3]
cat(sprintf("\n    three lowest: %s\n", paste(sort(lowest3), collapse = ", ")))
cat(sprintf("    RMQ key predicts: %s\n", paste(sort(REV), collapse = ", ")))

cat("\nNOT ESTABLISHED: the order of the nine positively-worded items among themselves,\n")
cat("nor which of Q2/Q10/Q27 is which. Alpha is permutation-invariant; the item-total\n")
cat("signature pins a polarity class, not positions within it. Status is PARTIAL.\n\n")

ok <- abs(a_stored - PUBLISHED_ALPHA) <= TOL &&
      a_flipped < a_stored &&
      setequal(lowest3, REV)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
