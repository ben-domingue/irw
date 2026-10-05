# verify_FomoNegativeAffect_cremer_2026_panas.R -- Step 5b mapping check (batch_433).
#
# Claim: panas1_m..panas20_m are the 20 PANAS words (Watson, Clark & Tellegen, 1988) in
# the canonical standard-form order: interested, distressed, excited, upset, strong,
# guilty, scared, hostile, enthusiastic, proud, irritable, alert, ashamed, inspired,
# nervous, determined, attentive, jittery, active, afraid. The deposit has no labels and
# the paper prints no items, so the mapping rests on the code numbering. Predictions:
#   (a) PA/NA block structure: canonical NA positions {2,4,6,7,8,11,13,15,18,20} and PA
#       positions {1,3,5,9,10,12,14,16,17,19}. Each item should correlate more on average
#       with its own block than with the other one -- 20/20.
#   (b) Published NA subscale totals (Elhai & Casale 2026, Table 1: 6-item "NA-Fear"
#       13.53/4.97, 4-item "NA-Distress" 9.68/3.68; Table 2 men 13.02/4.88 & 8.81/3.28,
#       women 13.83/5.01 & 10.20/3.81). The deposit's panas_fear_sum is reproduced 461/461
#       only by {2,4,6,8,11,13} and panas_distress_sum only by {7,15,18,20}. Check that
#       these sets reproduce the published M/SD from the live table and are the ONLY
#       6-subset / 4-subset of the 20 items that do.
#       Under canonical numbering {7,15,18,20} = scared/nervous/jittery/afraid, i.e. the
#       literature's Afraid/Fear cluster, and {2,4,6,8,11,13} = distressed/upset/guilty/
#       hostile/irritable/ashamed, the Upset/Distress cluster -- the canonical partition,
#       though the paper's LABELS (6 fear, 4 distress) are the other way round.
# Does NOT establish: order WITHIN the PA block, within {2,4,6,8,11,13}, or within
# {7,15,18,20}. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "FomoNegativeAffect_cremer_2026_panas"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, paste0("panas", 1:20, "_m")])
sex <- tapply(d$cov_sex, d$id, function(x) x[1])[as.character(w$id)]
ok <- TRUE

# (a) block structure
NA_pos <- c(2,4,6,7,8,11,13,15,18,20); PA_pos <- setdiff(1:20, NA_pos)
R <- cor(X); diag(R) <- NA
cat("(a) mean r with own block vs other block\n")
nhit <- 0
for (i in 1:20) {
  own <- if (i %in% NA_pos) NA_pos else PA_pos
  oth <- setdiff(1:20, own)
  a <- mean(R[i, own], na.rm = TRUE); b <- mean(R[i, oth])
  hit <- a > b; nhit <- nhit + hit
  cat(sprintf("  panas%-2d %s  own %.3f  other %+.3f %s\n", i, if (i %in% NA_pos) "NA" else "PA", a, b, if (hit) "" else "<-- MISS"))
}
cat(sprintf("  %d/20 items closer to canonical block\n", nhit))
ok <- ok && nhit == 20

# (b) subscale totals
chk <- function(lbl, x, M, S) {
  cat(sprintf("  %-30s published %5.2f (%4.2f)  observed %5.2f (%4.2f)\n", lbl, M, S, mean(x), sd(x)))
  abs(mean(x) - M) <= 0.006 && abs(sd(x) - S) <= 0.006
}
f6 <- rowSums(X[, c(2,4,6,8,11,13)]); d4 <- rowSums(X[, c(7,15,18,20)])
men <- names(which(table(sex) == 172)); women <- setdiff(names(table(sex)), men)
cat(sprintf("\n(b) n = %d; sex code with n=172 (men per paper): %s\n", nrow(X), men))
ok <- chk("'NA-Fear' {2,4,6,8,11,13} all", f6, 13.53, 4.97) & ok
ok <- chk("'NA-Distress' {7,15,18,20} all", d4, 9.68, 3.68) & ok
ok <- chk("'NA-Fear' men", f6[sex == men], 13.02, 4.88) & ok
ok <- chk("'NA-Fear' women", f6[sex == women], 13.83, 5.01) & ok
ok <- chk("'NA-Distress' men", d4[sex == men], 8.81, 3.28) & ok
ok <- chk("'NA-Distress' women", d4[sex == women], 10.20, 3.81) & ok

scan <- function(k, M, S) {
  hits <- c()
  cmb <- combn(20, k)
  for (j in seq_len(ncol(cmb))) {
    x <- rowSums(X[, cmb[, j]])
    if (abs(mean(x) - M) <= 0.006 && abs(sd(x) - S) <= 0.006) hits <- c(hits, paste(cmb[, j], collapse = ","))
  }
  hits
}
h6 <- scan(6, 13.53, 4.97); h4 <- scan(4, 9.68, 3.68)
cat("  6-subsets of 20 (38760) matching 13.53/4.97:", paste(h6, collapse = " | "), "\n")
cat("  4-subsets of 20 (4845)  matching  9.68/3.68:", paste(h4, collapse = " | "), "\n")
ok <- ok && identical(h6, "2,4,6,8,11,13") && identical(h4, "7,15,18,20")

cat("\nCanonical words at those positions: 6-set = distressed, upset, guilty, hostile, irritable, ashamed;\n",
    "4-set = scared, nervous, jittery, afraid (the fear/afraid cluster; the paper labels this set 'distress').\n", sep = "")
cat("Not established: order within the PA block, within the 6-set, or within the 4-set.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
