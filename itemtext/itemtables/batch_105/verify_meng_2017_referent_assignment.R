# verify_meng_2017_referent_assignment.R
#
# CLAIM UNDER TEST (Step 5b, route 1 -- per-item descriptive statistics):
#   The five live item codes EQ, AQ, EQ2, AQ2, AQ3 denote the five successive
#   questions of Meng, Murakami & Hashiya (2017)'s reference assignment task in
#   the order the paper names them, so the wording transcribed from the paper's
#   Methods (EQ/EQ2 = the explicit name/color question, AQ/AQ2/AQ3 = "What about
#   this?") attaches to the right code.
#
# FALSIFIABLE PREDICTION: the paper's Table 1 publishes a mean and SD for each of
# the five answers, labelled with those same five codes. If the item->text
# assignment were permuted, the live per-item mean/SD pairs would land against the
# wrong published row. All five published pairs are distinct at the printed
# precision, so this route separates every item from every other item.
#
# Published values, PLOS ONE 12(10):e0187368, Table 1 ("Children's performance on
# the tasks"), read from the table image (.t001) -- the table is served as an
# image only.

suppressMessages(library(irw))

TABLE <- "meng_2017_referent_assignment"
ITEMS <- c("EQ", "AQ", "EQ2", "AQ2", "AQ3")
PUB_MEAN <- c(EQ = 0.91, AQ = 0.90, EQ2 = 0.88, AQ2 = 0.78, AQ3 = 0.77)
PUB_SD   <- c(EQ = 0.283, AQ = 0.306, EQ2 = 0.327, AQ2 = 0.412, AQ3 = 0.423)
TOL_MEAN <- 0.005   # published to 2 dp
TOL_SD   <- 0.005   # published to 3 dp

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

obs_mean <- tapply(d$resp, d$item, mean)[ITEMS]
obs_sd   <- tapply(d$resp, d$item, sd)[ITEMS]

cat(sprintf("%-5s %9s %9s %8s | %9s %9s %8s\n",
            "item", "pub_mean", "obs_mean", "diff", "pub_sd", "obs_sd", "diff"))
for (it in ITEMS)
    cat(sprintf("%-5s %9.2f %9.4f %8.4f | %9.3f %9.4f %8.4f\n",
                it, PUB_MEAN[[it]], obs_mean[[it]], obs_mean[[it]] - PUB_MEAN[[it]],
                PUB_SD[[it]], obs_sd[[it]], obs_sd[[it]] - PUB_SD[[it]]))

worst_m <- max(abs(obs_mean - PUB_MEAN[ITEMS]))
worst_s <- max(abs(obs_sd   - PUB_SD[ITEMS]))
cat(sprintf("\nlargest deviation: mean %.4f (tol %.3f), sd %.4f (tol %.3f)\n",
            worst_m, TOL_MEAN, worst_s, TOL_SD))

# Cross-assignment check: is the observed vector closer to the published vector
# under the identity mapping than under any of the other 119 permutations?
perms <- function(v) if (length(v) <= 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
cost <- sapply(perms(ITEMS), function(p)
    sum(abs(obs_mean[p] - PUB_MEAN[ITEMS])) + sum(abs(obs_sd[p] - PUB_SD[ITEMS])))
best <- perms(ITEMS)[[which.min(cost)]]
cat("best-fitting permutation of item codes onto the published rows:",
    paste(best, collapse = " "), "\n")
cat("identity is uniquely best:",
    identical(best, ITEMS) && sum(cost == min(cost)) == 1, "\n")

# What this does NOT establish: EQ and EQ2 each carry two literal wordings
# (name-question in NC trials, color-question in CN trials); this route pins
# which CODE is the first vs. second explicit question, not which of the two
# dimension wordings a given respondent's trial used -- that comes from the
# paper's fixed NWCWW / CWNWW sequences and the cov_pattern column. AQ, AQ2 and
# AQ3 share one identical literal question ("What about this?"), so nothing here
# needs to tell their wording apart -- only their position, which it does.

ok <- worst_m <= TOL_MEAN && worst_s <= TOL_SD &&
      identical(best, ITEMS) && sum(cost == min(cost)) == 1
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
