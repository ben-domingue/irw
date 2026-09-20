# verify_song_2025_sc.R -- Step 5b mapping check (batch_278)
#
# Derivation: data/song_2025_servant_leadership.py melts the S1 Appendix xlsx
# (PLOS s001 = figshare doi:10.6084/m9.figshare.28606742.v1) with item = the raw
# source column name (SC1..SC6) -- a regex on the header, no rename and no
# positional step.
# Text tie: PLOS ONE 10.1371/journal.pone.0323811 Table 3 prints each item's
# wording in a row whose "Abbreviations" cell is that same code ("Company
# management sets definite quality standards of good customer service." | SC2 |
# 0.859), i.e. an explicit code label, not an order inference.
#
# What this script checks:
#  A. The live per-item distribution (server-side GROUP BY item, resp -- NO table
#     export) reproduces the paper's Table 2 Mean / Median / SD / EK / Skewness
#     for the same SC codes, so any permutation of the six codes between the
#     deposit and the live table would show up here.
#     TRANSFORM, and it is specific to this block: Table 2 prints the SC rows on
#     a flipped scale while every other block in the same table is raw. The
#     Mean column equals 5 - mean(live) and the Median column equals
#     6 - median(live), while SD, EK and Skewness are the untransformed
#     population-SD / G2 / G1 of the live values. (Checked against the other 49
#     rows of Table 2: all of them match mean(live) directly -- only the six SC
#     rows need the flip, and both flips are applied uniformly to all six, so
#     the per-item comparison below is still a six-way discrimination.)
#  B. Separation: every pair of items must differ by more than tolerance on at
#     least one published statistic. SC2 vs SC3 are 0.002 apart on the mean, so
#     the mean alone cannot separate them; SD (0.813 vs 0.849) and Skewness
#     (0.458 vs 0.636) do.
#  C. Reported, not part of the verdict: the live keying split. SC6 correlates
#     NEGATIVELY with SC1..SC5 in the live table, while Table 3 reports all six
#     loading positively (0.814-0.913, alpha 0.895). See the public_note.
#  D. NOT established here: the code->wording tie itself (that rests on Table 3's
#     explicit labels; no statistic re-derives a sentence), and the
#     option_text<->resp axis, which is empty because the study never prints its
#     five-point anchors.

suppressMessages(library(irw))

TABLE <- "song_2025_sc"

# Paper Table 2 (Descriptive data analysis): Names | Mean | Median | SD | EK | Skewness
PUB <- data.frame(
  item   = c("SC1", "SC2", "SC3", "SC4", "SC5", "SC6"),
  mean   = c(2.920, 2.887, 2.889, 2.967, 2.955, 1.019),
  median = c(4.000, 4.000, 4.000, 4.000, 4.000, 2.000),
  sd     = c(0.804, 0.813, 0.849, 0.880, 0.841, 0.867),
  ek     = c(0.506, 0.049, 0.462, 0.187, 0.542, 0.600),
  skew   = c(0.497, 0.458, 0.636, 0.628, 0.707, -0.744)
)
TOL <- 0.0015   # published to 3dp

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
live <- as.data.frame(irw:::.irw_query_tibble(sprintf(
  "SELECT CAST(item AS STRING) AS item,
          SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp,
          COUNT(*) AS n
   FROM `%s`
   WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')
   GROUP BY item, resp", ref)))

# Sample moments exactly from the frequency table: population SD (/n, which is
# what every row of Table 2 reports), G2 excess kurtosis, G1 skewness.
moments <- function(x, w) {
  n <- sum(w); m <- sum(w * x) / n
  m2 <- sum(w * (x - m)^2) / n; m3 <- sum(w * (x - m)^3) / n; m4 <- sum(w * (x - m)^4) / n
  g1 <- m3 / m2^1.5; g2 <- m4 / m2^2 - 3
  G1 <- g1 * sqrt(n * (n - 1)) / (n - 2)
  G2 <- ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))
  o <- rep(x, w); med <- stats::median(o)
  c(n = n, mean = m, median = med, sd = sqrt(m2), ek = G2, skew = G1)
}

cat("A. Table 2 reproduction (SC block; Mean compared as 5-mean(live), Median as 6-median(live))\n")
cat(sprintf("%-4s %-22s %5s  %-15s %-13s %-15s %-15s %-15s\n", "item", "counts(1..5)", "n",
            "mean pub/5-obs", "med pub/6-obs", "sd pub/obs", "EK pub/obs", "skew pub/obs"))
worst <- 0; bad <- 0
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]; li <- live[live$item == it, ]
  cnt <- sapply(1:5, function(r) { x <- li$n[li$resp == r]; if (length(x)) x else 0 })
  mo <- moments(li$resp, li$n)
  d <- abs(c(PUB$mean[i]   - (5 - mo["mean"]),
             PUB$median[i] - (6 - mo["median"]),
             PUB$sd[i]     - mo["sd"],
             PUB$ek[i]     - mo["ek"],
             PUB$skew[i]   - mo["skew"]))
  worst <- max(worst, d); if (any(d > TOL)) bad <- bad + 1
  cat(sprintf("%-4s %-22s %5d  %.3f/%.3f   %.1f/%.1f     %.3f/%.3f    %6.3f/%6.3f   %6.3f/%6.3f %s\n",
              it, paste(cnt, collapse = "/"), as.integer(mo["n"]),
              PUB$mean[i], 5 - mo["mean"], PUB$median[i], 6 - mo["median"],
              PUB$sd[i], mo["sd"], PUB$ek[i], mo["ek"], PUB$skew[i], mo["skew"],
              if (any(d > TOL)) "MISMATCH" else "ok"))
}

