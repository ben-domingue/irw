# verify_scs_2025_cfanonclinic.R -- Step 5b mapping check (batch_450).
#
# Claim: live codes i01..i12 are SCS-SF items 1..12 (Raes et al. 2011 numbering), and
# the six negatively worded items {1,4,8,9,11,12} are stored ALREADY REVERSE-SCORED,
# so their shipped anchors run resp 1 = "Almost always" .. 5 = "Almost never".
#
# Route 6 (keying polarity) + route 5 (subscale pairs) on the item axis; a
# direction check on the resp axis. What this does NOT establish: order within the
# positive class {2,3,5,6,7,10} or within Isolation {4,8} -- the positive facets are
# near-collinear in this sample, so pair structure only pins the SJ {11,12} and OI {1,9}
# pairs. That part rests on the study's own Mplus syntax (Mendeley 10.17632/58my34fsg3,
# Syntax.docx: kind BY i2 i6; judgement BY i11 i12; common BY i5 i10; isolation BY i4 i8;
# mindful BY i3 i7; over BY i1 i9 -- the canonical SCS-SF key), not on this script.

suppressMessages(library(irw))
TABLE <- "scs_2025_cfanonclinic"
NEG <- sprintf("i%02d", c(1, 4, 8, 9, 11, 12))
POS <- sprintf("i%02d", c(2, 3, 5, 6, 7, 10))

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, sprintf("i%02d", 1:12)]
r <- cor(w, use = "pairwise.complete.obs")
ok <- TRUE

# 1. Polarity class: every item correlates more with its own class than the other.
cat("1. polarity class (mean r within own class vs other class)\n")
for (it in colnames(r)) {
  own <- if (it %in% NEG) NEG else POS; oth <- if (it %in% NEG) POS else NEG
  a <- mean(r[it, setdiff(own, it)]); b <- mean(r[it, oth])
  cat(sprintf("   %s %s  own %.3f  other %.3f  %s\n", it, if (it %in% NEG) "NEG" else "POS",
              a, b, if (a > b) "ok" else "MISMATCH"))
  if (a <= b) ok <- FALSE
}

# 2. Self-judgment {11,12} and over-identification {1,9} are mutual best partners.
bp <- function(it) { o <- r[it, ]; o[it] <- -Inf; names(which.max(o)) }
cat("\n2. subscale pairs (mutual best partner)\n")
for (pr in list(c("i11", "i12"), c("i01", "i09"))) {
  m <- bp(pr[1]) == pr[2] && bp(pr[2]) == pr[1]
  cat(sprintf("   %s-%s r=%.3f  best(%s)=%s best(%s)=%s  %s\n", pr[1], pr[2], r[pr[1], pr[2]],
              pr[1], bp(pr[1]), pr[2], bp(pr[2]), if (m) "ok" else "MISMATCH"))
  if (!m) ok <- FALSE
}

# 3. Storage direction of the negative items.
#  (a) Raw SCS negative items correlate NEGATIVELY with positive items; stored-reversed
#      ones correlate positively. The study's own 2-factor CFA (MplusNonClinic/2factor.out)
#      gives POSITIVE WITH NEGATIVE = +0.420 (STDYX), and the deposit's US sample
#      (MIUSATR.sav, country==1) has mean cross-block item r = +0.32.
xb <- mean(r[NEG, POS])
cat(sprintf("\n3a. live mean cross-block r (NEG x POS) = %+.3f  (raw storage predicts < 0)\n", xb))
if (xb <= 0) ok <- FALSE
#  (b) The same deposit's clinical sample (MplusClinic.rar -> CFAClinic.sav, n=246,
#      depression/anxiety patients; sha256 3baebee3...2aa82fa2) item means, hard-coded.
#      Patients should score HIGHER raw on "obsess and fixate on everything that's
#      wrong" (i09) and the self-judgment pair; stored-reversed they score LOWER.
CLINIC <- c(2.8130, 3.0691, 3.0244, 2.8902, 2.9228, 2.5081, 2.6626, 2.6667, 2.2276, 2.7561, 2.8496, 3.0081)
names(CLINIC) <- sprintf("i%02d", 1:12)
nc <- colMeans(w, na.rm = TRUE)
cat("3b. clinic - nonclinic stored means for over-identification / self-judgment items\n")
for (it in c("i01", "i09", "i11", "i12")) {
  dd <- CLINIC[it] - nc[it]
  cat(sprintf("   %s nonclinic %.3f clinic %.3f diff %+.3f %s\n", it, nc[it], CLINIC[it], dd,
              if (dd < 0) "ok (reversed)" else "MISMATCH"))
  if (dd >= 0) ok <- FALSE
}
cat("   (i04 diff and i08 diff are near zero/slightly positive and are not used.)\n")

cat("\nNot established here: order within the positive class and within Isolation {4,8};\n",
    "those rest on the study's Mplus syntax + canonical numbering.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
