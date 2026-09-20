# verify_mekheimer_2026_id.R -- Step 5b evidence, re-runnable.
#
# Claim under test: the wording shipped for ID_1..ID_10 is Appendix 4's Identity
# Dissonance Scale, taken in appendix order (Section 1 items 1-5 -> ID_1..ID_5,
# Section 2 items 1-5 -> ID_6..ID_10).
#
# What this script CAN check, with numbers:
#   (A) that the live IRW codes ID_1..ID_10 are literally the deposit
#       spreadsheet's own ID_* columns (per-item n and mean reproduce exactly),
#       i.e. code derivation is pattern 1 -- the code IS the source column name;
#   (B) that the two candidate discriminating routes for the wording->code axis
#       both fail to discriminate, which is why the recorded status is NO_ROUTE.
#
# It CANNOT establish which appendix sentence belongs to which code. Nothing can:
# the appendix prints no item codes, the study publishes no per-item statistics,
# all ten items share one 1-7 agreement-style range and one polarity, and the
# subscale-block test below is non-identifying in these data.

suppressMessages(library(irw))
TABLE <- "mekheimer_2026_id"
ITEMS <- paste0("ID_", 1:10)

# Deposit: Additional file 7 of 10.1186/s40862-025-00378-1
# (figshare 31387864, 40862_2025_378_MOESM7_ESM.xlsx, sheet "survey_data (1)"),
# columns ID_1..ID_10, n = 160 complete for every column.
DEP_N    <- rep(160, 10)
DEP_MEAN <- c(4.58125, 4.00000, 3.53750, 4.13750, 4.06250,
              3.88125, 4.31250, 3.78125, 4.34375, 4.02500)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs_n    <- as.integer(table(factor(d$item, levels = ITEMS)))
obs_mean <- as.numeric(tapply(d$resp, factor(d$item, levels = ITEMS), mean))

cat("(A) live IRW table vs deposit spreadsheet columns\n")
cat(sprintf("%-6s %8s %8s %12s %12s %10s\n",
            "item", "dep n", "live n", "dep mean", "live mean", "diff"))
for (i in seq_along(ITEMS))
  cat(sprintf("%-6s %8d %8d %12.5f %12.5f %10.2e\n",
              ITEMS[i], DEP_N[i], obs_n[i], DEP_MEAN[i], obs_mean[i],
              obs_mean[i] - DEP_MEAN[i]))
ok_n    <- identical(obs_n, as.integer(DEP_N))
worst   <- max(abs(obs_mean - DEP_MEAN))
cat(sprintf("n identical: %s ; largest mean deviation: %.2e\n\n", ok_n, worst))

# (B1) Subscale-block test (Step 5b route 5). If ID_1..ID_5 are Section 1
# (Internal Dissonance) and ID_6..ID_10 are Section 2 (Environmental), the
# within-block correlations should exceed the between-block ones.
dd <- as.data.frame(d[, c("id", "item", "resp")])
w <- reshape(dd, idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, paste0("resp.", ITEMS)])
cm <- cor(m, use = "pairwise.complete.obs")
off <- function(idx) mean(cm[idx, idx][upper.tri(diag(length(idx)))])
w1 <- off(1:5); w2 <- off(6:10); btw <- mean(cm[1:5, 6:10])
cat("(B1) subscale-block structure (route 5)\n")
cat(sprintf("  mean r within ID_1-5 = %.4f ; within ID_6-10 = %.4f ; between = %.4f\n",
            w1, w2, btw))
cat("  Non-identifying: the between-block mean EXCEEDS the ID_1-5 within-block mean,\n")
cat("  so the data carry no two-block signature to match the appendix's two sections.\n\n")

# (B2) Published subscale totals (route 3). Additional file 3 (SPSS t-test
# output) reports Section 1 Internal Dissonance and Section 2 Environmental
# Dissonance sum-score means -- but on N = 496, a different sample from the
# N = 160 deposit, and the two live block sums are indistinguishable anyway.
PUB_S1 <- (242 * 17.09504132231405 + 254 * 16.62992125984252) / 496
PUB_S2 <- (242 * 18.363636363636363 + 254 * 18.318897637795274) / 496
s1 <- mean(rowSums(m[, 1:5])); s2 <- mean(rowSums(m[, 6:10]))
cat("(B2) published section sum-score means (route 3)\n")
cat(sprintf("  published (Additional file 3, N=496): S1 %.3f  S2 %.3f\n", PUB_S1, PUB_S2))
cat(sprintf("  live (N=160):  sum(ID_1-5) %.3f   sum(ID_6-10) %.3f\n", s1, s2))
cat(sprintf("  |live S1 - pub S1| = %.3f vs |live S1 - pub S2| = %.3f ; the two live block\n",
            abs(s1 - PUB_S1), abs(s1 - PUB_S2)))
cat(sprintf("  sums differ from each other by only %.3f, so this cannot assign a block either.\n\n",
            abs(s1 - s2)))

cat("A PASS below covers claim (A) only -- the code<->deposit-column tie. The\n")
cat("wording->code axis is recorded NO_ROUTE, not verified.\n")
cat("VERDICT: ", if (ok_n && worst < 1e-6) "PASS" else "FAIL", "\n", sep = "")
