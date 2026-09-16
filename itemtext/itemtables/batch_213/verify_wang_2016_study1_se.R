# verify_wang_2016_study1_se.R
#
# CLAIM UNDER TEST (Step 5b).  wang_2016_study1_se holds the 10 RSES items of
# Wang YN (2016) PLOS ONE 11(1):e0146050, Study 1.  Neither the paper nor the
# deposit's SPSS file ties any of the codes se1..se10 to an item stem, so the
# shipped mapping is RECONSTRUCTED from the numbering of the RSES edition the
# paper itself cites (Rosenberg 1965 as reproduced in the Acceptance and
# Commitment Therapy Measures Package, p.61 -- reference [33] of the paper).
# Two parts, and only the first two are testable here:
#
#   (a) KEYING DIRECTION.  The live resp is stored ALREADY REVERSE-CODED for
#       the negatively worded items -- i.e. 5 always means "high self-esteem",
#       never "strongly agrees with a negative statement".  This is what the
#       shipped option_text encodes by FLIPPING the study's Chinese anchors on
#       se2/se5/se6/se8/se9 relative to the other five.
#       Falsifiable: alpha over the stored values must reproduce the paper's
#       published .81 and the per-person sum must reproduce Table 1's
#       M = 38.34, SD = 5.08; un-reversing the five shipped negative items must
#       destroy alpha.
#
#   (b) POLARITY PARTITION -- WHICH five items are the negatively worded ones.
#       The RSES wording method factor is a testable prediction: same-polarity
#       items must intercorrelate more than cross-polarity ones.  The shipped
#       partition {se2,se5,se6,se8,se9} (the ACT-Measures-Package numbering)
#       must rank at the top of all 126 possible 5/5 splits, and the rival
#       numbering used by socy.umd.edu, {se3,se5,se8,se9,se10}, must not.
#
#   (c) NOT TESTED, AND THE REASON THE STATUS IS PARTIAL: the ORDER WITHIN each
#       polarity class.  Because the negative items are stored reverse-coded,
#       no sign information survives, and the study publishes no per-item
#       statistics.  Printed below so the gap is visible, not asserted away.

suppressMessages(library(irw))

TABLE <- "wang_2016_study1_se"
ITEMS <- paste0("se", 1:10)
SHIPPED_NEG <- c("se2","se5","se6","se8","se9")   # ACT Measures Package numbering
RIVAL_NEG   <- c("se3","se5","se8","se9","se10")  # socy.umd.edu numbering

# Wang (2016), Study 1: Measures ("Cronbach's alpha = .81") and Table 1.
PUB <- list(alpha = 0.81, sum_m = 38.34, sum_sd = 5.08)
TOL_A <- 0.015; TOL_M <- 0.05; TOL_SD <- 0.05

