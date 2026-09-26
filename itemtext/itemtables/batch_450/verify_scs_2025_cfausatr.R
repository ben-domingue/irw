# verify_scs_2025_cfausatr.R -- Step 5b re-runnable check (batch_450).
#
# Claim: SCS01..SCS12 are SCS-SF items 1..12 in the canonical Raes et al. (2011)
# order (the .sav's own variable labels read "SCS-SF01".."SCS-SF12"), and the six
# negatively worded items {1,4,8,9,11,12} are stored ALREADY REVERSE-SCORED, which is
# why their option_text runs 1 = "Almost always" ... 5 = "Almost never".
#
# Routes:
#   A. Keying polarity (route 6): with the negative items reversed, the two
#      polarity blocks should still separate -- each item correlates more with its
#      own polarity block than with the other. Pins polarity CLASS per item.
#   B. Subscale pairs (route 5): canonical key (Neff SCS-SF information PDF, and the
#      deposit's own Mplus MODEL statements: kind BY i2 i6; judgement BY i11 i12;
#      common BY i5 i10; isolation BY i4 i8; mindful BY i3 i7; over BY i1 i9).
#      Reported, not gated: 2-item facets within a polarity block are near-collinear.
#   C. Direction: the TR rows of this table are the deposit's non-clinical sample
#      (same 545 response vectors). The deposit's psychiatric clinical sample
#      (CFAClinic.sav, n=246; means hard-coded below) scores LOWER on 11/12 items,
#      including every positively worded item, so high stored values = more
#      self-compassion -> the negative items must have been reverse-scored.
#
# Means are from the deposit's CFANonClinic.sav / CFAClinic.sav (Mendeley 58my34fsg3,
# MplusNonClinic.rar / MplusClinic.rar), items i01..i12, 5 d.p.
#
# NOT established: order WITHIN a polarity class beyond pair membership; e.g. a
# swap of SCS02 and SCS06 (both self-kindness) would pass every route here.

suppressMessages(library(irw))
TABLE <- "scs_2025_cfausatr"
items <- sprintf("SCS%02d", 1:12)
neg <- c(1, 4, 8, 9, 11, 12); pos <- setdiff(1:12, neg)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, items]); r <- cor(X, use = "pairwise")

ok <- TRUE
cat("A. polarity block separation (mean r own block vs other block)\n")
for (i in 1:12) {
  own <- if (i %in% neg) neg else pos; oth <- setdiff(1:12, own)
  mo <- mean(r[i, setdiff(own, i)]); mx <- mean(r[i, oth])
  flag <- mo > mx; ok <- ok && flag
  cat(sprintf("  %s %-3s own=%.3f other=%.3f %s\n", items[i],
              if (i %in% neg) "neg" else "pos", mo, mx, if (flag) "ok" else "FAIL"))
}
cat(sprintf("  min between-block r = %.3f (all positive => negative items stored reversed or positive items reversed; C decides)\n",
            min(r[pos, neg])))

cat("\nB. canonical 2-item facets (informational)\n")
pairs <- list(kind = c(2, 6), judg = c(11, 12), common = c(5, 10),
              isol = c(4, 8), mindful = c(3, 7), overid = c(1, 9))
hit <- 0
for (i in 1:12) {
  g <- names(pairs)[sapply(pairs, function(p) i %in% p)]
  mate <- setdiff(pairs[[g]], i)
  best <- which.max(replace(r[i, ], i, -Inf))
  hit <- hit + (best == mate)
  cat(sprintf("  %s facet=%-7s r(mate)=%.2f  top partner=%s\n", items[i], g, r[i, mate], items[best]))
}
cat(sprintf("  %d/12 items have their facet mate as top partner\n", hit))

cat("\nC. direction: TR rows vs deposit non-clinical (hard-coded) and clinical means\n")
NONCLIN <- c(2.94679, 3.47339, 3.60000, 2.93028, 3.33945, 3.30459, 3.57798, 2.52110, 2.76330, 3.20183, 3.08807, 3.26055)
CLIN    <- c(2.81301, 3.06911, 3.02439, 2.89024, 2.92276, 2.50813, 2.66260, 2.66667, 2.22764, 2.75610, 2.84959, 3.00813)
ctry <- tapply(d$cov_country, d$id, `[`, 1)
tr <- X[as.character(w$id) %in% names(ctry)[ctry == 2], ]
trm <- colMeans(tr, na.rm = TRUE)
cat(sprintf("  TR n=%d; max |TR mean - nonclinical mean| = %.3f\n", nrow(tr), max(abs(trm - NONCLIN))))
same <- nrow(tr) == 545 && max(abs(trm - NONCLIN)) < 1e-4
dpos <- CLIN[pos] - NONCLIN[pos]
cat("  clinical - nonclinical, positive items:", sprintf("%.2f", dpos), "\n")
cat("  clinical - nonclinical, negative items:", sprintf("%.2f", CLIN[neg] - NONCLIN[neg]), "\n")
dir_ok <- all(dpos < 0) && sum(CLIN - NONCLIN < 0) >= 10
cat(sprintf("  TR rows == nonclinical file: %s; clinical lower on all positive items and >=10/12 overall: %s\n", same, dir_ok))

ok <- ok && same && dir_ok
cat("Note: pins polarity class, facet pairs only loosely (see B), and storage direction;\n",
    "does not separate items within a facet pair.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
