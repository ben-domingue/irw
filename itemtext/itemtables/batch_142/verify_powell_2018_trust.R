# verify_powell_2018_trust.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the one stem this table ships, on item `Trust1`
# ("In general, you can trust staff/students at the host university" -- the only
# adapted item wording Powell et al. 2018 print, PLOS ONE 10.1371/journal.pone.0194569),
# belongs on a POSITIVELY keyed item. Trust2 and Trust3 ship no stem, because the
# paper and all five of its supplements print none.
#
# ROUTE 6 (keying polarity). The adapted SOEP-Trust scale's canonical parent
# (Naef & Schupp 2009, IZA DP 4087) has two negatively worded statements of three;
# this administration has exactly one. Which one is a testable prediction:
#   - the S1 Dataset carries rTrust3 (and no rTrust1/rTrust2) as its only recoded
#     trust column, i.e. the authors reverse-scored item 3 and only item 3;
#   - so in the live (raw) table Trust3 must correlate NEGATIVELY with Trust1 and
#     Trust2, and Trust1 with Trust2 POSITIVELY.
# If the shipped stem had been placed on the reverse-worded item, the sign attached
# to it would flip. That is what this script would catch.
#
# WHAT IT DOES NOT ESTABLISH: Trust1 and Trust2 are both positively keyed, so
# polarity cannot separate them. The stem's placement on Trust1 rather than Trust2
# rests on presentation order (canonical SOEP-trust lists "In general, you can trust
# people" first), which no statistic here tests. Hence status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "powell_2018_trust"
STEM_ITEM <- "Trust1"          # the item carrying the shipped stem
REVERSED  <- "Trust3"          # the only item the source file reverse-scores

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("Trust1", "Trust2", "Trust3")]
w <- w[complete.cases(w), ]

R <- cor(w)
cat(sprintf("n complete respondents: %d\n\n", nrow(w)))
cat("Pearson correlations among the three live trust items:\n")
print(round(R, 3))

cat(sprintf("\nr(Trust1,Trust2) = %+0.3f   (both positively keyed -> expect > 0)\n", R["Trust1","Trust2"]))
cat(sprintf("r(Trust1,Trust3) = %+0.3f   (Trust3 reverse worded  -> expect < 0)\n", R["Trust1","Trust3"]))
cat(sprintf("r(Trust2,Trust3) = %+0.3f   (Trust3 reverse worded  -> expect < 0)\n", R["Trust2","Trust3"]))

# Item-rest correlation with the scale scored the way the authors scored it
# (TrustScore = Trust1 + Trust2 + (5 - Trust3), which reproduces the S1 file's
# TrustScore for 523/523 respondents).
key <- c(Trust1 = 1, Trust2 = 1, Trust3 = -1)
scored <- sweep(w, 2, key, "*")
scored[, "Trust3"] <- 5 + scored[, "Trust3"]
irc <- sapply(names(key), function(v) cor(scored[[v]], rowSums(scored[, setdiff(names(key), v)])))
cat("\nitem-rest correlations under the authors' own scoring key (+,+,-):\n")
print(round(irc, 3))

ok <- R["Trust1","Trust2"] > 0.30 &&
      R["Trust1","Trust3"] < -0.20 &&
      R["Trust2","Trust3"] < -0.20 &&
      all(irc > 0.30)

cat("\nNOT established by this route: Trust1 vs Trust2 are both positive, so the\n",
    "shipped stem's placement on Trust1 rather than Trust2 is presentation order,\n",
    "not evidence. Trust2/Trust3 ship no stem at all.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
