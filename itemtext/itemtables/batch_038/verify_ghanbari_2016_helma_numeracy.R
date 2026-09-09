# verify_ghanbari_2016_helma_numeracy.R
#
# CLAIM UNDER TEST: num1 = HELMA item 42 (carbohydrate arithmetic from a milk
# nutrition panel), num2 = item 43 (compute BMI for height 160 cm / weight 70 kg),
# num3 = item 44 (classify that BMI against the printed cut-off table).
#
# The S4 File scoring manual fixes the SUBSCALE ("Numeracy: 3 (item 42-44)"), and
# the SPSS file's columns are literally num1/num2/num3, so only the WITHIN-SUBSCALE
# ORDER is inferred (mapping_basis = paper_order). The paper publishes no per-item
# statistics, so the falsifiable predictions come from item CONTENT:
#
#   P1  Item 43 is a prerequisite for item 44: you classify the BMI you computed.
#       So items 43 and 44 must be far more strongly associated with each other
#       than either is with item 42, which is unrelated arithmetic.
#   P2  The dependency is ASYMMETRIC and directional. Getting 43 right should
#       almost force 44 right (just read the cut-off table), while 44 can be got
#       right without 43 (four printed alternatives, and an approximate BMI still
#       lands in the right band). So n(43 right & 44 wrong) << n(43 wrong & 44 right).
#       The reversed assignment num2=44 / num3=43 predicts the opposite imbalance.
#   P3  Difficulty ordering: item 42 (11 g x 3) is one multiplication and should be
#       the easiest; item 43 is an open-ended calculation requiring a squared metre
#       conversion and should be the hardest; item 44 is a four-option choice with a
#       guessing floor and should sit between them.
#
# Table is 1,746 rows, so irw_fetch() here is a deliberate, negligible export.

suppressMessages(library(irw))
suppressMessages(library(tidyr))

TABLE <- "ghanbari_2016_helma_numeracy"

d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "item", "resp")]
w <- as.data.frame(pivot_wider(d, names_from = item, values_from = resp))

p <- colMeans(w[, c("num1", "num2", "num3")], na.rm = TRUE)
cat("proportion correct\n")
for (i in c("num1", "num2", "num3"))
    cat(sprintf("  %-5s %.3f  (n=%d)\n", i, p[[i]], sum(!is.na(w[[i]]))))

R <- cor(w[, c("num1", "num2", "num3")], use = "pairwise.complete.obs")
cat("\ncorrelations\n")
cat(sprintf("  num2-num3 %.3f   num1-num2 %.3f   num1-num3 %.3f\n",
            R["num2", "num3"], R["num1", "num2"], R["num1", "num3"]))

a <- sum(w$num2 == 1 & w$num3 == 0, na.rm = TRUE)   # 43 right, 44 wrong
b <- sum(w$num2 == 0 & w$num3 == 1, na.rm = TRUE)   # 43 wrong, 44 right
cat(sprintf("\nasymmetry: n(num2=1 & num3=0) = %d   n(num2=0 & num3=1) = %d\n", a, b))
cat(sprintf("  P(num3=1 | num2=1) = %.3f   P(num2=1 | num3=1) = %.3f\n",
            mean(w$num3[w$num2 == 1], na.rm = TRUE),
            mean(w$num2[w$num3 == 1], na.rm = TRUE)))

P1 <- R["num2", "num3"] > max(R["num1", "num2"], R["num1", "num3"]) + 0.30
P2 <- a < b / 3
P3 <- p[["num1"]] > p[["num3"]] && p[["num3"]] > p[["num2"]]

cat(sprintf("\nP1 (43-44 dependency dominates)        : %s\n", P1))
cat(sprintf("P2 (43 implies 44, not the reverse)    : %s\n", P2))
cat(sprintf("P3 (p(42) > p(44) > p(43))             : %s\n", P3))

cat("\nNot established by this script: subscale MEMBERSHIP (that num1-num3 are HELMA\n",
    "items 42-44 at all) -- that comes from the S4 File scoring manual, which states\n",
    "'Numeracy 3 (item 42-44)', and from these being the instrument's only 0/1-scored\n",
    "items. This script tests only the order WITHIN the subscale, and it does so\n",
    "against item content rather than against any published per-item statistic,\n",
    "because the paper reports none.\n", sep = "")

cat(if (P1 && P2 && P3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
