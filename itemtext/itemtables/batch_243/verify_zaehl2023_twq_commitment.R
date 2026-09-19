# verify_zaehl2023_twq_commitment.R -- Step 5b check, batch_243.
#
# Claim: live item codes COMT1..COMT4r are the raw OSF CSV's own column headers
# (data/zaehl2023_hexaco_teamwork.py melts the columns BY NAME), and the study's
# questionnaire (OSF jb94w, HEXACO_TWQ_questionnaire.pdf, Table I) prints each
# item's German wording + English against that same ID. So the code<->text tie is
# a label match; what needs checking against numbers is that the live codes really
# are those source columns (not shuffled in processing) and which item is the
# reverse-worded one.
#
# Route A: per-item x resp counts, live vs the source CSV (osf.io/download/k4syv,
#          HEXACO_TWQ_raw-data.csv, counted 2026-09-18). Each item's distribution is
#          distinct, so a cell-for-cell match ties every live code to its own column.
# Route B: arXiv:2507.00481v2 reports the COMT facet mean as 3.47 (61.75%). It is
#          reproduced only if COMT4r (the "conflicts regarding ... effort" item) is
#          reverse-scored: reversed 3.477 vs raw 3.116. Pins COMT4r's polarity and
#          that the table stores it raw.
suppressMessages(library(irw))
TABLE <- "zaehl2023_twq_commitment"
SRC <- rbind(COMT1  = c( 1,  7, 20, 16, 10),
             COMT2  = c( 4, 14, 20, 14,  2),
             COMT3  = c( 1,  6, 13, 19, 15),
             COMT4r = c(19, 12, 15,  5,  3))
PUB_COMT_MEAN <- 3.47; TOL <- 0.01

d <- irw::irw_fetch(TABLE)
live <- as.matrix(table(factor(d$item, levels = rownames(SRC)), factor(d$resp, levels = 1:5)))
cat("Route A: item x resp counts (source CSV | live)\n")
for (i in rownames(SRC)) cat(sprintf("%-7s %-18s | %s\n", i, paste(SRC[i, ], collapse = " "), paste(live[i, ], collapse = " ")))
okA <- all(live == SRC)
# would any permutation of codes also match? (distinct rows => no)
distinct <- nrow(unique(SRC)) == nrow(SRC)
cat(sprintf("cells matching: %d/%d; source rows pairwise distinct: %s\n", sum(live == SRC), length(SRC), distinct))

w <- reshape(as.data.frame(d)[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
raw_mean <- mean(rowMeans(w[, rownames(SRC)]))
rev_mean <- mean(rowMeans(cbind(w[, c("COMT1","COMT2","COMT3")], 6 - w$COMT4r)))
cat(sprintf("\nRoute B: published COMT mean %.2f; live raw %.3f; live with COMT4r reversed %.3f\n", PUB_COMT_MEAN, raw_mean, rev_mean))
okB <- abs(rev_mean - PUB_COMT_MEAN) <= TOL && abs(raw_mean - PUB_COMT_MEAN) > 0.1
cat("Note: Route B pins only COMT4r (polarity); items 1-3 are separated by Route A plus the\n",
    "questionnaire's own ID column, not by any published per-item statistic (none exists).\n", sep = "")
cat(if (okA && distinct && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
