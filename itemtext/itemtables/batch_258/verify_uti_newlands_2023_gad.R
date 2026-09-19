# verify_uti_newlands_2023_gad.R -- Step 5b check for batch_258.
#
# Claim: gad_1..gad_7 are GAD-7 items 1..7 in the instrument's printed order (codes come from
# the OSF raw file's gad1_k/gad2_k columns, number-preserving rename by data/uti_newlands_2023.py;
# neither the deposit codebook nor the paper prints GAD wording), and resp 1..4 = the GAD-7's
# printed 0..3 (Not at all .. Nearly every day), shifted by +1.
#
# Checks (all on the baseline wave, the N=240 sample the paper describes):
#  A. OPTION AXIS: total = sum(resp) - 7 reproduces Online Resource 11's GAD-7 M=9.23, SD=6.21,
#     range 0-21. The reversed coding (4 = Not at all) would give M = 21 - 9.23 = 11.77.
#  B. Marker: gad_5 ("so restless that it is hard to sit still") is the least-endorsed item.
#  C. Cross-instrument: gad_5 is the GAD item most correlated with PHQ-9 item 8
#     (psychomotor slowing / "fidgety or restless"), and phq_8 is gad_5's strongest PHQ correlate.
#  D. gad_4 ("Trouble relaxing") is the GAD item most correlated with PHQ-9 items 3 (sleep)
#     and 4 (tired / little energy).
# NOT established: the order among gad_1/gad_2/gad_3/gad_6/gad_7 -- no route here separates
# those five from one another (the paper publishes no per-item GAD statistics).
suppressMessages(library(irw))
g <- irw::irw_fetch("uti_newlands_2023_gad")
p <- irw::irw_fetch("uti_newlands_2023_phq")
g <- g[g$wave == 1, ]; p <- p[p$wave == 1, ]
gw <- reshape(as.data.frame(g[, c("id","item","resp")]), idvar="id", timevar="item", direction="wide")
pw <- reshape(as.data.frame(p[, c("id","item","resp")]), idvar="id", timevar="item", direction="wide")
names(gw) <- sub("resp.", "", names(gw)); names(pw) <- sub("resp.", "", names(pw))
gi <- paste0("gad_", 1:7); pi <- paste0("phq_", 1:9)
ok <- TRUE

tot <- rowSums(gw[, gi]) - 7
cat(sprintf("A. n=%d  total M=%.2f SD=%.2f range %d-%d  (published 240, 9.23, 6.21, 0-21; reversed coding would give M=%.2f)\n",
            sum(!is.na(tot)), mean(tot, na.rm=TRUE), sd(tot, na.rm=TRUE), min(tot, na.rm=TRUE), max(tot, na.rm=TRUE),
            21 - mean(tot, na.rm=TRUE)))
ok <- ok && abs(mean(tot, na.rm=TRUE) - 9.23) < 0.01 && abs(sd(tot, na.rm=TRUE) - 6.21) < 0.01

mu <- colMeans(gw[, gi], na.rm=TRUE)
cat("B. item means:", paste(sprintf("%s=%.3f", gi, mu), collapse="  "), "\n")
ok <- ok && names(which.min(mu)) == "gad_5"

m <- merge(gw, pw, by="id")
cc <- cor(m[, gi], m[, pi], use="pairwise")
cat("C/D. GAD x PHQ correlations (baseline):\n"); print(round(cc, 3))
cat(sprintf("C. cor(gad_*, phq_8): max at %s (%.3f); gad_5's max PHQ correlate: %s (%.3f)\n",
            gi[which.max(cc[, "phq_8"])], max(cc[, "phq_8"]), pi[which.max(cc["gad_5", ])], max(cc["gad_5", ])))
ok <- ok && gi[which.max(cc[, "phq_8"])] == "gad_5" && pi[which.max(cc["gad_5", ])] == "phq_8"
cat(sprintf("D. max GAD correlate of phq_3: %s (%.3f); of phq_4: %s (%.3f)\n",
            gi[which.max(cc[, "phq_3"])], max(cc[, "phq_3"]), gi[which.max(cc[, "phq_4"])], max(cc[, "phq_4"])))
ok <- ok && gi[which.max(cc[, "phq_3"])] == "gad_4" && gi[which.max(cc[, "phq_4"])] == "gad_4"
cat("Does NOT establish the order among gad_1, gad_2, gad_3, gad_6, gad_7 (PARTIAL).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
