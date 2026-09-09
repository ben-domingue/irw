# Step 5b verification for laksmita_2020_mspss.
#
# Claim: item codes MSPSS1..MSPSS12 carry the canonically numbered MSPSS items
# 1..12 (Zimet et al. 1988), as shipped in laksmita_2020_mspss__items.csv.
#
# Falsifiable prediction: Laksmita et al. (2020) PLOS ONE 15(3):e0229958 Table 3
# publishes Mean +/- SD for each numbered item over the same n = 299 sample.
# If any two item_texts were swapped, the mean/SD pair at those positions would
# swap too. Three items tie at mean 5.48 (1, 2, 11); their SDs (1.28 / 1.15 /
# 1.30) separate them, so mean AND SD are both checked.

suppressMessages(library(irw))

TABLE <- "laksmita_2020_mspss"

# Paper Table 3, "Item number and description" / "Mean+/-SD", items 1..12.
PUB_MEAN <- c(5.48, 5.48, 5.83, 5.34, 5.76, 5.25, 4.19, 5.03, 5.37, 5.55, 5.48, 4.78)
PUB_SD   <- c(1.28, 1.15, 1.29, 1.46, 1.24, 1.22, 1.56, 1.32, 1.26, 1.37, 1.30, 1.33)
TOL <- 0.011   # paper reports 2 d.p.; rounding alone allows 0.005

d  <- irw::irw_fetch(TABLE)
ky <- paste0("MSPSS", 1:12)
obs_m <- tapply(d$resp, d$item, mean)[ky]
obs_s <- tapply(d$resp, d$item, stats::sd)[ky]

cat(sprintf("%-9s %9s %9s %8s %9s %9s %8s\n",
            "item", "pub_mean", "obs_mean", "dM", "pub_sd", "obs_sd", "dSD"))
for (i in 1:12)
    cat(sprintf("%-9s %9.2f %9.2f %8.3f %9.2f %9.2f %8.3f\n",
                ky[i], PUB_MEAN[i], obs_m[i], obs_m[i] - PUB_MEAN[i],
                PUB_SD[i], obs_s[i], obs_s[i] - PUB_SD[i]))

worst_m <- max(abs(obs_m - PUB_MEAN))
worst_s <- max(abs(obs_s - PUB_SD))
cat(sprintf("\nlargest deviation: mean %.4f, SD %.4f (tolerance %.3f)\n",
            worst_m, worst_s, TOL))

cat("This pins every one of the 12 item codes to a distinct published (mean, SD)\n",
    "pair, so it distinguishes every item from every other item. It does NOT\n",
    "verify the option_text<->resp mapping: the 1..7 anchors come from the\n",
    "rights holder's own MSPSS form and the paper states only the 1 = very\n",
    "strongly disagree / 7 = very strongly agree endpoints.\n", sep = "")

cat(if (worst_m <= TOL && worst_s <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
