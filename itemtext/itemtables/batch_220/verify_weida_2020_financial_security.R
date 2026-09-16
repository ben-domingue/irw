# verify_weida_2020_financial_security.R
#
# CLAIM UNDER TEST: the ten live item codes secf_1m..secf_10m are the ten items
# of the CES-D-10 (Andresen et al. 1994) IN THAT ORDER, stored in the DEPRESSIVE
# direction (i.e. the two positive-affect items, positions 5 "I felt hopeful
# about the future" and 8 "I was happy", are already reverse scored), and the
# four frequency anchors therefore ship reversed for those two items only.
#
# The table is NAMED weida_2020_financial_security but its items are the study's
# depression measure, not its financial-health measure -- see notes_*.csv.
#
# Routes (SKILL.md Step 5b):
#   3 -- published/derived totals: the sum of the ten items as stored must
#        reproduce the S1 file's own CES-D-10 score `dpsscore` and the paper's
#        stated 0-30 range and >=10 cutoff.
#   6/5 -- keying polarity / residual block structure: after removing the
#        general factor, the positive-affect PAIR must stand out as the single
#        strongest residual pair among all 45 pairs.
#   8 -- semantic coherence of the endorsement ordering.
#
# NOT established: the order among the eight negatively worded items. A
# permutation within {1,2,3,6,7,9,10} would leave every number below unchanged.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "weida_2020_financial_security"
ITEMS <- paste0("secf_", 1:10, "m")

# Values computed from the study's own S1 SAS file (PLOS ONE 10.1371/journal.pone.0233359.s001):
# dpsscore = rowSums of secf_1m..secf_10m, dps = (dpsscore >= 10).
S1_TOTAL_MEAN <- 11.404
S1_TOTAL_SD   <- 6.199
S1_PCT_GE10   <- 0.5633   # == mean(dps) in the S1 file, 209/371
# Paper: "The range of the 10-item scale is 0 to 30 and the recommended cutoff
# score of >=10 was used to indicate presence of depressive symptoms."
PAPER_MIN <- 0; PAPER_MAX <- 30

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
X <- w[, ITEMS]
X <- X[complete.cases(X), ]

ok <- TRUE

## ---- Route 3: totals ------------------------------------------------------
tot <- rowSums(X)
cat("== Route 3: CES-D-10 total from the live items, as stored ==\n")
cat(sprintf("  n complete        : %d\n", nrow(X)))
cat(sprintf("  mean   live %7.3f   S1 dpsscore %7.3f   diff %6.3f\n",
            mean(tot), S1_TOTAL_MEAN, mean(tot) - S1_TOTAL_MEAN))
cat(sprintf("  sd     live %7.3f   S1 dpsscore %7.3f   diff %6.3f\n",
            sd(tot), S1_TOTAL_SD, sd(tot) - S1_TOTAL_SD))
cat(sprintf("  range  live %g-%g      paper %g-%g\n",
            min(tot), max(tot), PAPER_MIN, PAPER_MAX))
cat(sprintf("  %% >= 10 live %6.4f   S1 dps %6.4f   diff %6.4f\n",
            mean(tot >= 10), S1_PCT_GE10, mean(tot >= 10) - S1_PCT_GE10))
r3 <- abs(mean(tot) - S1_TOTAL_MEAN) < 0.01 &&
      abs(sd(tot)   - S1_TOTAL_SD)   < 0.01 &&
      abs(mean(tot >= 10) - S1_PCT_GE10) < 0.001 &&
      min(tot) == PAPER_MIN && max(tot) == PAPER_MAX
cat("  -> ", if (r3) "PASS" else "FAIL",
    " (a raw, un-reversed storage of items 5/8 could not sum to this score)\n\n", sep = "")
ok <- ok && r3