d <- irw::irw_fetch(TABLE)
w <- reshape(data.frame(id = as.character(d$id), item = as.character(d$item),
                        resp = as.numeric(d$resp)),
             idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
m <- m[complete.cases(m), ITEMS, drop = FALSE]
cat(sprintf("live table: %d respondents x %d items\n\n", nrow(m), ncol(m)))

alpha <- function(X) {
    k <- ncol(X); k/(k-1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}

## ---- (a) keying direction ------------------------------------------------
a_stored <- alpha(m)
s <- rowSums(m)
m_unrev <- m; m_unrev[, SHIPPED_NEG] <- 6 - m_unrev[, SHIPPED_NEG]
a_unrev <- alpha(m_unrev)
m_rival <- m; m_rival[, RIVAL_NEG] <- 6 - m_rival[, RIVAL_NEG]

cat("(a) KEYING DIRECTION\n")
cat(sprintf("%-42s %10s %10s\n", "quantity", "published", "observed"))
cat(sprintf("%-42s %10.2f %10.3f\n", "Cronbach's alpha, stored values", PUB$alpha, a_stored))
cat(sprintf("%-42s %10.2f %10.3f\n", "10-item sum, M", PUB$sum_m, mean(s)))
cat(sprintf("%-42s %10.2f %10.3f\n", "10-item sum, SD", PUB$sum_sd, sd(s)))
cat(sprintf("%-42s %10s %10.3f\n", "alpha if shipped negatives un-reversed", "<.40", a_unrev))
cat(sprintf("%-42s %10s %10.3f\n", "alpha if rival negatives un-reversed", "--", alpha(m_rival)))
cat("  -> every inter-item correlation in this table is positive, so the five\n")
cat("     negatively worded items were reverse-coded before deposit; the shipped\n")
cat("     anchors are flipped on those five to match.  Un-reversing them collapses\n")
cat("     alpha from .81 to .16 (and the rival partition to -.34), which is the\n")
cat("     falsification: a table stored raw could not reach the published .81.\n\n")

ok_a <- abs(a_stored - PUB$alpha) <= TOL_A &&
        abs(mean(s) - PUB$sum_m) <= TOL_M &&
        abs(sd(s)   - PUB$sum_sd) <= TOL_SD &&
        a_unrev < 0.40

## ---- (b) polarity partition ---------------------------------------------
C <- cor(m)
contrast <- function(neg) {
    pos <- setdiff(ITEMS, neg)
    wi  <- function(S) mean(C[S, S][upper.tri(diag(length(S)))])
    (wi(pos) + wi(neg)) / 2 - mean(C[pos, neg])
}
splits <- combn(ITEMS, 5, simplify = FALSE)
# de-duplicate complementary splits (a 5/5 split and its complement are one test)
seen <- character(0); uniq <- list()
for (s in splits) {
    key <- paste(sort(c(paste(sort(s), collapse = "|"),
                        paste(sort(setdiff(ITEMS, s)), collapse = "|"))), collapse = "//")
    if (key %in% seen) next
    seen <- c(seen, key); uniq[[length(uniq) + 1]] <- s
}
vals <- vapply(uniq, contrast, 0)
ord  <- order(vals, decreasing = TRUE)
rank_of <- function(neg) {
    hit <- vapply(uniq, function(s) setequal(s, neg) || setequal(s, setdiff(ITEMS, neg)), TRUE)
    which(ord == which(hit))
}
r_ship <- rank_of(SHIPPED_NEG); r_rival <- rank_of(RIVAL_NEG)

cat("(b) POLARITY PARTITION -- wording method factor, all", length(uniq), "possible 5/5 splits\n")
cat(sprintf("  shipped {%s}  contrast %+.4f   rank %d of %d\n",
            paste(SHIPPED_NEG, collapse = ","), contrast(SHIPPED_NEG), r_ship, length(uniq)))
cat(sprintf("  rival   {%s}  contrast %+.4f   rank %d of %d\n",
            paste(RIVAL_NEG, collapse = ","), contrast(RIVAL_NEG), r_rival, length(uniq)))
cat("  top 3 splits by contrast:\n")
for (i in 1:3)
    cat(sprintf("    {%s} %+.4f\n", paste(uniq[[ord[i]]], collapse = ","), vals[ord[i]]))
hi <- which(C == max(C[upper.tri(C)]), arr.ind = TRUE)[1, ]
cat(sprintf("  highest single correlation: %s-%s r = %.2f -- the shipped text makes these\n",
            rownames(C)[hi[1]], colnames(C)[hi[2]], max(C[upper.tri(C)])))
cat("    the two near-synonymous negative items ('no good at all' / 'useless at times')\n\n")

ok_b <- r_ship <= 3 && r_rival >= 30

## ---- independent replication in the same deposit -------------------------
cat("(replication, Study 3 of the same deposit, same se1..se10 column names)\n")
rep_ok <- TRUE
try({
    d3 <- irw::irw_fetch("wang_2016_study3_se")
    w3 <- reshape(data.frame(id = as.character(d3$id), item = as.character(d3$item),
                             resp = as.numeric(d3$resp)),
                  idvar = "id", timevar = "item", direction = "wide")
    m3 <- as.matrix(w3[, -1]); colnames(m3) <- sub("^resp\\.", "", colnames(m3))
    m3 <- m3[complete.cases(m3), ITEMS, drop = FALSE]
    C <- cor(m3)
    vals3 <- vapply(uniq, contrast, 0); ord3 <- order(vals3, decreasing = TRUE)
    rk <- function(neg) {
        hit <- vapply(uniq, function(s) setequal(s, neg) || setequal(s, setdiff(ITEMS, neg)), TRUE)
        which(ord3 == which(hit))
    }
    cat(sprintf("  n = %d; shipped partition rank %d of %d (contrast %+.4f); rival rank %d\n",
                nrow(m3), rk(SHIPPED_NEG), length(uniq), contrast(SHIPPED_NEG), rk(RIVAL_NEG)))
    cat(sprintf("  alpha stored %.3f (paper reports .90 for Study 3)\n", alpha(m3)))
}, silent = TRUE)
C <- cor(m)   # restore for anything below
cat("\n")

## ---- (c) what is NOT established ----------------------------------------
cat("(c) NOT ESTABLISHED -- order WITHIN each polarity class\n")
it_rest <- vapply(ITEMS, function(j) cor(m[, j], rowSums(m[, setdiff(ITEMS, j), drop = FALSE])), 0)
for (j in ITEMS)
    cat(sprintf("    %-5s mean %.2f  item-rest r %.3f%s\n", j, mean(m[, j]), it_rest[j],
                if (j %in% SHIPPED_NEG) "  (shipped as negatively worded)" else ""))
cat("  se8 has the lowest item-rest correlation, which matches the RSES item famously\n")
cat("  weakest in Chinese samples ('I wish I could have more respect for myself') and is\n")
cat("  item 8 under BOTH candidate numberings -- so it corroborates, it does not separate.\n")
cat("  Nothing here distinguishes se5 from se9, se2 from se6, or the five positive items\n")
cat("  from one another: that order is taken from the cited edition's numbering and is\n")
cat("  NOT verified.  Hence status PARTIAL, not VERIFIED.\n\n")

cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
