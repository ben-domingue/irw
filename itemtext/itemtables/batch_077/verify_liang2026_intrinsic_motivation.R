# Step 5b verification for liang2026_intrinsic_motivation.
#
# CLAIM UNDER TEST: item code im_k carries the wording of item k of the
# Intrinsic Motivation block of Table 1 in Liang & Wang (2026), PLOS ONE
# 21(3): e0345759 (doi:10.1371/journal.pone.0345759).
#
# ROUTE 1 (per-item descriptive statistics). The paper's Table 8, "Descriptive
# statistics for exercise motivation items (N = 45)", prints a mean AND an SD
# for each of the ten numbered items. Those are a falsifiable prediction about
# every single item: if item_text for any two items were swapped, the (mean, SD)
# pair would land on the wrong code.
#
# The (mean, SD) pair is what makes this decisive rather than partial. Items 2
# and 4 both have mean 4.20 -- the means alone tie -- and items 3 and 5 both
# have SD 0.830. Neither statistic separates all five on its own; together they
# assign each item a unique published row.
#
# The option axis (option_text <-> resp) is verified separately, by route 9,
# against the deposit's own paired label/integer columns in S2 Data.

suppressMessages(library(irw))

TABLE <- "liang2026_intrinsic_motivation"
ITEMS <- paste0("im_", 1:5)

# Liang & Wang (2026) Table 1 wording, in the order Table 1 numbers it.
WORDING <- c(
  "Using the app makes me more willing to exercise.",
  "I would use the app to learn more about sports if time permits.",
  "Learning new knowledge in the app brings me happiness.",
  "Through the app, I found new training methods/content.",
  "Knowledge from the app inspires my confidence to participate.")

# Published Table 8, Intrinsic Motivation rows 1-5.
PUB_MEAN <- c(4.11, 4.20, 4.36, 4.20, 4.24)
PUB_SD   <- c(0.885, 0.815, 0.830, 0.842, 0.830)
PUB_SUBSCALE_MEAN <- 4.22       # Table 8 "Subscale Average"
PUB_ALPHA <- 0.914              # Table 2 / Measures text, intrinsic subscale
TOL_MEAN <- 0.02
TOL_SD   <- 0.005

d <- as.data.frame(irw::irw_fetch(TABLE))
stopifnot(setequal(unique(d$item), ITEMS))

obs_mean <- sapply(ITEMS, function(i) mean(d$resp[d$item == i]))
obs_sd   <- sapply(ITEMS, function(i) sd(d$resp[d$item == i]))

cat("Route 1 -- per-item M and SD, live table vs Liang & Wang (2026) Table 8\n\n")
cat(sprintf("%-6s %8s %8s %8s   %8s %8s %8s\n",
            "item", "pub M", "obs M", "dM", "pub SD", "obs SD", "dSD"))
for (k in 1:5)
  cat(sprintf("%-6s %8.2f %8.4f %8.4f   %8.3f %8.4f %8.4f\n",
              ITEMS[k], PUB_MEAN[k], obs_mean[k], obs_mean[k] - PUB_MEAN[k],
              PUB_SD[k], obs_sd[k], obs_sd[k] - PUB_SD[k]))

worst_m <- max(abs(obs_mean - PUB_MEAN))
worst_s <- max(abs(obs_sd - PUB_SD))
cat(sprintf("\nlargest |dM| = %.4f (tol %.2f);  largest |dSD| = %.4f (tol %.3f)\n",
            worst_m, TOL_MEAN, worst_s, TOL_SD))

# --- Uniqueness: does the (M, SD) pair pin EVERY item, or only some? ---
# For each live item, find which published rows it is compatible with.
cat("\nUniqueness of the assignment (which published rows each live item matches):\n")
unique_ok <- TRUE
for (k in 1:5) {
  hits <- which(abs(obs_mean[k] - PUB_MEAN) <= TOL_MEAN &
                abs(obs_sd[k]   - PUB_SD)   <= TOL_SD)
  cat(sprintf("  %-6s -> published item(s) %s   [%s]\n", ITEMS[k],
              paste(hits, collapse = ","),
              if (identical(hits, k)) "unique, correct" else "AMBIGUOUS/WRONG"))
  if (!identical(as.integer(hits), as.integer(k))) unique_ok <- FALSE
}
cat("\nWhy the pair is needed: published means tie at 4.20 for items 2 and 4,\n",
    "and published SDs tie at 0.830 for items 3 and 5. Mean alone or SD alone\n",
    "would leave two pairs unresolved; together they are one-to-one.\n", sep = "")

# --- Corroboration that this is the INTRINSIC block, not the extrinsic one ---
sub_mean <- mean(obs_mean)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
w <- w[, paste0("resp.", ITEMS)]
kk <- ncol(w)
alpha <- kk / (kk - 1) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
cat(sprintf("\nSubscale average: observed %.4f vs published %.2f (Table 8)\n",
            sub_mean, PUB_SUBSCALE_MEAN))
cat(sprintf("Cronbach's alpha: observed %.4f vs published %.3f (intrinsic subscale)\n",
            alpha, PUB_ALPHA))

sub_ok   <- abs(sub_mean - PUB_SUBSCALE_MEAN) <= TOL_MEAN
alpha_ok <- abs(alpha - PUB_ALPHA) <= 0.01

cat("\nWhat this does NOT establish: the option_text <-> resp mapping. That axis\n",
    "is settled separately and decisively by route 9 against S2 Data's paired\n",
    "label/integer columns (see provenance), not by anything in this script.\n", sep = "")

ok <- (worst_m <= TOL_MEAN) && (worst_s <= TOL_SD) && unique_ok && sub_ok && alpha_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