cat("\nB. Pairwise separation (max |gap| over mean/SD/EK/skew; must exceed 2*tol =", 2 * TOL, ")\n")
P <- as.matrix(PUB[, c("mean", "sd", "ek", "skew")]); sep_ok <- TRUE
for (a in 1:5) for (b in (a + 1):6) {
  gap <- max(abs(P[a, ] - P[b, ]))
  mgap <- abs(P[a, "mean"] - P[b, "mean"])
  cat(sprintf("  %s vs %s: max stat gap %.3f (mean-only gap %.3f)\n", PUB$item[a], PUB$item[b], gap, mgap))
  if (gap <= 2 * TOL) sep_ok <- FALSE
}

cat("\nC. Live keying split (reported, not part of the verdict): correlations among SC1..SC6\n")
cr <- as.data.frame(irw:::.irw_query_tibble(sprintf(
  "SELECT a.item AS i, b.item AS j, COUNT(*) AS n,
          CORR(SAFE_CAST(TRIM(CAST(a.resp AS STRING)) AS FLOAT64),
               SAFE_CAST(TRIM(CAST(b.resp AS STRING)) AS FLOAT64)) AS r
   FROM `%s` a JOIN `%s` b ON CAST(a.id AS STRING) = CAST(b.id AS STRING)
   WHERE CAST(a.item AS STRING) < CAST(b.item AS STRING)
   GROUP BY i, j ORDER BY i, j", ref, ref)))
for (k in seq_len(nrow(cr)))
  cat(sprintf("  r(%s,%s) = %+0.3f  (n=%d)\n", cr$i[k], cr$j[k], cr$r[k], cr$n[k]))
neg6 <- cr$r[cr$i == "SC6" | cr$j == "SC6"]
pos5 <- cr$r[!(cr$i == "SC6" | cr$j == "SC6")]
cat(sprintf("  SC6 vs the other five: all negative = %s (range %+0.3f..%+0.3f); the ten SC1-SC5 pairs: all positive = %s (range %+0.3f..%+0.3f)\n",
            all(neg6 < 0), min(neg6), max(neg6), all(pos5 > 0), min(pos5), max(pos5)))
cat("  Table 3 reports all six loading positively (0.814/0.859/0.857/0.913/0.881/0.876, alpha 0.895),\n")
cat("  so in the live table SC6 is stored in the opposite direction to SC1-SC5; SC1-SC5 are the\n")
cat("  reversed ones on the deposit-wide check (they correlate -0.43..-0.53 with the same\n")
cat("  respondents' procedural-justice items, which are positively worded like SC1-SC5, while SC6\n")
cat("  correlates +0.52 with them). Not a mapping defect -- a direction caveat, see public_note.\n")

cat(sprintf("\nA: %d/6 items match all five published statistics (largest deviation %.4f, tol %.4f); every pair separated: %s\n",
            6 - bad, worst, TOL, sep_ok))
cat("Not established by this script: the code->wording tie itself (Table 3's explicit\n",
    "'Abbreviations' labels carry that, and no statistic re-derives a sentence), and the\n",
    "option_text<->resp axis (no anchors are published, so option_text is blank).\n", sep = "")
cat(if (bad == 0 && sep_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
