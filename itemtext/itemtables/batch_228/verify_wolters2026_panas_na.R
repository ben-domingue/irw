# verify_wolters2026_panas_na.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: panas_na_1..panas_na_10 are the figshare deposit's columns
#   PANAS_NA_2, _5, _7, _8, _9, _12, _14, _16, _19, _20 (in that order), and
#   those column numbers are positions in the German PANAS of Krohne, Egloff,
#   Kohlmann & Tausch (1996) -- documented in ZIS doi 10.6102/zis146 Tabelle 2
#   and doi 10.6102/zis242 Tabelle 2, which give the English original
#   (Watson, Clark & Tellegen, 1988) for each position.
#
# The check that would break if any two item_texts were swapped: each live
# item's FULL 5-level response-frequency vector must match exactly one raw
# column of the deposit, and it must be the claimed one.

suppressMessages(library(irw))
TABLE <- "wolters2026_panas_na"

# Raw per-column response counts (resp 1..5), computed from the deposit file
# "Wolters Pollklas - 2026 - Online health research fosters health concerns - Raw data.xlsx"
# (figshare 10.6084/m9.figshare.32044005.v1, sheet "DrGoogle-2022022  (2)", N = 83,
#  sha256 276aa0114d6b507ef2b14dfcbe14b8a93e9df0712699e138e12daa41a3cd90cb).
RAW <- list(
  PANAS_NA_2  = c(19, 28, 20, 12,  4),
  PANAS_NA_5  = c(18, 35, 14, 13,  3),
  PANAS_NA_7  = c(44, 18,  9,  9,  3),
  PANAS_NA_8  = c(42, 24,  9,  5,  3),
  PANAS_NA_9  = c(52, 25,  2,  4,  0),
  PANAS_NA_12 = c(17, 27, 14, 21,  4),
  PANAS_NA_14 = c(37, 22, 17,  6,  1),
  PANAS_NA_16 = c(15, 26, 23, 13,  6),
  PANAS_NA_19 = c(21, 18, 22, 16,  6),
  PANAS_NA_20 = c(27, 25, 10, 13,  8)
)
CLAIM <- names(RAW)                       # claimed source column per panas_na_1..10
TEXT  <- c("distressed","upset","guilty","scared","hostile",
           "irritable","ashamed","nervous","jittery","afraid")
# Published per-item means for the same German items, same positions:
#   ZIS 10.6102/zis242 Tabelle 7 (GESIS Panel, n = 4,188)
#   ZIS 10.6102/zis146 Tabelle 5 (Janke & Gloeckner-Rist 2014)
ZIS242_MEAN <- c(2.28, 2.03, 1.38, 1.45, 1.37, 1.96, 1.36, 1.97, 1.73, 1.68)
ZIS146_MEAN <- c(2.40, 2.10, 1.50, 1.90, 1.60, 2.40, 1.50, 3.00, 2.50, 2.10)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
items <- paste0("panas_na_", 1:10)

cat("A. live response-frequency vector -> matching deposit column\n")
cat(sprintf("%-12s %-22s %-12s %-24s %s\n",
            "item", "live counts 1..5", "text shipped", "unique raw match", "claimed"))
ok_match <- TRUE
for (i in seq_along(items)) {
  v <- as.integer(table(factor(d$resp[d$item == items[i]], levels = 1:5)))
  hits <- names(RAW)[vapply(RAW, function(r) all(r == v), logical(1))]
  cat(sprintf("%-12s %-22s %-12s %-24s %s\n",
              items[i], paste(v, collapse = ","), TEXT[i],
              if (length(hits) == 1) hits else paste0("<", length(hits), " hits>"),
              CLAIM[i]))
  if (length(hits) != 1 || hits != CLAIM[i]) ok_match <- FALSE
}
cat(sprintf("all ten uniquely matched, in the claimed order: %s\n\n", ok_match))

cat("B. corroboration that deposit column number == ZIS/Krohne item position\n")
obs <- vapply(items, function(it) mean(d$resp[d$item == it]), numeric(1))
cat(sprintf("%-12s %-12s %10s %10s %10s\n", "item", "text", "zis242", "zis146", "live"))
for (i in seq_along(items))
  cat(sprintf("%-12s %-12s %10.2f %10.2f %10.2f\n",
              items[i], TEXT[i], ZIS242_MEAN[i], ZIS146_MEAN[i], obs[i]))
r242 <- cor(obs, ZIS242_MEAN); r146 <- cor(obs, ZIS146_MEAN)
p242 <- replicate(20000, cor(sample(obs), ZIS242_MEAN))
p146 <- replicate(20000, cor(sample(obs), ZIS146_MEAN))
cat(sprintf("Pearson r(live, zis242) = %.3f  (permutation percentile %.4f, 95th pct %.3f)\n",
            r242, mean(p242 < r242), quantile(p242, .95)))
cat(sprintf("Pearson r(live, zis146) = %.3f  (permutation percentile %.4f, 95th pct %.3f)\n\n",
            r146, mean(p146 < r146), quantile(p146, .95)))

cat("WHAT THIS DOES NOT ESTABLISH: part A pins live item <-> deposit column\n")
cat("exactly and leaves no permutation open, but the step from column NUMBER to\n")
cat("item WORDING is a numbering convention, not a statistic. It rests on the\n")
cat("deposit's PA/NA column labels reproducing the Krohne/ZIS subscale positions\n")
cat("20 of 20 (NA at 2,5,7,8,9,12,14,16,19,20; PA at 1,3,4,6,10,11,13,15,17,18)\n")
cat("plus part B's rank agreement against different samples; corroborated, not\n")
cat("proved. Part B cannot separate gereizt/irritable (published 1.96) from\n")
cat("nervoes/nervous (1.97), nor the live pair panas_na_6 2.6145 / panas_na_9\n")
cat("2.6145, which are exactly tied in mean and separated only by part A's full\n")
cat("frequency vectors and by the numbering convention.\n")

cat(if (ok_match && r242 > 0.7 && r146 > 0.7) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
