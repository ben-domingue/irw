# verify_WMD_bartczuk_2023.R -- Step 5b check for WMD_bartczuk_2023 (batch_417).
#
# Claim: item code WMDSnn carries the wording that the study's own deposit file
# Items_properties.xlsx (osf.io/download/d84xe, OSF rxb5y) pairs with code WMDSnn,
# and the Polish wording is item nn of the study's Polish form (Supplementary1.pdf,
# osf.io/download/u9twx), whose printed numbering 1..24 follows the same order.
#
# Route 1 (per-item descriptives): Items_properties.xlsx publishes, per code, Mean,
# Variance, Skewness and Kurtosis (zero-centred). If the xlsx codes refer to the same
# columns as the live WMDSnn items, every live item's 4-stat profile must be nearest to
# its OWN published row. Several means tie within 0.02 (02/13/07, 04/20/18, 14/15), so
# the check uses all four moments, each standardised by its across-item SD.
#
# What this does NOT establish: that the authors paired each code with the right English
# sentence inside the xlsx (that pairing is taken as authoritative source labelling), or
# the Polish<->code link, which rests on the form's printed item numbers plus a 24/24
# content read of Polish item n against the xlsx's English for WMDSnn.
# The xlsx stats appear to be from the imputed file (wmds.dat), the live table keeps NA,
# so small residuals (<~0.03) are expected.

suppressMessages(library(irw))
TABLE <- "WMD_bartczuk_2023"

PUB <- rbind(
  WMDS01 = c(1.531, 0.776, 1.946, 3.685),
  WMDS02 = c(1.764, 1.108, 1.343, 0.884),
  WMDS03 = c(2.111, 1.112, 0.699, -0.413),
  WMDS04 = c(1.835, 0.969, 1.259, 1.184),
  WMDS05 = c(2.017, 1.118, 0.966, 0.187),
  WMDS06 = c(2.501, 1.218, 0.292, -0.724),
  WMDS07 = c(1.777, 0.856, 1.413, 1.927),
  WMDS08 = c(1.716, 0.901, 1.467, 1.867),
  WMDS09 = c(2.605, 1.497, 0.222, -1.029),
  WMDS10 = c(2.032, 0.954, 0.989, 0.61),
  WMDS11 = c(2.243, 1.305, 0.742, -0.377),
  WMDS12 = c(2.15, 1.089, 0.806, 0.191),
  WMDS13 = c(1.744, 1.036, 1.501, 1.769),
  WMDS14 = c(1.852, 0.972, 1.22, 1.081),
  WMDS15 = c(1.857, 0.853, 1.192, 1.368),
  WMDS16 = c(2.416, 1.196, 0.331, -0.754),
  WMDS17 = c(1.994, 1.056, 1.101, 0.815),
  WMDS18 = c(1.82, 0.793, 1.339, 2.057),
  WMDS19 = c(2.096, 0.907, 0.813, 0.326),
  WMDS20 = c(1.837, 0.548, 0.82, 1.123),
  WMDS21 = c(2.206, 1.266, 0.646, -0.588),
  WMDS22 = c(1.705, 0.842, 1.468, 1.987),
  WMDS23 = c(1.603, 0.681, 1.723, 3.473),
  WMDS24 = c(1.942, 1.015, 1.195, 1.121))
colnames(PUB) <- c("mean", "var", "skew", "kurt")

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
mom <- function(z) {
  m <- mean(z); c0 <- z - m; s2 <- mean(c0^2)
  c(mean = m, var = var(z), skew = mean(c0^3) / s2^1.5, kurt = mean(c0^4) / s2^2 - 3)
}
OBS <- do.call(rbind, lapply(split(d$resp, d$item), mom))[rownames(PUB), ]

sc <- apply(PUB, 2, sd)
Z <- function(M) sweep(M, 2, sc, "/")
D <- as.matrix(dist(rbind(Z(OBS), Z(PUB))))[1:24, 25:48]
dimnames(D) <- list(rownames(PUB), rownames(PUB))

cat(sprintf("%-7s %6s %6s | %6s %6s | %6s %6s | %6s %6s | %6s %-7s %6s\n",
            "item", "pubM", "obsM", "pubV", "obsV", "pubSk", "obsSk", "pubKu", "obsKu",
            "d_own", "nearest", "d_2nd"))
ok <- TRUE; minratio <- Inf
for (i in rownames(PUB)) {
  own <- D[i, i]; other <- D[i, colnames(D) != i]
  nn <- names(which.min(D[i, ]))
  ok <- ok && nn == i
  minratio <- min(minratio, min(other) / own)
  cat(sprintf("%-7s %6.3f %6.3f | %6.3f %6.3f | %6.3f %6.3f | %6.3f %6.3f | %6.3f %-7s %6.3f\n",
              i, PUB[i, 1], OBS[i, 1], PUB[i, 2], OBS[i, 2], PUB[i, 3], OBS[i, 3],
              PUB[i, 4], OBS[i, 4], own, nn, min(other)))
}
cat(sprintf("\nmax |mean diff| = %.3f; max |var diff| = %.3f; max |skew diff| = %.3f; max |kurt diff| = %.3f\n",
            max(abs(OBS[, 1] - PUB[, 1])), max(abs(OBS[, 2] - PUB[, 2])),
            max(abs(OBS[, 3] - PUB[, 3])), max(abs(OBS[, 4] - PUB[, 4]))))
cat(sprintf("every item nearest its own published row: %s; smallest (nearest-other / own) distance ratio: %.1f\n",
            ok, minratio))
cat("Not established here: the xlsx's own code->sentence pairing, and the Polish form's numbering (content read 24/24).\n")
cat(if (ok && minratio > 2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
