# verify_pierro_2018_locomotion_s4.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order)
#   pierro_2018_locomotion_s4 holds the 12-item Locomotion scale of the Regulatory
#   Mode Questionnaire (Kruglanski et al., 2000). The item codes are the S4 .sav's
#   own column names, melted unrenamed by data/pierro_2018_selfforgiveness.py
#   (loc1, loc2, loc3, loc4, loc5, locR6, loc7, loc8, locR9, loc10, loc11, loc12),
#   and the claim is that they are the Locomotion items in the RMQ scoring key's
#   own within-subscale order -- 30-item numbers Q1, Q3, Q4, Q5, Q8, Q13, Q16,
#   Q21, Q24, Q25, Q28, Q29 -- with the "R" marking the two reverse-worded items
#   (Q13, Q24), which that key places at within-subscale positions 6 and 9.
#
# WHAT THIS SCRIPT CHECKS against the live IRW data:
#   (a) SCALE IDENTITY AND STORAGE DIRECTION (route 3, published totals). The
#       deposit's own `locomotion` composite is the plain unrecoded mean of the 12
#       columns, so if the paper's published Study 4 statistics are reproduced by
#       the values exactly as stored, the two R columns must ALREADY be
#       reverse-recoded. That is what decides the shipped anchors for locR6/locR9
#       are flipped (resp 1 = Strongly Agree ... resp 6 = Strongly Disagree
#       against the printed statement). Published for Study 4: alpha .83, M 4.37,
#       SD .62, and r(locomotion, assessment) = -.05.
#       NOTE this is NOT inherited from a sibling: the same instrument is stored
#       RAW in pierro_2018_locomotion_s3 and already-recoded in _s1. Storage
#       direction is a property of the table and is tested here from scratch.
#   (b) WHICH POSITIONS ARE REVERSE-WORDED (route 6, keying polarity). Undo the
#       recoding (7 - x on the two R codes) to recover the raw administered
#       direction; in raw form exactly the reverse-worded items must show negative
#       corrected item-rest correlations. Positions 6 and 9 are the RMQ key's
#       prediction, and that is what ties the code numbering to the instrument's
#       item order.
#
# WHAT IT DOES NOT ESTABLISH: nothing here separates the ten positively-worded
#   items from one another, nor locR6 from locR9. Alpha is permutation-invariant
#   by construction and the sign test pins a polarity CLASS, not an order within
#   it. Their assignment rests on the RMQ scoring key's enumeration (corroborated
#   by the paper's one quoted locomotion item, canonical Q21 = position 8 = loc8,
#   which is content evidence and not testable here). Status is PARTIAL.

suppressMessages(library(irw))

TABLE <- "pierro_2018_locomotion_s4"
ORDER <- c("loc1","loc2","loc3","loc4","loc5","locR6",
           "loc7","loc8","locR9","loc10","loc11","loc12")
REV   <- c("locR6","locR9")   # within-subscale positions 6 and 9

# Pierro et al. (2018) PLoS ONE 13(3):e0193357, Study 4 Measures:
# "the Cronbach's alpha for the locomotion scale was .83 ... M of the locomotion
#  score was 4.37 (SD = .62) ... the two scales were not correlated (r = -.05)".
PUB_ALPHA <- 0.83; PUB_M <- 4.37; PUB_SD <- 0.62; PUB_R_LOC_ASS <- -0.05
TOL_A <- 0.01; TOL_M <- 0.01; TOL_R <- 0.02

ASS_TABLE <- "pierro_2018_assessment_s4"
ASS_ORDER <- c("assR1","ass2","ass3","ass4","assR5","ass6",
               "ass7","ass8","ass9","ass10","assR11","ass12")

alpha <- function(X) { k <- ncol(X); k/(k-1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
itemrest <- function(X) sapply(colnames(X), function(c) cor(X[[c]], rowSums(X) - X[[c]]))

widen <- function(tbl, ord) {
  d <- as.data.frame(irw::irw_fetch(tbl))
  w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
  names(w) <- sub("^resp\\.", "", names(w))
  w[, c("id", ord), drop = FALSE]
}

W <- widen(TABLE, ORDER)
X <- W[complete.cases(W[, ORDER]), ORDER, drop = FALSE]
cat(sprintf("respondents with complete data: %d x %d items\n\n", nrow(X), ncol(X)))

sc <- rowMeans(X)
a_stored <- alpha(X)
Y <- X; Y[, REV] <- 7 - Y[, REV]
a_flipped <- alpha(Y)

cat("(a) scale identity + storage direction -- against Study 4's published numbers\n")
cat(sprintf("    alpha   published %.2f   as stored %.4f  (diff %+.4f)\n", PUB_ALPHA, a_stored, a_stored - PUB_ALPHA))
cat(sprintf("    mean    published %.2f   as stored %.4f  (diff %+.4f)\n", PUB_M, mean(sc), mean(sc) - PUB_M))
cat(sprintf("    SD      published %.2f   as stored %.4f  (diff %+.4f)\n", PUB_SD, sd(sc), sd(sc) - PUB_SD))
cat(sprintf("    alpha if locR6/locR9 are flipped (7-x): %.4f  (mean %.4f, SD %.4f)\n",
            a_flipped, mean(rowMeans(Y)), sd(rowMeans(Y))))
cat("    -> the stored values already carry the reversal; flipping misses all three published values.\n\n")

# Cross-scale corroboration that this is the locomotion block of Study 4 and not
# some other 12-item 1-6 scale: the published null correlation with assessment.
r_loc_ass <- NA
ok_r <- TRUE
ass <- try(widen(ASS_TABLE, ASS_ORDER), silent = TRUE)
if (!inherits(ass, "try-error")) {
  M <- merge(data.frame(id = W$id, loc = rowMeans(W[, ORDER])),
             data.frame(id = ass$id, ass = rowMeans(ass[, ASS_ORDER])), by = "id")
  M <- M[complete.cases(M), ]
  r_loc_ass <- cor(M$loc, M$ass)
  ok_r <- abs(r_loc_ass - PUB_R_LOC_ASS) <= TOL_R
  cat(sprintf("    r(locomotion, assessment) published %.2f   observed %.4f  (n=%d)\n\n",
              PUB_R_LOC_ASS, r_loc_ass, nrow(M)))
} else {
  cat("    r(locomotion, assessment): sibling table unavailable, check skipped\n\n")
}

raw <- Y   # raw administered direction
ir_raw <- itemrest(raw); ir_st <- itemrest(X)
cat("(b) keying polarity -- corrected item-rest r, raw (un-recoded) vs stored\n")
cat(sprintf("    %-8s %-4s %10s %10s\n", "item", "key", "raw", "stored"))
for (c in ORDER) cat(sprintf("    %-8s %-4s %+10.3f %+10.3f\n", c,
                             if (c %in% REV) "[R]" else "", ir_raw[[c]], ir_st[[c]]))
neg <- names(ir_raw)[ir_raw < 0]
cat(sprintf("\n    negative in raw direction: %s\n", paste(sort(neg), collapse = ", ")))
cat(sprintf("    RMQ scoring key predicts : %s\n\n", paste(sort(REV), collapse = ", ")))

cat("NOT ESTABLISHED: the order of the ten positively-worded items among themselves,\n")
cat("nor which of Q13/Q24 is locR6 vs locR9. Status is PARTIAL.\n\n")

ok <- abs(a_stored - PUB_ALPHA) <= TOL_A &&
      abs(mean(sc) - PUB_M) <= TOL_M && abs(sd(sc) - PUB_SD) <= TOL_M &&
      a_flipped < a_stored && setequal(neg, REV) && ok_r
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
