# verify_zaehl2023_twq_support.R -- Step 5b check, batch_244.
#
# Claim: live item codes SPRT1..SPRT6 are the raw OSF CSV's own column headers
# (data/zaehl2023_hexaco_teamwork.py melts the columns BY NAME), and the study's
# questionnaire (OSF jb94w, HEXACO_TWQ_questionnaire.pdf, Table I) prints each
# item's German wording + English against that same ID. So the code<->text tie is
# a label match; what the numbers check is that the live codes really are those
# source columns (not shuffled in processing) and that the facet is stored raw.
#
# Route A: per-item x resp counts, live vs the source CSV (osf.io/download/k4syv,
#          HEXACO_TWQ_raw-data.csv, sha256 e471e58d..., counted 2026-09-18). The six
#          distributions are pairwise distinct, so a cell-for-cell match ties every
#          live code to its own source column; no permutation of codes also matches.
# Route B: arXiv:2507.00481v2 reports the SPRT facet mean as 3.98 (74.5 %) and
#          alpha_SPRT = 0.92. The paper truncates to 2 dp (CMNC 3.719 -> 3.71,
#          CRDN 3.639 -> 3.63), so live 3.9846 -> 3.98. All six items are
#          positively worded (no 'r' suffix) and the facet mean reproduces from raw
#          values, confirming no item is stored reversed. Pins facet membership and
#          storage direction only, not order within the facet.
suppressMessages(library(irw))
TABLE <- "zaehl2023_twq_support"
SRC <- rbind(SPRT1 = c(2, 5,  6, 19, 22),
             SPRT2 = c(2, 3, 16, 19, 14),
             SPRT3 = c(3, 0, 13, 15, 23),
             SPRT4 = c(2, 1,  8, 15, 28),
             SPRT5 = c(2, 3,  9, 20, 20),
             SPRT6 = c(4, 1,  8, 22, 19))
PUB_MEAN <- 3.98; PUB_ALPHA <- 0.92

d <- irw::irw_fetch(TABLE)
live <- as.matrix(table(factor(d$item, levels = rownames(SRC)), factor(d$resp, levels = 1:5)))
cat("Route A: item x resp counts (source CSV | live)\n")
for (i in rownames(SRC)) cat(sprintf("%-6s %-16s | %s\n", i, paste(SRC[i, ], collapse = " "), paste(live[i, ], collapse = " ")))
okA <- all(live == SRC)
distinct <- nrow(unique(SRC)) == nrow(SRC)
cat(sprintf("cells matching: %d/%d; source rows pairwise distinct: %s\n", sum(live == SRC), length(SRC), distinct))

w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
x <- w[, rownames(SRC)]
m <- mean(rowMeans(x)); k <- ncol(x)
a <- k / (k - 1) * (1 - sum(apply(x, 2, var)) / var(rowSums(x)))
cat(sprintf("\nRoute B: published SPRT mean %.2f (truncated); live raw %.4f -> %.2f truncated\n", PUB_MEAN, m, floor(m * 100) / 100))
cat(sprintf("         published alpha %.2f; live alpha %.3f\n", PUB_ALPHA, a))
okB <- abs(floor(m * 100) / 100 - PUB_MEAN) < 1e-9 && abs(round(a, 2) - PUB_ALPHA) < 1e-9
cat("Note: Route B pins facet membership/storage direction only; order among SPRT1-6 rests on\n",
    "Route A plus the questionnaire's own ID column (a label match), not on any published\n",
    "per-item statistic (none exists).\n", sep = "")
cat(if (okA && distinct && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
