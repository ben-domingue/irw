# verify_liang_2026_intrinsic_motivation.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order): the paper never prints the
# IM1..IM5 codes the data uses, so the assignment IM1 = Table 1 item 1 ...
# IM5 = Table 1 item 5 is an inference from presentation order.
#
# THE FALSIFIABLE PREDICTION: the same paper's Table 8 ("Descriptive statistics
# for exercise motivation items (N = 45)", doi:10.1371/journal.pone.0345759.t008)
# publishes a mean AND an SD for each of the five items, printed against the very
# item wording that Table 1 numbers 1-5. If the item_text shipped for any two IM
# codes were swapped, the observed (mean, SD) pair for those codes would land on
# the wrong published row. The five published pairs are mutually distinct -- items
# 2 and 4 tie at mean 4.20 but separate on SD (0.815 vs 0.842), and items 3 and 5
# tie at SD 0.830 but separate on mean (4.36 vs 4.24) -- so the pair distinguishes
# EVERY item from EVERY other item, which is what makes this VERIFIED rather than
# PARTIAL.
#
# Note the sibling table liang_2026_extrinsic_motivation was only PARTIAL: its
# agent used the correlation structure, not Table 8. Table 8 is a stronger route
# and it settles the intrinsic block outright.

suppressMessages(library(irw))

TABLE <- "liang_2026_intrinsic_motivation"
ITEMS <- c("IM1", "IM2", "IM3", "IM4", "IM5")

# Published in Table 8, Intrinsic Motivation block, items 1-5, in that order.
PUB_MEAN <- c(4.11, 4.20, 4.36, 4.20, 4.24)
PUB_SD   <- c(0.885, 0.815, 0.830, 0.842, 0.830)
PUB_SUBSCALE_MEAN <- 4.22          # Table 8 "Subscale Average" row
TOL_MEAN <- 0.01
TOL_SD   <- 0.001

d <- irw::irw_fetch(TABLE)
obs_mean <- tapply(d$resp, d$item, mean)[ITEMS]
obs_sd   <- tapply(d$resp, d$item, stats::sd)[ITEMS]
obs_n    <- tapply(d$resp, d$item, length)[ITEMS]

cat(sprintf("%-5s %3s %10s %10s %8s %10s %10s %8s\n",
            "item", "n", "pub.mean", "obs.mean", "dMean", "pub.sd", "obs.sd", "dSD"))
for (i in seq_along(ITEMS))
  cat(sprintf("%-5s %3d %10.2f %10.3f %8.3f %10.3f %10.3f %8.4f\n",
              ITEMS[i], obs_n[i], PUB_MEAN[i], obs_mean[i], obs_mean[i] - PUB_MEAN[i],
              PUB_SD[i], obs_sd[i], obs_sd[i] - PUB_SD[i]))

worst_mean <- max(abs(obs_mean - PUB_MEAN))
worst_sd   <- max(abs(obs_sd - PUB_SD))
cat(sprintf("\nlargest |dMean| = %.4f (tol %.2f); largest |dSD| = %.5f (tol %.3f)\n",
            worst_mean, TOL_MEAN, worst_sd, TOL_SD))

# Subscale average, an independent line of Table 8.
sub <- mean(tapply(d$resp, d$id, mean))
cat(sprintf("subscale average: published %.2f, observed %.4f\n", PUB_SUBSCALE_MEAN, sub))

# The permutation test: does any OTHER assignment of the five texts to the five
# codes fit the published table as well? Score every permutation on the joint
# (mean, SD) residual; a unique minimum at the identity is the whole claim.
perms <- function(v) { if (length(v) == 1) return(list(v))
  out <- list(); for (i in seq_along(v)) for (p in perms(v[-i])) out[[length(out)+1]] <- c(v[i], p); out }
P <- perms(1:5)
score <- sapply(P, function(p) max(abs(obs_mean[p] - PUB_MEAN)) + max(abs(obs_sd[p] - PUB_SD)))
best <- which.min(score)
ident <- which(sapply(P, function(p) identical(p, 1:5)))
runner <- min(score[-ident])
cat(sprintf("permutations scored: %d; identity score %.5f; best-other score %.5f\n",
            length(P), score[ident], runner))
cat(sprintf("identity is the unique minimum: %s\n", identical(best, ident)))

cat("Note: this route pins each of the five item codes to a distinct published row,",
    "because the five (mean, SD) pairs are mutually distinct. It does NOT establish",
    "the response-option wording -- that axis is settled separately and non-inferentially",
    "by the deposit's own paired label/integer columns (S2 Data), not by this script.",
    sep = "\n")

ok <- worst_mean <= TOL_MEAN && worst_sd <= TOL_SD && identical(best, ident)
cat(if (ok) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")
