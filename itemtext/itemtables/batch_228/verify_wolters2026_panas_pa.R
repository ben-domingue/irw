# verify_wolters2026_panas_pa.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: panas_pa_1..panas_pa_10 are the figshare deposit's columns
#   PANAS_PA_1, _3, _4, _6, _10, _11, _13, _15, _17, _18 (in that order), and
#   those column numbers are positions in the German PANAS of Krohne, Egloff,
#   Kohlmann & Tausch (1996) as documented in ZIS doi 10.6102/zis242, whose
#   Table 2 gives the English original for each position.
#
# The check that would break if any two item_texts were swapped: each live
# item's FULL 5-level response-frequency vector must match exactly one raw
# column of the deposit, and it must be the claimed one.

suppressMessages(library(irw))
TABLE <- "wolters2026_panas_pa"

# Raw per-column response counts (resp 1..5), computed from the deposit file
# "Wolters Pollklas - 2026 - Online health research fosters health concerns - Raw data.xlsx"
# (figshare 10.6084/m9.figshare.32044005.v1, sheet "DrGoogle-2022022  (2)", N = 83).
RAW <- list(
  PANAS_PA_1  = c(8, 12, 30, 27,  6),
  PANAS_PA_3  = c(2, 10, 30, 30, 11),
  PANAS_PA_4  = c(3, 23, 28, 22,  7),
  PANAS_PA_6  = c(16, 16, 31, 17,  3),
  PANAS_PA_10 = c(13, 23, 28, 17,  2),
  PANAS_PA_11 = c(11, 28, 22, 17,  5),
  PANAS_PA_13 = c(9, 29, 21, 19,  5),
  PANAS_PA_15 = c(6, 21, 26, 21,  9),
  PANAS_PA_17 = c(3, 17, 29, 27,  7),
  PANAS_PA_18 = c(1, 11, 33, 29,  9)
)
CLAIM <- names(RAW)                       # claimed source column per panas_pa_1..10
TEXT  <- c("active","interested","excited","strong","inspired",
           "proud","enthusiastic","alert","determined","attentive")
# ZIS 10.6102/zis242 Table 7: published means for the same German items,
# GESIS Panel n = 4,188 (positions 1,3,4,6,10,11,13,15,17,18).
ZIS_MEAN <- c(3.36, 3.77, 2.83, 3.00, 2.72, 2.73, 2.89, 3.31, 3.36, 3.67)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
items <- paste0("panas_pa_", 1:10)

cat("A. live response-frequency vector -> matching deposit column\n")
cat(sprintf("%-12s %-22s %-14s %-24s %s\n",
            "item", "live counts 1..5", "text shipped", "unique raw match", "claimed"))
ok_match <- TRUE
for (i in seq_along(items)) {
  v <- as.integer(table(factor(d$resp[d$item == items[i]], levels = 1:5)))
  hits <- names(RAW)[vapply(RAW, function(r) all(r == v), logical(1))]
  cat(sprintf("%-12s %-22s %-14s %-24s %s\n",
              items[i], paste(v, collapse = ","), TEXT[i],
              if (length(hits) == 1) hits else paste0("<", length(hits), " hits>"),
              CLAIM[i]))
  if (length(hits) != 1 || hits != CLAIM[i]) ok_match <- FALSE
}
cat(sprintf("all ten uniquely matched, in the claimed order: %s\n\n", ok_match))

cat("B. corroboration that deposit column number == ZIS/Krohne item position\n")
obs <- vapply(items, function(it) mean(d$resp[d$item == it]), numeric(1))
cat(sprintf("%-12s %-14s %10s %10s\n", "item", "text", "ZIS mean", "live mean"))
for (i in seq_along(items))
  cat(sprintf("%-12s %-14s %10.2f %10.2f\n", items[i], TEXT[i], ZIS_MEAN[i], obs[i]))
r <- cor(obs, ZIS_MEAN)
cat(sprintf("Pearson r(live PA means, ZIS published PA means) = %.3f\n", r))
perm <- replicate(20000, cor(sample(obs), ZIS_MEAN))
cat(sprintf("random-permutation r: mean %.3f, 95th pct %.3f -> observed percentile %.4f\n\n",
            mean(perm), quantile(perm, .95), mean(perm < r)))

cat("WHAT THIS DOES NOT ESTABLISH: part A pins live item <-> deposit column\n")
cat("exactly and leaves no permutation open, but the step from column NUMBER to\n")
cat("item WORDING is a numbering convention, not a statistic. It rests on the\n")
cat("deposit's PA/NA column labels reproducing the Krohne/ZIS subscale positions\n")
cat("20 of 20 (PA at 1,3,4,6,10,11,13,15,17,18) plus part B's rank agreement\n")
cat("against a different sample; it is corroborated, not proved. The two PA items\n")
cat("whose published means are nearly tied (angeregt 2.72 / stolz 2.73) are\n")
cat("separated by that convention, not by part B.\n")

cat(if (ok_match && r > 0.7) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
