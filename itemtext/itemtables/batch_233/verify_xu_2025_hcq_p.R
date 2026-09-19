# verify_xu_2025_hcq_p.R -- Step 5b, route 1 (per-item descriptive statistics)
# plus route 3 (published totals / subscale totals, which settles the stored
# reverse-scoring direction that the shipped option_text depends on).
#
# CLAIM UNDER TEST: live item Qn carries the wording of HCQ-Pn in Table 1 of
# Xu et al. (2025) PeerJ 13:e19562, and the 23 items the paper names as
# reverse-scored are stored ALREADY reversed, so their shipped anchors run
# 1 = Strongly agree ... 6 = Strongly disagree.
#
# FALSIFIABLE PREDICTION: the paper's Table 3 prints Mean and SD for each of
# HCQ-P1..P49. If the Qn <-> HCQ-Pn tie were permuted, those 49 (mean, SD)
# pairs would land on the wrong items. All 49 pairs are distinct in the paper,
# so the route distinguishes every item from every other item.
#
# Export note: irw_fetch() is used deliberately. This table is 360 x 49 =
# 17,640 rows; irw_table_sets() returns sets only and cannot supply means.

suppressMessages(library(irw))

TABLE <- "xu_2025_hcq_p"

# Xu et al. (2025) PeerJ 13:e19562, Table 3 ("Mean, standard deviation and ICC
# of items (n = 360)"), rows HCQ-P1 .. HCQ-P49 in numeric order.
MEAN <- c(
  4.96, 4.62, 4.56, 5.35, 4.86, 3.41, 3.87, 5.19, 5.31, 5.60,
  5.01, 4.54, 4.69, 4.49, 4.92, 4.84, 5.03, 3.91, 4.72, 5.35,
  4.91, 4.42, 5.27, 3.79, 1.79, 2.62, 4.12, 5.18, 4.20, 4.66,
  4.31, 4.45, 4.54, 4.53, 5.03, 5.15, 5.16, 4.60, 2.01, 4.65,
  3.78, 4.88, 4.81, 5.21, 4.93, 4.85, 5.15, 4.83, 5.05)
SD <- c(
  1.400, 1.823, 1.658, 1.119, 1.636, 1.960, 2.113, 1.183, 1.248, 0.862,
  1.438, 1.785, 1.704, 1.773, 1.489, 1.530, 1.486, 1.890, 1.679, 1.129,
  1.636, 1.839, 1.263, 2.026, 1.316, 1.676, 1.841, 1.168, 1.790, 1.561,
  1.618, 1.661, 1.609, 1.650, 1.288, 1.286, 1.214, 1.622, 1.319, 1.594,
  1.884, 1.340, 1.541, 1.130, 1.471, 1.395, 1.284, 1.636, 1.239)

# Table 4 ("The scores and reliability"), total and subscale Mean / SD.
TOT_MEAN <- 224.12; TOT_SD <- 38.421
SUB <- list(
  "Physiological" = list(items = c(1,2,5,12,14,16,19,27,29,31,34),        m = 50.20, s = 11.55),
  "Psychospiritual" = list(items = c(3,7,9,15,17,22,35,36,40,41,43,45,46), m = 61.31, s = 11.90),
  "Sociocultural" = list(items = c(4,6,8,10,13,20,23,24,26,28,37,44,47,48), m = 66.80, s = 10.01),
  "Environmental" = list(items = c(11,18,21,25,30,32,33,38,42,49),         m = 43.79, s = 9.51))

TOL_M <- 0.02; TOL_S <- 0.02; TOL_TOT <- 0.05

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
codes <- paste0("Q", 1:49)
obs_m <- tapply(d$resp, d$item, mean)[codes]
obs_s <- tapply(d$resp, d$item, sd)[codes]

cat("=== Route 1: per-item mean / SD vs paper Table 3 ===\n")
cat(sprintf("%-6s %-9s %9s %9s %9s %9s %8s %8s\n",
            "item", "paper", "pub_mean", "obs_mean", "pub_sd", "obs_sd", "d_mean", "d_sd"))
for (i in 1:49)
  cat(sprintf("%-6s %-9s %9.2f %9.3f %9.3f %9.3f %8.3f %8.3f\n",
              codes[i], paste0("HCQ-P", i), MEAN[i], obs_m[i], SD[i], obs_s[i],
              obs_m[i] - MEAN[i], obs_s[i] - SD[i]))
worst_m <- max(abs(obs_m - MEAN)); worst_s <- max(abs(obs_s - SD))
cat(sprintf("\nlargest |mean| deviation: %.4f (tol %.2f)\n", worst_m, TOL_M))
cat(sprintf("largest |SD|   deviation: %.4f (tol %.2f)\n", worst_s, TOL_S))

# Uniqueness: does the route actually separate every item from every other?
pairs <- paste(sprintf("%.2f", MEAN), sprintf("%.3f", SD))
cat(sprintf("distinct published (mean, SD) pairs: %d of 49\n", length(unique(pairs))))
cat(sprintf("duplicated published means alone:    %d (broken by SD)\n",
            sum(duplicated(sprintf("%.2f", MEAN)))))

cat("\n=== Route 3: stored direction, via published totals ===\n")
wide <- as.data.frame(tapply(d$resp, list(as.character(d$id), as.character(d$item)), mean))
wide <- wide[, codes, drop = FALSE]
stopifnot(!anyNA(wide))
tot <- rowSums(wide[, codes])
cat(sprintf("total  : obs %.2f / %.3f  (range %d-%d)   paper %.2f / %.3f (range 144-280)\n",
            mean(tot), sd(tot), min(tot), max(tot), TOT_MEAN, TOT_SD))
tot_ok <- abs(mean(tot) - TOT_MEAN) < TOL_TOT && abs(sd(tot) - TOT_SD) < TOL_TOT &&
          min(tot) == 144 && max(tot) == 280
sub_ok <- TRUE
for (nm in names(SUB)) {
  s <- rowSums(wide[, paste0("Q", SUB[[nm]]$items), drop = FALSE])
  cat(sprintf("%-16s obs %7.2f / %6.2f   paper %7.2f / %6.2f\n",
              nm, mean(s), sd(s), SUB[[nm]]$m, SUB[[nm]]$s))
  sub_ok <- sub_ok && abs(mean(s) - SUB[[nm]]$m) < TOL_TOT && abs(sd(s) - SUB[[nm]]$s) < 0.02
}
cat("The paper sums these columns UNCHANGED and reads a higher total as greater\n",
    "comfort, so the 23 items it names as reverse-scored are already reversed in\n",
    "the stored values. That is what the shipped per-item anchor direction rests on.\n", sep = "")

cat("\nWhat this does NOT establish: the Chinese wording of the six scale anchors\n",
    "(the paper names only the English endpoints), and whether the two rows with a\n",
    "corrupt cov_age value affect anything (they do not enter resp).\n", sep = "")

cat(if (worst_m <= TOL_M && worst_s <= TOL_S && tot_ok && sub_ok &&
        length(unique(pairs)) == 49) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
