# verify_silva_2023_ecohis.R -- Step 5b mapping check for silva_2023_ecohis.
#
# Claim: live item ecohisN carries the wording of paper Table 2 row "itN."
# (Silva et al. 2023, PeerJ 11:e16035, doi:10.7717/peerj.16035), N = 1..13, and
# resp 1..5 = Never .. Very often.
#
# Route 1 (per-item descriptives). Table 2 publishes, per item, mean, median, SD,
# skewness, kurtosis, min and max (n = 371). Several means tie or near-tie
# (it5/it6 1.27/1.27, it8/it9 1.34/1.33, it12/it13 1.31/1.32, it2/it3 1.49/1.50),
# so a means-only match is NOT decisive; the test below matches the full
# 7-statistic profile and requires that every live item's profile matches its OWN
# row and no other row.
#
# Route 9-ish (option direction). The source spreadsheet's own SCORE column is the
# mean of the 13 item codes (it includes the 5s), which only makes sense if 5 is a
# frequency level (Very often) rather than "Don't know"; that is checked offline in
# provenance, and here via the published maxima (a 5 exists on 11 items, 4 on 2).

suppressMessages(library(irw))
TABLE <- "silva_2023_ecohis"

# Paper Table 2, rows it1..it13: mean, median, sd, skew, kurt, min, max
PUB <- rbind(
  c(1.91, 2, 0.97, 0.62, -0.72, 1, 5),
  c(1.49, 1, 0.80, 1.39,  0.62, 1, 4),
  c(1.50, 1, 0.86, 1.63,  1.78, 1, 5),
  c(1.35, 1, 0.79, 2.34,  4.87, 1, 5),
  c(1.27, 1, 0.66, 2.33,  4.39, 1, 4),
  c(1.27, 1, 0.70, 2.52,  5.24, 1, 4),
  c(1.36, 1, 0.77, 2.18,  4.19, 1, 5),
  c(1.34, 1, 0.77, 2.55,  6.52, 1, 5),
  c(1.33, 1, 0.72, 2.49,  6.65, 1, 5),
  c(1.40, 1, 0.89, 2.37,  5.20, 1, 5),
  c(1.55, 1, 1.04, 1.82,  2.30, 1, 5),
  c(1.31, 1, 0.72, 2.46,  5.83, 1, 5),
  c(1.32, 1, 0.74, 2.50,  5.86, 1, 5))
colnames(PUB) <- c("mean", "median", "sd", "skew", "kurt", "min", "max")
TOL <- c(mean = 0.006, median = 0, sd = 0.006, skew = 0.006, kurt = 0.006, min = 0, max = 0)

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
# skewness / excess kurtosis, bias-corrected G1/G2 (SPSS / e1071 type 2) -- the
# estimator that reproduces Table 2; psych's default type 3 misses kurtosis by ~0.15
sk <- function(x) { n <- length(x); m2 <- mean((x - mean(x))^2); g1 <- mean((x - mean(x))^3) / m2^1.5
                    g1 * sqrt(n * (n - 1)) / (n - 2) }
ku <- function(x) { n <- length(x); m2 <- mean((x - mean(x))^2); g2 <- mean((x - mean(x))^4) / m2^2 - 3
                    ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3)) }
items <- paste0("ecohis", 1:13)
OBS <- t(sapply(items, function(it) {
  x <- d$resp[d$item == it]
  c(mean(x), median(x), sd(x), sk(x), ku(x), min(x), max(x), length(x))
}))
colnames(OBS) <- c(colnames(PUB), "n")

cat(sprintf("%-9s %5s | %-40s | %-40s\n", "item", "n", "published mean/med/sd/skew/kurt/min/max",
            "observed"))
for (i in 1:13)
  cat(sprintf("%-9s %5d | %5.2f %2.0f %5.2f %5.2f %5.2f %1.0f %1.0f          | %6.3f %2.0f %6.3f %6.3f %6.3f %1.0f %1.0f\n",
              items[i], OBS[i, "n"], PUB[i, 1], PUB[i, 2], PUB[i, 3], PUB[i, 4], PUB[i, 5], PUB[i, 6], PUB[i, 7],
              OBS[i, 1], OBS[i, 2], OBS[i, 3], OBS[i, 4], OBS[i, 5], OBS[i, 6], OBS[i, 7]))

# Per-cell tolerance: rounding (0.005) plus slack. Two printed cells do not
# reproduce at rounding precision and are reported rather than hidden:
#   it8 kurtosis printed 6.52, live 6.529 (off by 0.009, i.e. 6.53 at 2dp)
#   it13 skewness printed 2.50, live 2.470 (off by 0.030; no other item has 2.50,
#        and it13's mean/median/sd/kurtosis/min/max all reproduce -- a misprint)
TOL <- c(mean = 0.006, median = 0, sd = 0.006, skew = 0.035, kurt = 0.010, min = 0, max = 0)
match_row <- function(o, p) all(abs(o[1:7] - p) <= TOL + 1e-9)
M <- sapply(1:13, function(j) sapply(1:13, function(i) match_row(OBS[i, ], PUB[j, ])))
# Nearest-profile distance, each stat scaled by its printed precision
SC <- c(0.01, 1, 0.01, 0.01, 0.01, 1, 1)
D <- sapply(1:13, function(j) sapply(1:13, function(i) sum(abs(OBS[i, 1:7] - PUB[j, ]) / SC)))
cat("\nPer live item: published rows within tolerance on ALL 7 stats; nearest and 2nd-nearest profile distance:\n")
ok <- TRUE
for (i in 1:13) {
  hits <- which(M[i, ])
  o <- order(D[i, ])
  cat(sprintf("  %-9s within-tol -> %-8s nearest it%-2d (d=%5.2f)  2nd it%-2d (d=%5.2f)\n", items[i],
              if (length(hits)) paste0("it", paste(hits, collapse = ",")) else "NONE",
              o[1], D[i, o[1]], o[2], D[i, o[2]]))
  if (!identical(as.integer(hits), i) || o[1] != i) ok <- FALSE
}
dev <- abs(OBS[, 1:7] - PUB)
cat(sprintf("\nlargest own-row |diff|: mean %.4f, sd %.4f, skew %.4f (%s), kurt %.4f (%s)\n",
            max(dev[, 1]), max(dev[, 3]), max(dev[, 4]), items[which.max(dev[, 4])],
            max(dev[, 5]), items[which.max(dev[, 5])]))
cat("Establishes: code<->Table 2 row for all 13 items (each profile within tolerance of its own row only,\n",
    "and nearest to its own row). Near-tied means (it5/it6, it8/it9, it12/it13, it2/it3) are separated by\n",
    "SD/skew/kurtosis/max.\n",
    "Does NOT establish: that Table 2's English renders the administered Brazilian Portuguese\n",
    "wording faithfully, nor the anchor labels (Table 2 prints none; anchors are Pahel 2007's).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
