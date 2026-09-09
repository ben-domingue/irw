# Step 5b verification for jimenezherrera_2022_moral_sensitivity.
#
# CLAIM UNDER TEST: the live item code "Item Moral k" is the paper's "Ítem k"
# (Jimenez-Herrera et al. 2022, PLOS ONE 10.1371/journal.pone.0270049, Table 1),
# whose Spanish wording is what ships as item_text. mapping_basis = paper_explicit.
#
# FALSIFIABLE PREDICTION: the paper's Table 3 publishes, for each numbered item,
# the scale mean and the scale variance WITH THAT ITEM DELETED. Those two numbers
# are a per-item fingerprint: swapping any two items' text would leave the
# published pair sitting on the wrong live code. Item 2 and item 7 have
# near-identical deleted means (37.21 vs 37.22) and are separated by their
# deleted variances (19.369 vs 19.689), so the pair distinguishes all 9 items.
#
# This does NOT re-check item or resp sets -- validate_items.R did that.

suppressMessages(library(irw))
TABLE <- "jimenezherrera_2022_moral_sensitivity"

# Paper Table 3 ("Cronbach's alpha and moral sensitivity questionnaire index for
# each item"), rows Item 1..Item 9, columns 2 and 3.
PUB_MEAN_DEL <- c(36.89, 37.21, 38.08, 38.14, 37.41, 38.26, 37.22, 38.63, 38.31)
PUB_VAR_DEL  <- c(20.315, 19.369, 18.816, 17.257, 19.263, 17.581, 19.689, 17.000, 16.826)
TOL_MEAN <- 0.02
TOL_VAR  <- 0.01

d <- irw::irw_fetch(TABLE)
its <- paste("Item Moral", 1:9)
m <- sapply(its, function(i) { x <- d[d$item == i, c("id", "resp")]; x[order(x$id), ]$resp })
tot <- rowSums(m)

obs_mean_del <- sapply(1:9, function(i) mean(tot - m[, i]))
obs_var_del  <- sapply(1:9, function(i) var(tot - m[, i]))

cat(sprintf("n respondents: %d ; scale mean %.2f (paper 42.51)\n\n", nrow(m), mean(tot)))
cat(sprintf("%-14s %12s %10s %8s | %12s %10s %8s\n",
            "item", "pub mean-del", "observed", "diff", "pub var-del", "observed", "diff"))
for (i in 1:9)
  cat(sprintf("%-14s %12.2f %10.2f %8.3f | %12.3f %10.3f %8.3f\n",
              its[i], PUB_MEAN_DEL[i], obs_mean_del[i], obs_mean_del[i] - PUB_MEAN_DEL[i],
              PUB_VAR_DEL[i], obs_var_del[i], obs_var_del[i] - PUB_VAR_DEL[i]))

worst_m <- max(abs(obs_mean_del - PUB_MEAN_DEL))
worst_v <- max(abs(obs_var_del  - PUB_VAR_DEL))
cat(sprintf("\nlargest deviation: mean-deleted %.3f (tol %.2f), variance-deleted %.3f (tol %.2f)\n",
            worst_m, TOL_MEAN, worst_v, TOL_VAR))

# Uniqueness: no OTHER permutation of the 9 codes fits the published pair.
perm_ok <- 0
for (p in list(1:9)) NULL
best_alt <- Inf
for (i in 1:9) for (j in 1:9) if (i != j) {
  alt_m <- obs_mean_del; alt_m[c(i, j)] <- alt_m[c(j, i)]
  alt_v <- obs_var_del;  alt_v[c(i, j)] <- alt_v[c(j, i)]
  best_alt <- min(best_alt, max(max(abs(alt_m - PUB_MEAN_DEL)) / TOL_MEAN,
                                max(abs(alt_v - PUB_VAR_DEL)) / TOL_VAR))
}
cat(sprintf("closest rival mapping (any single transposition) misses by %.1fx tolerance\n", best_alt))
cat("Establishes: which live code carries which numbered item, for all 9.\n")
cat("Does NOT establish: the Spanish wording transcribed from the Table 1 image is\n",
    "character-accurate, nor the option_text<->resp direction (1=disagree..6=agree),\n",
    "which rests on the paper's prose statement rather than on these numbers.\n", sep = "")

cat(if (worst_m <= TOL_MEAN && worst_v <= TOL_VAR && best_alt > 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
