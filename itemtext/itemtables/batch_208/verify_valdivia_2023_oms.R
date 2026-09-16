# verify_valdivia_2023_oms.R
#
# CLAIM UNDER TEST (Step 5b): the S1-File Spanish questionnaire's items, numbered
# 1..15, map to the live item codes oms1..oms15 in that order; and option_text is
# oriented UNIFORMLY (resp 1 = "Completamente en desacuerdo" ... resp 5 =
# "Completamente de acuerdo") for every item, including the five items whose .sav
# value labels are stored in the reversed direction.
#
# The falsifiable prediction comes from Valdivia Ramos et al. (2023) PeerJ
# 10.7717/peerj.16375, Table 3, which publishes per-item M, SD and the
# Agree/Neutral/Disagree distribution for all 15 items, numbered 1..15.
#
# Two independent axes:
#   AXIS 1 (item_text <-> item).  Table 3's means are on the SCORED metric, so
#     for the 5 reverse-keyed items (2i, 6i, 7i, 8i, 14i -- flagged with "i" in
#     the paper's Tables 2 and 3, and stored with reversed value labels in the
#     source .sav) the live mean must equal 6 - published mean; for the other 10
#     it must equal the published mean directly. SD is unchanged by reversal.
#   AXIS 2 (option_text <-> resp).  Table 3's Agree% is the share endorsing the
#     item as printed, so it must equal the live share of resp in {4,5} for EVERY
#     item. If the shipped anchors had followed the .sav's per-item value labels
#     instead of the uniform label->integer recode the processing script actually
#     performs, the five reverse-keyed items would come out inverted here.

suppressMessages(library(irw))

TABLE <- "valdivia_2023_oms"
ITEMS <- paste0("oms", 1:15)

# Valdivia et al. (2023) PeerJ, Table 3 -- rows reordered from the paper's
# subscale grouping into item-number order 1..15.
PUB_M  <- c(2.55, 1.69, 3.07, 2.54, 1.56, 1.78, 2.13, 2.16,
            1.87, 1.83, 1.86, 2.34, 1.73, 1.93, 1.77)
PUB_SD <- c(1.07, 0.90, 1.17, 1.25, 0.86, 0.92, 0.98, 1.01,
            0.91, 0.99, 0.88, 1.06, 0.89, 1.05, 0.88)
PUB_AGREE <- c(17.8, 86.7, 42.3, 29.5, 5.1, 81.5, 69.2, 72.5,
               5.2, 8.7, 4.9, 14.2, 5.0, 77.3, 4.0)
REVERSED <- c(2, 6, 7, 8, 14)   # "i"-flagged in the paper; reversed in the .sav

TOL_M <- 0.015; TOL_SD <- 0.015; TOL_P <- 0.15

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

obs_m  <- tapply(d$resp, d$item, mean)[ITEMS]
obs_sd <- tapply(d$resp, d$item, sd)[ITEMS]
obs_ag <- 100 * tapply(d$resp, d$item, function(x) mean(x >= 4))[ITEMS]

exp_m <- ifelse(1:15 %in% REVERSED, 6 - PUB_M, PUB_M)

cat("AXIS 1 -- per-item mean and SD vs paper Table 3\n")
cat(sprintf("%-6s %4s %9s %9s %8s | %8s %8s %8s\n",
            "item", "rev", "exp_mean", "obs_mean", "diff", "pub_sd", "obs_sd", "diff"))
for (i in 1:15)
    cat(sprintf("%-6s %4s %9.2f %9.2f %8.3f | %8.2f %8.2f %8.3f\n",
                ITEMS[i], if (i %in% REVERSED) "yes" else "-",
                exp_m[i], obs_m[i], obs_m[i] - exp_m[i],
                PUB_SD[i], obs_sd[i], obs_sd[i] - PUB_SD[i]))

w_m <- max(abs(obs_m - exp_m)); w_sd <- max(abs(obs_sd - PUB_SD))
cat(sprintf("\nlargest mean deviation: %.3f (tol %.3f);  largest SD deviation: %.3f (tol %.3f)\n",
            w_m, TOL_M, w_sd, TOL_SD))

# Uniqueness: does (M, SD) actually separate every item from every other?
key <- paste(round(PUB_M, 2), round(PUB_SD, 2))
cat(sprintf("distinct published (M,SD) pairs: %d of 15\n", length(unique(key))))

cat("\nAXIS 2 -- %% endorsing (resp in {4,5}) vs paper Table 3 'Agree'\n")
cat(sprintf("%-6s %4s %9s %9s %8s\n", "item", "rev", "pub_agr", "obs_agr", "diff"))
for (i in 1:15)
    cat(sprintf("%-6s %4s %9.1f %9.1f %8.2f\n",
                ITEMS[i], if (i %in% REVERSED) "yes" else "-",
                PUB_AGREE[i], obs_ag[i], obs_ag[i] - PUB_AGREE[i]))
w_p <- max(abs(obs_ag - PUB_AGREE))
cat(sprintf("\nlargest agree%%%% deviation: %.2f pp (tol %.2f)\n", w_p, TOL_P))

ok <- (w_m <= TOL_M) && (w_sd <= TOL_SD) && (w_p <= TOL_P) && (length(unique(key)) == 15)

cat("\nWhat this does NOT establish: nothing here tests the Spanish wording itself --\n",
    "only that the item numbered N in the S1 questionnaire is the item coded omsN.\n",
    "The English in the *_translated columns is Modgill et al. (2014)'s official\n",
    "OMS-HC wording as reprinted in this paper's Table 3, and instructions_translated\n",
    "is an IRW rendering; neither is checked by this script.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
