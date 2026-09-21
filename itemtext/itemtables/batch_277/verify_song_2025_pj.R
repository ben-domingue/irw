# verify_song_2025_pj.R -- Step 5b mapping check (batch_277)
#
# Derivation: data/song_2025_servant_leadership.py melts the S1 Appendix xlsx
# (PLOS s001 = doi:10.6084/m9.figshare.28606742.v1) with item = the raw source
# column name (PJ1..PJ4) -- no rename, no positional step.
# Text tie: PLOS ONE 10.1371/journal.pone.0323811 Table 3 prints each item's
# wording in a cell whose neighbouring "Abbreviations" cell is the very code the
# data use ("I believe my manager really tries to conduct a fair and objective
# appraisal." | PJ1 | 0.852), i.e. an explicit code label, not an order inference.
#
# What this script checks (and what would break it):
#  A. The live per-item distribution (server-side GROUP BY item, resp -- NO table
#     export) reproduces the paper's Table 2 Mean / SD / EK / Skewness for the
#     same PJ codes. This establishes that the IRW column labelled PJ_i IS the
#     paper's PJ_i, so any permutation of the four codes between the deposit and
#     the live table would show up here.
#  B. Separation: every pair of items must differ by more than the tolerance on
#     at least one published statistic, otherwise a swap would be invisible.
#     The closest pair on the mean is PJ1 vs PJ3 (3.678 vs 3.625, gap 0.053);
#     all four means, EKs and skews are distinct well above tolerance.
#  C. NOT established by this script: the code->wording tie itself, which rests
#     on Table 3's explicit labels and no statistic re-derives it; the
#     option_text<->resp axis, which is empty because the study publishes no
#     anchor labels for its five-point scale; and -- most importantly -- PJ4's
#     wording, which Table 3 does not publish (its PJ4 cell repeats PJ3's
#     sentence verbatim, so item_text is shipped blank for PJ4). A statistic
#     cannot recover a sentence the source never printed.

suppressMessages(library(irw))

TABLE <- "song_2025_pj"

# Paper Table 2 (Descriptive data analysis): Names | Mean | Median | SD | EK | Skewness
PUB <- data.frame(
  item = c("PJ1", "PJ2", "PJ3", "PJ4"),
  mean = c(3.678, 3.511, 3.625, 3.720),
  sd   = c(0.812, 0.819, 0.829, 0.797),
  ek   = c(-0.267, 0.050, 0.657, 0.187),
  skew = c(-0.252, -0.172, -0.684, -0.386)
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
cat("Not established by this script: the code->wording tie itself (that rests on Table 3's\n",
    "explicit 'Abbreviations' labels, and no statistic re-derives it); the option_text<->resp\n",
    "axis (the study publishes no anchor labels for its five-point scale, so option_text is\n",
    "blank); and PJ4's wording, which Table 3 never printed -- its PJ4 cell repeats PJ3's\n",
    "sentence verbatim, so item_text is shipped blank for PJ4.\n", sep = "")
cat(if (bad == 0 && sep_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
