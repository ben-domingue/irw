# verify_weatherspoon_2015_family_physicians_freq.R
#
# CLAIM: item code Q12_Na carries the wording of row N of Question 12 in the
# study's S1 Document (Physician Survey), and resp 5..1 = Always / Most of the
# time / Occasionally / Rarely / Never.
#
# FALSIFIABLE PREDICTION: Table 2 of the paper (10.1371/journal.pone.0119855.t002,
# "Percentage distribution of techniques used routinely by family physicians and
# mean Likert scale scores") publishes, per named technique, n and the full
# five-cell percent distribution over Always/Most of the time/Occasionally/
# Rarely/Never. If any two item_texts were swapped, the distribution vector for
# those two items would no longer match the published row for their wording.
# All 17 published vectors are distinct, so this pins every item individually.
# It also pins the option->resp direction: reversing the anchors would turn
# every published vector back-to-front (e.g. Q12_14a "Use video or DVD",
# 0.0/0.0/8.82/23.53/67.65, becomes its own mirror image).

suppressMessages(library(irw))

TABLE <- "weatherspoon_2015_family_physicians_freq"

# Paper Table 2, keyed by survey item number. c(n, %Always, %Most, %Occ, %Rarely, %Never)
PUB <- list(
  "1"  = c(68,  2.94, 29.41, 48.53, 13.24,  5.88),  # Ask patients to repeat back information or instructions
  "2"  = c(67, 10.45, 55.22, 28.36,  4.48,  1.49),  # Speak slowly
  "3"  = c(67,  7.46, 65.67, 23.88,  1.49,  1.49),  # Limit number of concepts presented at a time to 2-3
  "4"  = c(68,  1.47, 29.41, 48.53, 10.29, 10.29),  # Ask patients to tell you what they will do at home
  "5"  = c(67, 38.81, 52.24,  7.46,  0.00,  1.49),  # Use simple language
  "6"  = c(68, 19.12, 38.24, 26.47,  8.82,  7.35),  # Read instructions out loud
  "7"  = c(68, 22.06, 33.82, 32.35,  8.82,  2.94),  # Hand out printed materials
  "8"  = c(68, 10.29, 20.59, 38.24, 17.65, 13.24),  # Underline key points on print materials
  "9"  = c(68, 25.00, 36.76, 35.29,  0.00,  2.94),  # Write or print out instructions
  "10" = c(69,  4.35, 27.54, 47.83, 14.49,  5.80),  # Draw pictures or use printed illustrations
  "11" = c(69,  2.90,  7.25, 43.48, 27.54, 18.84),  # Use models or x-rays to explain
  "12" = c(69,  2.90, 34.78, 46.38, 10.14,  5.80),  # Refer patients to the Internet or other sources
  "13" = c(68,  2.94, 14.71, 32.35, 32.35, 17.65),  # Ask office staff to follow-up with patients
  "14" = c(68,  0.00,  0.00,  8.82, 23.53, 67.65),  # Use video or DVD
  "15" = c(68,  0.00,  8.82, 38.24, 35.29, 17.65),  # Follow-up with patients by telephone
  "16" = c(68,  0.00, 11.76, 51.47, 26.47, 10.29),  # Ask patients whether they would like a family member
  "17" = c(69, 27.54, 21.74, 23.19, 20.29,  7.25)   # Use a translator or interpreter when needed
)
TOL <- 0.02  # published to 2dp

d <- irw::irw_fetch(TABLE)
worst <- 0; bad_n <- 0
cat(sprintf("%-9s %4s %4s | %s\n", "item", "n", "pubn",
            "published vs observed %  (5 / 4 / 3 / 2 / 1)"))
for (i in 1:17) {
  it <- paste0("Q12_", i, "a")
  r  <- d$resp[d$item == it]
  n  <- length(r)
  obs <- sapply(5:1, function(k) 100 * sum(r == k) / n)
  pub <- PUB[[as.character(i)]]
  if (n != pub[1]) bad_n <- bad_n + 1
  dev <- max(abs(obs - pub[2:6])); worst <- max(worst, dev)
  cat(sprintf("%-9s %4d %4d | pub %s\n%-9s %9s | obs %s   maxdiff %.2f\n",
              it, n, pub[1], paste(sprintf("%6.2f", pub[2:6]), collapse = " "),
              "", "", paste(sprintf("%6.2f", obs), collapse = " "), dev))
}
cat(sprintf("\nitems with n mismatching the paper: %d of 17\n", bad_n))
cat(sprintf("largest percentage-point deviation across 17 items x 5 cells: %.2f (tolerance %.2f)\n",
            worst, TOL))
cat("This route distinguishes every item from every other (all 17 published vectors\n",
    "are distinct) and fixes the anchor order. It does NOT independently verify the\n",
    "exact wording transcribed from the S1 Document image, only which row each code is.\n", sep = "")

cat(if (worst <= TOL && bad_n == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
