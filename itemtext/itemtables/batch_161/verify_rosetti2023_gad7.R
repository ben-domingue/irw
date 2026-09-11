# verify_rosetti2023_gad7.R -- Step 5b, re-runnable mapping evidence.
#
# CLAIM UNDER TEST: GAD7_q1..GAD7_q7 carry the canonical GAD-7 items 1..7, and
# resp 0..3 runs "Not at all" -> "Nearly every day" (not the reverse).
# Nothing in the deposit or the (paywalled) paper labels the columns, so the
# claim rests on the canonical numbering; this script tests the falsifiable
# consequences of that numbering in the response data itself.
#
# Three predictions, each of which would break if the mapping were permuted:
#   P1 item 6 ("Becoming easily annoyed or irritable") is the content outlier of
#      the GAD-7 -- irritability, not worry or tension -- so it must have the
#      LOWEST mean inter-item correlation of the seven.
#   P2 item 5 ("Being so restless that it is hard to sit still") is the somatic
#      twin of item 4 ("Trouble relaxing"), so q4 must be q5's single strongest
#      correlate.
#   P3 direction: women score higher than men on the GAD-7 (one of the most
#      replicated findings in anxiety epidemiology), so cov_gender Female must
#      exceed Male on the RAW 0-3 sum. A flipped coding reverses the sign.
#
# NOT tested here, and stated in the verification row as PARTIAL: q1, q2, q3, q4
# and q7 are not distinguished from one another by any of these routes.

suppressMessages(library(irw))

TABLE <- "rosetti2023_gad7"
d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)

items <- paste0("GAD7_q", 1:7)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", items)]
cm <- cor(w[, items], use = "pairwise.complete.obs")

cat("=== per-item mean and mean inter-item r (P1: q6 lowest) ===\n")
mr <- sapply(items, function(i) mean(cm[i, setdiff(items, i)]))
mn <- sapply(items, function(i) mean(w[[i]], na.rm = TRUE))
for (i in items) cat(sprintf("%-8s mean %.3f   mean r %.3f\n", i, mn[i], mr[i]))
p1 <- names(which.min(mr)) == "GAD7_q6"
cat(sprintf("P1: lowest mean r is %s (%.3f); next lowest %.3f -> %s\n",
            names(which.min(mr)), min(mr), sort(mr)[2], ifelse(p1, "PASS", "FAIL")))

cat("\n=== P2: q5's strongest correlate should be q4 ===\n")
r5 <- sort(cm["GAD7_q5", setdiff(items, "GAD7_q5")], decreasing = TRUE)
print(round(r5, 3))
p2 <- names(r5)[1] == "GAD7_q4"
cat(sprintf("P2: top correlate of q5 is %s (%.3f) -> %s\n",
            names(r5)[1], r5[1], ifelse(p2, "PASS", "FAIL")))

cat("\n=== P3: scale direction, raw 0-3 sum by cov_gender ===\n")
w2 <- merge(w, unique(d[, c("id", "cov_gender")]), by = "id")
w2$total <- rowSums(w2[, items])
agg <- aggregate(total ~ cov_gender, w2, function(x) c(mean(mean(x)), length(x)))
print(agg)
fm <- mean(w2$total[w2$cov_gender == "Female"])
ml <- mean(w2$total[w2$cov_gender == "Male"])
p3 <- fm > ml
cat(sprintf("P3: Female %.2f vs Male %.2f (flipped coding would read %.2f vs %.2f) -> %s\n",
            fm, ml, 21 - fm, 21 - ml, ifelse(p3, "PASS", "FAIL")))

cat("\nNOTE: these routes pin GAD7_q6 (irritability), GAD7_q5 (restlessness, via its\n",
    "tie to GAD7_q4) and the 0->3 direction. They do NOT separate GAD7_q1, GAD7_q2,\n",
    "GAD7_q3, GAD7_q4 and GAD7_q7 from one another -- a permutation among those five\n",
    "would survive this script. Hence the recorded status is PARTIAL, not VERIFIED.\n", sep = "")

cat(if (p1 && p2 && p3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
