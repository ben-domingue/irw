# verify_pinheiro_2023_srq.R -- Step 5b check for batch_447.
#
# Claim being verified: the deposit's columns srq_1..srq_20 are SRQ-20 items 1..20 in
# the WHO canonical order (Beusenberg & Orley 1994, WHO/MNH/PSF/94.8, p.3), and
# resp 1 = "yes" (symptom present), 0 = "no".
#
# No per-item statistics for this sample are published, so the routes are:
#   A. Option axis / scoring (route 3): the summed score reproduces the study's
#      published SRQ-20 total, Pinheiro et al. (2026) Psicol. Pesqui. 20:e44013,
#      Table 2: M = 6.46, SD = 4.67, N = 235. A flipped yes/no coding would give
#      M = 20 - 6.46 = 13.54.
#   B. Semantic partner pairs (route 8 / structure): three pairs of near-synonymous
#      SRQ-20 items should be MUTUAL nearest neighbours in the inter-item
#      correlation matrix:
#        18 "tired all the time"          <-> 20 "easily tired"
#         7 "digestion poor"              <-> 19 "uncomfortable feelings in stomach"
#         8 "trouble thinking clearly"    <-> 12 "difficult to make decisions"
#      and the anhedonia / low-mood block 9, 11, 13, 15 ("unhappy", "difficult to
#      enjoy daily activities", "daily work suffering", "lost interest") should take
#      each of its members' top-2 correlates from inside the block.
#   C. Marker (route 7): item 6 "nervous, tense or worried" -- the SRQ-20's most
#      commonly endorsed symptom in Brazilian worker samples -- has the highest mean.
#
# What this does NOT establish: the order WITHIN each partner pair (18 vs 20, 7 vs 19,
# 8 vs 12 cannot be told apart by these routes), the order within the 9/11/13/15
# block, and the positions of the remaining items beyond "semantically coherent".
# Item 17 (suicidal thoughts) is NOT the least endorsed item here (14.9%, vs 6.0% for
# item 16 and 10.2% for item 14), so the usual item-17 marker does not pin it.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
TABLE <- "pinheiro_2023_srq"
it <- paste0("srq_", 1:20)

d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, it]
ok <- TRUE

# --- A. total score vs published ---------------------------------------------------
tot <- rowSums(w)
cat(sprintf("A. SRQ-20 total: observed M=%.2f SD=%.2f N=%d | published M=6.46 SD=4.67 N=235 | flipped coding would give M=%.2f\n",
            mean(tot), sd(tot), nrow(w), 20 - mean(tot)))
okA <- abs(mean(tot) - 6.46) <= 0.02 && abs(sd(tot) - 4.67) <= 0.02 && nrow(w) == 235
cat("   ", if (okA) "match" else "MISMATCH", "\n")
ok <- ok && okA

# --- B. semantic partner pairs -----------------------------------------------------
r <- cor(w); diag(r) <- NA
top <- function(i, k = 1) names(sort(r[i, ], decreasing = TRUE))[1:k]
for (p in list(c(18, 20), c(7, 19), c(8, 12))) {
  a <- it[p[1]]; b <- it[p[2]]
  m <- top(a) == b && top(b) == a
  cat(sprintf("B. %s <-> %s r=%.3f ; top of %s = %s, top of %s = %s -> %s\n",
              a, b, r[a, b], a, top(a), b, top(b), if (m) "mutual nearest" else "NOT mutual"))
  ok <- ok && m
}
blk <- it[c(9, 11, 13, 15)]
for (a in blk) {
  t2 <- top(a, 2); m <- all(t2 %in% blk)
  cat(sprintf("B. block 9/11/13/15: top-2 of %s = %s (r=%s) -> %s\n", a, paste(t2, collapse = ","),
              paste(sprintf("%.2f", r[a, t2]), collapse = ","), if (m) "in block" else "OUTSIDE"))
  ok <- ok && m
}
cat(sprintf("   mean off-diagonal r = %.3f; largest in matrix = %.3f (%s)\n", mean(r, na.rm = TRUE),
            max(r, na.rm = TRUE), paste(which(r == max(r, na.rm = TRUE), arr.ind = TRUE)[1, ], collapse = ",")))

# --- C. marker ---------------------------------------------------------------------
mu <- colMeans(w)
cat("C. item means:", paste(sprintf("%s=%.3f", names(mu), mu), collapse = " "), "\n")
okC <- names(which.max(mu)) == "srq_6"
cat(sprintf("   highest mean = %s (%.3f) -> %s\n", names(which.max(mu)), max(mu), if (okC) "item 6 as predicted" else "NOT item 6"))
ok <- ok && okC

cat("Not established: order within pairs 18/20, 7/19, 8/12, within block 9/11/13/15, and exact positions of the rest; srq_17 is not the least endorsed item (0.149 vs srq_16 0.060).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
