# verify_song_2025_wwb.R -- Step 5b mapping check (batch_278)
#
# Derivation (core model section 3, pattern 1): data/song_2025_servant_leadership.py
# melts the S1 Appendix xlsx (PLOS s001 = figshare 10.6084/m9.figshare.28606742.v1,
# sha256 28d72fc5a8a7fc1bb72b80c5c437c98694b64928e25074a1c215e8a6b08e11f0) keeping
# item = the raw source column name (WWB1..WWB3) -- no rename, no positional step.
# Text tie: PLOS ONE 10.1371/journal.pone.0323811 Table 3 ("Reliability and validity
# of the constructs", columns "Scale items | Abbreviations | ...") prints each
# wording beside that same code under the heading "Work wellbeing".
#
# What this script checks -- it would break if two WWB codes were swapped in the
# IRW table relative to the paper: the live per-item distribution, from a
# server-side GROUP BY (no table export), reproduces the paper's Table 2
# Mean / SD / EK / Skewness for that same code. Table 2's SD is the POPULATION SD
# (WWB2 sample 0.89513, population 0.89421; 0.894 is what is printed).

suppressMessages(library(irw))

TABLE <- "song_2025_wwb"

# Song et al. (2025) PLOS ONE 10.1371/journal.pone.0323811, Table 2
# "Descriptive data analysis" (Names / Mean / Median / SD / EK / Skewness).
PUB <- data.frame(
  item   = c("WWB1", "WWB2", "WWB3"),
  mean   = c(3.825, 3.410, 3.736),
  median = c(4, 3, 4),
  sd     = c(0.840, 0.894, 0.830),
  ek     = c(-0.457, -0.198, -0.173),
  skew   = c(-0.267, -0.120, -0.320),
  stringsAsFactors = FALSE
)
# Per-level counts of WWB1..WWB3 in the S1 Appendix xlsx itself (n = 485 each),
# the file data/song_2025_servant_leadership.py melts. A recode or a column
# shift in the melt would break these before it broke the moments.
XLSX <- rbind(c(1, 25, 140, 211, 108), c(8, 58, 199, 167, 53), c(2, 31, 143, 226, 83))
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

cat("item  live counts 1..5       xlsx counts 1..5          n    mean pub/obs      sd pub/obs       ek pub/obs        skew pub/obs\n")
worst <- 0; bad <- 0; cnt_bad <- 0
for (i in seq_len(nrow(PUB))) {
  it <- PUB$item[i]; li <- live[live$item == it, ]
  cnt <- sapply(1:5, function(r) { x <- li$n[li$resp == r]; if (length(x)) x else 0 })
  if (!identical(as.numeric(cnt), as.numeric(XLSX[i, ]))) cnt_bad <- cnt_bad + 1
  mo <- moments(li$resp, li$n)
  d <- abs(c(mo["mean"] - PUB$mean[i], mo["sd"] - PUB$sd[i],
             mo["ek"] - PUB$ek[i], mo["skew"] - PUB$skew[i]))
  worst <- max(worst, d); if (any(d > TOL)) bad <- bad + 1
  cat(sprintf("%-5s %-22s %-22s %4d  %.3f/%.3f  %.3f/%.3f  %6.3f/%6.3f  %6.3f/%6.3f %s\n",
              it, paste(cnt, collapse = "/"), paste(XLSX[i, ], collapse = "/"),
              as.integer(mo["n"]),
              PUB$mean[i], mo["mean"], PUB$sd[i], mo["sd"],
              PUB$ek[i], mo["ek"], PUB$skew[i], mo["skew"],
              if (any(d > TOL)) "MISMATCH" else "ok"))
}

# Does the published profile separate every item from every other? A swap of two
# codes has to move at least one statistic by more than the tolerance.
P <- as.matrix(PUB[, c("mean", "sd", "ek", "skew")]); sep_ok <- TRUE
for (a in 1:2) for (b in (a + 1):3) {
  gap <- max(abs(P[a, ] - P[b, ]))
  cat(sprintf("separation %s vs %s: max stat gap %.3f\n", PUB$item[a], PUB$item[b], gap))
  if (gap <= 2 * TOL) sep_ok <- FALSE
}

cat(sprintf("\n%d/3 items match Table 2 on mean, SD, EK and skewness (largest deviation %.4f, tol %.4f); %d/3 match the S1 xlsx counts cell for cell; every pair separated: %s\n",
            3 - bad, worst, TOL, 3 - cnt_bad, sep_ok))
cat("Not established by this script: the code->wording tie itself, which rests on Table 3's\n",
    "explicit 'Abbreviations' labels rather than on any statistic; the option_text<->resp axis\n",
    "(no anchors are published anywhere, so option_text is blank in every row and carries no\n",
    "claim); and that the published English is what respondents read -- the administration was\n",
    "Chinese with back-translation, and only English is published.\n", sep = "")
cat(if (bad == 0 && cnt_bad == 0 && sep_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
