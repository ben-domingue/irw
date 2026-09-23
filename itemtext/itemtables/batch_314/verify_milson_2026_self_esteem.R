# verify_milson_2026_self_esteem.R -- batch_314, from references/verify_template.R.
#
# CLAIM: Rosenburg_esteem_<n> carries RSES item <n> in the COMMONLY CIRCULATED
# order (1 satisfied, 2 no good, 3 good qualities, 4 as well as most, 5 not much
# to be proud of, 6 useless, 7 person of worth, 8 more respect, 9 failure,
# 10 positive attitude; negatively worded = {2,5,6,8,9}), NOT in the order printed
# on the rights holder's own UMD sheet (1 person of worth, 2 good qualities,
# 3 failure, ..., 10 no good; negatively worded = {3,5,8,9,10}); and resp is
# stored already reverse-scored so that higher = higher self-esteem on every item.
# The deposit (figshare 32113705) carries no labels, so these are data checks.
#
# Evidence (all from the live table):
#   A. polarity-class structure: of the 126 distinct 5/5 splits of the 10 items,
#      rank the within-class-minus-between-class mean correlation. The claimed
#      split should rank near the top and beat the UMD-sheet split.
#   B. marker: RSES item 8 ("I wish I could have more respect for myself") is the
#      scale's well-known weakest item -- lowest item-rest r -- at position 8.
#      (Position 8 is item 8 under BOTH orders, so B checks direction/order
#      consistency, not the choice between orders.)
#   C. "I feel that I have a number of good qualities" is the most-endorsed item
#      in nearly every RSES sample: under the claim it is position 3 and should
#      have the highest mean; under the UMD order position 3 is "failure" and
#      position 2 (1.82 here) would be "good qualities".
#   D. direction: under higher = higher self-esteem, item 8's stored low end
#      means AGREE with "wish more respect" -- the item's usual majority response.
# Does NOT establish: order WITHIN a polarity class beyond positions 3 and 8.

suppressMessages(library(irw))
TABLE <- "milson_2026_self_esteem"
d <- irw::irw_fetch(TABLE)
codes <- paste0("Rosenburg_esteem_", 1:10)
w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
x <- w[, codes]
R <- cor(x, use = "pairwise.complete.obs")

split_score <- function(neg) {
  pos <- setdiff(1:10, neg)
  within <- c(R[neg, neg][upper.tri(R[neg, neg])], R[pos, pos][upper.tri(R[pos, pos])])
  mean(within) - mean(R[neg, pos])
}
splits <- combn(10, 5, simplify = FALSE)
splits <- splits[sapply(splits, function(s) 1 %in% s)]   # 126 distinct partitions
sc <- sapply(splits, function(s) split_score(setdiff(1:10, s)))
rank_of <- function(neg) {
  key <- if (1 %in% neg) neg else setdiff(1:10, neg)
  i <- which(sapply(splits, function(s) identical(sort(s), sort(key))))
  sum(sc > sc[i]) + 1
}
claim <- c(2, 5, 6, 8, 9); umd <- c(3, 5, 8, 9, 10)
cat("A. polarity split (within - between mean r), of", length(splits), "partitions\n")
cat(sprintf("   claimed {2,5,6,8,9}: %.3f  rank %d\n", split_score(claim), rank_of(claim)))
cat(sprintf("   UMD-sheet {3,5,8,9,10}: %.3f  rank %d\n", split_score(umd), rank_of(umd)))
best <- setdiff(1:10, splits[[which.max(sc)]])
cat(sprintf("   best split: {%s} %.3f\n", paste(best, collapse = ","), max(sc)))

tot <- rowSums(x)
irest <- sapply(1:10, function(i) cor(x[[i]], tot - x[[i]], use = "complete.obs"))
m <- colMeans(x, na.rm = TRUE)
cat("\nitem   mean  item-rest r\n")
for (i in 1:10) cat(sprintf("%4d  %5.2f  %6.3f\n", i, m[i], irest[i]))

p8_agree <- mean(x[[8]] <= 2, na.rm = TRUE)
cat(sprintf("\nD. item 8 share at resp 1-2 (= agree under claim): %.3f\n", p8_agree))

ok <- c(A = rank_of(claim) <= 6 && split_score(claim) > split_score(umd),
        B = which.min(irest) == 8,
        C = which.max(m) == 3,
        D = p8_agree > 0.5)
print(ok)
cat("Not established: order within each polarity class except positions 3 and 8.\n")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
