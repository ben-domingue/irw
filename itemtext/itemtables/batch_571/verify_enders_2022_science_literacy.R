# verify_enders_2022_science_literacy.R -- Step 5b check for batch_571.
#
# Claim: SCILIT_1..11 are the eleven statements of the S1 Appendix
# (pone.0276082.s001, 'Science literacy.') in printed order, live resp 1 = the
# respondent answered "True", 0 = "False", and the appendix's (True)/(False)
# keys are the correct answers.
#
# What the data can test: the KEYING PATTERN. Six statements are true
# (positions 1,3,4,6,9,10) and five false (2,5,7,8,11). The study's own
# Analyses.do (OSF 6a7et, lines 273-319) scores scilit_k correct when == 1 for
# exactly those six codes and when == 0 for the other five -- the same pattern.
# If the text->code mapping crossed the true/false classes, or resp 1 meant
# "False", the keyed items would score far below chance / correlate negatively
# with the rest of the test.
#
# (a) direction: under 1 = True every item scores 47-89% correct; the flip
#     would put 'The center of the Earth is very hot' at ~12%.
# (b) of all choose(11,6) = 462 ways to say which six codes are the true
#     statements, the appendix/do-file set is the unique maximiser of total %
#     correct (it is exactly the six codes with the highest P(resp = 1)).
# (c) every item, scored with that key, has a positive corrected item-rest
#     correlation.
#
# NOT established: order WITHIN the true class and within the false class
# (e.g. SCILIT_6 electrons vs SCILIT_10 father's gene). That rests on the
# appendix listing and the do-file keying following the same code order.
suppressMessages(library(irw))
TABLE <- "enders_2022_science_literacy"
TRUE_KEYED <- c(1, 3, 4, 6, 9, 10)                     # appendix (True) positions
LABEL <- c("continents moving", "radioactivity manmade", "Earth centre hot",
           "oxygen from plants", "lasers sound waves", "electrons < atoms",
           "antibiotics kill viruses", "humans with dinosaurs", "evolution",
           "father's gene", "radioactive milk boiling")

d <- as.data.frame(irw::irw_fetch(TABLE))
codes <- paste0("SCILIT_", 1:11)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- as.matrix(w[, codes])
p1 <- colMeans(X, na.rm = TRUE)
n  <- colSums(!is.na(X))
key <- ifelse(1:11 %in% TRUE_KEYED, 1, 0)
C <- sweep(X, 2, key, `==`) * 1                          # 1 = correct
pc <- colMeans(C, na.rm = TRUE)
rest <- rowSums(C, na.rm = TRUE)
rit <- sapply(1:11, function(j) cor(C[, j], rest - C[, j], use = "complete.obs"))

cat(sprintf("%-10s %-26s %5s %6s %6s %8s %8s\n", "item", "statement", "key",
            "n", "P(1)", "%correct", "r_it"))
for (j in 1:11)
  cat(sprintf("%-10s %-26s %5s %6d %6.3f %8.1f %8.3f\n", codes[j], LABEL[j],
              if (key[j] == 1) "T" else "F", n[j], p1[j], 100 * pc[j], rit[j]))

ok_a <- all(pc > 0.45) && all((1 - pc) < 0.55)
flip <- 1 - pc
cat(sprintf("\n(a) %%correct range under 1=True: %.1f-%.1f; under the flip (1=False): %.1f-%.1f\n",
            100 * min(pc), 100 * max(pc), 100 * min(flip), 100 * max(flip)))

sets <- combn(11, 6)
score <- apply(sets, 2, function(s) sum(p1[s]) + sum(1 - p1[-s]))
ours <- which(apply(sets, 2, function(s) setequal(s, TRUE_KEYED)))
rk <- rank(-score, ties.method = "min")[ours]
second <- sort(score, decreasing = TRUE)[2]
cat(sprintf("(b) total expected correct (sum over 11 items): appendix key %.3f, rank %d of %d; runner-up %.3f (margin %.3f)\n",
            score[ours], rk, length(score), second, score[ours] - second))
cat("    top-6 codes by P(resp=1):", paste(codes[order(-p1)][1:6], collapse = ", "), "\n")
ok_b <- rk == 1 && sum(score == max(score)) == 1

cat(sprintf("(c) corrected item-rest r, min %.3f max %.3f; all positive: %s\n",
            min(rit), max(rit), all(rit > 0)))
ok_c <- all(rit > 0)

cat("\nNOT established: order within the true-keyed class {1,3,4,6,9,10} and within\n",
    "the false-keyed class {2,5,7,8,11}; that rests on the appendix listing order,\n",
    "which the do-file's code-by-code keying agrees with only at the class level.\n", sep = "")
cat(if (ok_a && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
