# verify_personalitychange_kramer_2025_sccs.R -- batch_518
#
# Claim under test: sc01_01..sc01_12 carry the Campbell et al. (1996) SCCS items in
# the codebook's SC01_01..SC01_12 order (item code IS the SoSci source column name,
# lowercased), and resp runs 1 = Strongly disagree .. 5 = strongly AGREE, stored raw.
# The codebook prints "5 = strongly disagree"; the shipped anchor overrides that.
#
# Route: keying polarity (Step 5b route 6) with an EXTERNAL direction anchor. The
# same raw files carry the SWLS (sw06_*), whose 7-point scale is fully labelled
# 1 = Strongly disagree .. 7 = Strongly agree. Self-concept clarity correlates
# positively with life satisfaction, so:
#   - the 10 low-clarity items (1-5, 7-10, 12) must correlate NEGATIVELY with SWLS;
#   - item 11 ("clear sense of who I am") must correlate POSITIVELY with SWLS and
#     negatively with the mean of the 10 low-clarity items.
# Holding in all three studies both pins resp direction (5 = agree) and the
# polarity class of every item except 6. Also checks the live table equals the
# raw deposit (no IRW-side reversal), per-item means.
#
# Does NOT establish: order WITHIN the 10 negatively keyed items, and item 6's
# polarity (r ~ 0 with everything). That rests on the codebook's explicit codes.

suppressMessages(library(irw))
TABLE <- "personalitychange_kramer_2025_sccs"
td <- file.path(tempdir(), "kramer_sccs"); dir.create(td, showWarnings = FALSE)
zf <- file.path(td, "reproduce.zip")
if (!file.exists(zf)) download.file("https://osf.io/download/6xv7f/", zf, mode = "wb", quiet = TRUE)
unzip(zf, exdir = td)
files <- file.path(td, "reproduce/data", c("df_sbsa.rda", "df_sbsa2.rda", "df_sbsa3.rda"))

neg <- setdiff(1:12, c(6, 11)); ok <- TRUE; pooled <- list()
for (f in files) {
  e <- new.env(); load(f, e); d <- as.data.frame(get(ls(e)[1], e))
  sc <- d[, sprintf("sc01_%02d", 1:12)]; sc[sc == -9] <- NA
  sw <- d[, sprintf("sw06_%02d", 1:5)]; sw[sw == -9] <- NA
  swm <- rowMeans(sw)
  r_sw <- sapply(sc, function(x) cor(x, swm, use = "pair"))
  r11 <- cor(sc$sc01_11, rowMeans(sc[, neg]), use = "pair")
  cat("\n", basename(f), "  n =", nrow(d), "\n cor(item, SWLS mean):\n")
  print(round(r_sw, 3))
  cat(sprintf(" cor(sc01_11, mean of 10 low-clarity items) = %.3f\n", r11))
  pass <- all(r_sw[neg] < 0) && r_sw[11] > 0 && r11 < 0
  cat(" low-clarity items all < 0:", all(r_sw[neg] < 0), "| sc01_11 > 0:", r_sw[11] > 0,
      "| sc01_11 vs low-clarity < 0:", r11 < 0, "\n")
  ok <- ok && pass
  pooled[[f]] <- sc
}
raw <- do.call(rbind, pooled)
rawm <- colMeans(raw, na.rm = TRUE)
live <- irw::irw_fetch(TABLE)
livem <- tapply(live$resp, live$item, mean)[names(rawm)]
cat("\nlive vs raw-deposit per-item means (pooled over studies and waves):\n")
print(round(rbind(raw = rawm, live = livem), 4))
dev <- max(abs(rawm - livem))
cat(sprintf("max |live - raw| = %.2e\n", dev))
ok <- ok && dev < 1e-6
cat("Not established: order within the 10 negatively keyed items; sc01_06 polarity (r ~ 0).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
