# verify_weatherspoon_2015_pediatricians_freq.R
#
# CLAIM: item code Q12_Na carries the wording of row N of Question 12 in the
# study's S1 Document (Physician Survey -- the same questionnaire was given to
# family physicians and pediatricians, per the S1 Document caption), and
# resp 5..1 = Always / Most of the time / Occasionally / Rarely / Never.
#
# FALSIFIABLE PREDICTION: Table 3 of the paper (10.1371/journal.pone.0119855.t003,
# "Percentage distribution of techniques used routinely by pediatricians and mean
# Likert scale scores") publishes, per NAMED technique, the sample size n and the
# full five-cell percent distribution over Always(5)/Most of the Time(4)/
# Occasionally(3)/Rarely(2)/Never(1). Table 3 orders its rows by domain, not by
# survey item number, so the pairing below is by wording, not by position.
# If any two item_texts were swapped, those two items' observed distribution
# vectors would no longer match the published row carrying their wording.
# All 17 published vectors are distinct, so this pins every item individually.
# It also pins the option->resp direction: reversing the anchors would mirror
# every published vector (e.g. item 14 "Use video or DVD",
# 0.00/2.07/5.70/18.13/74.09, would have to read 74.09/18.13/5.70/2.07/0.00).

suppressMessages(library(irw))

TABLE <- "weatherspoon_2015_pediatricians_freq"

# Paper Table 3, keyed by survey item number. c(n, %Always, %Most, %Occ, %Rarely, %Never)
PUB <- list(
  "1"  = c(192,  3.13, 24.48, 43.23, 23.44,  5.73),  # Ask patients to repeat back information or instructions
  "2"  = c(192, 14.06, 59.38, 21.35,  3.13,  2.08),  # Speak slowly
  "3"  = c(190,  9.47, 61.58, 21.05,  6.32,  1.58),  # Limit number of concepts presented at a time to 2-3
  "4"  = c(192,  7.29, 20.31, 32.81, 29.69,  9.90),  # Ask patients to tell you what they will do at home
  "5"  = c(194, 32.99, 60.31,  4.64,  1.03,  1.03),  # Use simple language
  "6"  = c(193, 13.99, 38.86, 21.24, 15.03, 10.88),  # Read instructions out loud
  "7"  = c(191, 14.14, 42.93, 34.03,  6.81,  2.09),  # Hand out printed materials
  "8"  = c(192,  4.69, 34.90, 28.13, 19.79, 12.50),  # Underline key points on print materials
  "9"  = c(193, 10.88, 50.78, 31.09,  5.70,  1.55),  # Write or print out instructions
  "10" = c(192,  3.65, 21.35, 47.92, 22.40,  4.69),  # Draw pictures or use printed illustrations
  "11" = c(193,  1.04,  8.29, 26.42, 38.86, 25.39),  # Use models or x-rays to explain
  "12" = c(192,  2.08, 20.83, 55.73, 17.19,  4.17),  # Refer patients to the Internet or other sources
  "13" = c(192,  3.13, 11.46, 33.85, 32.81, 18.75),  # Ask office staff to follow-up with patients
  "14" = c(193,  0.00,  2.07,  5.70, 18.13, 74.09),  # Use video or DVD
  "15" = c(194,  2.58,  9.28, 43.81, 26.29, 18.04),  # Follow-up with patients by telephone
  "16" = c(194,  1.55,  6.19, 26.29, 32.99, 32.99),  # Ask patients whether they would like a family member
  "17" = c(189, 28.57, 20.11, 21.69, 20.63,  8.99)   # Use a translator or interpreter when needed
)
TOL <- 0.02  # published to 2dp

d <- irw::irw_fetch(TABLE)
worst <- 0; bad_n <- 0
# Also check that no OTHER published row fits an item better than its own --
# i.e. that the assignment is unique, not merely consistent.
obs_mat <- matrix(NA_real_, 17, 5)
cat(sprintf("%-9s %4s %4s | %s\n", "item", "n", "pubn",
            "published vs observed %  (5 / 4 / 3 / 2 / 1)"))
for (i in 1:17) {
  it <- paste0("Q12_", i, "a")
  r  <- d$resp[d$item == it]
  n  <- length(r)
  obs <- sapply(5:1, function(k) 100 * sum(r == k) / n)
  obs_mat[i, ] <- obs
  pub <- PUB[[as.character(i)]]
  if (n != pub[1]) bad_n <- bad_n + 1
  dev <- max(abs(obs - pub[2:6])); worst <- max(worst, dev)
  cat(sprintf("%-9s %4d %4d | pub %s\n%-9s %9s | obs %s   maxdiff %.2f\n",
              it, n, pub[1], paste(sprintf("%6.2f", pub[2:6]), collapse = " "),
              "", "", paste(sprintf("%6.2f", obs), collapse = " "), dev))
}

# Uniqueness: for each item, is its own published row the closest of all 17?
pub_mat <- t(sapply(1:17, function(i) PUB[[as.character(i)]][2:6]))
amb <- 0
for (i in 1:17) {
  dists <- apply(pub_mat, 1, function(p) max(abs(obs_mat[i, ] - p)))
  if (which.min(dists) != i) amb <- amb + 1
  second <- min(dists[-i])
  if (second <= TOL) amb <- amb + 1   # another published row also fits within tolerance
}
cat(sprintf("\nitems with n mismatching the paper: %d of 17\n", bad_n))
cat(sprintf("largest percentage-point deviation across 17 items x 5 cells: %.2f (tolerance %.2f)\n",
            worst, TOL))
cat(sprintf("items whose own published row is NOT the unique best fit: %d of 17\n", amb))
cat("This route distinguishes every item from every other (all 17 published vectors\n",
    "are distinct, checked above) and fixes the anchor order. It does NOT independently\n",
    "verify the exact wording transcribed from the image-only S1 Document, only which\n",
    "survey row each item code refers to.\n", sep = "")

cat(if (worst <= TOL && bad_n == 0 && amb == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
