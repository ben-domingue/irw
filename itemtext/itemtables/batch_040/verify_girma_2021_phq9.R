# verify_girma_2021_phq9.R -- Step 5b mapping verification.
#
# CLAIM: each 8-character item code in girma_2021_phq9 is the PHQ-9 symptom its
# abbreviation names (INTEREST=1 anhedonia ... DEATHWIS=9 death/self-harm), and
# the shipped 0-3 anchors (Not at all / Several days / More than half the days /
# Nearly every day) run in the instrument's published direction.
#
# The primary basis is the self-describing-codes exemption: the source XLS column
# names abbreviate the item content, so no permutation of the nine is possible
# without being self-evident (APPETITE cannot be the sleep item). This script
# adds the two falsifiable numeric predictions that a wrong mapping or a flipped
# response direction would break.
#
#   1. Route 3 (published total). Girma et al. 2021 (PLOS ONE 16(5):e0250927)
#      report 28% depression prevalence at PHQ-9 >= 10, 95% CI (24.5, 32.1).
#      The nine items summed per person must reproduce 28%. A reversed anchor
#      order (3=Not at all) turns a mean total of 6.8 into 20.2 and the
#      prevalence into ~99%.
#   2. Route 7 (marker item). PHQ-9 item 9 (death/self-harm) must be the least
#      endorsed item in a school-based community sample. DEATHWIS must have the
#      lowest mean of the nine.

suppressMessages(library(irw))

TABLE <- "girma_2021_phq9"
PUB_PREV <- 28.0      # % with PHQ-9 total >= 10 (paper, Results)
PUB_CI   <- c(24.5, 32.1)

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

m <- sort(tapply(d$resp, d$item, mean))
cat("-- per-item mean (ascending) --\n")
for (i in seq_along(m)) cat(sprintf("%-9s %6.3f   %5.1f%% endorsed (resp > 0)\n",
    names(m)[i], m[i], 100 * mean(d$resp[d$item == names(m)[i]] > 0)))

tot  <- tapply(d$resp, d$id, sum)
prev <- 100 * mean(tot >= 10)
cat(sprintf("\nPHQ-9 total: mean %.3f  sd %.3f  range %d-%d  (n = %d)\n",
            mean(tot), sd(tot), min(tot), max(tot), length(tot)))
cat(sprintf("prevalence at total >= 10: observed %.2f%%  vs published %.1f%% [CI %.1f, %.1f]\n",
            prev, PUB_PREV, PUB_CI[1], PUB_CI[2]))

rev_tot  <- tapply(3 - d$resp, d$id, sum)
cat(sprintf("counterfactual if anchors were reversed: mean %.3f, prevalence %.1f%% -- ruled out\n",
            mean(rev_tot), 100 * mean(rev_tot >= 10)))

marker_ok <- names(m)[1] == "DEATHWIS"
cat(sprintf("\nlowest-mean item: %s (%.3f) vs next lowest %s (%.3f) -- PHQ-9 item 9 marker %s\n",
            names(m)[1], m[1], names(m)[2], m[2], if (marker_ok) "holds" else "FAILS"))

prev_ok <- abs(prev - PUB_PREV) <= 0.5

cat("\nWhat this does NOT establish: the statistics cannot separate items with\n",
    "near-identical means (DEPRESSF 0.918 vs SLEEPCON 0.932), and route 3 pins the\n",
    "item SET and the anchor direction rather than any individual item. Per-item\n",
    "identity rests on the self-describing column names, which do distinguish all nine.\n", sep = "")

cat(if (marker_ok && prev_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
