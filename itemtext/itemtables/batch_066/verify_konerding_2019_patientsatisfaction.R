# verify_konerding_2019_patientsatisfaction.R
#
# CLAIM UNDER TEST: the mapping of paper wording -> IRW item code, i.e.
#   Tangibles       -> UpToDateEquipment
#   Reliability     -> ServiceOnTime
#   Responsiveness  -> ReactPromptly
#   Assurance       -> Polite
#   Empathy         -> PersonalAttention
#   Communication   -> RightCommunication
#   'General satisfaction' -> ServicesSatisfaction
#
# ROUTE 1 (per-item published descriptives), applied on a 7 item x 6 country
# grid rather than pooled. Konerding et al. 2019 (PLOS ONE 10.1371/journal.pone.0197924)
# Table 4 prints Mean (SD) per country for each of the six basic items, the sum
# score and 'Satisfaction', in the paper's -3..+3 coding. The live IRW table
# stores 1..7, so the prediction is  mean(live resp) - 4 == published mean.
#
# Pooled means would NOT settle this (four of the seven tie at 1.9/2.0); the
# country profile does, because all 7 six-vectors are pairwise distinct.

suppressMessages(library(irw))

TABLE <- "konerding_2019_patientsatisfaction"
COUNTRIES <- c("England", "Finland", "Germany", "Greece", "Spain", "The Netherlands")

# Table 4, "Both surveys" column, one row per country block, hard-coded.
PUBLISHED <- rbind(
  UpToDateEquipment    = c(1.7, 2.2, 2.3, 1.1, 1.8, 1.9),  # Tangibles
  ServiceOnTime        = c(1.8, 2.1, 2.3, 1.4, 1.5, 2.3),  # Reliability
  ReactPromptly        = c(1.6, 2.0, 2.2, 1.7, 1.7, 2.2),  # Responsiveness
  Polite               = c(2.2, 2.5, 2.5, 2.2, 2.2, 2.5),  # Assurance
  PersonalAttention    = c(1.9, 2.0, 2.3, 2.1, 1.9, 2.4),  # Empathy
  RightCommunication   = c(1.9, 1.9, 2.3, 1.6, 1.8, 2.2),  # Communication
  ServicesSatisfaction = c(1.7, 2.1, 1.9, 1.4, 1.7, 2.2))  # Satisfaction
colnames(PUBLISHED) <- COUNTRIES
TOL <- 0.05   # paper rounds to 1 dp

d <- irw::irw_fetch(TABLE)
obs <- tapply(d$resp - 4, list(d$item, d$cov_country), mean)
obs <- obs[rownames(PUBLISHED), COUNTRIES, drop = FALSE]

cat("published (paper Table 4, -3..+3 coding):\n"); print(PUBLISHED)
cat("\nobserved  (live mean(resp) - 4):\n"); print(round(obs, 2))
cat("\ndifference:\n"); print(round(obs - PUBLISHED, 2))

worst <- max(abs(obs - PUBLISHED))
cat(sprintf("\nlargest deviation over %d cells: %.3f (tolerance %.2f)\n",
            length(obs), worst, TOL))

# Falsification check: is the country profile actually discriminating?
best_wrong <- Inf
for (i in seq_len(nrow(PUBLISHED))) for (j in seq_len(nrow(PUBLISHED))) if (i != j)
  best_wrong <- min(best_wrong, max(abs(obs[i, ] - PUBLISHED[j, ])))
cat("best deviation attainable by ANY mis-assignment of one item to another item's\n")
cat(sprintf("published row: %.3f -- must exceed the tolerance for the route to discriminate.\n",
            best_wrong))

ok <- worst <= TOL && best_wrong > TOL
cat("Note: this pins all 7 items individually (every pairwise swap is rejected above).\n")
cat("It does NOT check option_text: the 1/7 anchors come from the .sav's own value\n")
cat("labels and levels 2-6 are unlabelled in the source, so nothing is shipped for them.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
