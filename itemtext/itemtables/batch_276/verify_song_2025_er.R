# verify_song_2025_er.R -- Step 5b mapping check (batch_276)
#
# Derivation: data/song_2025_servant_leadership.py melts the S1 Appendix xlsx
# (PLOS s001, sha256 28d72fc5...e08e11f0) with item = the raw source column
# name (ER1..ER5) -- no rename, no positional step.
# Text tie: PLOS ONE 10.1371/journal.pone.0323811 Table 3 ("Reliability and
# validity of the constructs", columns "Scale items | Abbreviations | ...")
# prints each wording beside the very code the data use, under the heading
# "Employee retention" -- an explicit code label, not order inference.
#
# What this script checks (it would break if two ER codes were swapped in the
# IRW table relative to the paper): the live per-item distribution, obtained by
# a server-side GROUP BY (no table export), reproduces the paper's Table 2
# Mean / SD / EK / Skewness for that same code. The paper's SD is the
# POPULATION SD (ddof = 0): e.g. ER1's sample SD is 0.95014 and its population
# SD 0.94916, and 0.949 is what Table 2 prints; all five agree that way.
# ER1 and ER5 differ in mean by only 0.002, so that pair is separated by EK
# (0.229 vs 0.333) and skewness (-0.598 vs -0.754), not by means.

suppressMessages(library(irw))

TABLE <- "song_2025_er"

# Song et al. (2025) PLOS ONE 10.1371/journal.pone.0323811, Table 2
# "Descriptive data analysis" (Names / Mean / Median / SD / EK / Skewness).
PUB <- data.frame(
  item   = c("ER1", "ER2", "ER3", "ER4", "ER5"),
  mean   = c(3.569, 3.699, 3.546, 3.753, 3.567),
  median = c(4, 4, 4, 4, 4),
  sd     = c(0.949, 0.805, 0.963, 0.860, 0.941),
  ek     = c(0.229, 0.124, 0.077, 0.861, 0.333),
  skew   = c(-0.598, -0.497, -0.583, -0.771, -0.754),
  stringsAsFactors = FALSE
)
TOL <- 0.0015   # published to 3 dp

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
live <- as.data.frame(irw:::.irw_query_tibble(sprintf(
  "SELECT CAST(item AS STRING) AS item,
          SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp,
          COUNT(*) AS n
   FROM `%s`
   WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')
   GROUP BY item, resp", ref)))

# Moments from the frequency table: population SD (as Table 2 reports it),
# bias-corrected skewness G1 and excess kurtosis G2.
moments <- function(x, w) {
  n <- sum(w); m <- sum(w * x) / n
  m2 <- sum(w * (x - m)^2) / n
  m3 <- sum(w * (x - m)^3) / n
  m4 <- sum(w * (x - m)^4) / n
  g1 <- m3 / m2^1.5; g2 <- m4 / m2^2 - 3
  G1 <- g1 * sqrt(n * (n - 1)) / (n - 2)
  G2 <- ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))
  med <- { cs <- cumsum(w[order(x)]) / n; sort(x)[which(cs >= 0.5)[1]] }
  c(n = n, mean = m, sd = sqrt(m2), ek = G2, skew = G1, median = med)
}

cat("item  live counts 1..5        n    mean pub/obs      sd pub/obs       ek pub/obs        skew pub/obs\n")
worst <- 0; bad <- 0
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]; li <- live[live$item == it, ]
  cnt <- sapply(1:5, function(r) { x <- li$n[li$resp == r]; if (length(x)) x else 0 })
  mo <- moments(li$resp, li$n)
  d <- abs(c(mo["mean"] - PUB$mean[i], mo["sd"] - PUB$sd[i],
             mo["ek"] - PUB$ek[i], mo["skew"] - PUB$skew[i]))
  worst <- max(worst, d); if (any(d > TOL)) bad <- bad + 1
  cat(sprintf("%-5s %-22s %4d  %.3f/%.3f  %.3f/%.3f  %6.3f/%6.3f  %6.3f/%6.3f %s\n",
              it, paste(cnt, collapse = "/"), as.integer(mo["n"]),
              PUB$mean[i], mo["mean"], PUB$sd[i], mo["sd"],
              PUB$ek[i], mo["ek"], PUB$skew[i], mo["skew"],
              if (any(d > TOL)) "MISMATCH" else "ok"))
}

# Does the published profile separate every item from every other? Any swap of
# two codes has to move at least one statistic by more than the tolerance.
P <- as.matrix(PUB[, c("mean", "sd", "ek", "skew")]); sep_ok <- TRUE
for (a in 1:4) for (b in (a + 1):5) {
  gap <- max(abs(P[a, ] - P[b, ]))
  cat(sprintf("separation %s vs %s: max stat gap %.3f\n", PUB$item[a], PUB$item[b], gap))
  if (gap <= 2 * TOL) sep_ok <- FALSE
}

cat(sprintf("\n%d/5 items match Table 2 on mean, SD, EK and skewness (largest deviation %.4f, tol %.4f); every pair separated: %s\n",
            5 - bad, worst, TOL, sep_ok))
cat("Not established by this script: the code->wording tie itself, which rests on Table 3's\n",
    "explicit labels rather than on any statistic; and that the published English is what\n",
    "respondents read (the administration was Chinese, back-translated; only English is published).\n", sep = "")
cat(if (bad == 0 && sep_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
