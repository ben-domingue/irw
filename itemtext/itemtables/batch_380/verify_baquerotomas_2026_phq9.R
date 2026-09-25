# verify_baquerotomas_2026_phq9.R -- Step 5b check for batch_380.
#
# Claim: source columns PHQ9_1..PHQ9_9 (kept verbatim as IRW item codes by
# data/baquerotomas_2026_emotion_regulation.py) are canonical PHQ-9 items 1..9
# in canonical order. The deposit's .sav variable labels are just "0 1 2 3" and
# no paper/supplement exists, so the suffix -> item tie is an order inference
# (mapping_basis=paper_order). No published per-item statistics exist, so this
# script tests structural predictions of the canonical order instead:
#   (a) marker: item 9 (suicidal ideation) has the lowest mean and highest floor %;
#   (b) somatic block: items 3 (sleep), 4 (fatigue), 5 (appetite) are the three
#       highest means -- the usual PHQ-9 pattern in student samples;
#   (c) PHQ-2 pair: item 1 (anhedonia)'s strongest correlate is item 2 (depressed mood);
#   (d) somatic coherence: item 3's strongest correlate lies in {4,5}.
# NOT established: order within {3,4,5}, or among items 6,7,8 -- this is PARTIAL.

suppressMessages(library(irw))
TABLE <- "baquerotomas_2026_phq9"
d <- irw::irw_fetch(TABLE)
its <- paste0("PHQ9_", 1:9)
mn <- tapply(d$resp, d$item, mean)[its]
fl <- tapply(d$resp == 0, d$item, mean)[its] * 100
cat(sprintf("%-7s %6s %7s\n", "item", "mean", "floor%"))
for (i in its) cat(sprintf("%-7s %6.2f %7.1f\n", i, mn[i], fl[i]))

w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
m <- as.matrix(w[, paste0("resp.", its)]); colnames(m) <- its
r <- cor(m, use = "pairwise.complete.obs"); diag(r) <- NA
top <- apply(r, 1, function(x) names(which.max(x)))
cat("\nstrongest correlate per item:\n")
for (i in its) cat(sprintf("  %-7s -> %-7s r=%.2f\n", i, top[i], max(r[i, ], na.rm = TRUE)))

a <- names(which.min(mn)) == "PHQ9_9" && names(which.max(fl)) == "PHQ9_9"
b <- setequal(names(sort(mn, decreasing = TRUE))[1:3], c("PHQ9_3", "PHQ9_4", "PHQ9_5"))
c_ <- top["PHQ9_1"] == "PHQ9_2"
d_ <- top["PHQ9_3"] %in% c("PHQ9_4", "PHQ9_5")
cat(sprintf("\n(a) item 9 lowest mean & highest floor: %s\n", a))
cat(sprintf("(b) top-3 means = {3,4,5}: %s (%s)\n", b,
            paste(names(sort(mn, decreasing = TRUE))[1:3], collapse = ",")))
cat(sprintf("(c) PHQ9_1 strongest correlate is PHQ9_2: %s\n", c_))
cat(sprintf("(d) PHQ9_3 strongest correlate in {4,5}: %s\n", d_))
cat("Does NOT separate order within {3,4,5} or among {6,7,8}.\n")
cat(if (a && b && c_ && d_) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
