# verify_scs_2025_cfaclinic.R -- Step 5b check for scs_2025_cfaclinic (batch_450).
#
# Claim: live codes i01..i12 (the Mendeley 58my34fsg3 CFAClinic.sav column names,
# kept verbatim by data/scs_2025.R) are SCS-SF items 1..12 in Raes et al. (2011) /
# Neff numbering, and the negatively-worded items {1,4,8,9,11,12} are stored
# ALREADY REVERSE-SCORED (so their anchors are shipped flipped).
#
# Evidence re-run here, from the live data:
#  (a) Polarity class: every item correlates more, on average, with the other items
#      of its own keying class (Neff's reverse set {1,4,8,9,11,12} vs the rest) than
#      with the other class. A code permuted ACROSS classes breaks this.
#  (b) Direction: mean cross-class correlation is POSITIVE. On raw SCS data the
#      compassionate and uncompassionate items correlate negatively, so a positive
#      value means the negative items were reversed before deposit.
#  (c) Subscale pairs (reported, not gated): the authors' own Mplus 6factor.inp
#      (MplusClinic.rar) specifies kind BY i2 i6; judgement BY i11 i12; common BY
#      i5 i10; isolation BY i4 i8; mindful BY i3 i7; over BY i1 i9 -- identical to
#      Neff's SCS-SF scoring key. Within-pair r is printed for reading.
# NOT established: which member of a pair is which (i02 vs i06, etc.), nor the
# order within a polarity class beyond the authors' own pair assignment. PARTIAL.

suppressMessages(library(irw))
TABLE <- "scs_2025_cfaclinic"
d <- as.data.frame(irw::irw_fetch(TABLE))
it <- sprintf("i%02d", 1:12)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
r <- cor(w[, it], use = "pairwise.complete.obs")

neg <- sprintf("i%02d", c(1, 4, 8, 9, 11, 12))
pos <- setdiff(it, neg)
ok <- TRUE
cat(sprintf("%-5s %-4s %8s %8s\n", "item", "cls", "r_own", "r_other"))
for (i in it) {
  own <- if (i %in% neg) setdiff(neg, i) else setdiff(pos, i)
  oth <- if (i %in% neg) pos else neg
  a <- mean(r[i, own]); b <- mean(r[i, oth])
  cat(sprintf("%-5s %-4s %8.3f %8.3f %s\n", i, if (i %in% neg) "neg" else "pos", a, b, if (a > b) "" else "<-- FAIL"))
  if (a <= b) ok <- FALSE
}
cross <- mean(r[pos, neg])
cat(sprintf("\nmean cross-class r = %.3f (positive => negative items stored reverse-scored)\n", cross))
if (cross <= 0) ok <- FALSE

pairs <- list(kind = c("i02","i06"), judgement = c("i11","i12"), common = c("i05","i10"),
              isolation = c("i04","i08"), mindful = c("i03","i07"), over = c("i01","i09"))
cat("\nAuthors' Mplus 6-factor pairs (= Neff SCS-SF key), within-pair r (reported only):\n")
for (n in names(pairs)) cat(sprintf("  %-10s %s-%s r = %.3f\n", n, pairs[[n]][1], pairs[[n]][2], r[pairs[[n]][1], pairs[[n]][2]]))
cat("Note: this route pins polarity class and scoring direction; it does NOT separate\n",
    "the two items within a subscale pair or items within a polarity class.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
