# verify_huang_2023_d_scale.R -- Step 5b evidence, route 6 (keying polarity).
#
# CLAIM UNDER TEST: d1..d8 are the Index of Well-Being's general-affect items A..H
# in the instrument's published order, and d9 is the life-satisfaction item.
#
# The Chinese handbook rendering of the scale (心理学网 reproduction of the
# 幸福感指数量表) prints all eight affect pairs positive-adjective-first and then
# states: "注：在实际问卷中将A，C，F，G项颠倒" -- in the actual questionnaire items
# A, C, F, and G are flipped. That is a FALSIFIABLE prediction about the raw data:
# under the claimed mapping, exactly d1, d3, d6, d7 (= A, C, F, G) must be keyed
# high = good, and d2, d4, d5, d8 (= B, D, E, H) must be keyed high = bad.
# A wrong assignment of columns to letters breaks the partition immediately.
# The paper's own example anchor ("1 = tiring, 7 = interesting", PLOS ONE
# 10.1371/journal.pone.0290452 sec. 2.2.2) independently fixes the flipped
# direction for the boring/interesting pair.
#
# This is NOT a plumbing check: validate_items.R already matched the item and
# resp sets. What is tested here is which words go with which code.

suppressMessages(library(irw))

TABLE <- "huang_2023_d_scale"

# Predicted polarity class under the shipped mapping (+1 = high score is the
# positive pole, -1 = high score is the negative pole).
PRED <- c(d1 = +1, d2 = -1, d3 = +1, d4 = -1, d5 = -1,
          d6 = +1, d7 = +1, d8 = -1, d9 = +1)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, paste0("d", 1:9)]
w <- w[complete.cases(w), ]
cat(sprintf("respondents with complete d1-d9: %d\n\n", nrow(w)))

R <- cor(w)
cat("correlation matrix (live data):\n")
print(round(R, 2))

# Observed polarity: sign each item against the score keyed to the PREDICTED
# positive class, computed WITHOUT that item (so the test is not circular for it).
pos <- names(PRED)[PRED > 0]
neg <- names(PRED)[PRED < 0]
key <- sapply(colnames(w), function(v) PRED[[v]])
scored <- sweep(as.matrix(w), 2, key, `*`)   # + = pro-wellbeing direction
tot <- rowSums(scored)
cat("\ncorrected item-total r against the keyed total (predicted sign in parens):\n")
obs <- setNames(numeric(9), colnames(w))
for (v in colnames(w)) {
    obs[v] <- cor(scored[, v], tot - scored[, v])
    cat(sprintf("  %-3s %+6.3f   (predicted %+d)\n", v, obs[v], PRED[[v]]))
}
ok_polarity <- all(obs > 0.15)

# Raw-direction partition, stated explicitly: which items correlate positively
# with d1 (= A, boring/interesting, the item the paper's own example pins).
cat("\nraw correlations with d1 (the item the paper's '1 = tiring, 7 = interesting'\n",
    "example fixes as flipped, i.e. high = good):\n", sep = "")
for (v in setdiff(colnames(w), "d1"))
    cat(sprintf("  r(d1,%s) = %+5.2f   -> same polarity class as d1: %s\n",
                v, R["d1", v], ifelse(R["d1", v] > 0, "YES", "no")))
obs_pos <- c("d1", setdiff(colnames(w), "d1")[R["d1", setdiff(colnames(w), "d1")] > 0])
cat(sprintf("\nobserved high=good class: {%s}\n", paste(sort(obs_pos), collapse = ", ")))
cat(sprintf("predicted (A,C,F,G flipped + life satisfaction): {%s}\n",
            paste(sort(pos), collapse = ", ")))
ok_partition <- setequal(obs_pos, pos)

# Supporting, for d9 only: the life-satisfaction item is a different question
# format from the eight semantic-differential items, so it should be the least
# coherent with the rest. Mean |r| with the other eight.
cat("\nmean |r| with the other eight items (life-satisfaction item expected lowest):\n")
mabs <- sapply(colnames(w), function(v) mean(abs(R[v, setdiff(colnames(w), v)])))
for (v in names(sort(mabs))) cat(sprintf("  %-3s %.3f\n", v, mabs[v]))
ok_d9 <- names(which.min(mabs)) == "d9"
cat(sprintf("lowest is %s (%.3f) vs next-lowest %s (%.3f); shipped life-satisfaction\nitem is d9 -> %s. Margin is small, so this is corroboration, not proof, and it\nis NOT part of the verdict below.\n",
            names(sort(mabs))[1], sort(mabs)[1], names(sort(mabs))[2], sort(mabs)[2],
            ifelse(ok_d9, "consistent", "INCONSISTENT")))

cat("\n--- what this does NOT establish ---\n")
cat("Polarity partitions the eight affect items into {A,C,F,G} and {B,D,E,H} but does\n")
cat("not order items WITHIN either class: any permutation of d1/d3/d6/d7 among\n")
cat("themselves, or of d2/d4/d5/d8 among themselves, would reproduce every number\n")
cat("above. That within-class order rests on the assumption that the .sav's d1..d8\n")
cat("columns follow the instrument's published A..H order. Hence PARTIAL, not VERIFIED.\n\n")

cat(if (ok_polarity && ok_partition) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
