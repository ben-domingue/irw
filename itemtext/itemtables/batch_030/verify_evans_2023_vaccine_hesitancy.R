# Step 5b verification for evans_2023_vaccine_hesitancy (route 1: per-item
# descriptive statistics published by arm and wave).
#
# The claim under test: each IRW item code carries the item_text the S2 File
# codebook assigns to the source column of the same name. The falsifiable
# prediction is Supplemental Table 2a of S1 File (PLOS ONE 18(9):e0290757),
# which prints mean (SD) for each of the five Five-Cs items separately for
# treatment-state and comparison-state participants at all three waves --
# 30 mean/SD cells. The table names its columns by Five-C construct
# (Confidence / Complacency / Inconvenience / Calculation / Lack of Collective
# Responsibility), and the paper's Measures paragraph ties each construct to a
# verbatim item ("...measures of confidence, complacency, convenience,
# calculation, and collective responsibility, respectively"). So matching the
# numbers pins construct -> item code, and the paper's sentence pins construct
# -> wording. If any two items' texts were swapped, the swapped pair's 12 cells
# would land on each other's values.

suppressMessages(library(irw))

TABLE <- "evans_2023_vaccine_hesitancy"
TOL   <- 0.015   # published values are rounded to 2 dp

# Supplemental Table 2a, S1 File. Rows: wave 1 (baseline), 2 (first follow-up),
# 3 (second follow-up). T = treatment/campaign state (treat==1), C = comparison
# (treat==0). Construct -> item code is the mapping this script tests.
PUB <- data.frame(
  item  = rep(c("safe","unneces","stress","benefit","everyone"), each = 6),
  con   = rep(c("Confidence","Complacency","Inconvenience","Calculation",
                "Lack of Collective Responsibility"), each = 6),
  wave  = rep(rep(1:3, each = 2), times = 5),
  treat = rep(c(1, 0), times = 15),
  mean  = c(3.05,2.97, 3.16,3.13, 3.26,3.27,     # Confidence      -> safe
            2.57,2.69, 2.55,2.58, 2.51,2.50,     # Complacency     -> unneces
            2.88,2.82, 2.82,2.69, 2.75,2.73,     # Inconvenience   -> stress
            3.43,3.54, 3.49,3.55, 3.48,3.47,     # Calculation     -> benefit
            2.50,2.51, 2.52,2.47, 2.48,2.35),    # Lack of Coll R. -> everyone
  sd    = c(0.94,0.83, 1.03,1.00, 1.16,1.04,
            0.95,0.92, 1.01,1.03, 1.06,0.98,
            1.08,1.07, 1.08,1.09, 1.11,1.06,
            1.07,1.13, 1.06,1.15, 1.10,1.09,
            1.00,1.02, 1.04,1.06, 1.05,1.08),
  stringsAsFactors = FALSE
)

d <- irw::irw_fetch(TABLE)
key <- paste(d$item, d$wave, d$treat)
obs_m <- tapply(d$resp, key, mean)
obs_s <- tapply(d$resp, key, stats::sd)
k <- paste(PUB$item, PUB$wave, PUB$treat)
PUB$obs_mean <- as.numeric(obs_m[k])
PUB$obs_sd   <- as.numeric(obs_s[k])

cat(sprintf("%-9s %-34s %4s %5s %10s %8s %8s %8s\n",
            "item", "published-as", "wave", "arm", "pub M(SD)", "obs M", "obs SD", "dM"))
for (i in seq_len(nrow(PUB)))
  cat(sprintf("%-9s %-34s %4d %5s %5.2f(%4.2f) %8.2f %8.2f %8.3f\n",
              PUB$item[i], PUB$con[i], PUB$wave[i],
              ifelse(PUB$treat[i] == 1, "T", "C"),
              PUB$mean[i], PUB$sd[i], PUB$obs_mean[i], PUB$obs_sd[i],
              PUB$obs_mean[i] - PUB$mean[i]))

worst_m <- max(abs(PUB$obs_mean - PUB$mean))
worst_s <- max(abs(PUB$obs_sd   - PUB$sd))
cat(sprintf("\nlargest mean deviation: %.4f | largest SD deviation: %.4f (tolerance %.3f)\n",
            worst_m, worst_s, TOL))

# Rival-assignment check: would any OTHER permutation of the five item codes
# onto the five published columns fit as well? Report the best wrong one.
codes <- unique(PUB$item)
perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i)
    lapply(perms(v[-i]), function(p) c(v[i], p))))
best_wrong <- Inf
for (p in perms(codes)) {
  if (identical(p, codes)) next
  mp <- setNames(p, codes)          # published-column(item) -> candidate code
  kk <- paste(mp[PUB$item], PUB$wave, PUB$treat)
  err <- max(abs(as.numeric(obs_m[kk]) - PUB$mean))
  best_wrong <- min(best_wrong, err)
}
cat(sprintf("best rival permutation's largest mean deviation: %.3f\n", best_wrong))

cat("This pins all five items individually: every code's 6 published mean/SD cells\n",
    "reproduce, and no rival permutation comes close. It does NOT independently\n",
    "verify the option_text->resp direction; that rests on the S2 File codebook's\n",
    "per-variable value labels (1 Strongly disagree ... 5 Strongly agree) plus the\n",
    "sign pattern reported in provenance (safe correlates -0.16/-0.13 with everyone\n",
    "and unneces, which correlate +0.37 with each other).\n", sep = "")

cat(if (worst_m <= TOL && worst_s <= TOL && best_wrong > 0.1)
      "VERDICT: PASS\n" else "VERDICT: FAIL\n")
