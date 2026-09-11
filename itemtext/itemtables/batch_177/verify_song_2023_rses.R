# verify_song_2023_rses.R -- Step 5b, re-runnable mapping check (batch_177).
#
# CLAIM UNDER TEST. Live codes RSES1..RSES10 carry the Rosenberg Self-Esteem
# Scale sentences in the order of the University of Maryland / Morris Rosenberg
# Foundation form (reverse-worded items at positions 3, 5, 8, 9, 10), which is
# the numbering Song et al. (2023, PLOS ONE 10.1371/journal.pone.0284335) state:
# "Items 1, 2, 4, 6, and 7 are positively rated and items 3, 5, 8, 9, and 10 are
# negatively rated". And the option_text direction shipped per item:
#   RSES1,2,4,6,7,8 : 1=Strongly disagree .. 4=Strongly agree
#   RSES3,5,9,10    : 1=Strongly agree    .. 4=Strongly disagree (stored reverse-scored)
#
# LEG 1 -- storage direction (route 3, published totals). Table 2 of the paper
#   prints Self-esteem M=29.92, SD=4.79; Methods prints alpha=0.863. If the
#   stored columns, summed AS STORED, reproduce all three, then the stored values
#   are already the authors' scored values (negatives reversed, high = high
#   self-esteem). Un-reversing {3,5,9,10}, or reversing RSES8, must NOT reproduce.
# LEG 2 -- polarity classes (route 6). With negatives already reversed, the RSES
#   method factor shows as two clusters. Under the shipped (UMD) ordering the
#   clusters must be {1,2,4,6,7,8} and {3,5,9,10} -- item 8 sits with the
#   positives, the documented behaviour of that item in Chinese administrations.
#   The rival circulated ordering (reverse-worded at 2,5,6,8,9) predicts
#   {2,5,6,9} as the reverse cluster instead, and must fail.
# LEG 3 -- RSES8 option direction (route 9-style, distribution). The shipped
#   reading (stored raw, 4=Strongly agree) implies ~91% agreement with "I wish I
#   could have more respect for myself"; the paper-keyed reading implies ~91%
#   DISagreement. qi_2025_self_esteem (Chinese students, stored raw, paper-stated
#   1=SD..4=SA) shows 125/134 = 93.3% agreement on the same item.
#
# WHAT THIS DOES NOT ESTABLISH: order WITHIN a polarity class. Swapping the
# shipped text of RSES1 and RSES2, or of RSES9 and RSES10, moves none of these
# numbers. Status is therefore PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "song_2023_rses"
PUB_M <- 29.92; PUB_SD <- 4.79; PUB_ALPHA <- 0.863
QI_E8_AGREE <- 125 / 134   # hard-coded from qi_2025_self_esteem live data, resp 3-4

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- as.matrix(w[, paste0("RSES", 1:10)])
cat(sprintf("respondents %d, complete cases %d\n\n", nrow(w), sum(complete.cases(w))))

alpha <- function(m) { k <- ncol(m); k/(k-1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
flip  <- function(m, idx) { m[, idx] <- 5 - m[, idx]; m }
show  <- function(lbl, m) {
  s <- rowSums(m); a <- alpha(m)
  cat(sprintf("  %-38s M=%6.3f SD=%5.3f alpha=%6.3f\n", lbl, mean(s), sd(s), a))
  c(mean(s), sd(s), a)
}
cat(sprintf("LEG 1: published M=%.2f SD=%.2f alpha=%.3f\n", PUB_M, PUB_SD, PUB_ALPHA))
st  <- show("as stored (shipped reading)", w)
un  <- show("un-reverse 3,5,9,10 (raw hypothesis)", flip(w, c(3,5,9,10)))
f8  <- show("reverse RSES8 as well", flip(w, 8))
leg1 <- abs(st[1]-PUB_M) <= 0.01 && abs(st[2]-PUB_SD) <= 0.01 && abs(st[3]-PUB_ALPHA) <= 0.001 &&
        abs(un[3]-PUB_ALPHA) > 0.05 && abs(f8[3]-PUB_ALPHA) > 0.05
cat(sprintf("  LEG 1 %s\n\n", if (leg1) "ok" else "FAILED"))

r <- cor(w)
cluster_test <- function(lbl, B) {
  A <- setdiff(1:10, B); ok <- TRUE
  cat(sprintf("LEG 2 [%s]: class A {%s} vs class B {%s}\n", lbl,
              paste(A, collapse=","), paste(B, collapse=",")))
  for (i in 1:10) {
    own <- if (i %in% A) A else B; oth <- setdiff(1:10, own)
    wi <- mean(r[i, setdiff(own, i)]); xo <- mean(r[i, oth])
    if (wi <= xo) ok <- FALSE
    cat(sprintf("  RSES%-3d within %.3f  cross %.3f %s\n", i, wi, xo, if (wi > xo) "" else "<-- violates"))
  }
  ok
}
leg2_ship  <- cluster_test("shipped UMD order, item 8 with positives", c(3,5,9,10))
leg2_rival <- cluster_test("rival order, reverse 2,5,6,8,9 minus 8", c(2,5,6,9))
cat(sprintf("  shipped clusters hold: %s; rival clusters hold: %s\n\n", leg2_ship, leg2_rival))

e8 <- table(factor(w[, 8], levels = 1:4))
agree <- sum(e8[3:4]) / sum(e8)
cat("LEG 3: RSES8 counts resp 1..4:", paste(e8, collapse=" / "), "\n")
cat(sprintf("  share at resp 3-4 = %.3f; qi_2025_self_esteem raw agreement on item 8 = %.3f\n",
            agree, QI_E8_AGREE))
cat(sprintf("  shipped reading => %.1f%% agree; paper-keyed reading => %.1f%% disagree\n",
            100*agree, 100*agree))
leg3 <- agree > 0.8 && QI_E8_AGREE > 0.8
cat(sprintf("  LEG 3 %s\n\n", if (leg3) "ok" else "FAILED"))

cat("Not established: order within a polarity class (e.g. RSES1<->RSES2, RSES9<->RSES10 swaps are invisible).\n")
cat(if (leg1 && leg2_ship && !leg2_rival && leg3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
