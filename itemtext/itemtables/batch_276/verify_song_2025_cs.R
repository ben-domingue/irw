# verify_song_2025_cs.R -- Step 5b mapping check (batch_276)
#
# Derivation: data/song_2025_servant_leadership.py melts the S1 Appendix xlsx
# (PLOS s001 = doi:10.6084/m9.figshare.28606742.v1) with item = the raw source
# column name (CS1..CS4) -- no rename, no positional step.
# Text tie: PLOS ONE 10.1371/journal.pone.0323811 Table 3 prints each item's
# wording in a cell whose neighbouring "Abbreviations" cell is the very code the
# data use ("I am satisfied with the service we provide." | CS1 | 0.894), i.e.
# an explicit code label, not an order inference.
#
# What this script checks (and what would break it):
#  A. The live per-item distribution (server-side GROUP BY item, resp -- NO table
#     export) reproduces the paper's Table 2 Mean / SD / EK / Skewness for the
#     same CS codes. This establishes that the IRW column labelled CS_i IS the
#     paper's CS_i, so any permutation of the four codes between the deposit and
#     the live table would show up here.
#  B. Separation: every pair of items must differ by more than the tolerance on
#     at least one published statistic, otherwise a swap would be invisible.
#     CS2 vs CS4 differ by only 0.015 on the mean; the tie is broken by excess
#     kurtosis (1.031 vs 0.018) and SD (0.769 vs 0.698), not by means.
#  C. NOT established by this script: the code->wording tie itself, which rests
#     on Table 3's explicit labels and no statistic re-derives it; and the
#     option_text<->resp axis, which is empty because the study publishes no
#     anchor labels for its five-point scale.

suppressMessages(library(irw))

TABLE <- "song_2025_cs"

# Paper Table 2 (Descriptive data analysis): Names | Mean | Median | SD | EK | Skewness
PUB <- data.frame(
  item = c("CS1", "CS2", "CS3", "CS4"),
  mean = c(3.767, 3.810, 3.924, 3.825),
  sd   = c(0.803, 0.769, 0.741, 0.698),
  ek   = c(-0.255, 1.031, -0.046, 0.018),
  skew = c(-0.345, -0.618, -0.366, -0.257)
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

P <- as.matrix(PUB[, -1]); sep_ok <- TRUE
for (a in 1:3) for (b in (a + 1):4) {
  gap <- max(abs(P[a, ] - P[b, ]))
  cat(sprintf("separation %s vs %s: max stat gap %.3f\n", PUB$item[a], PUB$item[b], gap))
  if (gap <= 2 * TOL) sep_ok <- FALSE
}

cat(sprintf("\nA: %d/4 items match Table 2 on all four statistics (largest deviation %.4f, tol %.4f); every pair separated: %s\n",
            4 - bad, worst, TOL, sep_ok))
cat("Not established by this script: the code->wording tie (Table 3's explicit labels), and the\n",
    "option_text<->resp axis (the study publishes no anchor labels for its five-point scale).\n", sep = "")
cat(if (bad == 0 && sep_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
