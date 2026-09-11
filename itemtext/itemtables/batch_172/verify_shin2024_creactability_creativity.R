# verify_shin2024_creactability_creativity.R -- Step 5b check, batch_172.
#
# Claim: item codes Creativity1/2/3 carry the paper's Table 2 creativity items in
# listed order ("plays unexpected way from opponent", "tries new methods
# resolutely", "plays unique way compared to others"), and resp 1..7 runs
# "not at all" .. "very" in the paper's listed order.
#
# Source: Shin, Kim, Lee & Lee (2025) Front. Sports Act. Living 7:1521073
# (doi 10.3389/fspor.2025.1521073, PMC12417516). The paper's Table 3 numbers the
# nine creactability items 1-9 and prints a Rasch logit for each; its Table 4
# prints the pooled frequency of each response category 1-7 over all nine items.
# Neither table carries item wording, and Table 2 (the wording) is unnumbered.
#
# Checks, both against live IRW data for the three sibling tables (each 723 rows;
# a read of sibling tables only, nothing written for them):
#   A. Table 4 pooled category counts (all 9 items, 241 players) reproduce
#      exactly -> the live resp integers are the paper's category numbers, not
#      reversed (reversed would put 130 at 1).
#   B. The order of Table 3's logits over items 1-9 equals the order of live item
#      means over Quickness1..3, Creativity1..3, Adaptability1..3 -> the paper's
#      item numbering follows the deposit's column order, which pins
#      Creativity1/2/3 = paper items 4/5/6 (any swap among them breaks the rank
#      match). Table 3's sign convention is that a higher logit goes with a
#      higher mean, despite the text calling it difficulty.
#
# NOT established: that Table 2's unnumbered listing is in item-number order,
# i.e. which of the three creativity wordings is item 4, 5 or 6. No response-side
# route reaches that; it rests on presentation order. Hence PARTIAL in the ledger.

suppressMessages(library(irw))

tabs <- paste0("shin2024_creactability_", c("quickness", "creativity", "adaptability"))
codes <- c(paste0("Quickness", 1:3), paste0("Creativity", 1:3), paste0("Adaptability", 1:3))

d <- do.call(rbind, lapply(tabs, function(t) {
    x <- irw::irw_fetch(t)
    data.frame(item = x$item, resp = as.numeric(x$resp))
}))

# ---- A. Table 4 pooled category frequencies ----
PUB_FREQ <- c(`1` = 19, `2` = 142, `3` = 398, `4` = 429, `5` = 610, `6` = 441, `7` = 130)
obs_freq <- table(factor(d$resp[d$item %in% codes], levels = 1:7))
cat("A. Pooled category counts over 9 items (paper Table 4 vs live)\n")
cat(sprintf("  cat %s: published %4d  live %4d  reversed-reading %4d\n",
            1:7, PUB_FREQ, as.integer(obs_freq), rev(as.integer(obs_freq))), sep = "")
A_ok <- all(as.integer(obs_freq) == PUB_FREQ)
cat("  exact match:", A_ok, "\n\n")

# ---- B. Table 3 logits vs live item means ----
PUB_LOGIT <- c(-0.37, 0.16, -0.10, 0.12, -0.05, -0.02, -0.25, 0.23, 0.28)  # items 1..9
obs_mean <- tapply(d$resp, d$item, mean)[codes]
cat("B. Paper Table 3 item logit vs live item mean (paper item k = k-th deposit column)\n")
cat(sprintf("  item %d %-14s logit %6.2f  mean %.3f  rank(logit) %d  rank(mean) %d\n",
            1:9, codes, PUB_LOGIT, obs_mean, rank(PUB_LOGIT), rank(obs_mean)), sep = "")
rho <- cor(PUB_LOGIT, obs_mean, method = "spearman")
B_ok <- all(rank(PUB_LOGIT) == rank(obs_mean))
cat(sprintf("  Spearman rho = %.3f; all 9 ranks identical: %s\n", rho, B_ok))

# discrimination within the creativity block: every permutation of items 4/5/6
perms <- list(c(4,5,6), c(4,6,5), c(5,4,6), c(5,6,4), c(6,4,5), c(6,5,4))
cat("  Creativity1/2/3 assigned to paper items (a,b,c): ranks still identical?\n")
for (p in perms) {
    lg <- PUB_LOGIT; lg[4:6] <- PUB_LOGIT[p]
    cat(sprintf("    (%d,%d,%d): %s\n", p[1], p[2], p[3], all(rank(lg) == rank(obs_mean))))
}
cat("  Caveat: Creativity2 vs Creativity3 is a near-tie (means 4.502 vs 4.519,\n",
    "  logits -0.05 vs -0.02), so that one pair rests on a small gap.\n", sep = "")
cat("NOT established: which Table 2 wording is paper item 4, 5 or 6 -- Table 2 is\n",
    "unnumbered, so the text-to-code tie within the subscale rests on listed order.\n", sep = "")

cat(if (A_ok && B_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
