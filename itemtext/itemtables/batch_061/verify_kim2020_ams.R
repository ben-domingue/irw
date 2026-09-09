# verify_kim2020_ams.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the live item codes Q01..Q17 carry the Aging Males' Symptoms
# (AMS) scale items 1..17 in the instrument's canonical numbering, i.e. the
# Korean AMS wording shipped in kim2020_ams__items.csv sits on the right code.
# Nothing in the deposit labels the columns (the Dataverse .xlsx header is bare
# Q01..Q17), so the tie is an inference from the AMS's fixed item numbering and
# it has to be paid for with data.
#
# The falsifiable prediction: the AMS's published three-factor structure assigns
#   psychological     = items 6, 7, 8, 11, 13
#   somato-vegetative = items 1, 2, 3, 4, 5, 9, 10
#   sexual            = items 12, 14, 15, 16, 17
# If the shipped text were permuted across those blocks, the correlation
# structure would stop agreeing with it.
#
# What this does NOT establish: order WITHIN a block. It cannot separate
# Q06/Q07/Q08 (irritability / nervousness / anxiety) from each other, nor
# Q15 from Q16. Status is recorded as PARTIAL for that reason.

suppressMessages(library(irw))
TABLE <- "kim2020_ams"

GROUPS <- list(
  psychological     = c(6, 7, 8, 11, 13),
  somato_vegetative = c(1, 2, 3, 4, 5, 9, 10),
  sexual            = c(12, 14, 15, 16, 17)
)
lbl <- character(0)
for (g in names(GROUPS)) lbl[sprintf("Q%02d", GROUPS[[g]])] <- g

d <- irw::irw_fetch(TABLE)
d$resp <- suppressWarnings(as.numeric(d$resp))
d$id <- as.character(d$id); d$item <- as.character(d$item)
ids <- sort(unique(d$id)); items <- sprintf("Q%02d", 1:17)
mat <- matrix(NA_real_, length(ids), length(items), dimnames = list(ids, items))
mat[cbind(match(d$id, ids), match(d$item, items))] <- d$resp
cm <- stats::cor(mat, use = "pairwise.complete.obs")
mns <- colMeans(mat, na.rm = TRUE)

cat("--- nearest neighbour of each item, vs its canonical AMS subscale ---\n")
hits <- 0
for (a in items) {
  r <- cm[a, setdiff(items, a)]
  best <- names(which.max(r))
  hit <- lbl[[best]] == lbl[[a]]
  hits <- hits + hit
  cat(sprintf("%-4s %-18s -> %-4s %-18s r=%.3f  %s\n",
              a, lbl[[a]], best, lbl[[best]], max(r), if (hit) "HIT" else "MISS"))
}
cat(sprintf("\nsame-subscale nearest neighbours: %d/17 (threshold 13)\n", hits))

pair <- t(utils::combn(items, 2))
same <- lbl[pair[, 1]] == lbl[pair[, 2]]
rr <- cm[pair]
cat(sprintf("mean within-subscale r = %.3f   mean between-subscale r = %.3f\n",
            mean(rr[same]), mean(rr[!same])))

tri <- c("Q15", "Q16", "Q17")
tri_r <- c(cm["Q15","Q16"], cm["Q15","Q17"], cm["Q16","Q17"])
cat(sprintf("\nsexual triad Q15/Q16/Q17 mutual r: %.3f %.3f %.3f\n",
            tri_r[1], tri_r[2], tri_r[3]))
tri_closed <- TRUE
for (a in tri) {
  r <- sort(cm[a, setdiff(items, a)], decreasing = TRUE)
  cat(sprintf("  %s top-3 correlates: %s\n", a,
              paste(sprintf("%s=%.3f", names(r)[1:3], r[1:3]), collapse = ", ")))
  tri_closed <- tri_closed && setequal(names(r)[1:2], setdiff(tri, a))
}
cat("  criterion: the other two triad members are each item's top-2 correlates -> ",
    if (tri_closed) "yes\n" else "no\n", sep = "")
top3 <- names(sort(mns, decreasing = TRUE))[1:3]
cat("three highest item means: ",
    paste(sprintf("%s=%.3f", top3, mns[top3]), collapse = ", "),
    "\n  (the three explicitly sexual AMS items should be the most endorsed in an\n",
    "   andrology sample; 4th is ", names(sort(mns, decreasing = TRUE))[4], "=",
    sprintf("%.3f", sort(mns, decreasing = TRUE)[4]), ")\n", sep = "")

cat(sprintf("\nlowest item mean: %s = %.3f (AMS item 14, decrease in beard growth --\n",
            names(which.min(mns)), min(mns)))
cat("  the item the source paper calls 'generally ignored'; next lowest is ",
    names(sort(mns))[2], "=", sprintf("%.3f", sort(mns)[2]),
    ", a near tie, so this is context, not a criterion.\n", sep = "")

ok <- (hits >= 13) &&
      (mean(rr[same]) > mean(rr[!same])) &&
      tri_closed &&
      setequal(top3, tri)

cat("\nNot established by this route: the order of items WITHIN a subscale\n",
    "(Q06/Q07/Q08 and Q15/Q16 are interchangeable under these tests).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
