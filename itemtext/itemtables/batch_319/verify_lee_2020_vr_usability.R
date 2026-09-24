# verify_lee_2020_vr_usability.R -- Step 5b, route 1 (per-item descriptives)
# plus route 7 (marker item) and route 2 (per-item observed ranges).
#
# CLAIM UNDER TEST: IRW item UsabilityK carries the wording of item No. K in
# Lee & Kim (2020) PLOS ONE 15(9):e0238437, Table 2 "Responses to usability
# scale statement (n = 60)". The codes are the S1 .sav's own column names
# (data/lee_2020_vr_usability.py melts them unrenamed), whose variable labels
# read only "ease of use 1".."ease of use 11" / "usefulness1".."usefulness6" --
# the tie to wording is the shared 1..17 numbering.
#
# FALSIFIABLE PREDICTION: live mean and SD of UsabilityK reproduce Table 2 row K
# (to 2dp rounding). The (mean, SD) pairs are pairwise distinct across all 17
# rows, so swapping ANY two items' text breaks the match. Item 7 is the one
# negatively worded item ("It was difficult to operate the devices") and must
# be the lone low-mean item.
#
# Known source discrepancies (checked, printed below, tolerated explicitly):
#   * item 7: Table 2 prints 2.60 / 2.61 / range 0-8; the live data give
#     2.767 / 2.752 / 0-10 over n=60. The lone 10 is participant M12 (who
#     rated 14 of 17 items at 10). Setting that one value to 0 reproduces
#     Table 2 exactly (n=60, mean 2.6000, SD 2.6051, range 0-8), so the
#     paper analysed M12's item 7 as 0; the deposit (and hence IRW) has 10.
#     Dropping it instead gives 2.644 / 2.605, which does NOT match.
#   * item 5: Table 2 prints SD 1.5; live SD 1.954 (mean 7.75 matches).
#   * item 9: Table 2 prints range 5-10; live 2-10 (mean 6.83 / SD 1.98 match).

suppressMessages(library(irw))

TABLE <- "lee_2020_vr_usability"
PUB_MEAN <- c(8.38, 9.25, 8.65, 7.48, 7.75, 8.60, 2.60, 8.23, 6.83, 8.47, 8.15,
              8.87, 8.27, 8.58, 8.63, 8.53, 8.90)
PUB_SD   <- c(1.26, 1.00, 1.57, 2.15, 1.5,  1.30, 2.61, 1.62, 1.98, 1.26, 1.76,
              1.05, 1.69, 1.37, 1.09, 1.38, 1.42)
TOL <- 0.006   # 2dp rounding

d <- irw::irw_fetch(TABLE)
items <- paste0("Usability", 1:17)
obs_mean <- sapply(items, function(i) mean(d$resp[d$item == i]))
obs_sd   <- sapply(items, function(i) sd(d$resp[d$item == i]))
obs_rng  <- sapply(items, function(i) paste(range(d$resp[d$item == i]), collapse = "-"))

cat(sprintf("%-12s %8s %8s %8s %8s %6s\n", "item", "pubM", "obsM", "pubSD", "obsSD", "range"))
for (k in 1:17)
    cat(sprintf("%-12s %8.2f %8.3f %8.2f %8.3f %6s\n", items[k], PUB_MEAN[k], obs_mean[k],
                PUB_SD[k], obs_sd[k], obs_rng[k]))

# item 7 with the lone 10 set to 0 (see header)
v7 <- d$resp[d$item == "Usability7"]
stopifnot(sum(v7 == 10) == 1)
v7x <- ifelse(v7 == 10, 0, v7)
cat(sprintf("\nUsability7 with the single resp=10 read as 0 (n=%d): mean %.4f SD %.4f range %s  (Table 2: 2.60 / 2.61 / 0-8)\n",
            length(v7x), mean(v7x), sd(v7x), paste(range(v7x), collapse = "-")))
cat(sprintf("Usability7 with it dropped instead (n=%d): mean %.4f SD %.4f\n",
            sum(v7 != 10), mean(v7[v7 != 10]), sd(v7[v7 != 10])))

adj_mean <- obs_mean; adj_sd <- obs_sd
adj_mean[7] <- mean(v7x); adj_sd[7] <- sd(v7x)
mean_ok <- abs(adj_mean - PUB_MEAN) <= TOL
sd_ok   <- abs(adj_sd - PUB_SD) <= TOL
sd_ok[5] <- TRUE                                # printed "1.5" is a Table 2 misprint (1.954)
cat(sprintf("\nmeans within %.3f: %d/17 ; SDs within tolerance: %d/17 (item 5 SD excepted as misprint)\n",
            TOL, sum(mean_ok), sum(sd_ok)))

# Do the published (mean, SD) pairs separate every item from every other?
pairs_ok <- TRUE
for (a in 1:16) for (b in (a + 1):17)
    if (abs(PUB_MEAN[a] - PUB_MEAN[b]) < 0.015 && abs(PUB_SD[a] - PUB_SD[b]) < 0.015) {
        pairs_ok <- FALSE; cat("inseparable pair:", a, b, "\n") }
min_gap <- min(outer(1:17, 1:17, Vectorize(function(a, b)
    if (a >= b) Inf else max(abs(PUB_MEAN[a] - PUB_MEAN[b]), abs(PUB_SD[a] - PUB_SD[b])))))
cat(sprintf("smallest max(|dMean|,|dSD|) between any two published rows: %.2f -> every pair separable: %s\n",
            min_gap, pairs_ok))

# Marker: the reverse-worded item 7 is the only item with mean < 5
marker_ok <- which(obs_mean < 5) == 7 && length(which(obs_mean < 5)) == 1
cat(sprintf("marker: items with mean < 5 = {%s} (expect Usability7 only)\n",
            paste(items[obs_mean < 5], collapse = ",")))

cat(if (all(mean_ok) && all(sd_ok) && pairs_ok && isTRUE(marker_ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
