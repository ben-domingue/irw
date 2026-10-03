# verify_saha_2026_cesd.R -- Step 5b, route 9 (response-frequency matching), both axes.
#
# Claim: live item Qn is the deposit raw_dataset.xlsx column "Q-n <question>", and
# live resp maps to the raw Google-Form labels as
#   Rarely..=0, Some..=1, Occasionally..=2, Most..=3   for every item except
#   Q4, Q8, Q12, Q16 (positively worded), where it is REVERSED (Most..=0 .. Rarely..=3).
#
# The Mendeley deposit (10.17632/c5gpdtj8jv) was removed "As per author's request"
# (HTTP 451) after IRW fetched it, so the raw labels cannot be re-downloaded. The
# counts below were tallied on 2026-09-25 from the copy fetched 2026-08-27
# (raw_dataset.xlsx sha256 cd1b8320630efb52f15b257c784c6d422a32041b6d35faafc45c87f10471aad6),
# restricted to the 892 raw rows that survive into final_preprocessed_dataset.xlsx
# (all 892 matched as an in-order subsequence, whole 20-item rows equal). Columns are
# raw label counts in the order Rarely, Some, Occasionally, Most -- NOT resp order.
suppressMessages(library(irw))
TABLE <- "saha_2026_cesd"
RAW <- rbind(
  Q1=c(307,381,124,80),  Q2=c(316,310,160,106), Q3=c(357,250,132,153), Q4=c(209,221,200,262),
  Q5=c(154,270,225,243), Q6=c(192,307,199,194), Q7=c(221,302,194,175), Q8=c(145,218,217,312),
  Q9=c(359,230,132,171), Q10=c(268,300,156,168), Q11=c(206,235,232,219), Q12=c(169,338,241,144),
  Q13=c(271,247,175,199), Q14=c(268,237,168,219), Q15=c(303,284,182,123), Q16=c(231,265,210,186),
  Q17=c(346,238,136,172), Q18=c(219,291,197,185), Q19=c(307,303,139,143), Q20=c(249,304,150,189))
REV <- c("Q4","Q8","Q12","Q16")
# expected live resp 0..3 counts under the claimed mapping
EXP <- RAW; EXP[REV, ] <- RAW[REV, 4:1]

d <- irw::irw_fetch(TABLE)
items <- paste0("Q", 1:20)
OBS <- t(sapply(items, function(i) sapply(0:3, function(v) sum(d$resp[d$item == i] == v))))

cat(sprintf("%-4s %-22s %-22s %s\n", "item", "expected resp0..3", "live resp0..3", "match"))
ok <- logical(20)
for (k in seq_along(items)) {
  ok[k] <- all(OBS[k, ] == EXP[k, ])
  cat(sprintf("%-4s %-22s %-22s %s\n", items[k], paste(EXP[k, ], collapse="/"),
              paste(OBS[k, ], collapse="/"), ok[k]))
}
# How discriminating is this? Count cross-item matches (any other item's expected vector
# equal to this item's live vector) and the unreversed alternative for the four REV items.
cross <- sum(sapply(1:20, function(a) sum(sapply(setdiff(1:20, a), function(b) all(OBS[a, ] == EXP[b, ])))))
unrev <- sum(sapply(REV, function(i) all(OBS[i, ] == RAW[i, ])))
cat(sprintf("\nitems matching cell-for-cell: %d/20\n", sum(ok)))
cat(sprintf("cross-item matches (would hide a swap): %d; REV items that also match unreversed: %d\n", cross, unrev))
cat("Not established by this script: the raw->live ROW alignment itself (done offline on the\n",
    "cached xlsx: 892/892 rows equal on all 20 items, best off-diagonal column agreement 483/892).\n", sep="")
cat(if (all(ok) && cross == 0 && unrev == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
