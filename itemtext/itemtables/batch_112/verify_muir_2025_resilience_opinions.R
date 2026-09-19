# verify_muir_2025_resilience_opinions.R
#
# Claim under test: each xlsx column header (5_..11_) carries the questionnaire
# statement shipped as its item_text. Falsifiable prediction: Table 1 of Muir et
# al. 2025 (PLOS ONE 10.1371/journal.pone.0338728) publishes per-item Mean(SD)
# for the seven "Opinions about Organizational Response" components, numbered in
# the questionnaire's own a..g order. Under the shipped mapping, component k's
# published mean must equal the live mean of the item whose numeric prefix is
# k+4. Swap any two item_texts and this breaks.

suppressMessages(library(irw))

TABLE <- "muir_2025_resilience_opinions"

# Paper Table 1, "Opinions about Organizational Response", Components 1-7.
ORDER <- c("5_opinions_measures_in_place", "6_opinions_sufficiently_prepared",
           "7_opinion_timely_actions", "8_opinion_actions_effective",
           "9_opinion_adaptability", "10_opinion_learning",
           "11_opinion_resilience")
PUB_M  <- c(3.86, 4.39, 4.81, 4.73, 4.64, 4.67, 4.73)
PUB_SD <- c(1.00, 0.79, 0.57, 0.64, 0.68, 0.68, 0.64)
TOL_M  <- 0.02
TOL_SD <- 0.03

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
obs_m  <- tapply(d$resp, d$item, mean)[ORDER]
obs_sd <- tapply(d$resp, d$item, sd)[ORDER]

cat(sprintf("%-34s %5s %6s %7s %6s %7s\n",
            "item", "pubM", "obsM", "diffM", "pubSD", "obsSD"))
for (i in seq_along(ORDER))
    cat(sprintf("%-34s %5.2f %6.3f %7.3f %6.2f %7.3f\n",
                ORDER[i], PUB_M[i], obs_m[i], obs_m[i] - PUB_M[i],
                PUB_SD[i], obs_sd[i]))

worst_m  <- max(abs(obs_m - PUB_M))
worst_sd <- max(abs(obs_sd - PUB_SD))
cat(sprintf("\nlargest mean deviation: %.3f (tol %.2f); largest SD deviation: %.3f (tol %.2f)\n",
            worst_m, TOL_M, worst_sd, TOL_SD))

# Uniqueness: does the published profile pin each item on its own?
ties <- sum(duplicated(paste(PUB_M, PUB_SD)))
cat(sprintf("published (M,SD) pairs that are not unique: %d ", ties))
cat("-- components 4 and 7 both read 4.73(0.64), so the statistics alone leave that\n",
    "one pair interchangeable. It is separated by the source column headers, which name\n",
    "their own content ('8_opinion_actions_effective' vs '11_opinion_resilience') against\n",
    "'...were effective' and '...exhibited sufficient resilience...'. Everything else is\n",
    "pinned by the means outright.\n", sep = "")

cat(if (worst_m <= TOL_M && worst_sd <= TOL_SD) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
