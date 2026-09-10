# verify_pierro_2018_tf_future_s4.R
#
# CLAIM UNDER TEST (Step 5b, route 3 -- published subscale statistics):
#   the four live items TFfuture1..4 are the FUTURE Focus subscale of the
#   Temporal Focus Scale (Shipp, Edwards & Lambert 2009), stored RAW (no
#   reverse-keying, no rescaling), and NOT the past or present subscale from
#   the same S4 file.
#
# Pierro et al. (2018) PLoS ONE 13(3):e0193357, Table 4 publishes M, SD and
# Cronbach's alpha for each of the three temporal-focus composites, computed by
# averaging that subscale's four items (N = 189). Those three triples are far
# enough apart that reproducing one of them from the live data identifies which
# subscale this table holds. That is the falsifiable prediction.
#
# WHAT THIS DOES NOT ESTABLISH: it says nothing about which of the four future
# items is TFfuture1 vs TFfuture2 vs TFfuture3 vs TFfuture4. The composite is
# permutation-invariant, so any reordering of the four shipped wordings passes
# this check identically. The within-subscale order is taken from the
# instrument's own published order and is NOT verified here -- hence PARTIAL.

suppressMessages(library(irw))

TABLE <- "pierro_2018_tf_future_s4"

# Pierro et al. 2018, Table 4 (10.1371/journal.pone.0193357.t004), N = 189.
PUB <- data.frame(
  subscale = c("Past temporal focus", "Present temporal focus", "Future temporal focus"),
  M        = c(5.10, 5.12, 5.54),
  SD       = c(1.09, 1.00, 1.05),
  alpha    = c(0.91, 0.85, 0.92),
  stringsAsFactors = FALSE
)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
X <- as.matrix(w[, setdiff(names(w), "id")])
X <- X[stats::complete.cases(X), , drop = FALSE]

k     <- ncol(X)
comp  <- rowMeans(X)
M     <- mean(comp)
SD    <- stats::sd(comp)
alpha <- (k / (k - 1)) * (1 - sum(apply(X, 2, stats::var)) / stats::var(rowSums(X)))

cat(sprintf("live table %s: n = %d complete respondents, k = %d items\n\n", TABLE, nrow(X), k))
cat(sprintf("observed composite: M = %.3f  SD = %.3f  alpha = %.3f\n\n", M, SD, alpha))

cat(sprintf("%-24s %6s %6s %6s | %8s\n", "published (Table 4)", "M", "SD", "alpha", "L1 dist"))
for (i in seq_len(nrow(PUB))) {
  dist <- abs(M - PUB$M[i]) + abs(SD - PUB$SD[i]) + abs(alpha - PUB$alpha[i])
  cat(sprintf("%-24s %6.2f %6.2f %6.2f | %8.3f%s\n", PUB$subscale[i],
              PUB$M[i], PUB$SD[i], PUB$alpha[i], dist,
              if (PUB$subscale[i] == "Future temporal focus") "   <- claimed" else ""))
}

fut <- PUB[PUB$subscale == "Future temporal focus", ]
ok_fit <- abs(M - fut$M) <= 0.01 && abs(SD - fut$SD) <= 0.01 && abs(alpha - fut$alpha) <= 0.005
d_fut  <- abs(M - fut$M) + abs(SD - fut$SD) + abs(alpha - fut$alpha)
d_oth  <- min(sapply(which(PUB$subscale != "Future temporal focus"),
                     function(i) abs(M - PUB$M[i]) + abs(SD - PUB$SD[i]) + abs(alpha - PUB$alpha[i])))
cat(sprintf("\nfuture-row distance %.3f vs nearest rival %.3f\n", d_fut, d_oth))

cat("\nNote: permutation-invariant. This pins the SUBSCALE and the raw (unreversed)\n",
    "storage direction; it does not distinguish TFfuture1..4 from one another.\n", sep = "")

cat(if (ok_fit && d_fut < d_oth) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
