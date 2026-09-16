# verify_song_2025_hu.R -- Step 5b mapping check (batch_178)
#
# TABLE IS BLOCKED ON INSTRUMENT RIGHTS (see notes_song_2025_hu.csv); no
# __items.csv was written. This script banks the mapping analysis so an unblock
# can ship without re-deriving it.
#
# Derivation: data/song_2025_servant_leadership.py melts the S1 Appendix xlsx
# (PLOS s001, sha256 28d72fc5...e08e11f0) with item = the raw source column
# name (HU1..HU4) -- no rename, no positional step.
# Text tie: PLOS ONE 10.1371/journal.pone.0323811 Table 3 prints each item's
# wording beside the very code the data use ("My manager does not learn from
# criticism." HU1, ...) -- an explicit code label, not order inference.
#
# What this script checks (would break if two codes were swapped):
#  A. Live per-item distribution (server-side GROUP BY item, resp -- NO table
#     export) -> mean, SD, excess kurtosis, skewness, compared with the paper's
#     Table 2 (Mean / SD / "EK" / Skewness, same HU codes). This establishes that
#     the IRW codes ARE the paper's codes. HU2 and HU3 means differ by only
#     0.014, so that pair is separated by EK (0.754 vs -0.267) and skewness
#     (0.610 vs 0.287), not by means.
#  B. The code->wording tie itself rests on Table 3's explicit labels; no
#     statistic re-derives it.

suppressMessages(library(irw))

TABLE <- "song_2025_hu"

# Paper Table 2 (Descriptive data analysis), columns Mean, SD, EK, Skewness.
PUB <- data.frame(
  item = c("HU1", "HU2", "HU3", "HU4"),
  mean = c(2.291, 2.122, 2.136, 2.247),
  sd   = c(0.842, 0.804, 0.767, 0.828),
  ek   = c(-0.109, 0.754, -0.267, 0.584),
  skew = c(0.239, 0.610, 0.287, 0.583)
)
TOL <- 0.0015   # published to 3dp

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
live <- as.data.frame(irw:::.irw_query_tibble(sprintf(
  "SELECT CAST(item AS STRING) AS item, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp, COUNT(*) AS n
   FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY item, resp", ref)))

# Sample moments as SPSS/Excel report them (bias-corrected skew G1, kurtosis G2),
# computed exactly from the frequency table.
moments <- function(x, w) {
  n <- sum(w); m <- sum(w * x) / n
  s2 <- sum(w * (x - m)^2) / (n - 1); s <- sqrt(s2)
  m2 <- sum(w * (x - m)^2) / n; m3 <- sum(w * (x - m)^3) / n; m4 <- sum(w * (x - m)^4) / n
  g1 <- m3 / m2^1.5; g2 <- m4 / m2^2 - 3
  G1 <- g1 * sqrt(n * (n - 1)) / (n - 2)
  G2 <- ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))
  c(n = n, mean = m, sd = s, ek = G2, skew = G1)
}

cat("item  counts(1..5)            n     mean(pub/obs)     sd(pub/obs)      ek(pub/obs)      skew(pub/obs)\n")
worst <- 0; bad <- 0
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]; li <- live[live$item == it, ]
  cnt <- sapply(1:5, function(r) { x <- li$n[li$resp == r]; if (length(x)) x else 0 })
  mo <- moments(li$resp, li$n)
  d <- abs(c(mo["mean"] - PUB$mean[i], mo["sd"] - PUB$sd[i], mo["ek"] - PUB$ek[i], mo["skew"] - PUB$skew[i]))
  worst <- max(worst, d); if (any(d > TOL)) bad <- bad + 1
  cat(sprintf("%-5s %-22s %4d  %.3f/%.3f  %.3f/%.3f  %6.3f/%6.3f  %.3f/%.3f %s\n", it,
              paste(cnt, collapse = "/"), as.integer(mo["n"]),
              PUB$mean[i], mo["mean"], PUB$sd[i], mo["sd"], PUB$ek[i], mo["ek"], PUB$skew[i], mo["skew"],
              if (any(d > TOL)) "MISMATCH" else "ok"))
}

# Does the published profile separate every item from every other? Any swap of
# two codes must move at least one statistic by more than the tolerance.
P <- as.matrix(PUB[, -1]); sep_ok <- TRUE
for (a in 1:3) for (b in (a + 1):4) {
  gap <- max(abs(P[a, ] - P[b, ]))
  cat(sprintf("separation %s vs %s: max stat gap %.3f\n", PUB$item[a], PUB$item[b], gap))
  if (gap <= 2 * TOL) sep_ok <- FALSE
}

cat(sprintf("\nA: %d/4 items match Table 2 on all four statistics (largest deviation %.4f, tol %.4f); every pair separated: %s\n",
            4 - bad, worst, TOL, sep_ok))
cat("Not established by this script: the code->wording tie, which rests on the paper's Table 3 explicit labels;\n",
    "nor that the published English is what respondents read (Chinese back-translated administration; only English published).\n", sep = "")
cat(if (bad == 0 && sep_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