## ---- Route 6: polarity, stored direction ----------------------------------
# NOTE, stated up front because it is a real anomaly and not a tuned threshold:
# secf_4m is detached from this scale in this sample (item-rest r = 0.07, against
# 0.27-0.73 for the other nine), and it is the ONLY item the two positive-affect
# items correlate negatively with. The direction test below is therefore run
# against the other seven negatively worded items, and secf_4m is printed
# separately rather than dropped quietly.
cat("== Route 6: are secf_5m / secf_8m stored in the depressive direction? ==\n")
others <- setdiff(ITEMS, c("secf_5m", "secf_8m", "secf_4m"))
tot_all <- rowSums(X)
cat("  item-rest correlations:\n")
for (i in ITEMS)
    cat(sprintf("    %-9s %+.3f%s\n", i, cor(X[[i]], tot_all - X[[i]]),
                if (i == "secf_4m") "   <- detached from the scale" else ""))
for (p in c("secf_5m", "secf_8m")) {
    rr <- sapply(others, function(o) cor(X[[p]], X[[o]]))
    cat(sprintf("  %-9s r with the 7 other negatively worded items: %+.2f .. %+.2f (all %s); with secf_4m: %+.2f\n",
                p, min(rr), max(rr), if (all(rr > 0)) "positive" else "NOT all positive",
                cor(X[[p]], X[["secf_4m"]])))
}
r6 <- all(sapply(c("secf_5m", "secf_8m"),
                 function(p) all(sapply(others, function(o) cor(X[[p]], X[[o]])) > 0)))
cat("  -> ", if (r6) "PASS" else "FAIL",
    " (raw positive-affect items would correlate NEGATIVELY with these)\n\n", sep = "")
ok <- ok && r6

## ---- Route 5: residual block structure pins WHICH two are positive affect --
cat("== Route 5: strongest residual pair among all 45 pairs ==\n")
g <- rowMeans(X)
R <- as.data.frame(lapply(X, function(c) resid(lm(c ~ g))))
C <- cor(R)
pr <- do.call(rbind, lapply(1:9, function(i) do.call(rbind, lapply((i + 1):10, function(j)
        data.frame(a = ITEMS[i], b = ITEMS[j], r = C[i, j], stringsAsFactors = FALSE)))))
pr <- pr[order(-pr$r), ]
for (k in 1:4) cat(sprintf("  %d. %-9s %-9s  r = %+.3f\n", k, pr$a[k], pr$b[k], pr$r[k]))
top_is_pair <- setequal(c(pr$a[1], pr$b[1]), c("secf_5m", "secf_8m"))
ratio <- pr$r[1] / pr$r[2]
cat(sprintf("  top pair is {secf_5m, secf_8m}: %s; margin over runner-up: %.1fx\n",
            top_is_pair, ratio))
r5 <- top_is_pair && ratio > 2
cat("  -> ", if (r5) "PASS" else "FAIL",
    " (the CES-D's positive-affect method factor sits on exactly the two items\n",
    "     the CES-D-10 puts at positions 5 and 8)\n\n", sep = "")
ok <- ok && r5

## ---- Route 8: endorsement ordering ----------------------------------------
cat("== Route 8: item means, most- and least-endorsed ==\n")
m <- sort(sapply(X, mean), decreasing = TRUE)
for (i in seq_along(m)) cat(sprintf("  %-9s %.3f\n", names(m)[i], m[i]))
r8 <- names(m)[1] == "secf_4m" && names(m)[length(m)] == "secf_6m"
cat(sprintf("  highest = %s (shipped \"everything I did was an effort\"),",
            names(m)[1]))
cat(sprintf(" lowest = %s (shipped \"I felt fearful\")\n", names(m)[length(m)]))
cat("  -> ", if (r8) "PASS" else "FAIL",
    " (the CES-D's canonical endorsement pattern: effort/restless sleep top,\n",
    "     fearful bottom; corroborative only, it orders nothing else)\n\n", sep = "")
ok <- ok && r8

cat("Caveat: secf_4m's item-rest correlation of 0.07 means position 4 rests on the\n",
    "canonical CES-D-10 order and on its being the most-endorsed item, not on any\n",
    "correlational signal -- the \"everything I did was an effort\" item is the CES-D's\n",
    "known weak item, but this is weaker support than the other nine positions carry.\n\n", sep = "")

cat("Note: none of the routes above separates the eight negatively worded items\n",
    "from one another. A permutation within {secf_1m,2m,3m,6m,7m,9m,10m} would\n",
    "reproduce every number printed here, which is why the recorded status is\n",
    "PARTIAL rather than VERIFIED.\n\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
