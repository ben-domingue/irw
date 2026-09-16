# verify_yang_2018_cesd.R -- Step 5b re-runnable evidence.
#
# CONTEXT. data/yang_2018_cesd.py melts the PLOS S1 .sav columns E1..E20
# straight through, so the IRW item code IS the source column name. But the
# .sav labels those twenty columns "01  e1" .. "20  e20" -- no wording at all --
# so item_text is the canonical Radloff (1977) CES-D, aligned to the codes by
# assuming E<i> is CES-D item <i>. That assumption is what this script tests.
#
# CLAIM 1 (route 3, published totals + storage direction): if E<i> = CES-D item
#   <i>, then the four positively worded items sit at E4, E8, E12, E16. The
#   authors' own CES-D total is in the same .sav as `depressionS` ("total score
#   of CES-D"), and the paper publishes M = 12.9, SD = 9.0, range 0-46.
#   FALSIFIABLE PREDICTION: recoding the live 1-4 responses to 0-3 and reversing
#   exactly {E4,E8,E12,E16} must reproduce depressionS respondent by respondent.
#   Leaving them unreversed must not. Only one of the two can be right, and a
#   different reverse-quadruple would break it too.
#   It also settles the option axis: the live table therefore stores RAW
#   responses, so all twenty items ship their anchors ascending
#   (resp 1 = "Never/ rarely" ... resp 4 = "Almost always").
#
# CLAIM 2 (routes 6 + 5, polarity and residual block structure): those same four
#   codes must be the ones that correlate NEGATIVELY with the sum of the other
#   sixteen, and -- after removing the general severity factor that makes raw
#   CES-D correlations underpowered -- must have each other as their strongest
#   residual correlates.
#
# CLAIM 3 (route 8, semantic coherence): among the sixteen negatively worded
#   items the shipped wording predicts which ends of the ordering are which:
#   "My sleep was restless" (E11) is the most endorsed somatic complaint, and the
#   two interpersonal-hostility items "People were unfriendly" (E15) and "I felt
#   that people dislike me" (E19) are the least endorsed. Rules out a
#   permutation; does not separate adjacent items.
#
# WHAT THIS DOES NOT ESTABLISH: claims 1-2 separate the positive-affect
# quadruple from the other sixteen as SETS and fix the storage direction; claim 3
# pins the extremes of the negative block. None of them order the four positive
# items among themselves, nor the middle of the sixteen negatively worded ones.
# No per-item statistics are published for this sample and all twenty items share
# one 1-4 scale, so no route separates those. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "yang_2018_cesd"
ALL <- paste0("E", 1:20)
POS <- paste0("E", c(4, 8, 12, 16))
NEG <- setdiff(ALL, POS)

# Published in Yang et al. 2018 PLOS ONE 13(2):e0191632, Results:
# "depressive symptoms (CES-D score >= 16; range = 0-46, M = 12.9, SD = 9.0)"
PUB_M <- 12.9; PUB_SD <- 9.0; PUB_MIN <- 0; PUB_MAX <- 46

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", ALL)]
w <- w[complete.cases(w), ]
cat(sprintf("complete cases in live data: %d\n", nrow(w)))

X <- as.matrix(w[, ALL])          # 1-4 as stored
X0 <- X - 1                       # 0-3

## ---- CLAIM 1 -----------------------------------------------------------
rev_tot <- rowSums(X0) + rowSums(3 - X0[, POS]) - rowSums(X0[, POS])
raw_tot <- rowSums(X0)
cat("\nCLAIM 1  reconstructed CES-D total vs the paper's published statistics\n")
cat(sprintf("  reversing {E4,E8,E12,E16} : M=%.3f SD=%.3f range=%d-%d\n",
            mean(rev_tot), sd(rev_tot), min(rev_tot), max(rev_tot)))
cat(sprintf("  no reversal               : M=%.3f SD=%.3f range=%d-%d\n",
            mean(raw_tot), sd(raw_tot), min(raw_tot), max(raw_tot)))
cat(sprintf("  published                 : M=%.1f SD=%.1f range=%d-%d\n",
            PUB_M, PUB_SD, PUB_MIN, PUB_MAX))
claim1a <- abs(mean(rev_tot) - PUB_M) <= 0.05 && abs(sd(rev_tot) - PUB_SD) <= 0.05 &&
           min(rev_tot) == PUB_MIN && max(rev_tot) == PUB_MAX

