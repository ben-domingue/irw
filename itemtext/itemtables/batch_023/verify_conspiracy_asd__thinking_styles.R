# verify_conspiracy_asd__thinking_styles.R
#
# CLAIM UNDER TEST: item codes ts_1..ts_10 are assigned POSITIONALLY by
# data/conspiracy_belief_schizotypy_asd.py -- ts_N <- column index (21 + N - 1)
# (0-based) of the deposit's raw workbook, i.e. the 10 "Thinking Styles - ..."
# columns of Figshare 10.6084/m9.figshare.30903575.v2. The item_text shipped for
# ts_N is the wording at that source position. A positional code keeps no trace
# of the source column name, so the claim is checked, not assumed.
#
# FALSIFIABLE PREDICTION: the per-item mean, floor% (resp==1) and ceiling%
# (resp==5) computed from source column 21+N-1 must reproduce the LIVE IRW
# per-item statistics for ts_N. A shifted range or any permutation of the ten
# columns breaks this immediately.
#
# The SOURCE-side numbers below were computed from the deposit workbook
# (raw.xlsx, rows 3+, 0-based columns 21..30) and are hard-coded so this script
# needs no network access to Figshare. Only the live IRW data is fetched.

suppressMessages(library(irw))

TABLE <- "conspiracy_asd__thinking_styles"
ITEMS <- paste0("ts_", 1:10)

# Source workbook columns 21..30 (0-based), in order -> ts_1..ts_10
SRC_MEAN  <- c(3.930716, 3.341801, 3.833718, 3.688222, 3.875289,
               2.200924, 2.706697, 3.748268, 3.699769, 2.187067)
SRC_FLOOR <- c(0.4619, 5.0808, 0.4619, 1.8476, 0.2309,
               26.3279, 16.3972, 1.3857, 2.0785, 28.1755)
SRC_CEIL  <- c(27.7136, 13.1640, 25.4042, 18.9376, 24.2494,
               3.0023,  7.3903, 19.6305, 21.0162,  3.2333)

TOL_MEAN <- 1e-4
TOL_PCT  <- 1e-2

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

obs_mean  <- sapply(ITEMS, function(i) mean(d$resp[d$item == i]))
obs_floor <- sapply(ITEMS, function(i) 100 * mean(d$resp[d$item == i] == 1))
obs_ceil  <- sapply(ITEMS, function(i) 100 * mean(d$resp[d$item == i] == 5))

cat(sprintf("%-6s %9s %9s %9s | %8s %8s | %8s %8s\n",
            "item", "src_mean", "irw_mean", "diff", "src_fl%", "irw_fl%", "src_ce%", "irw_ce%"))
for (k in seq_along(ITEMS))
    cat(sprintf("%-6s %9.6f %9.6f %9.2e | %8.2f %8.2f | %8.2f %8.2f\n",
                ITEMS[k], SRC_MEAN[k], obs_mean[k], obs_mean[k] - SRC_MEAN[k],
                SRC_FLOOR[k], obs_floor[k], SRC_CEIL[k], obs_ceil[k]))

worst_mean <- max(abs(obs_mean - SRC_MEAN))
worst_pct  <- max(abs(obs_floor - SRC_FLOOR), abs(obs_ceil - SRC_CEIL))
cat(sprintf("\nlargest mean deviation: %.2e (tol %.0e)\n", worst_mean, TOL_MEAN))
cat(sprintf("largest floor/ceiling deviation: %.4f pp (tol %.2f pp)\n", worst_pct, TOL_PCT))

# Separation: does this route distinguish EVERY item from EVERY other item?
# Two mean pairs are close (ts_4 3.6882 vs ts_9 3.6998; ts_6 2.2009 vs ts_10
# 2.1871), so check the (mean, floor%, ceiling%) triple is unique per item.
sig <- paste(round(obs_mean, 4), round(obs_floor, 3), round(obs_ceil, 3))
n_dup <- sum(duplicated(sig))
mind <- min(dist(cbind(obs_mean, obs_floor, obs_ceil)))
cat(sprintf("duplicate (mean,floor%%,ceil%%) signatures among the 10 items: %d\n", n_dup))
cat(sprintf("closest pair distance in that 3-space: %.4f\n", mind))

cat("Note: this pins the item axis (item_text <-> item) only. The option axis\n",
    "(1 = 'completely false' .. 5 = 'completely true') is not tested here; it is\n",
    "stated outright in the survey's own instruction line and anchor table, so no\n",
    "inference was made about it.\n", sep = "")

ok <- worst_mean <= TOL_MEAN && worst_pct <= TOL_PCT && n_dup == 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
