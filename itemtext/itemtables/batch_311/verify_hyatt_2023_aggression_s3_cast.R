# verify_hyatt_2023_aggression_s3_cast.R -- batch_311
# Item axis: item codes ARE the Study 3 .sav column names lowercased (data/hyatt_2023_aggression.py
# _norm_item), and item_text is each column's SPSS variable label. This checks that each live item
# reproduces its source column's response-frequency profile cell for cell (hard-coded below from
# OSF fuz6h "Study 3 Data + Syntax/AEQ_Study 3.sav", downloaded 2026-09-23), so a label attached to
# the wrong code would show up as a profile mismatch.
# Resp axis: the two r-suffixed items (cast_6vr, cast_16vir) ship REVERSED anchors (resp 1 =
# "strongly agree"). That rests on their being stored already reverse-scored: their mean
# correlation with their own subscale's other items must be POSITIVE (raw "I would never purposely
# humiliate someone" would correlate negatively with verbal sadism).
suppressMessages(library(irw))
TABLE <- "hyatt_2023_aggression_s3_cast"
SAV <- list(  # counts at resp 1..7 in the .sav
  cast_1v=c(197,47,37,23,19,8,7), cast_2v=c(185,67,38,30,16,2,1), cast_3v=c(192,44,32,33,22,11,5),
  cast_4v=c(239,40,27,17,8,7,2), cast_5v=c(215,51,31,22,12,5,3), cast_6vr=c(141,46,19,12,24,30,68),
  cast_7p=c(297,24,9,7,2,0,0),   # .sav also holds 1 response stored as code 8 (label "6"); absent live
  cast_8p=c(286,33,7,10,2,1,0), cast_9p=c(266,41,9,13,8,2,0), cast_10p=c(251,34,13,23,12,3,3),
  cast_11p=c(243,40,18,21,11,3,3), cast_12vi=c(196,47,24,29,20,12,11), cast_13vi=c(231,39,20,15,20,10,4),
  cast_14vi=c(253,35,13,18,8,4,8), cast_15vi=c(256,34,9,21,5,5,8), cast_16vir=c(11,17,36,75,49,56,95),
  cast_17vi=c(225,44,19,23,16,8,4), cast_18vi=c(269,30,14,14,8,3,1))
d <- irw::irw_fetch(TABLE)
ok <- TRUE
cat("Item axis: live vs .sav frequency profile (resp 1..7)\n")
for (it in names(SAV)) {
  live <- as.integer(table(factor(d$resp[d$item == it], levels = 1:7)))
  m <- identical(live, as.integer(SAV[[it]]))
  cat(sprintf("%-11s live %-28s sav %-28s %s\n", it, paste(live, collapse = "/"),
              paste(SAV[[it]], collapse = "/"), if (m) "match" else "MISMATCH"))
  ok <- ok && m
}
prof <- sapply(SAV, paste, collapse = "/")
cat(sprintf("distinct .sav profiles: %d of %d (a swap of any two items would break a match)\n",
            length(unique(prof)), length(prof)))
ok <- ok && length(unique(prof)) == length(prof)

w <- reshape(as.data.frame(d[, c("id", "wave", "item", "resp")]), idvar = c("id", "wave"),
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
r <- cor(w[, names(SAV)], use = "pairwise")
verbal <- c("cast_1v","cast_2v","cast_3v","cast_4v","cast_5v")
vicar  <- c("cast_12vi","cast_13vi","cast_14vi","cast_15vi","cast_17vi","cast_18vi")
m6  <- mean(r["cast_6vr", verbal]); m16 <- mean(r["cast_16vir", vicar])
cat(sprintf("\nResp axis: mean r(cast_6vr, other verbal items) = %+.3f\n", m6))
cat(sprintf("           mean r(cast_16vir, other vicarious items) = %+.3f\n", m16))
cat("Positive => stored already reverse-scored => resp 1 = 'strongly agree' for these two items.\n")
ok <- ok && m6 > 0 && m16 > 0
cat("Does NOT establish: the correlation for cast_16vir is weak (mean +0.06; +0.11 to +0.14 with 12vi-14vi); the decisive\n",
    "evidence is that the .sav's own VerbSadism/VicariousSadism composites equal the mean of the\n",
    "STORED items for 338/340 and 338/339 respondents (flipped: 12 and 74), checked at extraction.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
