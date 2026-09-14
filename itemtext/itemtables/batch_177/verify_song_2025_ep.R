# verify_song_2025_ep.R -- Step 5b mapping check (batch_177)
#
# TABLE IS BLOCKED ON INSTRUMENT RIGHTS (see notes_song_2025_ep.csv); no
# __items.csv was written. This script banks the mapping analysis so an unblock
# can ship same-day without re-deriving it.
#
# Derivation: data/song_2025_servant_leadership.py melts the S1 Appendix xlsx
# (doi:10.6084/m9.figshare.28606742.v1 = PLOS s001) with item = the raw source
# column name (EP1..EP4) -- no rename, no positional step.
# Text tie: PLOS ONE 10.1371/journal.pone.0323811 Table 3 prints each item's
# wording next to the very code the data use ("My manager does not encourage me
# to use my talents. EP1", ...) -- an explicit code label, not order inference.
#
# What this script checks (would break if two item texts/codes were swapped):
#  A. Live per-item distribution (server-side GROUP BY item, resp -- NO table
#     export) -> mean, SD, skewness, excess kurtosis, compared to the paper's
#     Table 2 (Mean / SD / "EK" / Skewness, same EP codes). This establishes that
#     the IRW codes ARE the paper's codes. EP2 and EP3 means differ by only 0.017,
#     so the tie is broken by kurtosis (1.085 vs -0.035) and skewness (0.879 vs
#     0.555), not by means.
#  B. The code->wording tie itself rests on Table 3's explicit labels; no
#     statistic re-derives it. Polarity note (printed only): the paper's wording
#     is a NEGATED form of the SLS items, and EP3's negation ("does not just tell
#     me what to do but enables me...") reads positively in English, yet EP3
#     behaves like EP1/2/4 in the deposit (see notes). Not a pass/fail criterion.

suppressMessages(library(irw))

TABLE <- "song_2025_ep"

# Paper Table 2 (Descriptive data analysis), columns Mean, SD, EK, Skewness.
PUB <- data.frame(
  item = c("EP1", "EP2", "EP3", "EP4"),
  mean = c(1.895, 1.973, 1.990, 2.031),
  sd   = c(0.807, 0.843, 0.834, 0.867),
  ek   = c(0.960, 1.085, -0.035, 0.141),
  skew = c(0.832, 0.879, 0.555, 0.569)
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
    "and whether respondents read EP3 as a negated item (the English as printed reads positively).\n", sep = "")
cat(if (bad == 0 && sep_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
