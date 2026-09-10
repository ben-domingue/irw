# verify_pang_2023_behavioral_intent.R
#
# What is being verified
# ----------------------
# 1. item_01..item_05 -> Q40..Q44 of the S1 "Data for CFA" workbook.
#    data/pang_2023_nev_adoption.py assigns the IRW codes POSITIONALLY
#    (`col_map = {c: f"item_{i:02d}" ...}` over `item_cols[35:40]`), so the code
#    keeps no trace of the source column. The falsifiable prediction is that the
#    live per-item x per-level response counts reproduce the source columns
#    CELL FOR CELL, in that order. All five source distributions are mutually
#    distinct, so a match distinguishes every item from every other item.
#
# 2. Anchor direction. The paper's Methods says "1 point (strongly disagree) to
#    5 points (strongly agree)", but the S2 questionnaire lists every Likert
#    block agree-first ("Definitely agree / Agree / Neither / Disagree /
#    Definitely disagree"), and the survey platform numbered options in display
#    order. Tested on the live cov_age column, whose S2 options are
#    "Under 30 / 31-40 / 41-50 / Above 50": display-order coding predicts codes
#    1 and 2 dominate (sample recruited at ages 20-40); the reversed reading
#    predicts "Above 50" is the modal category.
#
# Hard-coded values are read off S1 File (10.1371/journal.pone.0285815.s001);
# they cannot change. Only the live IRW data is fetched.

suppressMessages(library(irw))
TABLE <- "pang_2023_behavioral_intent"

# S1 workbook, counts of values 1..5 in each BI column (headers quoted).
SRC <- rbind(
  item_01 = c(65, 154,  76, 13,  1),  # "40. I probably will drive an NEV in the future?"
  item_02 = c(45,  83, 111, 58, 12),  # "41. I am driving and will continue to drive an NEV?"
  item_03 = c(44, 113, 122, 27,  3),  # "42. I recommend others to drive an NEV?"
  item_04 = c(99, 149,  52,  6,  3),  # "43. I will switch to an NEV if they are safer and more reliable?"
  item_05 = c(101,131,  66,  9,  2))  # "44. ... if they are smarter and technology-intensive?"
colnames(SRC) <- 1:5

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
OBS <- table(factor(d$item, levels = rownames(SRC)), factor(d$resp, levels = 1:5))
OBS <- matrix(as.integer(OBS), nrow = 5, dimnames = dimnames(SRC))

cat("-- per-item response counts: S1 source column (src) vs live IRW table (obs) --\n")
cat(sprintf("%-8s %-22s %-22s\n", "item", "src 1..5", "obs 1..5"))
for (i in rownames(SRC))
  cat(sprintf("%-8s %-22s %-22s  %s\n", i,
              paste(SRC[i, ], collapse = ","), paste(OBS[i, ], collapse = ","),
              if (all(SRC[i, ] == OBS[i, ])) "match" else "MISMATCH"))
cells_ok <- sum(SRC == OBS)
cat(sprintf("\ncells matching: %d / %d\n", cells_ok, length(SRC)))

# The match is only informative if the five source rows differ from each other.
pairs_same <- 0
for (i in 1:4) for (j in (i + 1):5) if (all(SRC[i, ] == SRC[j, ])) pairs_same <- pairs_same + 1
cat(sprintf("source rows identical to another source row: %d of 10 pairs\n", pairs_same))

# Anchor direction, from the live covariate.
age <- table(factor(as.numeric(d$cov_age[!duplicated(d$id)]), levels = 1:4))
cat(sprintf("\ncov_age counts (S2 option order Under 30 / 31-40 / 41-50 / Above 50): %s\n",
            paste(as.integer(age), collapse = ", ")))
cat(sprintf("share in codes 1-2 (the recruited 20-40 band): %.1f%%\n",
            100 * sum(age[1:2]) / sum(age)))
display_order <- sum(age[1:2]) / sum(age) > 0.8

cat(sprintf("\nBI item means (live): %s\n",
            paste(sprintf("%s=%.2f", rownames(SRC), rowSums(OBS * col(OBS)) / rowSums(OBS)),
                  collapse = "  ")))
cat("Under agree-first coding these read: strongest endorsement for item_04/item_05\n",
    "(conditional switching) and item_01 (future intent), weakest for item_02\n",
    "(\"I am driving ... an NEV\") in a sample of POTENTIAL users. The reversed\n",
    "reading makes current NEV ownership the most-endorsed BI item.\n", sep = "")

cat("\nNot established by this script: nothing ties the wording to the Chinese\n",
    "original (S2 File contains only English), and the option_text direction rests\n",
    "on the covariate coding plus content, not on a statement in the paper --\n",
    "the paper's own Methods sentence asserts the opposite direction.\n", sep = "")

cat(if (cells_ok == length(SRC) && pairs_same == 0 && display_order)
      "VERDICT: PASS\n" else "VERDICT: FAIL\n")
