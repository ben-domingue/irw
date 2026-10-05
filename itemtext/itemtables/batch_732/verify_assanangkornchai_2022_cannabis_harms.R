# verify_assanangkornchai_2022_cannabis_harms.R -- Step 5b, batch_732.
#
# Claim: IRW item V5nn is questionnaire Part 4 item nn for the harm items
# (V521 = item 21 "Cause Palpitations" ... V532 = item 32 "Cause Hepatitis"),
# which is also what the deposit's Code sheet labels say for all 12 codes.
#
# Route: the paper's Table 3 (PeerJ 10:e12809) prints RDS-weighted % "yes" for all
# 12 harm items. An RDS-II (Volz-Heckathorn) estimate, weight = 1/network size,
# pooled over all four regions, is recomputed here from the live table's
# cov_network_size (the same estimator reproduced all 14 benefit rows in the
# sibling table, batch_731). Each published value must land on exactly one item
# (to 0.1), and on the item the questionnaire number predicts. The 12 published
# values are pairwise >= 0.5 apart, so a unique hit per value distinguishes every
# item from every other. A positive hit also fixes resp=1 as "yes".

suppressMessages(library(irw))
TABLE <- "assanangkornchai_2022_cannabis_harms"

PUB <- data.frame(
  label = c("Palpitations", "Panic symptoms", "Dementia, memory impairment, amotivation",
            "Schizophrenia-like psychotic symptoms", "Severe dry mouth",
            "Slow reaction time, abnormal sensory-motor function", "Hallucinations",
            "Acute hypotension", "Decreased sperm count, infertility",
            "Ataxia, uncontrollable body coordination", "Blurred vision", "Hepatitis"),
  pct = c(42.3, 35.3, 32.4, 31.9, 40.9, 33.4, 34.4, 24.4, 18.4, 37.8, 36.2, 10.3),
  predicted = sprintf("V%d", 521:532), stringsAsFactors = FALSE)

d <- as.data.frame(suppressMessages(irw::irw_fetch(TABLE)))
stopifnot("cov_network_size" %in% names(d))
d <- d[!is.na(d$cov_network_size) & d$cov_network_size > 0, ]
w <- 1 / d$cov_network_size
est <- 100 * tapply(d$resp * w, d$item, sum) / tapply(w, d$item, sum)
cat("RDS-II % yes per item (1/network size, pooled, n rows =", nrow(d), "):\n")
cat(sprintf("  %s %.3f\n", names(est), est), sep = "")

ok <- TRUE
cat(sprintf("\n%-52s %6s %-6s %-14s\n", "Table 3 label", "pub", "pred", "items within 0.05"))
for (i in seq_len(nrow(PUB))) {
  hits <- names(est)[abs(est - PUB$pct[i]) < 0.05]
  good <- identical(hits, PUB$predicted[i])
  ok <- ok && good
  cat(sprintf("%-52s %6.1f %-6s %-14s %s\n", PUB$label[i], PUB$pct[i], PUB$predicted[i],
              paste(hits, collapse = ","), if (good) "ok" else "MISMATCH"))
}
gap <- min(diff(sort(PUB$pct)))
cat(sprintf("\nsmallest gap between published values: %.1f\n", gap))
ok <- ok && gap >= 0.1
# Direction: under resp flipped (1 = no) the estimates would be 100 - est
flip_hits <- sum(sapply(PUB$pct, function(p) any(abs((100 - est) - p) < 0.05)))
cat(sprintf("published values matched if resp were flipped: %d of 12\n", flip_hits))
ok <- ok && flip_hits == 0

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
