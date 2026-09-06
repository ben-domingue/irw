# verify_GBJW_fadplus_goto2021.R
#
# STATUS: this table is BLOCKED on source availability. No __items.csv was written,
# so there is no item_text <-> item mapping in the corpus to verify, and the Step 5b
# row is NO_ROUTE. What this script re-runs is the pair of claims that a retry would
# otherwise have to rebuild from scratch:
#
#   CLAIM A (instrument identity + keying) -- TESTED HERE, falsifiable.
#     The table name mixes two instrument abbreviations, GBJW and FAD-Plus. The live
#     data is the Global Belief in a Just World scale (Lipkus, 1991; Japanese
#     translation Shirai, 2010), NOT either Japanese FAD-Plus, and its items are
#     stored raw and positively keyed. Goto (2021, Front. Psychol. 12:720601,
#     Table 5, N = 802) publishes for "Beliefs in a just world":
#         mean 3.220, SD 0.706, Cronbach's alpha 0.773
#     computed on the respondent mean of the seven items. The FAD-Plus blocks in the
#     same study are 27 items on a 1-5 scale, so reproducing those three numbers from
#     the seven live GBJW_* columns distinguishes the instruments outright. It also
#     fixes the keying direction: all seven GBJW items are positively worded on a
#     1 = strongly disagree .. 6 = strongly agree scale, and a stored reversal would
#     put the mean at 7 - 3.22 = 3.78, well outside tolerance.
#
#   CLAIM B (no route to item identity) -- DEMONSTRATED HERE, not a pass/fail test.
#     Which of Lipkus's seven items each code refers to cannot be checked against the
#     data at all. The script prints the per-item means to make that concrete: three
#     of the seven sit within 0.08 of one another, so no distributional argument could
#     separate them even if a candidate wording list existed. Every other Step 5b route
#     is structurally unavailable -- one shared 1-6 range for all items (route 2), a
#     unidimensional scale with no subscales (routes 3, 5), no published per-item
#     statistics (route 1), no implied parameter (route 4), no reverse-keyed items
#     (route 6), no predicted marker item (route 7).
#
# VERDICT semantics here: PASS means claim A reproduces, i.e. the block is correctly
# recorded against the GBJW and the round's reading of the live data holds. It is NOT
# a claim that any item wording was verified -- none was shipped.

suppressMessages(library(irw))

TABLE <- "GBJW_fadplus_goto2021"

# Goto (2021) Table 5, N = 802.
PUB_MEAN  <- 3.220
PUB_SD    <- 0.706
PUB_ALPHA <- 0.773
TOL_MEAN  <- 0.05   # the paper's figures are on its cleaned file; small residual expected
TOL_SD    <- 0.05
TOL_ALPHA <- 0.02

d <- irw::irw_fetch(TABLE)
d <- d[, c("id", "item", "resp")]

items <- paste0("GBJW_", 1:7)
stopifnot(setequal(unique(d$item), items))

w <- reshape(as.data.frame(d), idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, items, drop = FALSE]
w <- w[complete.cases(w), , drop = FALSE]

scale_score <- rowMeans(w)
obs_mean <- mean(scale_score)
obs_sd   <- sd(scale_score)

k <- ncol(w)
obs_alpha <- k / (k - 1) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))

cat(sprintf("complete respondents: %d (paper N = 802)\n\n", nrow(w)))
cat(sprintf("%-24s %10s %10s %8s\n", "statistic", "published", "observed", "diff"))
cat(sprintf("%-24s %10.3f %10.3f %8.3f\n", "scale mean",  PUB_MEAN,  obs_mean,  obs_mean  - PUB_MEAN))
cat(sprintf("%-24s %10.3f %10.3f %8.3f\n", "scale SD",    PUB_SD,    obs_sd,    obs_sd    - PUB_SD))
cat(sprintf("%-24s %10.3f %10.3f %8.3f\n", "alpha (raw)", PUB_ALPHA, obs_alpha, obs_alpha - PUB_ALPHA))

cat(sprintf("\nreversed-scoring counterfactual: 7 - observed mean = %.3f (vs published %.3f)\n",
            7 - obs_mean, PUB_MEAN))

cat("\nper-item means (claim B -- shows why no item-identity route exists):\n")
m <- sort(colMeans(w), decreasing = TRUE)
for (i in seq_along(m)) cat(sprintf("  %-8s %.3f\n", names(m)[i], m[i]))
gaps <- diff(rev(m))
cat(sprintf("smallest gap between adjacent item means: %.3f (%s vs %s)\n",
            min(abs(gaps)), names(m)[which.min(abs(gaps))],
            names(m)[which.min(abs(gaps)) + 1]))
cat("Three items sit within 0.08; no published per-item statistics exist to match them\n",
    "against, all seven share one 1-6 range, and the scale has no subscale structure --\n",
    "so item identity is NOT established by this script and no item text was shipped.\n", sep = "")

ok <- abs(obs_mean - PUB_MEAN) <= TOL_MEAN &&
      abs(obs_sd - PUB_SD) <= TOL_SD &&
      abs(obs_alpha - PUB_ALPHA) <= TOL_ALPHA

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
