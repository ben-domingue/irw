# verify_valverdeberrocoso_2021_sqd.R
#
# CLAIM: item code SQDnn carries the wording numbered n in the study's own
# questionnaire (S1 File) and in the paper's Table 3.
#
# FALSIFIABLE PREDICTION: Table 3 of Valverde-Berrocoso et al. (2021), PLOS ONE
# 10.1371/journal.pone.0256283, publishes M (2 dp) and SD (3 dp) for all 24
# numbered SQD items. Those 24 (M, SD) pairs must reappear on SQD01..SQD24 in
# the live IRW table, in that order. The 24 published SDs are all distinct, so
# SD alone is a per-item fingerprint: any permutation of the mapping -- including
# a swap of the near-tied means (item 1 = 4.27 vs item 5 = 4.28, 7 = 3.26 vs
# 11 = 3.25, 15 = 3.90 vs 20 = 3.89) -- breaks it.

suppressMessages(library(irw))

TABLE <- "valverdeberrocoso_2021_sqd"

# Paper Table 3, items 1..24, in printed order.
PUB_M  <- c(4.27,3.94,4.12,3.83,4.28,3.96,3.26,3.49,3.34,4.00,3.25,3.16,
            3.23,4.47,3.90,3.67,3.56,3.42,3.69,3.89,3.29,2.70,2.97,2.56)
PUB_SD <- c(1.166,1.187,1.294,1.361,1.170,1.213,1.371,1.306,1.327,1.180,1.341,1.284,
            1.297,1.288,1.311,1.397,1.190,1.329,1.351,1.225,1.277,1.174,1.117,1.120)
TOL_M  <- 0.005
TOL_SD <- 0.0005

items <- sprintf("SQD%02d", 1:24)
d <- irw::irw_fetch(TABLE)
obs_m  <- sapply(items, function(i) mean(d$resp[d$item == i]))
obs_sd <- sapply(items, function(i) sd(d$resp[d$item == i]))

cat(sprintf("%-7s %8s %8s %8s | %8s %8s %8s\n",
            "item", "pub M", "obs M", "dM", "pub SD", "obs SD", "dSD"))
for (i in 1:24)
    cat(sprintf("%-7s %8.2f %8.3f %8.3f | %8.3f %8.3f %8.4f\n",
                items[i], PUB_M[i], obs_m[i], obs_m[i] - PUB_M[i],
                PUB_SD[i], obs_sd[i], obs_sd[i] - PUB_SD[i]))

ok_m  <- max(abs(round(obs_m, 2)  - PUB_M))  <= TOL_M
ok_sd <- max(abs(round(obs_sd, 3) - PUB_SD)) <= TOL_SD
cat(sprintf("\nlargest |dM| (obs rounded to 2dp): %.4f\n", max(abs(round(obs_m,2)-PUB_M))))
cat(sprintf("largest |dSD| (obs rounded to 3dp): %.4f\n", max(abs(round(obs_sd,3)-PUB_SD))))

# Uniqueness: is the identity assignment the ONLY one consistent with these SDs?
cat(sprintf("distinct published SDs: %d of 24\n", length(unique(PUB_SD))))
best <- sapply(1:24, function(j) items[which.min(abs(round(obs_sd,3) - PUB_SD[j]))])
uniq_ok <- identical(unname(best), items) && length(unique(PUB_SD)) == 24
cat(sprintf("nearest-SD assignment reproduces the identity mapping: %s\n", uniq_ok))

# What this does NOT establish: nothing about the option_text<->resp axis, which
# is not inferred here -- the questionnaire prints the 1..6 legend itself.
cat("Note: this route pins every item individually (SDs are unique to 3dp); it says\n",
    "nothing about the option/resp mapping, which the questionnaire states outright.\n", sep = "")

cat(if (ok_m && ok_sd && uniq_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