# Respondent-by-respondent against the authors' own stored total.
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0191632.s001")
tf <- tempfile(fileext = ".sav")
ok <- tryCatch({ download.file(SI, tf, quiet = TRUE); TRUE }, error = function(e) FALSE)
claim1b <- NA
if (ok) {
    sav <- as.data.frame(haven::read_sav(tf))
    sav$id <- as.integer(sav$ID1)
    key <- sav[!is.na(sav$id) & !is.na(sav$depressionS), c("id", "depressionS")]
    m <- merge(w, key, by = "id")
    M <- as.matrix(m[, ALL]) - 1
    rv <- rowSums(M) + rowSums(3 - M[, POS]) - rowSums(M[, POS])
    rw <- rowSums(M)
    cat(sprintf("  matched to the .sav's own depressionS for %d respondents\n", nrow(m)))
    cat(sprintf("  exact matches, reversing {E4,E8,E12,E16} : %d / %d\n", sum(rv == m$depressionS), nrow(m)))
    cat(sprintf("  exact matches, no reversal               : %d / %d\n", sum(rw == m$depressionS), nrow(m)))
    claim1b <- sum(rv == m$depressionS) > sum(rw == m$depressionS) &&
               sum(rv == m$depressionS) >= 0.95 * nrow(m)
} else {
    cat("  (could not download the PLOS S1 .sav; the published-statistics half stands alone)\n")
}
claim1 <- isTRUE(claim1a) && (is.na(claim1b) || isTRUE(claim1b))

## ---- CLAIM 2 -----------------------------------------------------------
cat("\nCLAIM 2a  correlation of each item with the sum of the other fifteen/sixteen negatives\n")
negsum <- rowSums(X[, NEG])
rr <- sapply(ALL, function(c) cor(X[, c], negsum - if (c %in% NEG) X[, c] else 0))
for (c in ALL) cat(sprintf("  %-4s %+.3f%s\n", c, rr[c], if (c %in% POS) "   <- claimed positive" else ""))
claim2a <- all(rr[POS] < 0) && all(rr[NEG] > 0)
cat(sprintf("  claimed-positive range %.3f..%.3f ; other sixteen %.3f..%.3f\n",
            min(rr[POS]), max(rr[POS]), min(rr[NEG]), max(rr[NEG])))

Z <- scale(X); sv <- svd(Z)
R <- cor(Z - sv$u[, 1] %o% sv$v[, 1] * sv$d[1]); dimnames(R) <- list(ALL, ALL)
cat("\nCLAIM 2b  strongest RESIDUAL correlates of each claimed positive item\n")
claim2b <- TRUE
for (it in POS) {
    s <- sort(R[it, setdiff(ALL, it)], decreasing = TRUE)
    hit <- setequal(names(s)[1:3], setdiff(POS, it))
    claim2b <- claim2b && hit
    cat(sprintf("  %-4s %s | next %s=%.3f  %s\n", it,
                paste(sprintf("%s=%.3f", names(s)[1:3], s[1:3]), collapse = "  "),
                names(s)[4], s[4], if (hit) "= the other three claimed positives" else "MISS"))
}
subs <- combn(ALL, 4, simplify = FALSE)
sc <- sapply(subs, function(s) mean(R[s, s][upper.tri(R[s, s])]))
ord <- order(-sc)
rk <- which(sapply(subs[ord], function(s) setequal(s, POS)))
riv <- ord[if (rk == 1) 2 else 1]
cat(sprintf("  mean residual r within {E4,E8,E12,E16}: %.3f ; best rival {%s}: %.3f ; rank %d of %d\n",
            mean(R[POS, POS][upper.tri(R[POS, POS])]),
            paste(subs[[riv]], collapse = ","), sc[riv], as.integer(rk), length(subs)))
claim2 <- claim2a && claim2b && rk == 1

## ---- CLAIM 3 -----------------------------------------------------------
mns <- colMeans(X)
cat("\nCLAIM 3  per-item means within the sixteen negatively worded items (ascending)\n")
print(round(sort(mns[NEG]), 3))
top <- names(which.max(mns[NEG])); bot2 <- names(sort(mns[NEG]))[1:2]
cat(sprintf("  most endorsed: %s (claim E11, 'My sleep was restless')\n", top))
cat(sprintf("  least endorsed two: %s (claim E19/E15, the interpersonal-hostility pair)\n",
            paste(bot2, collapse = ", ")))
claim3 <- top == "E11" && setequal(bot2, c("E19", "E15"))

cat("\nNote: this pins the positive-affect quadruple as a SET, the storage direction,\n",
    "and the extremes of the negative block; it does not order items within either\n",
    "polarity block. PARTIAL, not VERIFIED.\n", sep = "")

cat(if (claim1 && claim2 && claim3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
